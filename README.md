# Novel Pipeline V4

AI-gestützte Roman-Generierung mit 7-Phasen Suspense-Backbone.

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: GROB-GLIEDERUNG                                   │
│  └─ Gemini (Self-Feedback Loop)                             │
│  └─ 📱 Telegram: Synopsis Approval                          │
├─────────────────────────────────────────────────────────────┤
│  PHASE 2: AKT-GLIEDERUNGEN                                  │
│  └─ Gemini (Self-Feedback)                                  │
├─────────────────────────────────────────────────────────────┤
│  PHASE 2.5: KAPITEL-GLIEDERUNGEN                            │
│  └─ Gemini (Szenen-Details)                                 │
│  └─ 📱 Telegram: Kapitel-Struktur Approval                  │
├─────────────────────────────────────────────────────────────┤
│  PHASE 3: SCHREIBEN                                         │
│  └─ Claude Code CLI (pro Kapitel)                           │
├─────────────────────────────────────────────────────────────┤
│  PHASE 4: KONSISTENZ-CHECK                                  │
│  └─ Gemini (prüft alles) → Claude (korrigiert)              │
└─────────────────────────────────────────────────────────────┘
```

## Setup

1. `.env` erstellen (siehe `.env.example`)
2. Dependencies installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. Claude Code CLI muss installiert sein

## Verwendung

```bash
python novel_pipeline.py "Archäologin entdeckt auf Kreta ein Geheimnis"
```

## 7-Phasen Struktur

| Phase | Anteil | Inhalt |
|-------|--------|--------|
| I | 0-15% | Immediate Tension + Flawed Victory |
| II | 15-35% | Forced Proximity + Escalation |
| III | 35-55% | Intimacy Under Fire |
| IV | 55-75% | Separation From Protection |
| V | 75-85% | All Is Lost (Forced) |
| VI | 85-95% | Active Finale |
| VII | 95-100% | New Equilibrium |

## Output

- `01_gliederung.md` - Grob-Gliederung
- `02_akt_*.md` - Akt-Gliederungen
- `02.5_kapitel_*_gliederung.md` - Kapitel-Gliederungen
- `kapitel_*.md` - Fertige Kapitel
- `ROMAN_KOMPLETT.md` - Zusammengefügter Roman
