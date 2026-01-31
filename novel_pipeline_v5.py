#!/usr/bin/env python3
"""
Novel Pipeline V5 - Restructured Romance Novel Generator

13-Step Process:
1. Gemini: Synopsis + Arbeitstitel
2. User: Approval → Ordner anlegen
3. Gemini: Master-Struktur ablegen
4. Gemini: Charaktersheets (Ghost/Lie/Banter) → Approval
5. Gemini: Detaillierte Gliederung (3000-4000 W.)
6. User: Gliederung Approval
7. Gemini: Kapitel-Gliederungen (500-1000 W.) + Fakten-Logbuch
8. User: Kapitelgliederungen Approval + Feedback
9. Gemini: Logik-Check → Mängelliste
10. Claude: Korrigiert nach Mängelliste
11. Claude: Schreibt Kapitel aus
12. Gemini: Final-Check → Feedback
13. Claude: Setzt Feedback um → Ausgabe
"""

import os
import json
import time
import re
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GEMINI_MODEL_PRO = "gemini-2.5-pro"
GEMINI_MODEL_FLASH = "gemini-2.5-flash"

# ============================================================
# MASTER-STRUKTUR (Der Roberts-Quinn-Code)
# ============================================================

MASTER_STRUKTUR = """
# MASTER-STRUKTUR: Modern High-Banter Romance

## GENRE & STIL
- **Genre:** Contemporary Romance / Enemies-to-Lovers
- **Zielumfang:** ca. 400 Seiten / 100.000 Wörter
- **Stil-Hybrid:**
  1. **Nora Roberts:** Emanzipierte, kompetente Frauen; atmosphärisches Setting; Fokus auf Beruf/Leidenschaft
  2. **Julia Quinn:** Spritzige Dialoge; humorvoller Schlagabtausch („Banter"); Leichtigkeit; familiäre Verwicklungen

## DIE GOLDENE REGEL (Der „Roberts-Quinn-Code")
- **Kompetenz ist sexy:** Wir sehen die Heldin bei der Arbeit, wo sie glänzt. Der Held verliebt sich zuerst in ihren Verstand/ihr Können, dann in ihren Körper.
- **Worte sind Vorspiel:** Bevor sie sich berühren, duellieren sie sich verbal. Schlagfertigkeit ist die Sprache der Liebe.
- **Lachen vor Küssen:** Jede romantische Szene braucht eine Prise Humor, um sie zu erden (kein Kitsch).

## CHARAKTER-ANFORDERUNGEN

### Die Heldin (Moderne Emanzipation)
- Muss eine spezifische Kompetenz haben (Job/Talent)
- Hat ein konkretes äußeres Ziel
- Verbirgt eine Unsicherheit hinter Stärke/Humor
- **The Ghost:** Welches schmerzhafte Ereignis aus der Vergangenheit blockiert sie emotional?
- **The Lie:** Welche falsche Überzeugung über sich selbst nutzt sie als Schutzschild?
- **Banter-Stil:** Welche Art von Humor/verbaler Verteidigung nutzt sie?

### Der Held (Der perfekte Antagonist)
- Ist charakterlich das genaue Gegenteil der Heldin (Reibungspunkte)
- Eigenschaften, die sie gleichzeitig wütend machen und faszinieren
- **The Ghost:** Sein schmerzhaftes Ereignis
- **The Lie:** Seine falsche Überzeugung
- **Banter-Stil:** Seine verbale Verteidigung

### Die Dynamik (Forced Proximity)
- Ein unwiderruflicher Zwang zur physischen Nähe (Beruf, Schneesturm, Projekt)
- Schlagabtausch: Sie provozieren sich gegenseitig intellektuell

### Die Nebencharaktere (5 funktionale Figuren)
1. **Der "Safe Space" der Heldin:** Beste Freundin/Schwester/Kollegin – loyal, aber direkt
2. **Der "Wingman" des Helden:** Freund/Bruder, der ihn durchschaut und aufzieht
3. **Der Störfaktor/Antagonist:** Verschärft den äußeren Konflikt
4. **Comic Relief / Stimme der Weisheit:** Exzentrische/ältere Figur für Humor und Wahrheit
5. **Die Variable:** Figur für das spezifische Setting (Nachbar, Klient, Kind)

## DIE 7 PHASEN

### PHASE I – Der „Meet-Disaster" & Die erste Klinge (0–15%)
- **Der Aufhänger:** Zeig die Heldin kompetent in ihrem Element. Dann passiert das Chaos.
- **Der Zusammenprall:** Der Held tritt als Hindernis auf. Sie feuert verbal zurück.
- **Der „Hook":** Situation zwingt sie zusammen, obwohl sie sich „hassen". Humorvoller Cliffhanger.

### PHASE II – Zwangsnähe & „Competence Kink" (15–35%)
- **Die Arena:** Gemeinsames Projekt zwingt sie in einen Raum.
- **Perspektivwechsel:** Held beobachtet sie heimlich, ist beeindruckt. Sie merkt, dass er gut ist.
- **Die Eskalation:** Streit, der fast in Kuss endet, aber lustig unterbrochen wird.

### PHASE III – Der Riss im Panzer & „Open Door" (35–55%)
- **Der Schild fällt:** Verletzlichkeit durch Krankheit, Panne oder schlechte Nachricht. Caretaking.
- **Der Wendepunkt (Midpoint):** Erster echter Kuss oder Sex. Leidenschaftlich, verspielt, chaotisch.
- **Die Ausrede:** „Nur Stressabbau". Sie leugnen die Gefühle.

### PHASE IV – Das Team gegen den Rest der Welt (55–75%)
- **Die Bedrohung:** Äußerer Konflikt (Job/Skandal) spitzt sich zu.
- **Die Partnerschaft:** Held stellt sich loyal an ihre Seite. Perfektes Team.
- **Der Insider:** „Enemies"-Dynamik wandelt sich zu spielerischem Necken.

### PHASE V – Der tiefe Fall (75–85%)
- **Der Bruch:** Konflikt der Werte oder Ängste. Einer zieht sich zurück.
- **Die Stille:** Ohne den anderen ist die Welt grau. Der Humor fehlt.
- **Die Emanzipation:** Heldin löst das äußere Problem allein.

### PHASE VI – Die große Geste & Das öffentliche Bekenntnis (85–95%)
- **Die Erkenntnis:** Held kapiert, dass er ohne sie unglücklich ist.
- **Der Grovel:** Er muss sich anstrengen, in ihre Welt kommen.
- **Die Szene:** Öffentliche/grandios-chaotische Liebeserklärung.
- **Die Reaktion:** Sie lässt ihn zappeln, dann Wiedervereinigung auf Augenhöhe.

### PHASE VII – Happy End (95–100%)
- **Der Epilog:** Blick in die glückliche Zukunft. Geschichte ist abgeschlossen.

## SPRACHE & STIL
- Deutsch (Deutschland)
- Deutsche Anführungszeichen: „..." und ‚...'
- Gedanken der Heldin: Ich-Form, KURSIV
- Dialoge: schlagfertig, mit Subtext
- Single POV (Heldin, dritte Person)
- Keine unnötigen Anglizismen
"""

# ============================================================
# LOGGING
# ============================================================

LOG_FILE = None

def log(msg: str):
    """Log to console and file"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    if LOG_FILE:
        with open(LOG_FILE, 'a') as f:
            f.write(line + "\n")

# ============================================================
# TELEGRAM FUNCTIONS
# ============================================================

def telegram_send(text: str):
    """Send message to Telegram (auto-split if too long)"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("   ⚠️ Telegram nicht konfiguriert")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Split if too long
    max_len = 3800
    if len(text) <= max_len:
        chunks = [text]
    else:
        chunks = []
        paragraphs = text.split('\n\n')
        current = ""
        for p in paragraphs:
            if len(current) + len(p) + 2 < max_len:
                current += ("\n\n" if current else "") + p
            else:
                if current:
                    chunks.append(current)
                current = p
        if current:
            chunks.append(current)
    
    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            chunk = f"*Teil {i+1}/{len(chunks)}*\n\n{chunk}"
        try:
            requests.post(url, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": chunk,
                "parse_mode": "Markdown"
            }, timeout=30)
            time.sleep(0.5)
        except Exception as e:
            log(f"   ⚠️ Telegram Fehler: {e}")


def telegram_send_file(filepath: Path, caption: str = ""):
    """Send file to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    
    try:
        with open(filepath, 'rb') as f:
            requests.post(url, data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption[:1024]
            }, files={
                "document": (filepath.name, f)
            }, timeout=60)
    except Exception as e:
        log(f"   ⚠️ Telegram Datei-Fehler: {e}")


def telegram_wait_for_start() -> str:
    """Wait for /start command and return setting/theme"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return input("Setting eingeben: ")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    last_update_id = 0
    
    telegram_send("🚀 *Novel Pipeline V5 bereit*\n\nSende `/start` um eine neue Synopsis zu generieren.")
    log("📱 Warte auf Telegram /start Befehl...")
    
    while True:
        try:
            r = requests.get(url, params={"offset": last_update_id + 1, "timeout": 30}, timeout=35)
            updates = r.json().get("result", [])
            
            for update in updates:
                last_update_id = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id", ""))
                
                if chat_id == TELEGRAM_CHAT_ID and text.startswith("/start"):
                    log(f"✅ Start-Befehl erhalten")
                    return "start"
                    
        except Exception as e:
            log(f"   ⚠️ Telegram Polling Fehler: {e}")
            time.sleep(5)


def telegram_approval(prompt: str, filepath: Path = None, timeout_minutes: int = 60) -> tuple[bool, str]:
    """
    Wait for user approval via Telegram.
    Returns (approved: bool, feedback: str)
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        response = input(f"{prompt} (JA/NEIN + Feedback): ")
        return response.upper().startswith("JA"), response
    
    # Send file if provided
    if filepath and filepath.exists():
        telegram_send_file(filepath, prompt)
    else:
        telegram_send(prompt)
    
    telegram_send("Antworte mit *JA* zur Bestätigung oder *NEIN* + Feedback für Änderungen.")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    last_update_id = 0
    start_time = time.time()
    timeout = timeout_minutes * 60
    
    log(f"      📱 Warte auf Approval (max {timeout_minutes} min)...")
    
    # Get current update_id
    try:
        r = requests.get(url, params={"offset": -1}, timeout=10)
        updates = r.json().get("result", [])
        if updates:
            last_update_id = updates[-1]["update_id"]
    except:
        pass
    
    while time.time() - start_time < timeout:
        try:
            r = requests.get(url, params={"offset": last_update_id + 1, "timeout": 30}, timeout=35)
            updates = r.json().get("result", [])
            
            for update in updates:
                last_update_id = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id", ""))
                
                if chat_id == TELEGRAM_CHAT_ID and text:
                    text_upper = text.upper().strip()
                    if text_upper.startswith("JA"):
                        log(f"      ✅ Approved!")
                        return True, ""
                    elif text_upper.startswith("NEIN"):
                        feedback = text[4:].strip() if len(text) > 4 else ""
                        log(f"      ❌ Abgelehnt - Feedback: {feedback[:50]}...")
                        return False, feedback
                        
        except Exception as e:
            log(f"   ⚠️ Polling Fehler: {e}")
            time.sleep(5)
    
    log(f"      ⏰ Timeout nach {timeout_minutes} Minuten")
    return False, "Timeout"


# ============================================================
# GEMINI API
# ============================================================

def call_gemini(prompt: str, max_tokens: int = 16000, use_flash: bool = False, retries: int = 3) -> str:
    """Call Gemini API with retries"""
    model = GEMINI_MODEL_FLASH if use_flash else GEMINI_MODEL_PRO
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    for attempt in range(retries):
        try:
            r = requests.post(url, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.8
                }
            }, timeout=120)
            
            data = r.json()
            
            if "candidates" in data and data["candidates"]:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    if text:
                        return text
                
                finish_reason = candidate.get("finishReason", "")
                if finish_reason == "MAX_TOKENS":
                    log(f"    ⚠️ Gemini MAX_TOKENS - Retry {attempt+1}")
                    continue
            
            log(f"    ⚠️ Gemini empty response - Retry {attempt+1}")
            
        except Exception as e:
            log(f"    ⚠️ Gemini Fehler: {e} - Retry {attempt+1}")
        
        time.sleep(2)
    
    return ""


# ============================================================
# CLAUDE CLI
# ============================================================

def call_claude(prompt: str) -> str:
    """Call Claude via CLI"""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--no-input"],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout.strip()
    except Exception as e:
        log(f"   ⚠️ Claude Fehler: {e}")
        return ""


# ============================================================
# FILE HELPERS
# ============================================================

def save_md(path: Path, content: str):
    """Save content as Markdown file"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    log(f"   ✓ Gespeichert: {path.name}")


def save_pdf(path: Path, content: str):
    """Save content as PDF (via Markdown conversion)"""
    # First save as MD
    md_path = path.with_suffix('.md')
    save_md(md_path, content)
    
    # Convert to PDF if pandoc available
    try:
        subprocess.run([
            "pandoc", str(md_path), "-o", str(path),
            "--pdf-engine=xelatex",
            "-V", "geometry:margin=2.5cm",
            "-V", "mainfont:Helvetica"
        ], capture_output=True, timeout=60)
        log(f"   ✓ PDF erstellt: {path.name}")
    except:
        log(f"   ⚠️ PDF-Konvertierung fehlgeschlagen, MD behalten")


# ============================================================
# PIPELINE STEPS
# ============================================================

def step1_synopsis(output_dir: Path, theme: str = None) -> str:
    """Step 1: Gemini generates Synopsis + Arbeitstitel"""
    log("\n" + "="*60)
    log("SCHRITT 1: SYNOPSIS GENERIEREN")
    log("="*60)
    
    if theme:
        log(f"   Thema vorgegeben: {theme}")
        theme_instruction = f"\n\nTHEMA/SETTING (vom User vorgegeben):\n{theme}\n\nEntwickle die Synopsis basierend auf diesem Thema."
    else:
        theme_instruction = ""
    
    prompt = f"""
{MASTER_STRUKTUR}{theme_instruction}

AUFGABE: Entwickle eine originelle Buchidee für einen Contemporary Romance / Enemies-to-Lovers Roman.

Erstelle:
1. **Arbeitstitel** (prägnant, marketingtauglich)
2. **Synopsis** (exakt 3 Sätze):
   - Satz 1: Wer ist die Heldin, was ist ihr Ziel?
   - Satz 2: Wer ist der Held, warum kollidieren sie?
   - Satz 3: Was steht auf dem Spiel?

Sei kreativ! Vermeide Klischees wie:
- Milliardär trifft Kellnerin
- Fake-Dating
- Hochzeit absagen

Suche nach frischen Settings und ungewöhnlichen Berufen.

FORMAT:
## ARBEITSTITEL
[Titel]

## SYNOPSIS
[Drei Sätze]
"""
    
    synopsis = call_gemini(prompt, max_tokens=2000)
    
    if not synopsis:
        log("   ❌ Synopsis-Generierung fehlgeschlagen")
        return ""
    
    log(f"   ✓ Synopsis generiert")
    
    # Save draft
    draft_path = output_dir / "00_synopsis_entwurf.md"
    save_md(draft_path, synopsis)
    
    return synopsis


def step2_approval_and_setup(synopsis: str, output_dir: Path) -> tuple[Path, str, str]:
    """Step 2: User approves synopsis, create project folder"""
    log("\n" + "="*60)
    log("SCHRITT 2: SYNOPSIS BESTÄTIGUNG")
    log("="*60)
    
    while True:
        # Send for approval
        approved, feedback = telegram_approval(
            f"📖 *SYNOPSIS VORSCHLAG*\n\n{synopsis}\n\n*Passt das?*",
            timeout_minutes=120
        )
        
        if approved:
            break
        
        if feedback and feedback != "Timeout":
            log(f"   🔄 Generiere neue Synopsis mit Feedback...")
            prompt = f"""
{MASTER_STRUKTUR}

Die vorherige Synopsis wurde abgelehnt:
{synopsis}

Feedback vom Nutzer:
{feedback}

Erstelle eine NEUE Synopsis die das Feedback berücksichtigt.

FORMAT:
## ARBEITSTITEL
[Titel]

## SYNOPSIS
[Drei Sätze]
"""
            synopsis = call_gemini(prompt, max_tokens=2000)
        else:
            # Generate completely new
            synopsis = call_gemini(f"{MASTER_STRUKTUR}\n\nErstelle eine komplett andere Buchidee als vorher. Sei kreativ!\n\nFORMAT:\n## ARBEITSTITEL\n[Titel]\n\n## SYNOPSIS\n[Drei Sätze]", max_tokens=2000)
    
    # Extract title
    title_match = re.search(r'##\s*ARBEITSTITEL\s*\n+([^\n]+)', synopsis)
    titel = title_match.group(1).strip() if title_match else "Unbenannt"
    titel_clean = re.sub(r'[^a-zA-ZäöüÄÖÜß0-9_\- ]', '', titel)[:50]
    
    # Create project folder
    project_dir = output_dir / titel_clean
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Save confirmed synopsis
    save_md(project_dir / "01_synopsis.md", synopsis)
    
    log(f"   ✓ Projekt erstellt: {titel_clean}")
    
    return project_dir, titel, synopsis


def step3_master_struktur(project_dir: Path):
    """Step 3: Save Master-Struktur to folder"""
    log("\n" + "="*60)
    log("SCHRITT 3: MASTER-STRUKTUR ABLEGEN")
    log("="*60)
    
    save_md(project_dir / "02_master_struktur.md", MASTER_STRUKTUR)


def step4_charaktere(project_dir: Path, synopsis: str) -> dict:
    """Step 4: Gemini creates character sheets with Ghost/Lie/Banter"""
    log("\n" + "="*60)
    log("SCHRITT 4: CHARAKTERSHEETS ERSTELLEN")
    log("="*60)
    
    prompt = f"""
{MASTER_STRUKTUR}

SYNOPSIS:
{synopsis}

AUFGABE: Entwickle das komplette Personal für diese Geschichte.

Für JEDEN Charakter erstelle ein detailliertes Profil:

---

## 1. DIE HELDIN

**Name:** [Vor- und Nachname]
**Alter:** [Jahre]
**Beruf/Kompetenz:** [Was macht sie, worin ist sie gut?]

**Äußeres Ziel:** [Was will sie konkret erreichen?]
**Inneres Ziel:** [Was braucht sie emotional?]

**The Ghost:** [Welches schmerzhafte Ereignis aus der Vergangenheit blockiert sie?]
**The Lie:** [Welche falsche Überzeugung über sich selbst nutzt sie als Schutzschild?]
**Die Wahrheit:** [Was muss sie lernen/akzeptieren?]

**Stärken:** [3-4 konkrete Stärken]
**Schwächen:** [3-4 konkrete Schwächen]
**Banter-Stil:** [Wie verteidigt sie sich verbal? Sarkasmus? Ironie? Fakten?]

**Aussehen:** [Markante Details]
**Gewohnheiten/Ticks:** [2-3 charakteristische Verhaltensweisen]

---

## 2. DER HELD

[Gleiche Struktur wie Heldin]

**Warum ist er ihr perfekter Antagonist?** [Spezifische Reibungspunkte]
**Was fasziniert sie (ungewollt)?** [Konkrete Eigenschaften]

---

## 3. DIE DYNAMIK

**Forced Proximity:** [Warum können sie sich nicht aus dem Weg gehen?]
**Themen für Schlagabtausch:** [3-4 konkrete Streitpunkte]
**Der erste Funke:** [Was ist der Moment, wo beide merken: "Oh nein..."]

---

## 4. NEBENFIGUR: DER SAFE SPACE (Heldin)

**Name:** [Vor- und Nachname]
**Alter:** [Jahre]
**Beziehung zur Heldin:** [Freundin/Schwester/Kollegin]
**Funktion:** [Wie unterstützt sie die Heldin?]
**Eigener Arc:** [Wie entwickelt sich diese Figur?]
**Charakteristik:** [2-3 prägnante Eigenschaften]

---

## 5. NEBENFIGUR: DER WINGMAN (Held)

[Gleiche Struktur]

---

## 6. NEBENFIGUR: DER ANTAGONIST/STÖRFAKTOR

**Name:** [Vor- und Nachname]
**Alter:** [Jahre]
**Beziehung zu Held/Heldin:** [Ex? Konkurrent? Chef?]
**Motivation:** [Was will diese Person?]
**Bedrohung:** [Wie verschärft sie den Konflikt?]
**Eigener Arc:** [Wie endet ihre Geschichte?]

---

## 7. NEBENFIGUR: COMIC RELIEF / STIMME DER WEISHEIT

[Gleiche Struktur - oft exzentrisch oder älter]

---

## 8. NEBENFIGUR: DIE VARIABLE

[Gleiche Struktur - spezifisch fürs Setting]

---

Sei KONKRET und SPEZIFISCH. Keine generischen Beschreibungen.
"""
    
    charaktere_raw = call_gemini(prompt, max_tokens=12000)
    
    if not charaktere_raw:
        log("   ❌ Charaktererstellung fehlgeschlagen")
        return {}
    
    # Save complete file
    all_chars_path = project_dir / "03_charaktere_komplett.md"
    save_md(all_chars_path, charaktere_raw)
    
    # Parse and save individual character files
    char_sections = re.split(r'\n##\s+\d+\.', charaktere_raw)
    charaktere = {}
    
    for i, section in enumerate(char_sections[1:], 1):  # Skip first empty split
        # Extract character name
        lines = section.strip().split('\n')
        char_type = lines[0].strip() if lines else f"Charakter_{i}"
        
        # Find name in content
        name_match = re.search(r'\*\*Name:\*\*\s*([^\n]+)', section)
        char_name = name_match.group(1).strip() if name_match else char_type
        
        # Clean filename
        filename = re.sub(r'[^a-zA-ZäöüÄÖÜß0-9_\- ]', '', char_name)[:30]
        
        char_path = project_dir / f"03_{i:02d}_{filename}.md"
        save_md(char_path, f"## {char_type}\n{section}")
        
        charaktere[char_type] = {
            "name": char_name,
            "content": section,
            "file": char_path.name
        }
    
    log(f"   ✓ {len(charaktere)} Charaktere erstellt")
    
    # Telegram Approval
    while True:
        approved, feedback = telegram_approval(
            f"👥 *CHARAKTERSHEETS*\n\n{len(charaktere)} Charaktere erstellt.\n\nBitte prüfe die Datei.",
            filepath=all_chars_path,
            timeout_minutes=120
        )
        
        if approved:
            break
        
        if feedback and feedback != "Timeout":
            log(f"   🔄 Überarbeite Charaktere mit Feedback...")
            prompt = f"""
Die Charaktersheets wurden abgelehnt.

AKTUELLE VERSION:
{charaktere_raw}

FEEDBACK:
{feedback}

Überarbeite die Charaktere entsprechend dem Feedback.
Behalte das gleiche Format bei.
"""
            charaktere_raw = call_gemini(prompt, max_tokens=12000)
            save_md(all_chars_path, charaktere_raw)
    
    return charaktere


def step5_gliederung(project_dir: Path, synopsis: str, charaktere: dict) -> str:
    """Step 5: Gemini creates detailed outline (3000-4000 words)"""
    log("\n" + "="*60)
    log("SCHRITT 5: DETAILLIERTE GLIEDERUNG")
    log("="*60)
    
    # Load character content
    char_content = ""
    all_chars_path = project_dir / "03_charaktere_komplett.md"
    if all_chars_path.exists():
        char_content = all_chars_path.read_text()
    
    prompt = f"""
{MASTER_STRUKTUR}

SYNOPSIS:
{synopsis}

CHARAKTERE:
{char_content[:15000]}

AUFGABE: Erstelle eine detaillierte Gliederung (3000-4000 Wörter) für den gesamten Roman.

Die Gliederung muss enthalten:

## 1. ÜBERBLICK
- Zentrale Themen
- Emotionale Reise der Heldin
- Entwicklung der Liebesbeziehung (vom Feind zum Liebhaber)

## 2. DIE 7 PHASEN IM DETAIL

Für JEDE Phase:
- Welche Kapitel gehören dazu
- Was passiert konkret
- Wie entwickelt sich die Romance
- Wie entwickeln sich die Nebencharaktere
- Emotionale Beats

## 3. CHARAKTER-ENTWICKLUNGEN

Für JEDEN Charakter:
- Wo startet er/sie emotional?
- Schlüsselmomente der Entwicklung
- Wo endet er/sie?

## 4. DER ÄUSSERE KONFLIKT
- Was ist die externe Bedrohung/das Problem?
- Wie eskaliert es?
- Wie wird es gelöst?

## 5. DER INNERE KONFLIKT
- Die Ghosts und Lies in Aktion
- Wann werden sie konfrontiert?
- Wie werden sie überwunden?

## 6. SCHLÜSSELSZENEN
- Der Meet-Disaster
- Der erste echte Moment
- Der Midpoint (erster Kuss/Intimität)
- Der Bruch
- Das Grovel
- Das Happy End

## 7. KAPITELÜBERSICHT
- Vorläufige Anzahl Kapitel
- Grobe Zuordnung zu Phasen

Schreibe 3000-4000 Wörter. Sei KONKRET, nicht vage.
"""
    
    gliederung = call_gemini(prompt, max_tokens=8000)
    
    if not gliederung:
        log("   ❌ Gliederungserstellung fehlgeschlagen")
        return ""
    
    gliederung_path = project_dir / "04_gliederung.md"
    save_md(gliederung_path, gliederung)
    
    log(f"   ✓ Gliederung erstellt ({len(gliederung.split())} Wörter)")
    
    return gliederung


def step6_gliederung_approval(project_dir: Path, gliederung: str) -> str:
    """Step 6: User approves outline"""
    log("\n" + "="*60)
    log("SCHRITT 6: GLIEDERUNG BESTÄTIGUNG")
    log("="*60)
    
    gliederung_path = project_dir / "04_gliederung.md"
    
    while True:
        approved, feedback = telegram_approval(
            f"📋 *GLIEDERUNG*\n\n{len(gliederung.split())} Wörter\n\nBitte prüfe die Datei.",
            filepath=gliederung_path,
            timeout_minutes=120
        )
        
        if approved:
            break
        
        if feedback and feedback != "Timeout":
            log(f"   🔄 Überarbeite Gliederung mit Feedback...")
            
            # Load current files
            synopsis = (project_dir / "01_synopsis.md").read_text()
            char_content = (project_dir / "03_charaktere_komplett.md").read_text()
            
            prompt = f"""
Die Gliederung wurde abgelehnt.

AKTUELLE GLIEDERUNG:
{gliederung}

FEEDBACK:
{feedback}

SYNOPSIS:
{synopsis}

CHARAKTERE:
{char_content[:10000]}

Überarbeite die Gliederung entsprechend dem Feedback.
Behalte Umfang (3000-4000 Wörter) und Struktur bei.
"""
            gliederung = call_gemini(prompt, max_tokens=8000)
            save_md(gliederung_path, gliederung)
    
    log(f"   ✓ Gliederung bestätigt")
    return gliederung


def step7_kapitel_gliederungen(project_dir: Path, gliederung: str) -> list:
    """Step 7: Gemini creates detailed chapter outlines with Fakten-Logbuch"""
    log("\n" + "="*60)
    log("SCHRITT 7: KAPITEL-GLIEDERUNGEN + FAKTEN-LOGBUCH")
    log("="*60)
    
    # Load context
    synopsis = (project_dir / "01_synopsis.md").read_text()
    char_content = (project_dir / "03_charaktere_komplett.md").read_text()
    
    # First: Let Gemini determine chapter count and structure
    prompt = f"""
{MASTER_STRUKTUR}

SYNOPSIS:
{synopsis}

GLIEDERUNG:
{gliederung}

AUFGABE: Bestimme die optimale Kapitelstruktur.

Für einen 100.000-Wörter-Roman:
- Wie viele Kapitel sind ideal?
- Welche Kapitel gehören zu welcher Phase?
- Wie lang sollte jedes Kapitel sein (keine feste Vorgabe - je nach Inhalt)?

FORMAT:
## KAPITELSTRUKTUR

| Nr | Titel | Phase | Geschätzte Wörter | Kerninhalt |
|----|-------|-------|-------------------|------------|
| 1  | ...   | I     | 4000              | ...        |
...

Begründe kurz deine Entscheidungen.
"""
    
    struktur = call_gemini(prompt, max_tokens=4000)
    struktur_path = project_dir / "05_kapitel_struktur.md"
    save_md(struktur_path, struktur)
    
    # Parse chapter count
    kapitel_matches = re.findall(r'\|\s*(\d+)\s*\|', struktur)
    num_chapters = max([int(k) for k in kapitel_matches]) if kapitel_matches else 20
    
    log(f"   ✓ {num_chapters} Kapitel geplant")
    
    # Create detailed outline for each chapter
    kapitel_gliederungen = []
    
    for kap_num in range(1, num_chapters + 1):
        log(f"\n   [Kapitel {kap_num}/{num_chapters}]...")
        
        # Context from previous chapter
        prev_context = ""
        if kap_num > 1 and kapitel_gliederungen:
            prev = kapitel_gliederungen[-1]
            prev_context = f"""
VORHERIGES KAPITEL ({kap_num-1}):
{prev.get('gliederung', '')[-2000:]}

FAKTEN-LOGBUCH BIS HIERHER:
{prev.get('fakten_logbuch', '')}
"""
        
        prompt = f"""
{MASTER_STRUKTUR}

SYNOPSIS:
{synopsis}

CHARAKTERE (Kurzfassung):
{char_content[:8000]}

GESAMT-GLIEDERUNG:
{gliederung[:6000]}

KAPITELSTRUKTUR:
{struktur[:3000]}

{prev_context}

AUFGABE: Erstelle eine DETAILLIERTE Gliederung für Kapitel {kap_num} (500-1000 Wörter).

Die Gliederung muss alles enthalten, was man braucht, um das Kapitel zu schreiben:

## KAPITEL {kap_num}: [TITEL]

### ÜBERBLICK
- Phase: [I-VII]
- Ziel-Wortzahl: [selbst festlegen basierend auf Inhalt]
- Funktion im Roman: [Was muss dieses Kapitel erreichen?]

### SZENEN
Für jede Szene:
1. **Szene X: [Titel]**
   - Ort: [konkret]
   - Zeit: [Tageszeit, wie viel Zeit seit letzter Szene]
   - Anwesende: [wer ist da]
   - Was passiert: [Beat für Beat]
   - Emotionaler Fokus: [Was fühlt die Heldin?]
   - Banter/Dialog-Highlights: [Schlüsseldialoge skizzieren]

### CHARAKTER-INNENLEBEN
- Heldin: [Ihre Gedanken, Gefühle, Motivation in diesem Kapitel]
- Held: [Sein Verhalten, was er verbirgt]
- Nebenfiguren: [Falls relevant]

### ENTWICKLUNG DER ROMANCE
- Wo stehen sie am Anfang des Kapitels?
- Was verändert sich?
- Wo stehen sie am Ende?

### HOOK/CLIFFHANGER
- Wie endet das Kapitel?
- Warum muss man weiterlesen?

---

## FAKTEN-LOGBUCH (KAPITEL {kap_num})

| Kategorie | Details |
|-----------|---------|
| **Zeitlicher Abstand zum Vor-Kapitel** | [Stunden/Tage] |
| **Aktueller Ort** | [Wo spielt das Kapitel?] |
| **Wetter/Atmosphäre** | [Falls relevant] |
| **Kleidung der Figuren** | [Falls beschrieben] |
| **Neu etablierte Fakten** | [Alles Neue: Backstory-Enthüllungen, physische Details, Beziehungen] |
| **Emotionaler Status** | [Heldin: ..., Held: ...] |
| **Stand der Romance** | [Feinde/Respekt/Anziehung/...] |

---

Schreibe 500-1000 Wörter. Sei KONKRET - jemand soll anhand dieser Gliederung das Kapitel schreiben können.
"""
        
        kap_gliederung = call_gemini(prompt, max_tokens=4000)
        
        if not kap_gliederung:
            log(f"      ⚠️ Kapitel {kap_num} fehlgeschlagen")
            continue
        
        # Extract Fakten-Logbuch
        fakten_match = re.search(r'##\s*FAKTEN-LOGBUCH.*?(?=\n##|\Z)', kap_gliederung, re.DOTALL)
        fakten_logbuch = fakten_match.group(0) if fakten_match else ""
        
        # Extract target word count
        wc_match = re.search(r'Ziel-Wortzahl:\s*(\d+)', kap_gliederung)
        target_wc = int(wc_match.group(1)) if wc_match else 4000
        
        kapitel_gliederungen.append({
            "nummer": kap_num,
            "gliederung": kap_gliederung,
            "fakten_logbuch": fakten_logbuch,
            "target_words": target_wc
        })
        
        # Save individual file
        kap_path = project_dir / f"06_kapitel_{kap_num:02d}_gliederung.md"
        save_md(kap_path, kap_gliederung)
        
        log(f"      ✓ Kapitel {kap_num} ({len(kap_gliederung.split())} Wörter, Ziel: {target_wc})")
    
    # Save combined file
    combined = "\n\n---\n\n".join([k["gliederung"] for k in kapitel_gliederungen])
    save_md(project_dir / "06_alle_kapitel_gliederungen.md", combined)
    
    return kapitel_gliederungen


def step8_kapitel_approval(project_dir: Path, kapitel_gliederungen: list) -> list:
    """Step 8: User approves chapter outlines with feedback"""
    log("\n" + "="*60)
    log("SCHRITT 8: KAPITEL-GLIEDERUNGEN BESTÄTIGUNG")
    log("="*60)
    
    combined_path = project_dir / "06_alle_kapitel_gliederungen.md"
    
    while True:
        approved, feedback = telegram_approval(
            f"📚 *KAPITEL-GLIEDERUNGEN*\n\n{len(kapitel_gliederungen)} Kapitel\n\nBitte prüfe die Datei.",
            filepath=combined_path,
            timeout_minutes=180
        )
        
        if approved:
            break
        
        if feedback and feedback != "Timeout":
            log(f"   🔄 Feedback erhalten, überarbeite...")
            
            # Load context
            synopsis = (project_dir / "01_synopsis.md").read_text()
            gliederung = (project_dir / "04_gliederung.md").read_text()
            current = combined_path.read_text()
            
            prompt = f"""
Die Kapitel-Gliederungen wurden abgelehnt.

FEEDBACK:
{feedback}

AKTUELLE GLIEDERUNGEN:
{current[:30000]}

SYNOPSIS:
{synopsis}

GESAMT-GLIEDERUNG:
{gliederung[:5000]}

Überarbeite die Kapitel-Gliederungen entsprechend dem Feedback.
Achte besonders auf die genannten Punkte.
Behalte das Fakten-Logbuch Format bei.
"""
            updated = call_gemini(prompt, max_tokens=16000)
            save_md(combined_path, updated)
            
            # Re-parse
            # (simplified - in production would re-parse properly)
    
    log(f"   ✓ Kapitel-Gliederungen bestätigt")
    return kapitel_gliederungen


def step9_logik_check(project_dir: Path, kapitel_gliederungen: list) -> str:
    """Step 9: Gemini checks all chapters for logic errors"""
    log("\n" + "="*60)
    log("SCHRITT 9: LOGIK-CHECK ÜBER ALLE KAPITEL")
    log("="*60)
    
    # Load all content
    synopsis = (project_dir / "01_synopsis.md").read_text()
    charaktere = (project_dir / "03_charaktere_komplett.md").read_text()
    gliederung = (project_dir / "04_gliederung.md").read_text()
    alle_kapitel = (project_dir / "06_alle_kapitel_gliederungen.md").read_text()
    
    prompt = f"""
Du bist ein erfahrener Lektor. Prüfe diese Roman-Planung auf ALLE Logikfehler.

SYNOPSIS:
{synopsis}

CHARAKTERE (mit Ghost/Lie/Banter):
{charaktere[:12000]}

GESAMT-GLIEDERUNG:
{gliederung[:8000]}

ALLE KAPITEL-GLIEDERUNGEN:
{alle_kapitel[:40000]}

PRÜFE AUF:

## 1. CHARAKTER-KONSISTENZ
- Verhalten sich alle Figuren konsistent zu ihren Charakterbögen?
- Werden die Ghosts und Lies korrekt aufgelöst?
- Stimmen die Banter-Stile?
- Verschwinden Charaktere plötzlich?

## 2. ROMANCE-ENTWICKLUNG
- Ist die Liebesbeziehung der MITTELPUNKT?
- Entwickelt sich die Romance schrittweise und glaubwürdig?
- Kippen die Charaktere zu plötzlich von Feinden zu Liebenden?
- Sind alle 7 Phasen abgedeckt?

## 3. PLOT-LOGIK
- Gibt es Zeitsprünge die nicht erklärt werden?
- Wissen Charaktere plötzlich Dinge die sie nicht wissen können?
- Gibt es ungelöste Handlungsstränge?
- Stimmt die Timeline?

## 4. FAKTEN-KONSISTENZ
- Sind Namen durchgehend konsistent?
- Sind Berufe/Fähigkeiten konsistent?
- Sind Orte konsistent beschrieben?
- Gibt es Widersprüche in etablierten Fakten?

## 5. STRUKTUR
- Stimmt die Verteilung auf die 7 Phasen?
- Ist der Midpoint am richtigen Punkt?
- Kommt das Grovel zur richtigen Zeit?

ERSTELLE EINE MÄNGELLISTE:

## MÄNGELLISTE

### KRITISCHE FEHLER (müssen korrigiert werden)
1. [Kapitel X]: [Problem] → [Lösung]
2. ...

### WARNUNGEN (sollten geprüft werden)
1. [Kapitel X]: [Bedenken]
2. ...

### VERBESSERUNGSVORSCHLÄGE
1. ...

Sei gründlich! Jeder übersehene Fehler führt zu Problemen im fertigen Roman.
"""
    
    check_result = call_gemini(prompt, max_tokens=8000, use_flash=True)
    
    if not check_result:
        log("   ❌ Logik-Check fehlgeschlagen")
        return ""
    
    maengel_path = project_dir / "07_maengelliste.md"
    save_md(maengel_path, check_result)
    
    # Count issues
    kritisch = len(re.findall(r'###\s*KRITISCHE FEHLER.*?(?=###|\Z)', check_result, re.DOTALL))
    
    log(f"   ✓ Logik-Check abgeschlossen")
    telegram_send_file(maengel_path, f"🔍 *LOGIK-CHECK*\n\nMängelliste erstellt.")
    
    return check_result


def step10_korrektur(project_dir: Path, maengelliste: str, kapitel_gliederungen: list) -> list:
    """Step 10: Claude corrects errors from Mängelliste"""
    log("\n" + "="*60)
    log("SCHRITT 10: KORREKTUREN (Claude)")
    log("="*60)
    
    if "KRITISCHE FEHLER" not in maengelliste or "Keine kritischen Fehler" in maengelliste:
        log("   ✓ Keine kritischen Fehler zu korrigieren")
        return kapitel_gliederungen
    
    # Extract critical errors
    kritisch_match = re.search(r'###\s*KRITISCHE FEHLER.*?(?=###|\Z)', maengelliste, re.DOTALL)
    kritische_fehler = kritisch_match.group(0) if kritisch_match else ""
    
    # For each chapter mentioned in errors, correct it
    kapitel_pattern = re.findall(r'Kapitel\s*(\d+)', kritische_fehler)
    kapitel_to_fix = list(set([int(k) for k in kapitel_pattern]))
    
    log(f"   Korrigiere Kapitel: {kapitel_to_fix}")
    
    for kap_num in kapitel_to_fix:
        if kap_num > len(kapitel_gliederungen):
            continue
        
        log(f"   [Kapitel {kap_num}]...")
        
        kap = kapitel_gliederungen[kap_num - 1]
        kap_path = project_dir / f"06_kapitel_{kap_num:02d}_gliederung.md"
        
        if not kap_path.exists():
            continue
        
        current_content = kap_path.read_text()
        
        prompt = f"""
Du bist Lektor. Korrigiere diese Kapitel-Gliederung basierend auf der Mängelliste.

MÄNGELLISTE (relevant für Kapitel {kap_num}):
{kritische_fehler}

AKTUELLE GLIEDERUNG KAPITEL {kap_num}:
{current_content}

Korrigiere NUR die genannten Probleme.
Behalte Format und Fakten-Logbuch bei.
Gib die VOLLSTÄNDIGE korrigierte Gliederung aus.
"""
        
        corrected = call_claude(prompt)
        
        if corrected and len(corrected) > 500:
            save_md(kap_path, corrected)
            kapitel_gliederungen[kap_num - 1]["gliederung"] = corrected
            log(f"      ✓ Korrigiert")
        else:
            log(f"      ⚠️ Korrektur fehlgeschlagen")
    
    # Update combined file
    combined = "\n\n---\n\n".join([k["gliederung"] for k in kapitel_gliederungen])
    save_md(project_dir / "06_alle_kapitel_gliederungen.md", combined)
    
    return kapitel_gliederungen


def step11_schreiben(project_dir: Path, kapitel_gliederungen: list) -> list:
    """Step 11: Claude writes each chapter"""
    log("\n" + "="*60)
    log("SCHRITT 11: KAPITEL SCHREIBEN (Claude)")
    log("="*60)
    
    # Load context
    charaktere = (project_dir / "03_charaktere_komplett.md").read_text()
    
    # Collect all Fakten-Logbücher
    fakten_gesamt = ""
    for kap in kapitel_gliederungen:
        fakten_gesamt += f"\n\n### Kapitel {kap['nummer']}\n{kap.get('fakten_logbuch', '')}"
    
    fertige_kapitel = []
    letzter_absatz = ""
    
    for i, kap in enumerate(kapitel_gliederungen):
        kap_num = kap["nummer"]
        target_words = kap.get("target_words", 4000)
        gliederung = kap["gliederung"]
        
        log(f"\n   [Kapitel {kap_num}/{len(kapitel_gliederungen)}] Ziel: {target_words} Wörter...")
        
        prompt = f"""
Du bist ein Bestseller-Autor. Schreibe Kapitel {kap_num} basierend auf dieser Gliederung.

STIL:
- Contemporary Romance / Enemies-to-Lovers
- Hybrid aus Nora Roberts (starke Frauen, atmosphärisch) und Julia Quinn (Banter, Humor)
- Deutsch (Deutschland)
- Deutsche Anführungszeichen: „..." und ‚...'
- Gedanken der Heldin: Ich-Form, KURSIV (*Gedanke*)
- Single POV (Heldin, dritte Person)
- Dialoge: schlagfertig, mit Subtext
- Kompetenz ist sexy, Worte sind Vorspiel, Lachen vor Küssen

CHARAKTERE:
{charaktere[:6000]}

KAPITEL-GLIEDERUNG:
{gliederung}

FAKTEN-LOGBUCH (alle bisherigen Kapitel):
{fakten_gesamt[:4000]}

LETZTER ABSATZ DES VORHERIGEN KAPITELS:
{letzter_absatz if letzter_absatz else "(Dies ist das erste Kapitel)"}

AUFGABE:
- Schreibe Kapitel {kap_num} mit ca. {target_words} Wörtern
- Folge der Gliederung EXAKT
- Achte auf Kontinuität zum vorherigen Kapitel
- Charaktere verhalten sich wie in ihren Bögen beschrieben (Ghost, Lie, Banter-Stil!)
- Baue Humor und Banter ein
- Keine Markdown-Überschriften im Text

Beginne direkt mit dem Kapiteltext:
"""
        
        chapter = call_claude(prompt)
        
        if not chapter:
            log(f"      ❌ Schreiben fehlgeschlagen")
            continue
        
        word_count = len(chapter.split())
        log(f"      ✓ Geschrieben: {word_count} Wörter")
        
        # Check if too short
        if word_count < target_words * 0.7:
            log(f"      ⚠️ Zu kurz ({word_count}/{target_words}) - Anreichern...")
            
            enrich_prompt = f"""
Das Kapitel ist zu kurz. Erweitere es auf ca. {target_words} Wörter.

AKTUELLER TEXT ({word_count} Wörter):
{chapter}

GLIEDERUNG (was fehlt vielleicht?):
{gliederung}

Erweitere den Text:
- Mehr Sinnesbeschreibungen
- Mehr innere Monologe der Heldin
- Mehr Dialog/Banter
- Mehr atmosphärische Details

Gib den VOLLSTÄNDIGEN erweiterten Text aus.
"""
            enriched = call_claude(enrich_prompt)
            if enriched and len(enriched.split()) > word_count:
                chapter = enriched
                word_count = len(chapter.split())
                log(f"      ✓ Angereichert: {word_count} Wörter")
        
        # Save
        kap_path = project_dir / f"08_kapitel_{kap_num:02d}.md"
        save_md(kap_path, f"**KAPITEL {kap_num}**\n\n{chapter}")
        
        fertige_kapitel.append({
            "nummer": kap_num,
            "text": chapter,
            "words": word_count
        })
        
        # Update letzter Absatz
        paragraphs = chapter.split('\n\n')
        letzter_absatz = paragraphs[-1] if paragraphs else ""
        
        # Progress update every 5 chapters
        if kap_num % 5 == 0:
            total_words = sum([k["words"] for k in fertige_kapitel])
            telegram_send(f"📝 *Fortschritt*\n\n{kap_num}/{len(kapitel_gliederungen)} Kapitel\n{total_words:,} Wörter")
    
    return fertige_kapitel


def step12_final_check(project_dir: Path, fertige_kapitel: list) -> str:
    """Step 12: Gemini does final check"""
    log("\n" + "="*60)
    log("SCHRITT 12: FINAL-CHECK (Gemini)")
    log("="*60)
    
    # Combine all chapters
    full_novel = "\n\n---\n\n".join([f"**Kapitel {k['nummer']}**\n\n{k['text']}" for k in fertige_kapitel])
    
    # Load context
    gliederung = (project_dir / "04_gliederung.md").read_text()
    charaktere = (project_dir / "03_charaktere_komplett.md").read_text()
    
    prompt = f"""
Du bist ein erfahrener Lektor. Prüfe diesen fertigen Roman auf Probleme.

GEPLANTE GLIEDERUNG:
{gliederung[:8000]}

CHARAKTERE:
{charaktere[:8000]}

FERTIGER ROMAN (Auszug):
{full_novel[:50000]}

PRÜFE:

1. **Erzählfluss:** Gibt es holprige Übergänge zwischen Kapiteln?
2. **Konsistenz:** Stimmen Namen, Fakten, Timeline?
3. **Charaktere:** Verhalten sich alle konsistent? Sind Ghost/Lie/Banter erkennbar?
4. **Romance:** Ist die Entwicklung glaubwürdig? Alle 7 Phasen abgedeckt?
5. **Gliederungs-Treue:** Passt der Text zur geplanten Gliederung?
6. **Qualität:** Wiederholungen? Flache Dialoge? Fehlender Humor?

ERSTELLE FEEDBACK:

## FINAL-CHECK ERGEBNIS

### KRITISCHE KORREKTUREN
[Kapitel X]: [Problem] → [Konkrete Korrektur]

### EMPFOHLENE VERBESSERUNGEN
[Kapitel X]: [Verbesserung]

### POSITIVES
[Was funktioniert gut?]

### GESAMTBEWERTUNG
[Kurzes Fazit]
"""
    
    feedback = call_gemini(prompt, max_tokens=8000, use_flash=True)
    
    feedback_path = project_dir / "09_final_check.md"
    save_md(feedback_path, feedback)
    
    telegram_send_file(feedback_path, "🔍 *FINAL-CHECK*\n\nFeedback erstellt.")
    
    return feedback


def step13_finalisierung(project_dir: Path, fertige_kapitel: list, feedback: str) -> Path:
    """Step 13: Claude implements feedback and creates final output"""
    log("\n" + "="*60)
    log("SCHRITT 13: FINALISIERUNG")
    log("="*60)
    
    # Check if critical corrections needed
    if "KRITISCHE KORREKTUREN" in feedback and "Keine" not in feedback:
        log("   Setze kritische Korrekturen um...")
        
        # Extract corrections
        kritisch_match = re.search(r'###\s*KRITISCHE KORREKTUREN.*?(?=###|\Z)', feedback, re.DOTALL)
        kritische = kritisch_match.group(0) if kritisch_match else ""
        
        # Find affected chapters
        kapitel_pattern = re.findall(r'Kapitel\s*(\d+)', kritische)
        kapitel_to_fix = list(set([int(k) for k in kapitel_pattern]))
        
        for kap_num in kapitel_to_fix:
            if kap_num > len(fertige_kapitel):
                continue
            
            log(f"   [Kapitel {kap_num}] Korrigiere...")
            
            kap = fertige_kapitel[kap_num - 1]
            
            prompt = f"""
Korrigiere dieses Kapitel basierend auf dem Feedback.

FEEDBACK:
{kritische}

AKTUELLES KAPITEL {kap_num}:
{kap['text']}

Setze NUR die genannten Korrekturen um.
Gib das VOLLSTÄNDIGE korrigierte Kapitel aus.
"""
            
            corrected = call_claude(prompt)
            
            if corrected and len(corrected) > 500:
                fertige_kapitel[kap_num - 1]["text"] = corrected
                fertige_kapitel[kap_num - 1]["words"] = len(corrected.split())
                log(f"      ✓ Korrigiert")
    
    # Create final novel file
    log("   Erstelle Gesamtdatei...")
    
    # Get title
    synopsis = (project_dir / "01_synopsis.md").read_text()
    title_match = re.search(r'##\s*ARBEITSTITEL\s*\n+([^\n]+)', synopsis)
    titel = title_match.group(1).strip() if title_match else "Roman"
    
    # Combine all chapters
    full_novel = f"# {titel}\n\n_Ein Roman_\n\n---\n\n"
    
    for kap in fertige_kapitel:
        full_novel += f"## Kapitel {kap['nummer']}\n\n{kap['text']}\n\n---\n\n"
    
    # Save
    roman_path = project_dir / f"{re.sub(r'[^a-zA-ZäöüÄÖÜß0-9 ]', '', titel)[:40]}.md"
    save_md(roman_path, full_novel)
    
    # Statistics
    total_words = sum([k["words"] for k in fertige_kapitel])
    
    log(f"\n   ✓ FERTIG: {roman_path.name}")
    log(f"   ✓ {len(fertige_kapitel)} Kapitel")
    log(f"   ✓ {total_words:,} Wörter")
    
    # Send via Telegram
    telegram_send(f"""✅ *ROMAN FERTIG!*

📖 *{titel}*
📚 {len(fertige_kapitel)} Kapitel
📊 {total_words:,} Wörter
📁 {project_dir.name}""")
    
    telegram_send_file(roman_path, f"📚 *{titel}*\n\n{total_words:,} Wörter")
    
    return roman_path


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(theme: str = None, wait_for_start: bool = True):
    """Run the complete 13-step pipeline"""
    global LOG_FILE
    
    # Setup
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    
    base_dir = Path("/Users/seba/Developer/novel-pipeline-v4")
    output_dir = base_dir / f"output_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    LOG_FILE = output_dir / "pipeline.log"
    
    log(f"\n{'#'*60}")
    log(f"# NOVEL PIPELINE V5")
    log(f"# Start: {start_time}")
    log(f"# Output: {output_dir}")
    log(f"{'#'*60}")
    
    # Wait for start if needed
    if wait_for_start:
        telegram_wait_for_start()
    
    try:
        # Step 1: Synopsis
        synopsis = step1_synopsis(output_dir, theme=theme)
        if not synopsis:
            raise Exception("Synopsis-Generierung fehlgeschlagen")
        
        # Step 2: Approval + Setup
        project_dir, titel, synopsis = step2_approval_and_setup(synopsis, output_dir)
        
        # Step 3: Master-Struktur
        step3_master_struktur(project_dir)
        
        # Step 4: Charaktere
        charaktere = step4_charaktere(project_dir, synopsis)
        if not charaktere:
            raise Exception("Charakter-Erstellung fehlgeschlagen")
        
        # Step 5: Gliederung
        gliederung = step5_gliederung(project_dir, synopsis, charaktere)
        if not gliederung:
            raise Exception("Gliederung fehlgeschlagen")
        
        # Step 6: Gliederung Approval
        gliederung = step6_gliederung_approval(project_dir, gliederung)
        
        # Step 7: Kapitel-Gliederungen
        kapitel_gliederungen = step7_kapitel_gliederungen(project_dir, gliederung)
        if not kapitel_gliederungen:
            raise Exception("Kapitel-Gliederungen fehlgeschlagen")
        
        # Step 8: Kapitel Approval
        kapitel_gliederungen = step8_kapitel_approval(project_dir, kapitel_gliederungen)
        
        # Step 9: Logik-Check
        maengelliste = step9_logik_check(project_dir, kapitel_gliederungen)
        
        # Step 10: Korrekturen
        kapitel_gliederungen = step10_korrektur(project_dir, maengelliste, kapitel_gliederungen)
        
        # Step 11: Schreiben
        fertige_kapitel = step11_schreiben(project_dir, kapitel_gliederungen)
        if not fertige_kapitel:
            raise Exception("Schreiben fehlgeschlagen")
        
        # Step 12: Final-Check
        feedback = step12_final_check(project_dir, fertige_kapitel)
        
        # Step 13: Finalisierung
        roman_path = step13_finalisierung(project_dir, fertige_kapitel, feedback)
        
        # Done
        duration = datetime.now() - start_time
        log(f"\n{'#'*60}")
        log(f"# PIPELINE ABGESCHLOSSEN")
        log(f"# Dauer: {duration}")
        log(f"# Output: {roman_path}")
        log(f"{'#'*60}")
        
        return roman_path
        
    except Exception as e:
        log(f"\n❌ PIPELINE FEHLER: {e}")
        telegram_send(f"❌ *Pipeline Fehler*\n\n{e}")
        raise


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    print("=== Novel Pipeline V5 ===")
    print("")
    print("Verwendung:")
    print("  python novel_pipeline_v5.py --telegram              # Warte auf /start, Gemini generiert Thema")
    print("  python novel_pipeline_v5.py --telegram 'Thema'      # Warte auf /start, nutze vorgegebenes Thema")
    print("  python novel_pipeline_v5.py 'Thema'                 # Direkt starten mit Thema")
    print("")
    print("Beispiel:")
    print("  python novel_pipeline_v5.py 'Winzerin im Rheingau trifft Weinkritiker'")
    print("")
    
    if len(sys.argv) < 2:
        print("Bitte Modus angeben (--telegram oder Thema)")
        sys.exit(1)
    
    theme = None
    wait_telegram = False
    
    for arg in sys.argv[1:]:
        if arg == "--telegram":
            wait_telegram = True
        elif not arg.startswith("-"):
            theme = arg
    
    if wait_telegram:
        run_pipeline(theme=theme, wait_for_start=True)
    elif theme:
        run_pipeline(theme=theme, wait_for_start=False)
    else:
        print("Bitte Thema angeben oder --telegram nutzen")
