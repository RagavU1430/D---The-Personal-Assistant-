# Development

## Backend

```powershell
cd apps/backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Frontend

```powershell
cd apps/desktop
npm install
npm run dev
```

Run backend checks with `python -m pytest`, `ruff check app tests`, and `mypy app`. Add new tools through `BaseTool` and `ToolRegistry`; add providers through `AIProvider` and `AIProviderFactory`. Keep Phase 0 scope limited to interfaces and the health API.
