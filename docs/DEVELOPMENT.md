Backend checks run from `apps/backend`:

```text
pytest -q
ruff check .
mypy app
```

When adding a tool, test registry behavior, schema rejection, permission decisions, timeouts, failures, audit events, and API integration. Keep tool registration centralized and do not place host-system logic in API routes.

To use a hosted model locally, put the credential only in `.env`, set `AI_PROVIDER`, and restart the backend. Supported configured providers are `gemini`, `openrouter`, and `nvidia_nim`; the NVIDIA NIM endpoint and model can be customized with `NVIDIA_NIM_BASE_URL` and `AI_MODEL`.

Phase 3 computer tests use `FakeComputerController`; they must not depend on the developer's active desktop. Production Windows actions are behind the same executor and permission checks, with explicit allowlists and emergency-stop coverage.
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
