<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Inter&weight=700&size=38&duration=3000&pause=1000&color=0EA5E9&center=true&vCenter=true&width=700&lines=D+%E2%80%94+The+Personal+Assistant;Your+AI+Operating+Partner" alt="D — The Personal Assistant" />
</p>

<p align="center">
  <strong>A Windows-first personal AI assistant that understands you, plans with you, and acts on your behalf — safely.</strong>
</p>

<p align="center">
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-"><img src="https://img.shields.io/github/stars/RagavU1430/D---The-Personal-Assistant-?style=for-the-badge&logo=github&color=0EA5E9&labelColor=0F172A" alt="Stars" /></a>
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/issues"><img src="https://img.shields.io/github/issues/RagavU1430/D---The-Personal-Assistant-?style=for-the-badge&logo=github&color=F59E0B&labelColor=0F172A" alt="Issues" /></a>
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/blob/main/LICENSE"><img src="https://img.shields.io/github/license/RagavU1430/D---The-Personal-Assistant-?style=for-the-badge&color=10B981&labelColor=0F172A" alt="License" /></a>
  <img src="https://img.shields.io/badge/Platform-Windows_10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white&labelColor=0F172A" alt="Windows" />
  <img src="https://img.shields.io/badge/Built_with-FastAPI_%2B_React_%2B_Tauri-6366F1?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0F172A" alt="Stack" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Phase_3-Complete-10B981?style=flat-square&logo=vercel&logoColor=white&labelColor=0F172A" />
  <img src="https://img.shields.io/badge/Phase_4-Complete-10B981?style=flat-square&logo=gitbook&logoColor=white&labelColor=0F172A" />
  <img src="https://img.shields.io/badge/Phase_5-Complete-10B981?style=flat-square&logo=github&logoColor=white&labelColor=0F172A" />
  <img src="https://img.shields.io/badge/AI_Providers-Custom_Endpoints_Supported-0EA5E9?style=flat-square&logo=anthropic&logoColor=white&labelColor=0F172A" />
  <img src="https://img.shields.io/badge/Registered_Tools-40+-8B5CF6?style=flat-square&logo=wrench&logoColor=white&labelColor=0F172A" />
  <img src="https://img.shields.io/badge/Tests-Passing-10B981?style=flat-square&logo=pytest&logoColor=white&labelColor=0F172A" />
</p>

---

## The Vision

**D** is a personal AI operating assistant designed for the way you actually work. It runs locally on Windows, understands natural language, and executes real actions — opening applications, managing windows, reading system health, capturing screens, organizing files — all through a **permissioned, audited, and reversible** tool framework.

No cloud dependency. No hidden autonomy. No surprise executions.

> **Inspired by JARVIS.** Built for **trust**.

---

## What It Does Today

| Capability | Description |
|------------|-------------|
| **System Intelligence** | Real-time CPU, memory, disk, and health telemetry |
| **Application Control** | Launch allowlisted apps (VS Code, Explorer, browsers, terminals) |
| **Window Management** | Focus, minimize, maximize, close — with confirmation |
| **Input Automation** | Precision mouse, keyboard, hotkeys — coordinate and key validated |
| **Screen Awareness** | On-demand screenshots, active window detection, window enumeration |
| **File System Intelligence** | Search, read, write, copy, move, rename, compress, find duplicates/large files, organize — all path-restricted |
| **Safe File Handling** | Move to Recycle Bin (reversible, path-restricted, confirmed) |
| **Developer JARVIS** | Controlled Git operations, multi-framework test runner, log diagnostics, and allowlisted CLI tools — boundary restricted |
| **Voice Assist** | Client-side speech recognition & synthesis, holographic energy orb, real-time waveform visualizer |

---

## How It Works

**Natural Language → Structured Plan → Validated Tool → Permission Gate → Audited Execution**

```
You speak or type        Planner maps intent        Registry validates        Engine checks risk        Executor runs with
to D                     to a registered tool       schema & existence        (SAFE / CONFIRM /      timeout, logs audit,
                                                                       BLOCK)                 returns structured result
```

Every action passes through:
- **Schema validation** — Pydantic models reject malformed input
- **Permission engine** — SAFE runs automatically, CONFIRM pauses for you, BLOCK never runs
- **Timeout bounds** — No tool runs longer than configured
- **Audit trail** — Tool, path, risk, decision, duration, result — all logged, secrets redacted

---

## AI Providers (Pluggable, Failover-Ready)

| Provider | Status | Notes |
|----------|--------|-------|
| **Gemini** | ✅ Ready | Primary recommended |
| **OpenRouter** | ✅ Ready | Access to 100+ models |
| **NVIDIA NIM** | ✅ Ready | Local/cloud hybrid |
| **OpenAI** | ⚠️ Stubbed | Interface complete |
| **Anthropic** | ⚠️ Stubbed | Interface complete |
| **Custom OpenAI-Compatible** | ✅ Ready | **Ollama, LM Studio, vLLM, any OpenAI-compatible endpoint** |

**Smart failover:** If a provider times out or rate-limits, D automatically tries the next — with per-model cooldown to prevent hammering.

**Custom endpoints:** Configure `CUSTOM_AI_PROVIDERS` in `.env` (format: `name=base_url,api_key,model|...`). Supports local models with empty API key.

---

## Security by Design

| Principle | Implementation |
|-----------|----------------|
| **No model-to-OS path** | All actions through registered, schema-validated tools |
| **Allowlists only** | Applications, file roots, keys, coordinates — all configured, never inferred |
| **Explicit confirmation** | Destructive or external actions require your approval |
| **Emergency stop** | One API call disables all computer control instantly |
| **Full auditability** | Every attempt logged with context; secrets never recorded |
| **Reversible by default** | File deletion → Recycle Bin; no permanent destruction |

---

## Quick Start

```powershell
# 1. Clone
git clone https://github.com/RagavU1430/D---The-Personal-Assistant-.git
cd D---The-Personal-Assistant-

# 2. Configure (optional API keys)
Copy-Item .env.example .env
# Edit .env with your provider keys

# 3. Install
cd apps/backend && python -m pip install -r requirements.txt
cd ../desktop && npm install

# 4. Run
# Terminal 1: Backend API
cd apps/backend && python -m uvicorn app.main:app --reload
# → http://127.0.0.1:8001/api/v1/health

# Terminal 2: Frontend
cd apps/desktop && npm run dev
# → http://localhost:8000

# Optional: Native desktop app
cd apps/desktop && npm run tauri dev
```

**Requirements:** Python 3.12+, Node.js 20+, Windows 10/11

---

## Project Layout

```
D - The Personal Assistant/
├── apps/
│   ├── backend/          # FastAPI service (API, agent, AI, tools, security, DB)
│   └── desktop/          # React + Vite + Tailwind + Tauri desktop shell
├── packages/
│   ├── shared-types/     # TypeScript contracts
│   └── shared-config/    # Frontend defaults
├── data/                 # SQLite, logs, memory, documents
├── docs/                 # Architecture, PRD, Roadmap, Security, Tools
├── scripts/              # Operational utilities
└── .env.example          # Configuration template
```

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **0** | Foundation & Architecture | ✅ Complete |
| **1** | AI Reasoning & Orchestration | ✅ Complete |
| **2** | Safe Tool Framework | ✅ Complete |
| **3** | Windows Computer Control | ✅ Complete |
| **4** | File System Intelligence | ✅ Complete |
| **5** | Developer JARVIS (Controlled Terminal) | 📝 Design in Progress |
| **6** | Browser Automation | 📋 Planned |
| **7** | Persistent Memory | 📋 Planned |
| **8** | RAG / Knowledge Base | 📋 Planned |
| **9** | Voice Interaction | 📋 Planned (API scaffolding done) |
| **10** | Screen Vision | 📋 Planned |
| **11–25** | Autonomy, Workflows, Scheduler, Services, HUD, Remote | 📋 Planned |

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for milestones and [`design_draft.md`](design_draft.md) for Phase 5 design.

---

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — System design and data flows
- [`docs/PRD.md`](docs/PRD.md) — Product requirements
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — Phase-by-phase plan
- [`docs/SECURITY.md`](docs/SECURITY.md) — Security model and guarantees
- [`docs/TOOLS.md`](docs/TOOLS.md) — Tool reference and extension guide

---

## Testing & Quality

```powershell
cd apps/backend
python -m pytest -v          # Unit + integration tests
ruff check app tests         # Lint
mypy app                     # Type check
```

All checks pass in CI.

---

## License

MIT — see [`LICENSE`](LICENSE).

---

## Acknowledgments

FastAPI • React • Vite • Tailwind • Tauri • pyautogui • SQLAlchemy • Pydantic • httpx • psutil

---

<p align="center">
  <strong>Local. Private. Powerful. Under your control.</strong>
</p>

<p align="center">
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/stargazers">⭐ Star</a> •
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/issues">🐛 Report Issue</a> •
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/issues/new?template=feature_request.md">💡 Request Feature</a>
</p>