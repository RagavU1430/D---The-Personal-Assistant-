# D - The Personal Assistant

## What is D - The Personal Assistant?

D - The Personal Assistant is a Windows-first personal AI operating assistant platform. Phase 0 creates the architectural foundation for future AI reasoning, agent orchestration, tool execution, memory, voice, desktop control, and safe operating-system integration without enabling unrestricted autonomy.

## Architecture

- Frontend: React + TypeScript + Vite + Tailwind UI
- Backend: FastAPI service with configuration, logging, health APIs, database foundation, security interfaces, and future-ready layers
- Shared contracts: TypeScript interfaces for health, chat, tools, permissions, and execution state
- Desktop shell: optional Tauri-based wrapper for the frontend
- Data: SQLite foundation for local persistence plus document, memory, and log directories

## Prerequisites

- Python 3.12+
- Node.js 20+
- npm
- Rust and Tauri tooling only for the desktop shell

## Installation

```powershell
Copy-Item .env.example .env
python -m pip install -r apps/backend/requirements.txt
cd apps/desktop
npm install
```

## Environment setup

Create a local `.env` file from `.env.example`. Provider keys are optional; select one with `AI_PROVIDER=gemini`, `AI_PROVIDER=openrouter`, or `AI_PROVIDER=nvidia_nim`. Configure the matching `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, or `NVIDIA_NIM_API_KEY`. With no provider selected, D uses the local mock provider.

## Backend startup

```powershell
cd apps/backend
python -m uvicorn app.main:app --reload
```

Health check: http://127.0.0.1:8000/api/v1/health

## Frontend startup

```powershell
cd apps/desktop
npm run dev
```

## Desktop startup

```powershell
cd apps/desktop
npm run tauri dev
```

This remains optional and is only used when Tauri tooling is available.

## Testing

```powershell
cd apps/backend
python -m pytest
ruff check app tests
mypy app
```

## Project structure

- `apps/backend`: FastAPI service and architecture layers
- `apps/desktop`: React + Vite desktop app shell
- `packages/shared-types`: shared TypeScript contracts
- `packages/shared-config`: shared frontend configuration defaults
- `data`: logs, memory, and documents
- `docs`: product and engineering documentation
- `scripts`: operational utilities

## Current phase

Phase 3 is implemented: registered read-only system and controlled Windows computer tools run through Pydantic validation, the permission engine, the timeout-bounded executor, and audit logging. Tool discovery is available at `/api/v1/tools`, execution at `/api/v1/tools/execute`, and safe computer requests can flow through chat. Arbitrary shell, browser, and file-mutation tools remain disabled.

## Roadmap

See `docs/ROADMAP.md` for the full plan. Phase 3 computer control remains planned.
