# Novel Pipeline V4 - Komplette Dokumentation

## ÜBERSICHT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NOVEL PIPELINE V4                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  INPUT: Setting (z.B. "Archäologin auf Kreta entdeckt antikes Geheimnis")  │
│  OUTPUT: Roman (~80k Wörter) als MD + MP3 Hörbuch                           │
│  DAUER: ~7-8 Stunden                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## MODELLE & ROLLEN

| Modell | Rolle | Verwendung |
|--------|-------|------------|
| **Gemini 3 Pro** | Dramaturg/Planer | Gliederung, Akte, Kapitel-Outlines |
| **Gemini 2.0 Flash** | Kritiker/Prüfer | Self-Critique, Flow-Check, Polish, Gesamt-Check |
| **Claude 3.5 Sonnet** | Autor | Prosa schreiben, Kapitel verfassen |
| **OpenAI text-embedding-3-small** | Embeddings | Qdrant Vektorspeicher |
| **macOS say (Anna)** | TTS | Hörbuch-Generierung |

---

## PHASE 0: START

### Telegram Start-Trigger
```
User sendet: /start <setting>
Pipeline empfängt Setting und startet
```

---

## PHASE 1: GROB-GLIEDERUNG

### 1.1 Erste Version erstellen

**Modell:** Gemini 3 Pro  
**Max Tokens:** 16.000  
**Input:**
```
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
```

**STIL-Definition:**
```
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

SPRACHE:
- Deutsch (Deutschland)
- Deutsche Anführungszeichen: „..." und ‚...'
- Keine unnötigen Anglizismen
- Natürlicher, flüssiger Sprachstil
"""

SELF_CRITIQUE_PROMPT = """
═══════════════════════════════════════════════════════════════
KRITISCHE SELBST-PRÜFUNG
═══════════════════════════════════════════════════════════════

WICHTIG: Schreib mir NICHT was ich hören möchte.
Schreib was SINN MACHT.
```

**Phase 1 Prompt:**
```
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

    gliederung = call_gemini(prompt, max_tokens=16000)
```

**Output:** Gliederung mit:
- Titel
- Heldin (Name, Alter, Beruf, Ziele, Konflikte, Schwächen, Stärken)
- Hero (Name, Alter, Beruf, Geheimnis, Verletzlichkeit)
- Antagonist (Name, Rolle, Motiv, Verbindung)
- 5-6 Nebencharaktere (detailliert mit Archetyp, Motivation, Arc)
- 7 Phasen mit Kapitelzuordnung

### 1.2 Self-Critique (3x)

**Modell:** Gemini 2.0 Flash  
**Max Tokens:** 16.000  

**Self-Critique Prompt:**
```
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


```

### 1.3 Telegram Approval

**Format:** MD-Datei als Attachment  
**Dateiname:** `gliederung_v{attempt}.md`  
**User antwortet:** JA/NEIN  
**Bei NEIN:** Neu generieren (unbegrenzt)

### 1.4 Qdrant Speicherung

**Collection:** `memory_novelpipeline`  
**Embedding:** OpenAI text-embedding-3-small (1536 dims)  
**Metadata:** `{type: "gliederung", phase: 1, setting: "...", approved: true}`

---

## PHASE 2: AKT-GLIEDERUNGEN

### Für jeden Akt (1, 2, 3):

**Modell:** Gemini 3 Pro  
**Max Tokens:** 12.000  

**Akt-Zuordnung:**
- Akt 1: Phase I + II (0-35%) - Setup + Forced Proximity
- Akt 2: Phase III + IV (35-75%) - Intimacy + Separation
- Akt 3: Phase V + VI + VII (75-100%) - Crisis + Finale + HEA

**Input:**
- REGELWERK
- Gesamt-Gliederung aus Phase 1

**Prompt:**
```
{REGELWERK}

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
```

**Self-Critique:** 1x mit Gemini Flash

**Telegram Approval:** Pro Akt als MD-Datei  
**Qdrant:** Speichern mit `{type: "akt", akt_num: X}`

---

## PHASE 2.5: KAPITEL-GLIEDERUNGEN

### Für jedes Kapitel:

**Modell:** Gemini 3 Pro  
**Max Tokens:** 8.000  

**Input:**
- Roman-Kontext (Gliederung, erste 4000 Zeichen)
- Charaktere (aus Phase 1 extrahiert, bis 3000 Zeichen)
- Akt-Gliederung (bis 2500 Zeichen)
- Kapitel-Info (Nummer, Titel)

**Prompt:**
```
{REGELWERK}

═══════════════════════════════════════════════════════════════
ROMAN-KONTEXT
═══════════════════════════════════════════════════════════════
{roman_kontext}

═══════════════════════════════════════════════════════════════
CHARAKTERE
═══════════════════════════════════════════════════════════════
{charaktere}

═══════════════════════════════════════════════════════════════
AKT-GLIEDERUNG
═══════════════════════════════════════════════════════════════
{akt_gliederung}

AUFGABE: Detaillierte Szenen-Gliederung für Kapitel {kapitel_nr}: {kapitel_titel}

## FIGUREN IN DIESEM KAPITEL
Liste ALLE Figuren die vorkommen mit:
- Name
- Rolle in dieser Szene
- Ihr typisches Verhalten (aus Charakter-Beschreibung!)
- Wie interagieren sie mit Heldin/Hero?

## SZENEN (3-5 pro Kapitel)
### Szene X: [Titel]
- Ort: [KONKRET]
- Anwesende Figuren: [Namen + was sie TUN]
- Charakter-Dynamik: [Wie verhalten sich die Figuren zueinander?]
- Was passiert: [Beat für Beat]
- Emotionaler Kern: [Was fühlt die Heldin?]
- Hook am Ende: [Warum weiterlesen?]

## CONSTRAINTS
- Was darf NICHT passieren?
- Welches Charakter-Verhalten wäre OOC (out of character)?
```

**Self-Critique:** 1x mit Gemini Flash

**Output-Struktur:**
```python
{
    "nummer": 1,
    "titel": "Der Nullpunkt",
    "akt": 1,
    "gliederung": "...",  # Volle Szenen-Gliederung
    "phase": "I"
}
```

**Telegram Approval:** Alle Kapitel zusammen als `kapitel_struktur.md`  
**Qdrant:** Speichern mit `{type: "kapitel_gliederung", kapitel: X}`

---

## PHASE 3: SCHREIBEN

### Für jedes Kapitel:

**Modell:** Claude 3.5 Sonnet (via CLI)  
**Ziel:** 3.500 Wörter pro Kapitel  

**Input (Kontext-Assembly):**

1. **STIL** (komplett)
2. **Charaktere** (aus Gliederung extrahiert, bis 4500 Zeichen)
3. **Akt-Gliederung** (bis 2000 Zeichen)
4. **Kapitel-Gliederung** (komplett aus Phase 2.5)
5. **Vorheriges Kapitel** (letzte 2000 Wörter)
6. **Qdrant-Kontext** (semantische Suche, 3 Ergebnisse)

**Prompt:**
```
{STIL}

═══════════════════════════════════════════════════════════════
CHARAKTERE (WICHTIG - Verhalten beachten!)
═══════════════════════════════════════════════════════════════
{charaktere}

═══════════════════════════════════════════════════════════════
AKT-GLIEDERUNG (Überblick)
═══════════════════════════════════════════════════════════════
{akt_gliederung}

═══════════════════════════════════════════════════════════════
KAPITEL-GLIEDERUNG (folge EXAKT!)
═══════════════════════════════════════════════════════════════
{kapitel_gliederung}

═══════════════════════════════════════════════════════════════
VORHERIGES KAPITEL (letzte Passage - für Kontinuität)
═══════════════════════════════════════════════════════════════
{vorheriges_kapitel}

═══════════════════════════════════════════════════════════════
ZUSÄTZLICHER KONTEXT (aus Qdrant)
═══════════════════════════════════════════════════════════════
{qdrant_kontext}

SCHREIBE JETZT KAPITEL {nummer}: {titel}

REGELN:
- {wortzahl_ziel} Wörter
- Charaktere verhalten sich wie in den Charakterbögen beschrieben!
- Single POV (Heldin, dritte Person)
- Gedanken der Heldin: Ich-Form, KURSIV (*Gedanke*)
- Dialoge: schlagfertig, mit Subtext
- Deutsche Anführungszeichen: „..." und ‚...'
- KEIN Markdown außer *kursiv* für Gedanken
```

**Bei zu kurz (<80% Ziel):** Anreicherungs-Prompt an Claude

**Output:** Kapitel-Text als MD-Datei

---

## PHASE 4: POLISH

### Für jedes Kapitel:

**Schritt 1: Kritik erstellen**

**Modell:** Gemini 2.0 Flash  
**Max Tokens:** 4.000  

**Prompt:**
```
{SELF_CRITIQUE_PROMPT}

Prüfe diesen Romantext auf:
1. Wortwiederholungen
2. Satzfragmente oder abgehackte Absätze
3. Unnatürliche Dialoge
4. Tempo-Probleme
5. Fehlende Sinnesbeschreibungen
6. Out-of-Character Momente

TEXT:
{kapitel_text[:12000]}

KONKRETE Verbesserungen (Liste):
```

**Schritt 2: Überarbeiten**

**Modell:** Claude 3.5 Sonnet (via CLI)  

**Prompt:**
```
Du erhältst einen Roman-Text und Feedback dazu.

STIL-REGELN:
{STIL}

FEEDBACK:
{kritik}

ORIGINALTEXT:
{kapitel_text}

Überarbeite den Text basierend auf dem Feedback.
Behalte Länge und Struktur bei.
```

**Output:** Polierter Kapitel-Text

---

## PHASE 5: FLOW-CHECK

### Für jeden Kapitel-Übergang (1→2, 2→3, ...):

**Modell:** Gemini 2.0 Flash  
**Max Tokens:** 4.000  

**Input:**
- Qdrant-Kontext (Charaktere, Gliederung)
- Ende von Kapitel N (letztes Drittel)
- Anfang von Kapitel N+1 (erstes Drittel)

**Prompt:**
```
Prüfe den Übergang zwischen zwei Kapiteln:

═══════════════════════════════════════════════════════════════
KONTEXT AUS QDRANT (Charaktere, Gliederung)
═══════════════════════════════════════════════════════════════
{qdrant_kontext}

═══════════════════════════════════════════════════════════════
ENDE KAPITEL {i}:
═══════════════════════════════════════════════════════════════
{prev_end}

═══════════════════════════════════════════════════════════════
ANFANG KAPITEL {i+1}:
═══════════════════════════════════════════════════════════════
{curr_start}

Prüfe:
1. Wissensstand-Konsistenz (weiß eine Figur plötzlich etwas?)
2. Emotionale Kontinuität (passt die Stimmung?)
3. Zeitliche Logik (wie viel Zeit ist vergangen?)
4. Fakten-Konsistenz (Namen, Orte, Beschreibungen)
5. Charakter-Konsistenz (verhalten sich Figuren wie in Charakterbögen?)

Antworte:
- "OK" wenn alles passt
- Oder liste die KONKRETEN Probleme
```

**Bei Problemen:** Claude korrigiert das nachfolgende Kapitel

---

## PHASE 6: GESAMT-CHECK

**Modell:** Gemini 2.0 Flash  
**Max Tokens:** 8.000  

**Input:** Gesamter Roman (erste 50.000 Zeichen)

**Prompt:**
```
Prüfe diesen Roman auf:

1. PLOT-LÖCHER
   - Ungelöste Handlungsstränge
   - Widersprüche in der Timeline
   - Vergessene Charaktere

2. CHARAKTER-KONSISTENZ
   - Verhaltensbrüche
   - Motivationsprobleme
   - Unlogische Entwicklungen

3. ROMANCE-BEATS
   - Ist die 7-Phasen-Struktur eingehalten?
   - Gibt es genug Tension?
   - Ist das HEA verdient?

4. SUSPENSE-LINIE
   - Steigt die Spannung?
   - Gibt es Durchhänger?
   - Funktioniert der Climax?

5. PACING
   - Durchhänger?
   - Zu schnelle Stellen?

ROMAN (Auszug - ca. 50.000 Zeichen):
{full_novel[:50000]}

DETAILLIERTER BERICHT mit konkreten Fundstellen:
```

**Output:** Qualitäts-Report als MD-Datei

---

## PHASE 7: OUTPUT

### 7.1 Roman zusammenfügen

**Datei:** `{Titel}.md`  
**Inhalt:** Alle Kapitel mit Trennern

### 7.2 Telegram-Versand

1. Status-Nachricht (Wortzahl, Kapitelanzahl, Dauer)
2. Roman als MD-Datei

### 7.3 Hörbuch-Generierung

**Tool:** macOS `say` + ffmpeg  
**Stimme:** Anna (deutsch)  
**Prozess:**
```
Text → say → AIFF → ffmpeg → MP3
```

**Telegram-Versand:** MP3 als Audio-Nachricht

---

## QDRANT SCHEMA

**Collection:** `memory_novelpipeline`  
**Embedding-Modell:** OpenAI text-embedding-3-small  
**Dimensionen:** 1536  

**Gespeicherte Dokumente:**

| Type | Phase | Inhalt |
|------|-------|--------|
| `gliederung` | 1 | Grob-Gliederung mit Charakteren |
| `akt` | 2 | Akt-Gliederung (je Akt) |
| `kapitel_gliederung` | 2.5 | Szenen-Gliederung (je Kapitel) |
| `kapitel` | 3 | Fertiges Kapitel (je Kapitel) |

**Suche:** Semantisch, max 3 Ergebnisse pro Query

---

## TELEGRAM INTERACTIONS

| Phase | Nachricht | User-Aktion |
|-------|-----------|-------------|
| Start | "Pipeline bereit" | `/start <setting>` |
| 1 | `gliederung_v{n}.md` | JA/NEIN |
| 2 | `akt_{n}.md` (3x) | JA/NEIN |
| 2.5 | `kapitel_struktur.md` | JA/NEIN |
| 3 | Progress alle 5 Kapitel | - |
| Ende | Status + `{Titel}.md` + `{Titel}.mp3` | - |

---

## DATEI-STRUKTUR (Output)

```
output_YYYYMMDD_HHMMSS_Setting/
├── 01_gliederung.md
├── 01_gliederung_v01.md (Versionen)
├── 02_akt_1.md
├── 02_akt_2.md
├── 02_akt_3.md
├── 02.5_kapitel_01_gliederung.md
├── 02.5_kapitel_02_gliederung.md
├── ...
├── kapitel_01.md
├── kapitel_01_v01.md (Versionen)
├── kapitel_02.md
├── ...
├── 06_qualitaets_report.md
├── {Titel}.md (Gesamt-Roman)
├── audiobook.mp3
└── pipeline.log
```

---

## TOKEN-LIMITS

| Call | Max Tokens | Modell |
|------|------------|--------|
| Phase 1 Gliederung | 16.000 | Pro |
| Phase 1 Self-Critique | 16.000 | Flash |
| Phase 2 Akt | 12.000 | Pro |
| Phase 2 Self-Critique | 12.000 | Flash |
| Phase 2.5 Kapitel | 8.000 | Pro |
| Phase 2.5 Self-Critique | 8.000 | Flash |
| Phase 4 Polish-Kritik | 4.000 | Flash |
| Phase 5 Flow-Check | 4.000 | Flash |
| Phase 6 Gesamt-Check | 8.000 | Flash |

---

## FEHLERBEHANDLUNG

- **Gemini MAX_TOKENS:** Retry mit kürzerem Input
- **Gemini empty response:** 3 Retries, dann Skip
- **Claude zu kurz:** Anreicherungs-Prompt
- **Polish fehlgeschlagen:** Original behalten
- **TTS Fehler:** Skip, nur MD senden

