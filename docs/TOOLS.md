# D - The Personal Assistant Tools

Tools are the only approved capability boundary between the agent and the host system. The model can request a registered tool, but it cannot execute shell, Python, or operating-system commands directly.

## Execution flow

`Planner -> ToolRegistry -> Pydantic input schema -> PermissionEngine -> ToolExecutor -> Tool -> ToolResult -> AI`

`ToolExecutor` is the only approved execution path. It performs lookup, enabled checks, argument validation, risk evaluation, bounded execution, result normalization, and audit logging. Tool failures are returned as structured results instead of crashing the agent.

## BaseTool contract

Implement `BaseTool` with `name`, `description`, `category`, `version`, `risk_level`, `enabled`, a Pydantic `input_schema`, and an async `execute` method returning `ToolResult`. Results contain `success`, `tool`, `data`, `error_code`, `message`, and `execution_time_ms`.

## Registry and APIs

The centralized registry is built in `app/dependencies.py`. Enabled metadata is available at `GET /api/v1/tools`. Execution is available at `POST /api/v1/tools/execute` with `{ "tool": "name", "arguments": {} }`.

### Phase 2: Read-Only System Tools
* `system_status` (SAFE): OS, CPU, RAM, Disk utilization, and Python/app versions.
* `cpu_usage` (SAFE): Current CPU percentage.
* `memory_usage` (SAFE): RAM totals, available, used, and percentage.
* `disk_usage` (SAFE): Disk statistics for the approved root.
* `current_time` (SAFE): Local system timestamp and timezone.
* `jarvis_health` (SAFE): Health status of database, AI provider, and tool system.

### Phase 3: Windows Computer Control Tools
* `open_application` (SAFE): Launches allowlisted applications only (`notepad`, `calc`, `explorer`, `code`, `chrome`, `edge`).
* `close_application` (CONFIRM): Gracefully closes windows via Win32 `PostMessageW(WM_CLOSE)`.
* `focus_window`, `minimize_window`, `maximize_window` (SAFE): Window focus and state adjustments.
* `move_mouse`, `click`, `double_click` (SAFE): Validated coordinate cursor movements and clicks.
* `type_text` (CONFIRM): Types user-provided text into the active window.
* `press_key`, `hotkey` (SAFE): Dispatches single keys or hotkeys against an approved key allowlist.
* `take_screenshot` (SAFE): Captures an on-demand temporary screenshot without continuous recording.
* `get_active_window`, `list_windows` (SAFE): Queries foreground window title and visible window list.

### Phase 4: File System Intelligence Tools
All file tools operate strictly under `APPROVED_FILE_ROOTS`. Mutating tools are additionally blocked from modifying any path under `PROTECTED_FILE_ROOTS`.

| Tool Name | Risk Level | Description |
|-----------|------------|-------------|
| `search_files` | SAFE | Searches for files by glob or regex within approved directories. |
| `read_file` | SAFE | Reads text file contents up to `max_bytes` with metadata and encoding check. |
| `write_file` | CONFIRM | Writes or creates file contents. Overwrite requires explicit confirmation. |
| `copy_file` | CONFIRM | Copies files or folders within approved roots. |
| `move_file` | CONFIRM | Moves files or folders within approved roots. |
| `rename_file` | CONFIRM | Renames a file or folder safely within its parent directory. |
| `compress_directory` | CONFIRM | Compresses a directory into `.zip` or `.tar.gz` format. |
| `list_large_files` | SAFE | Lists files exceeding a configurable size threshold. |
| `find_duplicates` | SAFE | Groups duplicate files based on file size and SHA-256 content hashes. |
| `organize_directory` | CONFIRM | Plans or executes directory organization by extension, date, or size. |
| `move_to_recycle_bin` | CONFIRM | Reversibly moves an approved item to the Windows Recycle Bin using `SHFileOperationW`. |

## Risk and Safety Governance

* `SAFE` tools execute automatically.
* `CONFIRM` tools return `CONFIRMATION_REQUIRED` and pause until confirmed by user.
* `BLOCK` tools return `BLOCKED`.
* Unknown tools return `TOOL_NOT_FOUND`.
* Malformed arguments return `VALIDATION_ERROR`.
* Execution is bounded by `tool_timeout_seconds`.
* Permanent deletion is not implemented.
