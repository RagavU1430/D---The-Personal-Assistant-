<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=600&size=32&duration=3000&pause=1000&color=00D4FF&center=true&vCenter=true&width=600&lines=D+-+The+Personal+Assistant;Windows-First+AI+Operating+Assistant;Phase+3+Complete+%7C+Phase+4+Next" alt="D - The Personal Assistant" />
</p>

<p align="center">
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-"><img src="https://img.shields.io/github/stars/RagavU1430/D---The-Personal-Assistant-?style=for-the-badge&logo=github&color=00D4FF" alt="Stars" /></a>
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/issues"><img src="https://img.shields.io/github/issues/RagavU1430/D---The-Personal-Assistant-?style=for-the-badge&logo=github&color=FFA500" alt="Issues" /></a>
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/blob/main/LICENSE"><img src="https://img.shields.io/github/license/RagavU1430/D---The-Personal-Assistant-?style=for-the-badge&color=00FF88" alt="License" /></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://react.dev"><img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" /></a>
  <a href="https://tauri.app"><img src="https://img.shields.io/badge/Tauri-2.0-24C8DB?style=for-the-badge&logo=tauri&logoColor=white" alt="Tauri" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Phase-3_Complete-00FF88?style=flat-square&logo=checkmarx&logoColor=black" />
  <img src="https://img.shields.io/badge/Next-Phase_4_Files-FFA500?style=flat-square&logo=gitbook&logoColor=black" />
  <img src="https://img.shields.io/badge/AI_Providers-5_Configured-00D4FF?style=flat-square&logo=anthropic&logoColor=white" />
  <img src="https://img.shields.io/badge/Tools-19_Registered-8B5CF6?style=flat-square&logo=wrench&logoColor=white" />
  <img src="https://img.shields.io/badge/Tests-Passing-00FF88?style=flat-square&logo=pytest&logoColor=black" />
</p>

---

## 🎯 What is D?

**D - The Personal Assistant** is a **Windows-first personal AI operating assistant** that runs locally on your machine. It understands natural language, plans multi-step tasks, and executes **controlled, audited tools** — system monitoring, application control, window management, mouse/keyboard input, screenshots, and file operations — all behind a **permission engine** that requires your confirmation for consequential actions.

> **Inspired by JARVIS.** Built with **permissioned autonomy.** No unrestricted shell. No hidden persistence. No surprises.

---

## ✨ Current Capabilities (Phase 3)

| Category | Tools | Risk | Description |
|----------|-------|------|-------------|
| **System** | `system_status`, `cpu_usage`, `memory_usage`, `disk_usage`, `current_time`, `jarvis_health` | 🟢 SAFE | Read-only system telemetry |
| **Applications** | `open_application` (allowlisted) | 🟢 SAFE | Launch Notepad, Calculator, VS Code, Explorer, Chrome, Edge |
| **Windows** | `focus_window`, `minimize_window`, `maximize_window`, `close_application` | 🟡 CONFIRM | Window state management |
| **Input** | `move_mouse`, `click`, `double_click`, `type_text`, `press_key`, `hotkey` | 🟡 CONFIRM | Mouse/keyboard control with coordinate/key validation |
| **Vision** | `take_screenshot`, `get_active_window`, `list_windows` | 🟢 SAFE / 🟡 CONFIRM | On-demand screen capture + window enumeration |
| **Files** | `move_to_recycle_bin` | 🟡 CONFIRM | Reversible deletion to Windows Recycle Bin (path-restricted) |

**AI Providers:** Mock (local), Gemini, OpenRouter, NVIDIA NIM, OpenAI*, Anthropic*, Local*  
*stubbed for future use

**Architecture:** Provider failover with per-model cooldown, structured planning, timeout-bounded execution, full audit logging.

---

## 🏗 Architecture

```mermaid
graph TB
    subgraph "Frontend (React + Vite + Tailwind)"
        UI[Chat UI] -->|HTTP| API
        Status[System Status Panel] -->|HTTP| API
        Launcher[Floating Launcher] -->|Hotkey| UI
    end

    subgraph "Backend (FastAPI)"
        API[/api/v1] --> Chat[Chat Endpoint]
        API --> Tools[Tools Endpoint]
        API --> Computer[Computer Endpoint]
        API --> Health[Health Endpoint]
        
        Chat --> Planner[Planner]
        Planner --> Registry[ToolRegistry]
        Registry --> Executor[ToolExecutor]
        Executor --> Perm[PermissionEngine]
        Perm --> Audit[AuditLogger]
        Executor --> ToolsImpl[Tool Implementations]
    end

    subgraph "Tool Layer"
        ToolsImpl --> SysTools[System Tools]
        ToolsImpl --> CompTools[Computer Tools]
        ToolsImpl --> FileTools[File Tools]
    end

    subgraph "Computer Control"
        CompTools --> Controller[ComputerController]
        Controller --> Fake[FakeComputerController]
        Controller --> Win[WindowsComputerController]
        Win --> PyAutoGUI[pyautogui]
        Win --> Win32[user32.dll]
    end

    subgraph "AI Layer"
        Chat --> Provider[AIProviderRouter]
        Provider --> Gemini[GeminiProvider]
        Provider --> OpenRouter[OpenRouterProvider]
        Provider --> NVIDIA[NvidiaNimProvider]
        Provider --> Mock[MockAIProvider]
    end

    subgraph "Persistence"
        API --> DB[(SQLite)]
    end
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** & **npm**
- **Windows 10/11** (for computer control)
- Optional: **Rust** + **Tauri CLI** for desktop shell

### Installation

```powershell
# 1. Clone
git clone https://github.com/RagavU1430/D---The-Personal-Assistant-.git
cd D---The-Personal-Assistant-

# 2. Environment
Copy-Item .env.example .env
# Edit .env with your API keys (optional)

# 3. Backend
cd apps/backend
python -m pip install -r requirements.txt

# 4. Frontend
cd ../desktop
npm install
```

### Running

| Mode | Command | URL |
|------|---------|-----|
| **Backend API** | `cd apps/backend && python -m uvicorn app.main:app --reload` | http://127.0.0.1:8001/api/v1/health |
| **Frontend (Vite)** | `cd apps/desktop && npm run dev` | http://localhost:8000 |
| **Desktop (Tauri)** | `cd apps/desktop && npm run tauri dev` | Native window |

---

## ⚙️ Configuration

Create `.env` from `.env.example`:

```ini
# Server
PORT=8001
APP_ENV=development

# AI Providers (pick one)
AI_PROVIDER=gemini          # gemini | openrouter | nvidia_nim
GEMINI_API_KEY=your_key
OPENROUTER_API_KEY=your_key
NVIDIA_NIM_API_KEY=your_key

# Multi-model failover (comma-separated)
AI_MODELS=gemini-3.8-flash,gemini-3.8-pro

# Features (Phase 3)
ENABLE_COMPUTER_CONTROL=true
ENABLE_SYSTEM_TOOLS=true
ENABLE_FILE_TOOLS=false     # Phase 4

# File tools (Phase 4)
APPROVED_FILE_ROOTS=C:/Users/YourName/Projects,C:/Users/YourName/Documents
PROTECTED_FILE_ROOTS=C:/Users/YourName/Projects/.git

# Security
AUTONOMY_LEVEL=1            # 0=read-only, 1=confirm, 2=auto-safe, 3=auto-confirm, 4=full
TOOL_TIMEOUT_SECONDS=10
PROVIDER_COOLDOWN_SECONDS=30

# Startup
START_WITH_WINDOWS=true
BACKGROUND_MODE=true
```

**Application Allowlist** (configured in `.env`):
```
APPLICATION_ALLOWLIST=notepad=notepad.exe,calculator=calc.exe,file_explorer=explorer.exe,vscode=code.exe,chrome=chrome.exe,edge=msedge.exe
```

---

## 💬 Example Interactions

```bash
# System status
> "What's my CPU and RAM usage?"
→ system_status tool executes, returns telemetry

# Application control
> "Open VS Code"
→ open_application tool launches VS Code

> "Take a screenshot"
→ take_screenshot captures desktop to temp file

> "Close the Notepad window"
→ close_application (requires confirmation)

# Window management
> "Minimize the browser window"
→ minimize_window

> "What window is active?"
→ get_active_window

# File operations (Phase 4 - requires ENABLE_FILE_TOOLS=true)
> "Find all Python files in my project"
→ search_files with pattern **/*.py

> "Read config.py"
→ read_file

> "Organize my Downloads folder by extension"
→ organize_directory (dry-run first, then confirm)
```

---

## 📁 Project Structure

```
D - The Personal Assistant/
├── apps/
│   ├── backend/                 # FastAPI service
│   │   ├── app/
│   │   │   ├── api/             # REST endpoints (chat, tools, computer, health)
│   │   │   ├── agent/           # Planner, intents, state machine, context
│   │   │   ├── ai/              # Provider abstraction, router, failover
│   │   │   ├── tools/           # BaseTool, registry, executor, system/computer/file tools
│   │   │   ├── computer/        # ComputerController (ABC + Windows impl)
│   │   │   ├── security/        # RiskLevel, PermissionEngine, AuditLogger
│   │   │   ├── db/              # SQLAlchemy models, repositories
│   │   │   ├── memory/          # MemoryRepository (interface)
│   │   │   ├── voice/           # STT/TTS (interface)
│   │   │   ├── config.py        # Pydantic Settings
│   │   │   ├── dependencies.py  # DI container (registry, providers, lifecycle)
│   │   │   ├── lifecycle.py     # DApplicationLifecycle (STARTING→READY→STOPPED)
│   │   │   └── main.py          # FastAPI app + lifespan
│   │   ├── tests/               # pytest suite (unit + integration)
│   │   ├── requirements.txt
│   │   └── pyproject.toml
│   │
│   └── desktop/                 # React + Vite + Tailwind + Tauri
│       ├── src/
│       │   ├── components/      # ChatPanel, CommandInput, SystemStatus, Header
│       │   ├── lib/api.ts       # Typed API client
│       │   └── types/api.ts     # Shared TS interfaces
│       ├── src-tauri/           # Tauri/Rust desktop shell
│       └── package.json
│
├── packages/
│   ├── shared-types/            # TypeScript contracts (HealthResponse, ChatRequest, etc.)
│   └── shared-config/           # Frontend config defaults
│
├── data/                        # SQLite DB, logs, memory, documents
├── docs/                        # ARCHITECTURE.md, PRD.md, ROADMAP.md, SECURITY.md, TOOLS.md
├── scripts/                     # Operational utilities (run-backend.ps1)
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 🧪 Testing

```powershell
cd apps/backend

# Unit + integration tests
python -m pytest -v

# Lint
ruff check app tests

# Type check
mypy app
```

**Test Coverage:**
- Tool registry, executor, permission engine
- Provider router failover & cooldown
- Computer controller (fake + Windows)
- Chat endpoint planner routing
- Phase 3 computer tools + file tools (recycle bin)

---

## 🗺 Roadmap

| Phase | Status | Focus |
|-------|--------|-------|
| **0** Foundation | ✅ Complete | Monorepo, FastAPI, React, Tauri, config, DB, health |
| **1** JARVIS Brain | ✅ Complete | AIProvider, planner, orchestrator, context, structured output |
| **2** Safe Tools | ✅ Complete | BaseTool, registry, executor, system tools, permission engine |
| **3** Computer Control | ✅ Complete | WindowsController, 13 tools, allowlist, emergency stop, lifecycle |
| **4** File System Intelligence | 🔄 **Next** | Search, read, write, copy, move, rename, compress, duplicates, organize |
| **5** Developer JARVIS | 📋 Planned | Controlled PowerShell, Git, test execution, log analysis |
| **6** Browser JARVIS | 📋 Planned | Playwright, navigation, search, page reading, downloads |
| **7** Memory | 📋 Planned | Conversation, semantic, episodic memory, retrieval |
| **8** RAG | 📋 Planned | Document ingestion, embeddings, vector store, citations |
| **9** Voice | 📋 Planned | STT, TTS, wake word, streaming, interruption |
| **10** Vision | 📋 Planned | Screenshot analysis, OCR, UI understanding, visual reasoning |
| **11–25** Advanced | 📋 Planned | Autonomous agent, workflows, scheduler, services, HUD, remote |

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for detailed milestones.

---

## 🔐 Security Model

| Level | Meaning | Examples |
|-------|---------|----------|
| **SAFE** | Auto-execute | Read system status, search files, screenshot |
| **CONFIRM** | Requires approval | Write file, close window, type text, move file |
| **BLOCK** | Prohibited | Permanent delete, shell exec, credential access |

- **No direct model → OS path**: All actions go through registered, schema-validated tools
- **Allowlists only**: Applications, file roots, keys, coordinates
- **Emergency stop**: `/api/v1/computer/stop` disables computer control instantly
- **Audit logging**: Every attempt logged with tool, path, risk, decision, duration, result
- **Secret redaction**: API keys, tokens, passwords never logged

See [`docs/SECURITY.md`](docs/SECURITY.md) and [`docs/TOOLS.md`](docs/TOOLS.md).

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Run checks: `pytest && ruff check . && mypy app`
4. Commit with conventional messages (`feat:`, `fix:`, `docs:`, `refactor:`)
5. Push and open a PR

---

## 📄 License

MIT License — see [`LICENSE`](LICENSE) for details.

---

## 🙏 Acknowledgments

- **FastAPI** — Modern, fast web framework
- **React + Vite + Tailwind** — Frontend stack
- **Tauri** — Lightweight desktop shell
- **pyautogui** — Cross-platform GUI automation
- **SQLAlchemy** — Database toolkit
- **Pydantic** — Data validation

---

<p align="center">
  <strong>Built with precision. Designed for control.</strong>
</p>

<p align="center">
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/stargazers">⭐ Star this repo</a> •
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/issues">🐛 Report Bug</a> •
  <a href="https://github.com/RagavU1430/D---The-Personal-Assistant-/issues/new?template=feature_request.md">💡 Request Feature</a>
</p>