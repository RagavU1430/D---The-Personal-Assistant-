# Architecture

D - The Personal Assistant is a monorepo with an independently runnable React/Vite frontend and a FastAPI backend. The backend is split into API, agent, AI, tools, security, memory, voice, and database packages.

## Frontend

The desktop UI is a dark, futuristic React app styled with Tailwind. It provides a health check and placeholder system status in Phase 0 without enabling real system metrics or autonomous actions.

## Backend

The FastAPI backend exposes an API versioned under `/api/v1` and supplies health checks, product metadata, logging, config, error handling, and a database foundation.

## AI layer

AI providers are abstracted through an `AIProvider` interface and a factory so the project can support OpenAI, Gemini, Anthropic, OpenRouter, and local models without hard-coding any provider dependency.

## Agent layer

The agent layer defines orchestrator, planner, executor, observer, and verifier interfaces only. No autonomous decision loops are implemented in Phase 0.

## Tools

Tools use a `BaseTool` abstraction plus a `ToolRegistry` for discovery and registration. This preserves separation between allowed actions and future OS/browser/terminal capabilities.

## Security

The security layer defines `SAFE`, `CONFIRM`, and `BLOCK` decisions through a permission engine and audit logger. This architecture prevents future tools from bypassing policy enforcement.

## Memory

The database foundation is initialized through SQLAlchemy with a repository pattern. SQLite is the default local database and is ready to evolve toward PostgreSQL without changing the service contracts.

## Future integrations

The foundation is intentionally narrow: voice, browser automation, shell execution, file operations, and direct OS access are reserved for later phases behind the existing interfaces and permission checks.
