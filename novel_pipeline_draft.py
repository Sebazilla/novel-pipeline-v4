#!/usr/bin/env python3
"""
Novel Pipeline V4
- Gemini für alle Planungs-Phasen (Self-Feedback)
- Claude Code CLI für Schreiben
- Telegram Approvals
- Läuft auf Mac Studio
"""

import os
import subprocess
import requests
import re
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Secrets aus .env laden
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

GEMINI_MODEL = "gemini-3-pro-preview"  # Aktuellstes Modell

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
                print(f"    ⚠️ Gemini Response ohne candidates: {data.get('error', data)}")
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                return ""
            
            content = data["candidates"][0].get("content", {})
            if not content or "parts" not in content:
                finish = data["candidates"][0].get("finishReason", "unknown")
                print(f"    ⚠️ Gemini empty response (finishReason: {finish})")
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                return ""
            return content["parts"][0]["text"]
            
        except Exception as e:
            print(f"    ⚠️ Gemini Fehler (Versuch {attempt + 1}): {e}")
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
        print("    ⚠️ Claude Timeout")
        return ""
    except Exception as e:
        print(f"    ⚠️ Claude Fehler: {e}")
        return ""


def telegram_send(message: str) -> bool:
    """Nachricht an Telegram senden"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=30)
        return True
    except Exception as e:
        print(f"    ⚠️ Telegram Fehler: {e}")
        return False


def telegram_approval(message: str, timeout_minutes: int = 60) -> bool:
    """Telegram Approval mit JA/NEIN Antwort"""
    telegram_send(message + "\n\n✅ JA = weiter\n❌ NEIN = neu generieren")
    
    print(f"      📱 Warte auf Approval (max {timeout_minutes} min)...")
    
    # Letzte Update-ID merken
    updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates").json()
    last_update_id = updates["result"][-1]["update_id"] if updates["result"] else 0
    
    start_time = time.time()
    while time.time() - start_time < timeout_minutes * 60:
        time.sleep(3)
        
        updates = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
            params={"offset": last_update_id + 1}
        ).json()
        
        for update in updates.get("result", []):
            last_update_id = update["update_id"]
            text = update.get("message", {}).get("text", "").lower().strip()
            
            if text in ["ja", "yes", "j", "y", "ok", "👍"]:
                print(f"      ✅ Approved!")
                return True
            elif text in ["nein", "no", "n", "👎"]:
                print(f"      ❌ Abgelehnt")
                return False
    
    print(f"      ⏰ Timeout - fahre fort")
    return True


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

STIL = """SCHREIBSTIL:

PACING:
- Schnell - kurze Kapitel, häufige Szenenwechsel
- Jedes Kapitel endet mit Hook
- Action und Dialog dominieren, minimale Beschreibungen

DIALOGE:
- Schlagfertig, witzig, sexy
- Subtext wichtiger als Text
- Necken, provozieren, herausfordern

INNENLEBEN:
- Gedanken der Heldin: direkt, selbstironisch
- Körperliche Reaktionen beschreiben
- Sie kommentiert ihre eigene Dummheit

TON:
- Warm, humorvoll, emotional
- Hoffnung scheint durch auch in dunklen Momenten
- Der Leser soll lachen UND mitfiebern
"""


# ============================================================
# SELF-FEEDBACK PROMPT
# ============================================================

SELF_FEEDBACK_INSTRUCTION = """
WICHTIG - EHRLICHES SELF-FEEDBACK:
Bevor du antwortest, prüfe deine Arbeit kritisch:
- Schreib mir NICHT was ich hören möchte
- Schreib was SINN MACHT
- Wenn etwas schwach ist, verbessere es
- Wenn die Struktur nicht stimmt, korrigiere sie
- Sei dein eigener härtester Kritiker

Frage dich:
1. Folgt das WIRKLICH der 7-Phasen-Struktur?
2. Ist die Suspense-Eskalation sichtbar?
3. Würde ich das selbst lesen wollen?
4. Wo sind die schwachen Stellen?
"""


# ============================================================
# PHASE 1: GROB-GLIEDERUNG
# ============================================================

def phase1_gliederung(setting: str, max_iterations: int = 5) -> str:
    """Grob-Gliederung mit Gemini Self-Feedback"""
    
    print(f"\n{'='*60}")
    print("PHASE 1: GROB-GLIEDERUNG")
    print(f"{'='*60}")
    
    prompt = f"""{REGELWERK}

{STIL}

{SELF_FEEDBACK_INSTRUCTION}

SETTING: {setting}

AUFGABE:
Erstelle eine detaillierte Gliederung für diesen Roman.

Die Gliederung MUSS enthalten:
1. Titel-Vorschlag
2. Heldin (Name, Alter, Beruf, Ziel, Schwäche)
3. Hero (Name, Beruf, Geheimnis, was macht ihn zum "Feind"?)
4. Antagonist (Wer, Motiv, Verbindung zu Leads)
5. 3+ Nebencharaktere (Archetyp + Funktion)
6. Die 7 Phasen mit je:
   - Welche Kapitel
   - Kernszenen
   - Suspense-Level
   - Emotionaler Beat
7. Der äußere Konflikt/Bedrohung (konkret!)

PRÜFE VOR DER AUSGABE:
- Stimmen die Proportionen (15% / 20% / 20% / 20% / 10% / 10% / 5%)?
- Eskaliert die Suspense parallel zur Romanze?
- Hat jede Phase einen klaren Höhepunkt?
"""

    gliederung = call_gemini(prompt, max_tokens=12000)
    print(f"   ✓ Erste Version ({len(gliederung)} Zeichen)")
    
    # Self-Feedback Loop
    for i in range(max_iterations - 1):
        print(f"\n   [Iteration {i+2}/{max_iterations}] Self-Feedback...")
        
        feedback_prompt = f"""{SELF_FEEDBACK_INSTRUCTION}

Hier ist deine aktuelle Roman-Gliederung:

{gliederung}

AUFGABE - KRITISCHE SELBST-PRÜFUNG:

1. STRUKTUR-CHECK:
   - Entspricht jede Phase EXAKT den Vorgaben?
   - Sind die Proportionen korrekt?
   - Fehlen wichtige Beats?

2. SUSPENSE-CHECK:
   - Eskaliert die äußere Bedrohung in 3 Stufen?
   - Ist der Antagonist früh genug präsent?
   - Gibt es echte Gefahr oder nur Andeutungen?

3. ROMANCE-CHECK:
   - Ist die Enemies-to-Lovers Dynamik glaubwürdig?
   - Kommen die Leads früh genug zusammen?
   - Ist der Midpoint-Sex emotional aufgeladen?

4. CHARACTER-CHECK:
   - Sind die Nebencharaktere mehr als Platzhalter?
   - Hat der Antagonist ein echtes Motiv?
   - Ist die Heldin AKTIV (nicht nur reaktiv)?

SCHREIB EHRLICH:
- Was ist SCHWACH an dieser Gliederung?
- Was würde ein Lektor kritisieren?
- Was fehlt?

Dann: Gib die VOLLSTÄNDIG ÜBERARBEITETE Gliederung aus.
Nicht nur die Änderungen - die KOMPLETTE neue Version.
"""
        
        verbessert = call_gemini(feedback_prompt, max_tokens=12000)
        
        if len(verbessert) > len(gliederung) * 0.5:  # Sanity check
            gliederung = verbessert
            print(f"   ✓ Überarbeitet ({len(gliederung)} Zeichen)")
        else:
            print(f"   ⚠️ Überarbeitung zu kurz, behalte vorherige Version")
    
    # Telegram Approval
    print(f"\n   📱 Sende zur Freigabe...")
    
    synopsis_prompt = f"""Fasse diese Gliederung in einer SPANNENDEN Synopsis zusammen (max 800 Zeichen):

{gliederung[:6000]}

Enthalten muss:
- Heldin + Hero (Namen!)
- Der zentrale Konflikt
- Was ist der Hook?
- Warum will man das lesen?

NUR die Synopsis, keine Einleitung."""

    synopsis = call_gemini(synopsis_prompt, max_tokens=500)
    
    for attempt in range(3):
        approved = telegram_approval(f"📖 *ROMAN-SYNOPSIS*\n\n{synopsis[:1500]}")
        if approved:
            break
        print(f"   🔄 Generiere neue Version...")
        gliederung = call_gemini(prompt, max_tokens=12000)
        synopsis = call_gemini(synopsis_prompt, max_tokens=500)
    
    return gliederung


# ============================================================
# PHASE 2: AKT-GLIEDERUNGEN
# ============================================================

def phase2_akte(gliederung: str) -> dict:
    """Detaillierte Akt-Gliederungen"""
    
    print(f"\n{'='*60}")
    print("PHASE 2: AKT-GLIEDERUNGEN")
    print(f"{'='*60}")
    
    akte = {}
    
    akt_phasen = {
        1: "Phase I + II (0-35%): Setup + Forced Proximity",
        2: "Phase III + IV (35-75%): Intimacy + Separation", 
        3: "Phase V + VI + VII (75-100%): Crisis + Finale + HEA"
    }
    
    for akt_num, beschreibung in akt_phasen.items():
        print(f"\n   [Akt {akt_num}] {beschreibung}")
        
        prompt = f"""{REGELWERK}

{SELF_FEEDBACK_INSTRUCTION}

GESAMT-GLIEDERUNG:
{gliederung}

AUFGABE: Detaillierte Gliederung für AKT {akt_num}
({beschreibung})

Für JEDES Kapitel in diesem Akt:
1. Kapitel-Nummer und Titel
2. Welche Phase(n) der 7-Phasen-Struktur
3. Suspense-Level (1/2/3)
4. Kernszenen (2-4 pro Kapitel)
5. Emotionaler Beat am Ende
6. Wortzahl-Ziel (Gesamt ~80.000 Wörter)

PRÜFE:
- Sind alle Phasen dieses Akts abgedeckt?
- Stimmt die Suspense-Eskalation?
- Endet jedes Kapitel mit Hook?
"""
        
        akt = call_gemini(prompt, max_tokens=8000)
        print(f"      ✓ Erstellt ({len(akt)} Zeichen)")
        
        # Self-Feedback
        feedback = call_gemini(f"""{SELF_FEEDBACK_INSTRUCTION}

Akt {akt_num} Gliederung:
{akt}

Kritische Prüfung:
1. Fehlen wichtige Szenen?
2. Ist die Kapitel-Aufteilung logisch?
3. Stimmt das Pacing?

Gib die VOLLSTÄNDIGE überarbeitete Akt-Gliederung aus.""", max_tokens=8000)
        
        if len(feedback) > len(akt) * 0.5:
            akt = feedback
            print(f"      ✓ Überarbeitet")
        
        akte[f"akt_{akt_num}"] = akt
    
    return akte


# ============================================================
# PHASE 2.5: KAPITEL-GLIEDERUNGEN  
# ============================================================

def phase2_5_kapitel(gliederung: str, akte: dict) -> list:
    """Detaillierte Szenen-Gliederung pro Kapitel"""
    
    print(f"\n{'='*60}")
    print("PHASE 2.5: KAPITEL-GLIEDERUNGEN")
    print(f"{'='*60}")
    
    kapitel_liste = []
    kapitel_nr = 1
    
    for akt_num in [1, 2, 3]:
        print(f"\n   [Akt {akt_num}]")
        akt_text = akte[f"akt_{akt_num}"]
        
        # Kapitel aus Akt extrahieren
        matches = re.findall(r'Kapitel\s*(\d+)[:\s]*([^\n]+)', akt_text, re.IGNORECASE)
        if not matches:
            matches = [(str(i), f"Kapitel {i}") for i in range(1, 8)]
        
        for _, titel in matches:
            print(f"      [Kapitel {kapitel_nr}] {titel[:40]}...")
            
            prompt = f"""{STIL}

{SELF_FEEDBACK_INSTRUCTION}

KONTEXT:
{gliederung[:3000]}

AKT {akt_num}:
{akt_text[:2000]}

AUFGABE: Szenen-Gliederung für KAPITEL {kapitel_nr}: {titel}

## METADATEN
- Nummer: {kapitel_nr}
- Titel: {titel}
- Wortzahl: [3000-4000]
- Phase: [Welche der 7 Phasen?]
- Suspense-Level: [1/2/3]

## SZENEN (3-5 pro Kapitel)

Für jede Szene:
### Szene X: [Titel]
- Ort: [konkret]
- Figuren: [wer ist anwesend]
- Ziel: [was muss passieren]
- Beats:
  1. [Einstieg]
  2. [Entwicklung]  
  3. [Wendepunkt/Hook]
- Wichtige Momente: [spezifische Dialoge/Aktionen]
- Stimmung: [Atmosphäre]

## VERBINDUNGEN
- Anknüpfung an Kapitel {kapitel_nr - 1}
- Setup für Kapitel {kapitel_nr + 1}

## CONSTRAINTS
- Was darf NICHT passieren?
"""
            
            kap_gliederung = call_gemini(prompt, max_tokens=4000)
            print(f"         ✓ Erstellt")
            
            kapitel_liste.append({
                "nummer": kapitel_nr,
                "titel": titel.strip(),
                "akt": akt_num,
                "gliederung": kap_gliederung
            })
            
            kapitel_nr += 1
    
    # Telegram Approval für alle Kapitel-Gliederungen
    print(f"\n   📱 Sende Kapitel-Übersicht zur Freigabe...")
    
    uebersicht = "\n".join([
        f"Kap {k['nummer']}: {k['titel'][:50]}" 
        for k in kapitel_liste
    ])
    
    telegram_approval(f"📚 *KAPITEL-STRUKTUR*\n\n{uebersicht[:1500]}\n\n*{len(kapitel_liste)} Kapitel total*")
    
    return kapitel_liste


# ============================================================
# PHASE 3: SCHREIBEN (Claude Code)
# ============================================================

def phase3_schreiben(kapitel: dict, vorheriges_kapitel: str = None) -> str:
    """Kapitel mit Claude Code schreiben"""
    
    nr = kapitel["nummer"]
    titel = kapitel["titel"]
    gliederung = kapitel["gliederung"]
    
    # Wortzahl aus Gliederung extrahieren
    match = re.search(r'Wortzahl[:\s]*(\d+)', gliederung)
    ziel_wortzahl = int(match.group(1)) if match else 3500
    
    print(f"\n   [Kapitel {nr}] Schreiben (Ziel: {ziel_wortzahl} Wörter)...")
    
    # Kontext vom vorherigen Kapitel
    kontext = ""
    if vorheriges_kapitel and nr > 1:
        # Nur die letzten ~2000 Wörter für Kontinuität
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
    
    prompt = f"""{STIL}

{kontext}

Du schreibst KAPITEL {nr}: {titel}

GLIEDERUNG (folge ihr EXAKT):
{gliederung}

REGELN:
- Exakt {ziel_wortzahl} Wörter (±10%)
- Folge den Szenen und Beats
- Single POV (Heldin)
- Dialoge: schlagfertig, mit Subtext
- Gedanken der Heldin: direkt, selbstironisch
- Ende mit Hook oder emotionalem Beat

BEGINNE DIREKT mit dem Text. Keine Meta-Kommentare."""

    text = call_claude(prompt)
    wortzahl = len(text.split())
    print(f"      ✓ Geschrieben: {wortzahl} Wörter")
    
    # Zu kurz? Anreichern
    if wortzahl < ziel_wortzahl * 0.75:
        print(f"      ⚠️ Zu kurz - reichere an...")
        
        anreicherung = f"""{STIL}

Der Text hat {wortzahl} Wörter, Ziel: {ziel_wortzahl}

NICHT aufblähen! Stattdessen BEREICHERN durch:
- Mehr Spannung zwischen den Charakteren
- Ein weiteres Wortgefecht
- Tiefere emotionale Beats
- Eine Komplikation

AKTUELLER TEXT:
{text}

Gib den VOLLSTÄNDIGEN angereicherten Text aus."""

        text = call_claude(anreicherung)
        print(f"      ✓ Angereichert: {len(text.split())} Wörter")
    
    return text


# ============================================================
# PHASE 4: KONSISTENZ-CHECK (Gemini) + FIX (Claude)
# ============================================================

def phase4_konsistenz(kapitel_texte: list) -> list:
    """Konsistenz-Check mit Gemini, Fixes mit Claude"""
    
    print(f"\n{'='*60}")
    print("PHASE 4: KONSISTENZ-CHECK")
    print(f"{'='*60}")
    
    # Alle Kapitel zusammenfügen für Gemini
    full_text = "\n\n---\n\n".join([
        f"KAPITEL {i+1}:\n{text}" 
        for i, text in enumerate(kapitel_texte)
    ])
    
    print(f"   Prüfe {len(kapitel_texte)} Kapitel ({len(full_text.split())} Wörter)...")
    
    # Gemini prüft (großer Kontext!)
    check_prompt = f"""Prüfe diesen Roman auf KONSISTENZ-FEHLER:

{full_text[:100000]}

Finde:
1. NAMEN-FEHLER (Name ändert sich, Schreibweise inkonsistent)
2. FAKTEN-FEHLER (Augenfarbe, Beruf, Ort ändert sich)
3. TIMELINE-FEHLER (Zeitsprünge die nicht passen)
4. WISSENS-FEHLER (Figur weiß plötzlich etwas)
5. CHARAKTER-FEHLER (Figur handelt out-of-character)

Für JEDEN Fehler:
- Kapitel + ungefähre Position
- Was ist falsch
- Was wäre richtig

Wenn KEINE Fehler: Schreib "KEINE FEHLER GEFUNDEN"
"""

    report = call_gemini(check_prompt, max_tokens=4000)
    print(f"   ✓ Check abgeschlossen")
    
    # Wenn Fehler, mit Claude fixen
    if "KEINE FEHLER" not in report.upper():
        print(f"   ⚠️ Fehler gefunden - korrigiere...")
        
        korrigierte_kapitel = []
        for i, text in enumerate(kapitel_texte):
            # Prüfen ob dieses Kapitel im Report erwähnt wird
            if f"Kapitel {i+1}" in report or f"KAPITEL {i+1}" in report:
                print(f"      [Kapitel {i+1}] Korrigiere...")
                
                fix_prompt = f"""FEHLER-REPORT:
{report}

KAPITEL {i+1} TEXT:
{text}

Korrigiere NUR die im Report genannten Fehler für dieses Kapitel.
Behalte alles andere bei.

Gib das VOLLSTÄNDIGE korrigierte Kapitel aus."""

                fixed = call_claude(fix_prompt)
                if len(fixed.split()) > len(text.split()) * 0.5:
                    korrigierte_kapitel.append(fixed)
                else:
                    korrigierte_kapitel.append(text)
            else:
                korrigierte_kapitel.append(text)
        
        return korrigierte_kapitel
    
    return kapitel_texte


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(setting: str, output_dir: str = None):
    """Hauptfunktion"""
    
    start = datetime.now()
    
    # Output-Verzeichnis
    if not output_dir:
        timestamp = start.strftime("%Y%m%d_%H%M%S")
        setting_clean = re.sub(r'[^a-zA-Z0-9äöüÄÖÜß]', '_', setting)[:30]
        output_dir = f"output_{timestamp}_{setting_clean}"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'#'*60}")
    print(f"# NOVEL PIPELINE V4")
    print(f"# Setting: {setting}")
    print(f"# Output: {output_dir}")
    print(f"# Start: {start}")
    print(f"{'#'*60}")
    
    telegram_send(f"🚀 *Pipeline gestartet*\n\nSetting: {setting}")
    
    # Phase 1: Grob-Gliederung
    gliederung = phase1_gliederung(setting)
    (output_path / "01_gliederung.md").write_text(gliederung)
    
    # Phase 2: Akt-Gliederungen
    akte = phase2_akte(gliederung)
    for name, content in akte.items():
        (output_path / f"02_{name}.md").write_text(content)
    
    # Phase 2.5: Kapitel-Gliederungen
    kapitel_liste = phase2_5_kapitel(gliederung, akte)
    for kap in kapitel_liste:
        filename = f"02.5_kapitel_{kap['nummer']:02d}_gliederung.md"
        (output_path / filename).write_text(kap["gliederung"])
    
    # Phase 3: Schreiben
    print(f"\n{'='*60}")
    print("PHASE 3: SCHREIBEN")
    print(f"{'='*60}")
    
    kapitel_texte = []
    vorheriges = None
    
    for kap in kapitel_liste:
        text = phase3_schreiben(kap, vorheriges)
        kapitel_texte.append(text)
        vorheriges = text
        
        # Zwischenspeichern
        filename = f"kapitel_{kap['nummer']:02d}.md"
        (output_path / filename).write_text(text)
    
    # Phase 4: Konsistenz
    kapitel_texte = phase4_konsistenz(kapitel_texte)
    
    # Finale Kapitel speichern
    for i, text in enumerate(kapitel_texte):
        filename = f"kapitel_{i+1:02d}.md"
        (output_path / filename).write_text(text)
    
    # Roman zusammenfügen
    full_novel = "\n\n---\n\n".join(kapitel_texte)
    (output_path / "ROMAN_KOMPLETT.md").write_text(full_novel)
    
    wortzahl = len(full_novel.split())
    duration = datetime.now() - start
    
    print(f"\n{'#'*60}")
    print(f"# FERTIG!")
    print(f"# Wortzahl: {wortzahl}")
    print(f"# Dauer: {duration}")
    print(f"{'#'*60}")
    
    telegram_send(f"✅ *Pipeline fertig!*\n\n📊 {wortzahl} Wörter\n⏱ {duration}")
    
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
