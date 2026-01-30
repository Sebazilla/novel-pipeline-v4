#!/usr/bin/env python3
"""
Novel Pipeline V4
- Gemini 3 Pro für Planung + Self-Critique (ersetzt GPT)
- Claude Code CLI für Schreiben
- Qdrant für Kontext-Speicherung
- Telegram Approvals an Checkpoints
- Versioniertes Speichern (jede Iteration)
"""

import os
import subprocess
import requests
import re
import time
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# ============================================================
# CONFIG
# ============================================================

# Aus .env oder Environment
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")

GEMINI_MODEL = "gemini-3-pro-preview"

# ============================================================
# LOGGING
# ============================================================

LOG_FILE = None

def log(message: str, also_print: bool = True):
    """Log to file and optionally print"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    if also_print:
        print(line)
    if LOG_FILE:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")

# ============================================================
# API CALLS
# ============================================================

def call_gemini(prompt: str, max_tokens: int = 16000, retries: int = 3) -> str:
    """Gemini API Call mit Retry-Logik"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": max_tokens}
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=300)
            data = response.json()
            
            if "candidates" not in data:
                log(f"    ⚠️ Gemini Response ohne candidates: {data.get('error', data)}")
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                return ""
            
            content = data["candidates"][0].get("content", {})
            if not content or "parts" not in content:
                finish = data["candidates"][0].get("finishReason", "unknown")
                log(f"    ⚠️ Gemini empty response (finishReason: {finish})")
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                return ""
            return content["parts"][0]["text"]
            
        except Exception as e:
            log(f"    ⚠️ Gemini Fehler (Versuch {attempt + 1}): {e}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    return ""


def call_claude(prompt: str, timeout: int = 600) -> str:
    """Claude Code CLI aufrufen"""
    try:
        result = subprocess.run(
            ["claude", "--print", prompt], 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        log("    ⚠️ Claude Timeout")
        return ""
    except Exception as e:
        log(f"    ⚠️ Claude Fehler: {e}")
        return ""


# ============================================================
# TELEGRAM
# ============================================================

def telegram_send(message: str) -> bool:
    """Nachricht an Telegram senden"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        # Markdown escapen für Telegram
        text = message[:4000]  # Telegram Limit
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }, timeout=30)
        return True
    except Exception as e:
        log(f"    ⚠️ Telegram Fehler: {e}")
        return False


def telegram_approval(message: str, timeout_minutes: int = 60) -> bool:
    """Telegram Approval mit JA/NEIN Antwort"""
    telegram_send(message + "\n\n✅ JA = weiter\n❌ NEIN = neu generieren")
    
    log(f"      📱 Warte auf Approval (max {timeout_minutes} min)...")
    
    # Letzte Update-ID merken
    try:
        updates = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
            timeout=10
        ).json()
        last_update_id = updates["result"][-1]["update_id"] if updates.get("result") else 0
    except:
        last_update_id = 0
    
    start_time = time.time()
    while time.time() - start_time < timeout_minutes * 60:
        time.sleep(3)
        
        try:
            updates = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
                params={"offset": last_update_id + 1},
                timeout=10
            ).json()
            
            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                text = update.get("message", {}).get("text", "").lower().strip()
                
                if text in ["ja", "yes", "j", "y", "ok", "👍"]:
                    log(f"      ✅ Approved!")
                    return True
                elif text in ["nein", "no", "n", "👎"]:
                    log(f"      ❌ Abgelehnt")
                    return False
        except:
            continue
    
    log(f"      ⏰ Timeout - fahre fort")
    return True


# ============================================================
# QDRANT + OPENAI EMBEDDINGS
# ============================================================

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "memory_novelpipeline")


def get_embedding(text: str) -> List[float]:
    """OpenAI Embedding für Text generieren (1536 dims)"""
    try:
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": text[:8000]  # Token limit
        }
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["data"][0]["embedding"]
    except Exception as e:
        log(f"   ⚠️ OpenAI Embedding Fehler: {e}")
        return []


def qdrant_init_collection(collection_name: str = None):
    """Prüft ob Qdrant Collection erreichbar ist"""
    collection_name = collection_name or QDRANT_COLLECTION
    try:
        r = requests.get(f"{QDRANT_URL}/collections/{collection_name}", timeout=5)
        if r.status_code == 200:
            log(f"   ✓ Qdrant Collection '{collection_name}' verbunden")
            return True
        log(f"   ⚠️ Qdrant Collection '{collection_name}' nicht gefunden")
        return False
    except Exception as e:
        log(f"   ⚠️ Qdrant nicht erreichbar: {e}")
        return False


def qdrant_store(content: str, metadata: dict, collection: str = None):
    """Text mit OpenAI Embedding in Qdrant speichern"""
    collection = collection or QDRANT_COLLECTION
    try:
        # OpenAI Embedding
        embedding = get_embedding(content[:4000])
        if not embedding:
            return False
        
        # Unique ID aus Metadata
        point_id = int(hashlib.md5(json.dumps(metadata, sort_keys=True).encode()).hexdigest()[:8], 16)
        
        requests.put(f"{QDRANT_URL}/collections/{collection}/points", json={
            "points": [{
                "id": point_id,
                "vector": embedding,
                "payload": {
                    "content": content[:15000],
                    "timestamp": datetime.now().isoformat(),
                    **metadata
                }
            }]
        }, timeout=15)
        return True
    except Exception as e:
        log(f"   ⚠️ Qdrant Store Fehler: {e}")
        return False


def qdrant_search(query: str, collection: str = None, limit: int = 5) -> List[dict]:
    """Semantische Suche in Qdrant mit OpenAI Embedding"""
    collection = collection or QDRANT_COLLECTION
    try:
        embedding = get_embedding(query)
        if not embedding:
            return []
        
        r = requests.post(f"{QDRANT_URL}/collections/{collection}/points/search", json={
            "vector": embedding,
            "limit": limit,
            "with_payload": True
        }, timeout=15)
        
        if r.status_code == 200:
            return [hit["payload"] for hit in r.json().get("result", [])]
        return []
    except Exception as e:
        log(f"   ⚠️ Qdrant Search Fehler: {e}")
        return []


# ============================================================
# VERSIONIERTES SPEICHERN
# ============================================================

def save_versioned(output_dir: Path, filename: str, content: str, iteration: int = None):
    """Speichert mit Versionierung - überschreibt nichts"""
    base = filename.rsplit(".", 1)[0]
    ext = filename.rsplit(".", 1)[1] if "." in filename else "md"
    
    if iteration is not None:
        versioned_name = f"{base}_v{iteration:02d}.{ext}"
    else:
        versioned_name = filename
    
    filepath = output_dir / versioned_name
    filepath.write_text(content, encoding="utf-8")
    
    # Auch immer die "aktuelle" Version speichern
    current = output_dir / filename
    current.write_text(content, encoding="utf-8")
    
    return filepath


# ============================================================
# REGELWERK V4 - 7-PHASEN SUSPENSE-BACKBONE
# ============================================================

REGELWERK = """Du planst einen packenden Liebesroman mit SUSPENSE-BACKBONE.

GRUNDPRINZIP: "Beziehung ist der Motor, Plot ist das Fundament. 
Jede emotionale Szene passiert während äußerer Eskalation."

═══════════════════════════════════════════════════════════════
7-PHASEN STRUKTUR (STRIKT EINHALTEN!)
═══════════════════════════════════════════════════════════════

PHASE I (0-15%): IMMEDIATE TENSION + FLAWED VICTORY
- Heldin gewinnt eine Schlacht, erschafft dabei aber ein größeres Problem
- Love Interest taucht auf - sofortige Spannung/Konflikt
- Äußere Bedrohung wird etabliert (Stufe 1: Störung)
- Ende: Sie hat "gewonnen" aber der Preis wird sichtbar

PHASE II (15-35%): FORCED PROXIMITY + ESCALATION  
- Zwangsläufige Nähe (müssen zusammenarbeiten)
- Enemies-to-Lovers Dynamik: Wortgefechte mit Subtext
- Äußere Bedrohung eskaliert (Stufe 2: Verfolgung)
- Erste körperliche Nähe, Fast-Küsse, Spannung
- Ende: Erster echter Kuss WÄHREND einer Gefahrensituation

PHASE III (35-55%): INTIMACY UNDER FIRE
- Sex-Szene mit emotionalen Stakes (nicht nur körperlich)
- Midpoint-Twist: Große Enthüllung verändert alles
- Sie vertrauen einander - aber die Welt brennt
- Äußere Bedrohung wird persönlich (Stufe 3: Konfrontation)
- Ende: Moment der Ruhe vor dem Sturm

PHASE IV (55-75%): SEPARATION FROM PROTECTION
- Sie werden getrennt (äußerer Zwang, nicht Missverständnis!)
- Heartbreak ohne toxisches Verhalten
- Beide kämpfen auf eigene Faust
- Die Bedrohung trifft ins Persönliche
- Ende: All-is-lost Moment für die Beziehung

PHASE V (75-85%): ALL IS LOST (FORCED)
- Äußere Katastrophe zwingt sie wieder zusammen
- Aber: Emotionale Schuld/Distanz steht zwischen ihnen
- Tiefpunkt: Sie glaubt, sie hat ihn verloren (oder umgekehrt)
- Ende: Sie muss sich entscheiden - Mission oder Liebe?

PHASE VI (85-95%): ACTIVE FINALE
- Heldin handelt entschlossen (NICHT gerettet werden!)
- Hero respektiert ihre Entscheidung, unterstützt
- Äußerer Konflikt wird gelöst (sie ist zentral beteiligt)
- Emotionales Bekenntnis WÄHREND der Action
- Ende: Bedrohung besiegt, aber noch kein HEA-Moment

PHASE VII (95-100%): NEW EQUILIBRIUM
- Ruhige Szene: Neues Gleichgewicht
- Happy End ohne ihre Stärke zu diminuieren
- Zukunft angedeutet
- Callback zu Phase I (zirkuläre Struktur)

═══════════════════════════════════════════════════════════════
3 SUSPENSE-ESKALATIONSSTUFEN (parallel zur Romanze!)
═══════════════════════════════════════════════════════════════

Stufe 1 - STÖRUNG (Phase I-II):
- Beobachtung, erste Bedrohung, Unbehagen
- "Etwas stimmt nicht" - noch keine direkte Gefahr

Stufe 2 - VERFOLGUNG (Phase II-IV):  
- Sie sind Teil des Problems geworden
- Aktive Bedrohung, müssen reagieren

Stufe 3 - KONFRONTATION (Phase IV-VI):
- Sie sind das Ziel
- Finale Auseinandersetzung

═══════════════════════════════════════════════════════════════
5 NEBENCHARAKTER-ARCHETYPEN (mindestens 3 verwenden!)
═══════════════════════════════════════════════════════════════

1. SPIEGEL DER HELDIN - zeigt was sie werden könnte
2. KONTRAST ZUM HERO - zeigt was er NICHT ist  
3. MORALISCHE AUTORITÄT - stellt unbequeme Fragen
4. EMOTIONALER KATALYSATOR - zwingt Leads zusammen
5. UNSICHERHEITSFAKTOR - hält Spannung hoch (Verräter?)

═══════════════════════════════════════════════════════════════
ANTAGONIST-REGEL
═══════════════════════════════════════════════════════════════

- KEIN Redemption-Arc!
- ABER: Klares Motiv + persönliche Verbindung zu Leads
- Muss früh etabliert werden (nicht erst in Phase V)

═══════════════════════════════════════════════════════════════
TECHNISCHE VORGABEN
═══════════════════════════════════════════════════════════════

- Ziel: 70.000-85.000 Wörter
- 18-22 Kapitel
- Jedes Kapitel: 3.000-4.500 Wörter
- Single POV (Heldin)
- Mindestens 1, maximal 2 explizite Sex-Szenen
- Kapitel enden mit Hook oder emotionalem Beat
"""

STIL = """
═══════════════════════════════════════════════════════════════
GENRE & STIL-DEFINITION
═══════════════════════════════════════════════════════════════

DU SCHREIBST: Einen modernen Romantic Suspense Roman
STIL-VORBILDER: Linda Howard (modern adaptiert) + Julia Quinn (Gedankenwelt)
DYNAMIK: Enemies-to-Lovers, Fast Burn

HELDIN:
- Emanzipiert, selbstständig, kompetent in ihrem Beruf
- Braucht KEINEN Retter - löst Probleme selbst
- Hat Schwächen, aber keine Hilflosigkeit
- Schlagfertig, nicht naiv

ERZÄHLPERSPEKTIVE:
- Grundsätzlich: Sie/Er-Form (dritte Person)
- AUSNAHME - Gedanken der Heldin: Ich-Form, KURSIV
  Beispiel: Sie starrte ihn an. *Was bildete er sich eigentlich ein?*
- Gedanken sind direkt, selbstironisch, ehrlich (Julia Quinn Stil)
- Nie "sie dachte, dass..." - sondern direkt kursiv

PACING:
- SCHNELL - kurze Kapitel, häufige Szenenwechsel
- Jedes Kapitel endet mit Hook oder emotionalem Moment
- Action und Dialog dominieren, minimale Beschreibungen
- Keine langen Landschaftsbeschreibungen

DIALOGE:
- Schlagfertig, witzig, sexy
- Subtext wichtiger als Text
- Necken, provozieren, herausfordern
- Wortgefechte mit Spannung aufgeladen

EROTIK:
- Aufbauende Spannung > explizite Szenen
- Fast-Küsse, unterbrochene Momente, Körperbewusstsein
- Wenn es passiert: sinnlich aber nicht vulgär
- Consent ist selbstverständlich, nie problematisiert

TON:
- Warm, humorvoll, emotional
- Hoffnung scheint durch auch in dunklen Momenten
- Der Leser soll lachen UND mitfiebern
- Moderne Sprache, keine altmodischen Floskeln
"""

SELF_CRITIQUE_PROMPT = """
═══════════════════════════════════════════════════════════════
KRITISCHE SELBST-PRÜFUNG
═══════════════════════════════════════════════════════════════

WICHTIG: Schreib mir NICHT was ich hören möchte.
Schreib was SINN MACHT.

Prüfe deine Arbeit SCHONUNGSLOS:
1. Ist das WIRKLICH gut oder nur "okay"?
2. Wo sind die SCHWACHEN Stellen?
3. Was würde ein erfahrener Lektor kritisieren?
4. Folgt es der 7-Phasen-Struktur EXAKT?
5. Ist die Suspense-Eskalation SICHTBAR?
6. Würdest DU das lesen wollen?

Sei EHRLICH. Sei KRITISCH. Dann VERBESSERE.
"""


# ============================================================
# PHASE 1: GROB-GLIEDERUNG
# ============================================================

def phase1_gliederung(setting: str, output_dir: Path, iterations: int = 3) -> str:
    """Grob-Gliederung mit Gemini Self-Critique"""
    
    log(f"\n{'='*60}")
    log("PHASE 1: GROB-GLIEDERUNG")
    log(f"{'='*60}")
    
    telegram_send(f"🚀 *Phase 1 gestartet*\n\nSetting: {setting}")
    
    prompt = f"""{REGELWERK}

{STIL}

Setting: {setting}

AUFGABE: Erstelle eine DETAILLIERTE Gliederung für diesen Roman.

Die Gliederung MUSS enthalten:

## 1. TITEL
- Titel-Vorschlag (packend, Genre-typisch)

## 2. HAUPTCHARAKTERE

### HELDIN (Protagonistin)
- Name, Alter, Beruf
- Äußere Ziele (was will sie erreichen?)
- Innerer Konflikt (was hält sie zurück?)
- Schwäche (die sie überwinden muss)
- Stärken (die sie zur Heldin machen)
- Typische Verhaltensweisen, Macken, Eigenheiten

### HERO (Love Interest)
- Name, Alter, Beruf
- Sein Geheimnis
- Was macht ihn zum "Feind" am Anfang?
- Seine Verletzlichkeit (unter der harten Schale)
- Warum ist ER der Richtige für SIE?

### ANTAGONIST
- Name, Rolle, Motiv
- Persönliche Verbindung zu den Leads
- Warum ist er/sie gefährlich?

## 3. NEBENCHARAKTERE (5-6 Personen, DETAILLIERT!)

Für JEDEN Nebencharakter:
- Name, Alter, Beruf/Rolle
- Beziehung zu Heldin und/oder Hero
- Archetyp (Spiegel, Kontrast, Mentor, Katalysator, Unsicherheitsfaktor)
- Innere Motivation (was treibt diese Person an?)
- Typisches Verhalten, Sprechweise, Eigenheiten
- Funktion in der Story (welche Szenen? welche Konflikte?)
- Charakter-Arc (verändert sich diese Person?)

## 4. DIE 7 PHASEN
Für jede Phase:
- Welche Kapitel (Nummern!)
- Kernszenen (konkret!)
- Suspense-Level (1/2/3)
- Welche Nebencharaktere treten auf?
- Emotionaler Beat am Ende

## 5. ÄUSSERER KONFLIKT
- Die konkrete Bedrohung (nicht vage!)
- Eskalationsstufen

PRÜFE VOR DER AUSGABE:
- Stimmen die Proportionen (15% / 20% / 20% / 20% / 10% / 10% / 5%)?
- Eskaliert die Suspense PARALLEL zur Romanze?
- Hat jede Phase einen KLAREN Höhepunkt?
"""

    gliederung = call_gemini(prompt, max_tokens=12000)
    log(f"   ✓ Erste Version ({len(gliederung)} Zeichen)")
    save_versioned(output_dir, "01_gliederung.md", gliederung, iteration=1)
    
    # Self-Critique Loop
    for i in range(iterations):
        log(f"\n   [Iteration {i+2}/{iterations+1}] Self-Critique...")
        
        critique_prompt = f"""{SELF_CRITIQUE_PROMPT}

Hier ist die aktuelle Roman-Gliederung:

{gliederung}

AUFGABE:
1. KRITISIERE diese Gliederung SCHONUNGSLOS
2. Liste KONKRETE Schwächen auf
3. Dann: Gib die VOLLSTÄNDIG ÜBERARBEITETE Gliederung aus

Die überarbeitete Version muss KOMPLETT sein - nicht nur die Änderungen!
"""
        
        verbessert = call_gemini(critique_prompt, max_tokens=12000)
        
        if len(verbessert) > len(gliederung) * 0.5:
            gliederung = verbessert
            log(f"   ✓ Überarbeitet ({len(gliederung)} Zeichen)")
            save_versioned(output_dir, "01_gliederung.md", gliederung, iteration=i+2)
        else:
            log(f"   ⚠️ Überarbeitung zu kurz, behalte vorherige Version")
    
    # TELEGRAM APPROVAL
    log(f"\n   📱 Sende Synopsis zur Freigabe...")
    
    synopsis_prompt = f"""Fasse diese Gliederung in einer SPANNENDEN Synopsis zusammen (max 800 Zeichen):

{gliederung[:6000]}

Enthalten muss:
- Heldin + Hero (Namen!)
- Der zentrale Konflikt
- Was ist der Hook?

NUR die Synopsis, keine Einleitung."""

    synopsis = call_gemini(synopsis_prompt, max_tokens=500)
    
    max_attempts = 5
    for attempt in range(max_attempts):
        approved = telegram_approval(
            f"📖 *SYNOPSIS* (Versuch {attempt+1}/{max_attempts}):\n\n{synopsis[:1500]}"
        )
        
        if approved:
            # In Qdrant speichern (erst nach Approval!)
            qdrant_store(gliederung, {
                "type": "gliederung",
                "phase": 1,
                "setting": setting,
                "approved": True
            })
            break
        else:
            log(f"   🔄 Generiere neue Version...")
            gliederung = call_gemini(prompt, max_tokens=12000)
            for j in range(iterations):
                critique_prompt = f"""{SELF_CRITIQUE_PROMPT}\n\n{gliederung}\n\nVOLLSTÄNDIG ÜBERARBEITETE Gliederung:"""
                gliederung = call_gemini(critique_prompt, max_tokens=12000)
            synopsis = call_gemini(synopsis_prompt, max_tokens=500)
            save_versioned(output_dir, "01_gliederung.md", gliederung, iteration=attempt+iterations+2)
    
    # Finale Version speichern
    save_versioned(output_dir, "01_gliederung.md", gliederung)
    
    log(f"\n✓ Phase 1 abgeschlossen!")
    return gliederung


# ============================================================
# PHASE 2: AKT-GLIEDERUNGEN
# ============================================================

def phase2_akte(gliederung: str, output_dir: Path) -> dict:
    """Detaillierte Akt-Gliederungen mit Self-Critique"""
    
    log(f"\n{'='*60}")
    log("PHASE 2: AKT-GLIEDERUNGEN")
    log(f"{'='*60}")
    
    telegram_send("📋 *Phase 2 gestartet*: Akt-Gliederungen")
    
    akte = {}
    akt_phasen = {
        1: "Phase I + II (0-35%): Setup + Forced Proximity",
        2: "Phase III + IV (35-75%): Intimacy + Separation", 
        3: "Phase V + VI + VII (75-100%): Crisis + Finale + HEA"
    }
    
    for akt_num, beschreibung in akt_phasen.items():
        log(f"\n   [Akt {akt_num}] {beschreibung}")
        
        prompt = f"""{REGELWERK}

GESAMT-GLIEDERUNG:
{gliederung}

AUFGABE: Detaillierte Gliederung für AKT {akt_num}
({beschreibung})

Für JEDES Kapitel in diesem Akt:
1. Kapitel-Nummer und Titel
2. Welche Phase(n) der 7-Phasen-Struktur
3. Suspense-Level (1/2/3)
4. Kernszenen (2-4 pro Kapitel, KONKRET!)
5. Emotionaler Beat am Ende
6. Wortzahl-Ziel (Gesamt ~80.000 Wörter, 18-22 Kapitel)
"""
        
        akt = call_gemini(prompt, max_tokens=8000)
        log(f"      ✓ Erstellt ({len(akt)} Zeichen)")
        save_versioned(output_dir, f"02_akt_{akt_num}.md", akt, iteration=1)
        
        # Self-Critique
        critique = call_gemini(f"""{SELF_CRITIQUE_PROMPT}

Akt {akt_num} Gliederung:
{akt}

KRITIK + VOLLSTÄNDIG ÜBERARBEITETE Akt-Gliederung:""", max_tokens=8000)
        
        if len(critique) > len(akt) * 0.5:
            akt = critique
            log(f"      ✓ Überarbeitet")
            save_versioned(output_dir, f"02_akt_{akt_num}.md", akt, iteration=2)
        
        akte[f"akt_{akt_num}"] = akt
        save_versioned(output_dir, f"02_akt_{akt_num}.md", akt)
        
        # In Qdrant
        qdrant_store(akt, {"type": "akt", "akt_num": akt_num})
    
    log(f"\n✓ Phase 2 abgeschlossen!")
    return akte


# ============================================================
# PHASE 2.5: KAPITEL-GLIEDERUNGEN  
# ============================================================

def phase2_5_kapitel(gliederung: str, akte: dict, output_dir: Path) -> list:
    """Detaillierte Szenen-Gliederung pro Kapitel"""
    
    log(f"\n{'='*60}")
    log("PHASE 2.5: KAPITEL-GLIEDERUNGEN")
    log(f"{'='*60}")
    
    telegram_send("📝 *Phase 2.5 gestartet*: Kapitel-Gliederungen")
    
    kapitel_liste = []
    kapitel_nr = 1
    
    for akt_num in [1, 2, 3]:
        log(f"\n   [Akt {akt_num}]")
        akt_text = akte[f"akt_{akt_num}"]
        
        # Kapitel aus Akt extrahieren
        matches = re.findall(r'Kapitel\s*(\d+)[:\s]*([^\n]+)', akt_text, re.IGNORECASE)
        if not matches:
            # Fallback: Schätze 6-7 Kapitel pro Akt
            matches = [(str(kapitel_nr + i), f"Kapitel {kapitel_nr + i}") for i in range(7)]
        
        for _, titel in matches:
            log(f"      [Kapitel {kapitel_nr}] {titel[:40]}...")
            
            prompt = f"""{STIL}

KONTEXT:
{gliederung[:3000]}

AKT {akt_num}:
{akt_text[:2000]}

AUFGABE: DETAILLIERTE Szenen-Gliederung für KAPITEL {kapitel_nr}: {titel}

## METADATEN
- Nummer: {kapitel_nr}
- Titel: {titel}
- Wortzahl: [3000-4000]
- Phase: [Welche der 7 Phasen?]
- Suspense-Level: [1/2/3]
- Emotionaler Bogen: [Start] → [Ende]

## SZENEN (3-5 pro Kapitel)

### Szene X: [Titel]
- Ort: [KONKRET]
- Figuren: [Namen]
- Ziel: [Was MUSS passieren?]
- Beats:
  1. [Einstieg]
  2. [Entwicklung]  
  3. [Wendepunkt/Hook]
- Wichtige Momente: [Spezifische Dialoge/Aktionen]
- Atmosphäre: [Stimmung]

## VERBINDUNGEN
- Anknüpfung an Kapitel {kapitel_nr - 1}
- Setup für Kapitel {kapitel_nr + 1}

## CONSTRAINTS
- Was darf NICHT passieren?
"""
            
            kap_gliederung = call_gemini(prompt, max_tokens=4000)
            save_versioned(output_dir, f"02.5_kapitel_{kapitel_nr:02d}_gliederung.md", kap_gliederung, iteration=1)
            
            # Self-Critique
            improved = call_gemini(f"""{SELF_CRITIQUE_PROMPT}

Kapitel-Gliederung:
{kap_gliederung}

KRITIK + VOLLSTÄNDIG ÜBERARBEITETE Kapitel-Gliederung:""", max_tokens=4000)
            
            if len(improved) > len(kap_gliederung) * 0.5:
                kap_gliederung = improved
                save_versioned(output_dir, f"02.5_kapitel_{kapitel_nr:02d}_gliederung.md", kap_gliederung, iteration=2)
            
            log(f"         ✓ Erstellt ({len(kap_gliederung)} Zeichen)")
            
            kapitel_liste.append({
                "nummer": kapitel_nr,
                "titel": titel.strip(),
                "akt": akt_num,
                "gliederung": kap_gliederung
            })
            
            # In Qdrant
            qdrant_store(kap_gliederung, {
                "type": "kapitel_gliederung",
                "kapitel": kapitel_nr,
                "akt": akt_num
            })
            
            save_versioned(output_dir, f"02.5_kapitel_{kapitel_nr:02d}_gliederung.md", kap_gliederung)
            kapitel_nr += 1
    
    # TELEGRAM APPROVAL für Kapitel-Struktur
    log(f"\n   📱 Sende Kapitel-Übersicht zur Freigabe...")
    
    uebersicht = "\n".join([
        f"Kap {k['nummer']}: {k['titel'][:50]}" 
        for k in kapitel_liste
    ])
    
    telegram_approval(f"📚 *KAPITEL-STRUKTUR*\n\n{uebersicht[:1500]}\n\n*{len(kapitel_liste)} Kapitel total*")
    
    log(f"\n✓ Phase 2.5 abgeschlossen! {len(kapitel_liste)} Kapitel")
    return kapitel_liste


# ============================================================
# PHASE 3: SCHREIBEN (Claude Code)
# ============================================================

def phase3_schreiben(kapitel: dict, vorheriges_kapitel: str, output_dir: Path) -> str:
    """Kapitel mit Claude Code schreiben"""
    
    nr = kapitel["nummer"]
    titel = kapitel["titel"]
    gliederung = kapitel["gliederung"]
    
    # Wortzahl aus Gliederung
    match = re.search(r'Wortzahl[:\s]*\[?(\d+)', gliederung)
    ziel_wortzahl = int(match.group(1)) if match else 3500
    
    log(f"\n   [Kapitel {nr}] Schreiben (Ziel: {ziel_wortzahl} Wörter)...")
    
    # Kontext vom vorherigen Kapitel
    kontext = ""
    if vorheriges_kapitel and nr > 1:
        worte = vorheriges_kapitel.split()
        if len(worte) > 2000:
            kontext = " ".join(worte[-2000:])
        else:
            kontext = vorheriges_kapitel
        
        kontext = f"""
=== ENDE KAPITEL {nr-1} (für Kontinuität) ===
{kontext}
=== ENDE KONTEXT ===
"""
    
    # Relevanten Kontext aus Qdrant holen
    qdrant_context = qdrant_search(f"Kapitel {nr} {titel}", limit=2)
    extra_context = ""
    if qdrant_context:
        extra_context = "\n\n=== ZUSÄTZLICHER KONTEXT ===\n"
        for ctx in qdrant_context:
            if ctx.get("type") == "kapitel_gliederung":
                extra_context += f"[Gliederung Kap {ctx.get('kapitel')}]: {ctx.get('content', '')[:500]}...\n"
    
    prompt = f"""{STIL}

{kontext}

{extra_context}

Du schreibst KAPITEL {nr}: {titel}

GLIEDERUNG (folge ihr EXAKT):
{gliederung}

REGELN:
- Exakt {ziel_wortzahl} Wörter (±10%)
- Folge den Szenen und Beats GENAU
- Single POV (Heldin)
- Dialoge: schlagfertig, mit Subtext
- Gedanken der Heldin: direkt, selbstironisch
- Ende mit Hook oder emotionalem Beat
- KEINE Meta-Kommentare, beginne DIREKT mit dem Text

BEGINNE JETZT:"""

    text = call_claude(prompt)
    wortzahl = len(text.split())
    log(f"      ✓ Geschrieben: {wortzahl} Wörter")
    save_versioned(output_dir, f"kapitel_{nr:02d}.md", text, iteration=1)
    
    # Zu kurz? Anreichern
    if wortzahl < ziel_wortzahl * 0.75:
        log(f"      ⚠️ Zu kurz ({wortzahl}/{ziel_wortzahl}) - reichere an...")
        
        anreicherung = f"""{STIL}

Der Text hat {wortzahl} Wörter, Ziel: {ziel_wortzahl}

NICHT aufblähen! Stattdessen BEREICHERN durch:
- Mehr Spannung zwischen den Charakteren
- Ein weiteres Wortgefecht
- Tiefere emotionale Beats
- Eine Komplikation

AKTUELLER TEXT:
{text}

Gib den VOLLSTÄNDIGEN angereicherten Text aus:"""

        text = call_claude(anreicherung)
        wortzahl = len(text.split())
        log(f"      ✓ Angereichert: {wortzahl} Wörter")
        save_versioned(output_dir, f"kapitel_{nr:02d}.md", text, iteration=2)
    
    return text


# ============================================================
# PHASE 4: POLISH (Gemini Critique + Claude Fix)
# ============================================================

def phase4_polish(text: str, kapitel_nr: int, output_dir: Path) -> str:
    """Kapitel polieren mit Gemini Critique"""
    
    log(f"   [Kapitel {kapitel_nr}] Polish...")
    
    # Gemini kritisiert (statt GPT)
    kritik = call_gemini(f"""{SELF_CRITIQUE_PROMPT}

Prüfe diesen Romantext auf:
1. Wortwiederholungen
2. Satzfragmente oder abgehackte Absätze
3. Unnatürliche Dialoge
4. Tempo-Probleme
5. Fehlende Sinnesbeschreibungen
6. Out-of-Character Momente

TEXT:
{text[:12000]}

KONKRETE Verbesserungen (Liste):""", max_tokens=2000)
    
    # Claude überarbeitet
    polished = call_claude(f"""Du erhältst einen Roman-Text und Feedback dazu.

STIL-REGELN:
{STIL}

FEEDBACK:
{kritik}

ORIGINALTEXT:
{text}

AUFGABE: Setze das Feedback um. Gib den VOLLSTÄNDIGEN überarbeiteten Text aus.
Beginne DIREKT mit dem ersten Satz des Kapitels:""")
    
    if len(polished.split()) > len(text.split()) * 0.5:
        log(f"      ✓ Poliert ({len(polished.split())} Wörter)")
        save_versioned(output_dir, f"kapitel_{kapitel_nr:02d}.md", polished, iteration=3)
        return polished
    else:
        log(f"      ⚠️ Polish fehlgeschlagen, behalte Original")
        return text


# ============================================================
# PHASE 5: FLOW-CHECK
# ============================================================

def phase5_flow_check(chapters: list, output_dir: Path) -> list:
    """Prüft und korrigiert Übergänge zwischen Kapiteln"""
    
    log(f"\n{'='*60}")
    log("PHASE 5: FLOW-CHECK (Kapitel-Übergänge)")
    log(f"{'='*60}")
    
    telegram_send("🔄 *Phase 5 gestartet*: Flow-Check")
    
    corrected = [chapters[0]]
    
    for i in range(1, len(chapters)):
        prev = corrected[i-1]
        curr = chapters[i]
        
        log(f"\n   Prüfe Übergang {i} → {i+1}...")
        
        # Relevante Teile extrahieren
        prev_words = prev.split()
        curr_words = curr.split()
        prev_end = ' '.join(prev_words[-(len(prev_words)//3):])
        curr_start = ' '.join(curr_words[:len(curr_words)//3])
        
        check = call_gemini(f"""Prüfe den Übergang zwischen zwei Kapiteln:

ENDE KAPITEL {i}:
{prev_end}

ANFANG KAPITEL {i+1}:
{curr_start}

Prüfe:
1. Wissensstand-Konsistenz
2. Emotionale Kontinuität
3. Zeitliche Logik
4. Fakten-Konsistenz (Namen, Orte)

Antworte:
- "OK" wenn alles passt
- Oder liste die KONKRETEN Probleme""", max_tokens=1000)
        
        if "OK" in check.upper() and len(check) < 100:
            log(f"      ✅ OK")
            corrected.append(curr)
        else:
            log(f"      ⚠️ Probleme - korrigiere...")
            
            fixed = call_claude(f"""Der Übergang zwischen Kapiteln hat Probleme:

PROBLEME:
{check}

ENDE KAPITEL {i}:
{prev_end}

KAPITEL {i+1} (vollständig):
{curr}

AUFGABE: Überarbeite Kapitel {i+1} so dass es nahtlos anschließt.
Behebe die Probleme, behalte den Rest.

{STIL}

VOLLSTÄNDIG KORRIGIERTES KAPITEL:""")
            
            if len(fixed.split()) > len(curr.split()) * 0.5:
                corrected.append(fixed)
                save_versioned(output_dir, f"kapitel_{i+1:02d}.md", fixed, iteration=4)
                log(f"      ✓ Korrigiert")
            else:
                corrected.append(curr)
    
    log(f"\n✓ Phase 5 abgeschlossen!")
    return corrected


# ============================================================
# PHASE 6: GESAMT-CHECK
# ============================================================

def phase6_check(full_novel: str, output_dir: Path) -> str:
    """Gesamt-Qualitätsprüfung"""
    
    log(f"\n{'='*60}")
    log("PHASE 6: GESAMT-CHECK")
    log(f"{'='*60}")
    
    telegram_send("🔍 *Phase 6 gestartet*: Qualitäts-Check")
    
    report = call_gemini(f"""Prüfe diesen Roman auf:

1. CHARAKTERKONSISTENZ
   - Namen korrekt?
   - Eigenschaften konsistent?
   - Wissen der Figuren logisch?

2. PLOT-LÖCHER
   - Unbeantwortete Fragen?
   - Logikfehler?
   - Vergessene Handlungsstränge?

3. ROMANCE-ARC
   - Enemies-to-Lovers glaubwürdig?
   - Spannung aufgebaut?
   - HEA earned?

4. SUSPENSE-ARC
   - Eskalation sichtbar (3 Stufen)?
   - Antagonist präsent?
   - Finale befriedigend?

5. PACING
   - Durchhänger?
   - Zu schnelle Stellen?

ROMAN (Auszug - ca. 50.000 Zeichen):
{full_novel[:50000]}

DETAILLIERTER BERICHT mit konkreten Fundstellen:""", max_tokens=4000)
    
    save_versioned(output_dir, "06_qualitaets_report.md", report)
    
    log(f"   ✓ Check abgeschlossen")
    telegram_send(f"📊 *Qualitäts-Report erstellt*\n\n{report[:500]}...")
    
    return report


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(setting: str, output_dir: str = None):
    """Hauptfunktion"""
    global LOG_FILE
    
    start = datetime.now()
    
    # Output-Verzeichnis mit Timestamp
    if not output_dir:
        timestamp = start.strftime("%Y%m%d_%H%M%S")
        setting_clean = re.sub(r'[^a-zA-Z0-9äöüÄÖÜß]', '_', setting)[:30]
        output_dir = f"output_{timestamp}_{setting_clean}"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    LOG_FILE = output_path / "pipeline.log"
    
    log(f"\n{'#'*60}")
    log(f"# NOVEL PIPELINE V4")
    log(f"# Setting: {setting}")
    log(f"# Output: {output_dir}")
    log(f"# Start: {start}")
    log(f"{'#'*60}")
    
    # Qdrant initialisieren
    qdrant_init_collection()
    
    telegram_send(f"🚀 *Pipeline V4 gestartet*\n\n📖 {setting}\n📁 {output_dir}")
    
    # Phase 1: Grob-Gliederung
    gliederung = phase1_gliederung(setting, output_path)
    
    # Phase 2: Akt-Gliederungen
    akte = phase2_akte(gliederung, output_path)
    
    # Phase 2.5: Kapitel-Gliederungen
    kapitel_liste = phase2_5_kapitel(gliederung, akte, output_path)
    
    # Phase 3 & 4: Schreiben + Polish
    log(f"\n{'='*60}")
    log("PHASE 3 & 4: SCHREIBEN + POLISH")
    log(f"{'='*60}")
    
    telegram_send(f"✍️ *Phase 3 & 4 gestartet*: Schreiben ({len(kapitel_liste)} Kapitel)")
    
    all_chapters = []
    vorheriges = None
    
    for kap in kapitel_liste:
        text = phase3_schreiben(kap, vorheriges, output_path)
        polished = phase4_polish(text, kap["nummer"], output_path)
        
        all_chapters.append(polished)
        vorheriges = polished
        
        save_versioned(output_path, f"kapitel_{kap['nummer']:02d}.md", polished)
        
        # In Qdrant speichern
        qdrant_store(polished, {
            "type": "kapitel_text",
            "kapitel": kap["nummer"],
            "wortzahl": len(polished.split())
        })
        
        # Telegram Update alle 5 Kapitel
        if kap["nummer"] % 5 == 0:
            telegram_send(f"📝 Kapitel {kap['nummer']}/{len(kapitel_liste)} fertig")
    
    # Phase 5: Flow-Check
    corrected = phase5_flow_check(all_chapters, output_path)
    
    # Korrigierte speichern
    for i, chapter in enumerate(corrected):
        save_versioned(output_path, f"kapitel_{i+1:02d}.md", chapter)
    
    # Roman zusammenfügen
    full_novel = "\n\n---\n\n".join(corrected)
    (output_path / "ROMAN_KOMPLETT.md").write_text(full_novel)
    
    wortzahl = len(full_novel.split())
    log(f"\n   Gesamtwortzahl: {wortzahl:,} Wörter")
    
    # Phase 6: Gesamt-Check
    report = phase6_check(full_novel, output_path)
    
    duration = datetime.now() - start
    
    log(f"\n{'#'*60}")
    log(f"# FERTIG!")
    log(f"# Wortzahl: {wortzahl:,}")
    log(f"# Kapitel: {len(corrected)}")
    log(f"# Dauer: {duration}")
    log(f"{'#'*60}")
    
    telegram_send(f"""✅ *PIPELINE FERTIG!*

📊 {wortzahl:,} Wörter
📚 {len(corrected)} Kapitel
⏱ {duration}
📁 {output_dir}""")
    
    return output_path


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python novel_pipeline.py 'Setting-Beschreibung'")
        print("Beispiel: python novel_pipeline.py 'Archäologin entdeckt auf Kreta ein Geheimnis'")
        sys.exit(1)
    
    setting = " ".join(sys.argv[1:])
    run_pipeline(setting)
