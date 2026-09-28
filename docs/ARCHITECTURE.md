# Architecture

D - The Personal Assistant is a monorepo with an independently runnable React/Vite frontend and a FastAPI backend. The backend is split into API, agent, AI, tools, security, memory, voice, and database packages.

## Frontend

The desktop UI is a dark, futuristic React app styled with Tailwind. It provides health status, chat, and visible tool execution status without enabling autonomous actions.

## Backend

The FastAPI backend exposes an API versioned under `/api/v1` and supplies health checks, product metadata, logging, config, error handling, and a database foundation.

## AI layer

AI providers are abstracted through an `AIProvider` interface and a factory so the project can support OpenAI, Gemini, Anthropic, OpenRouter, and local models without hard-coding any provider dependency.

## Agent layer

The planner maps supported system requests to registered tools. Chat executes SAFE plans through `ToolExecutor`, passes structured `ToolResult` data back to the provider, and exposes confirmation or failure states when execution cannot proceed.

## Tools

Phase 2 implements a metadata-aware `BaseTool`, Pydantic schemas, centralized `ToolRegistry`, and timeout-bounded `ToolExecutor`. The executor is the only path from a plan to a tool and enforces validation, risk policy, confirmation, result normalization, and audit logging. The default registry contains read-only system information tools only.

Phase 3 adds a `ComputerController` abstraction with a fake implementation for tests and a Windows implementation for allowlisted applications, window management, input, and on-demand screenshots. Computer tools remain ordinary registered tools and cannot bypass the executor.

## Always-on runtime

`DApplicationLifecycle` tracks `STARTING`, `READY`, `DEGRADED`, `STOPPING`, `STOPPED`, and `ERROR` states. It initializes the registry and controller during FastAPI lifespan startup, resumes only configured capabilities, and emergency-stops computer control during shutdown. User-controlled startup uses the standard per-user Windows Startup folder and can be disabled through the API or desktop UI.

## Security

The security layer defines `SAFE`, `CONFIRM`, and `BLOCK` decisions through a permission engine and audit logger. This architecture prevents future tools from bypassing policy enforcement.

## Memory

The database foundation is initialized through SQLAlchemy with a repository pattern. SQLite is the default local database and is ready to evolve toward PostgreSQL without changing the service contracts.

## Future integrations

The foundation is intentionally narrow: voice, browser automation, shell execution, file operations, and direct OS access are reserved for later phases behind the existing interfaces and permission checks.
