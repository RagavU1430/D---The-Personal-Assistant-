# D - The Personal Assistant Backend

FastAPI runtime for D - The Personal Assistant, including secure system tools, Windows-first computer control, lifecycle health, and user-controlled startup settings.

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend starts without an AI provider or API keys. Phase 0 exposes only the health API; agent, AI, tools, security, memory, and voice packages provide typed extension interfaces for later phases.
