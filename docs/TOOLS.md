# JARVIS-X Tools

Tools are the only approved capability boundary between the agent and the host system. The model can request a registered tool, but it cannot execute shell, Python, or operating-system commands directly.

## Execution flow

`Planner -> ToolRegistry -> Pydantic input schema -> PermissionEngine -> ToolExecutor -> Tool -> ToolResult -> AI`

`ToolExecutor` is the only approved execution path. It performs lookup, enabled checks, argument validation, risk evaluation, bounded execution, result normalization, and audit logging. Tool failures are returned as structured results instead of crashing the agent.

## BaseTool contract

Implement `BaseTool` with `name`, `description`, `category`, `version`, `risk_level`, `enabled`, a Pydantic `input_schema`, and an async `execute` method returning `ToolResult`. Results contain `success`, `tool`, `data`, `error_code`, `message`, and `execution_time_ms`.

## Registry and APIs

The centralized registry is built in `app/dependencies.py`. Enabled metadata is available at `GET /api/v1/tools`. Execution is available at `POST /api/v1/tools/execute` with `{ "tool": "name", "arguments": {} }`.

Phase 2 registers only read-only system tools: `system_status`, `cpu_usage`, `memory_usage`, `disk_usage`, `current_time`, and `jarvis_health`. Phase 3 adds Windows-first computer tools through `ComputerController`: application allowlisting, window state, mouse, keyboard, and on-demand screenshots.

## Risk and adding tools

`SAFE` tools may execute automatically. `CONFIRM` tools return `CONFIRMATION_REQUIRED` without executing. `BLOCK` tools return `BLOCKED`. Unknown tools return `TOOL_NOT_FOUND`; malformed arguments return `VALIDATION_ERROR`; execution is bounded by `tool_timeout_seconds`.

To add a tool, create its Pydantic input model, implement narrow metadata and a per-tool risk level, register it centrally, add permission/failure/timeout/audit tests, and document it. Computer tools must call `ComputerController`; they must never accept arbitrary executable paths or raw commands. Never use `eval`, `exec`, `os.system`, shell interpolation, or `subprocess(..., shell=True)` for model output.
