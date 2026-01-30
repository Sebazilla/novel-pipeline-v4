# Novel Pipeline V4

AI-gestützte Roman-Generierung mit Gemini (Planung) + Claude Code (Schreiben)

## Workflow
1. **Phase 1-2.5**: Gemini plant (Self-Critique Loop) → Telegram Approval
2. **Phase 3-4**: Claude Code schreibt + poliert
3. **Phase 5-6**: Gemini reviewed → Claude fixt

## Setup
```bash
cp .env.example .env
# API Keys eintragen
python3 novel_pipeline.py "Dein Setting hier"
```

