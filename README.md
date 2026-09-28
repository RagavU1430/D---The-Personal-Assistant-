# D - The Personal Assistant

**Personal AI Operating Assistant**

D - The Personal Assistant is a Windows-first assistant platform designed around strict separation between AI reasoning, agent orchestration, tools, security, memory, voice, UI, and integrations.

## Phase 0

Phase 0 provides a runnable FastAPI backend with configuration, structured logging, standardized errors, SQLite/SQLAlchemy persistence foundation, shared contracts, security interfaces, AI/agent/tool/memory/voice interfaces, a React + TypeScript + Vite + Tailwind dashboard, and an optional Tauri shell. Later-phase capabilities are intentionally not enabled.

## Prerequisites

- Python 3.12+
- Node.js 20+
- npm
- Rust and Tauri prerequisites are optional for the desktop shell

## Setup

```powershell
Copy-Item .env.example .env
python -m pip install -r apps/backend/requirements.txt
cd apps/backend
python -m uvicorn app.main:app --reload
```

Health: `http://127.0.0.1:8000/api/v1/health`

Start the frontend independently:

```powershell
cd apps/desktop
npm install
npm run dev
```

Optional Tauri shell: `npm run tauri dev` after installing Rust/Tauri prerequisites.

## Tests and quality

```powershell
cd apps/backend
python -m pytest
ruff check app tests
mypy app
```

## Structure

- `apps/backend`: FastAPI service and architecture layers
- `apps/desktop`: React/Vite UI and optional Tauri shell
- `packages`: shared TypeScript contracts and configuration
- `data`: documents, memory, and logs
- `docs`: product, architecture, security, development, and roadmap documentation

See `docs/ROADMAP.md` for planned phases. Only Phase 0 is active.
