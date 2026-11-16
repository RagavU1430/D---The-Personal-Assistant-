# Design Document: Phase 5 — Developer JARVIS (Controlled Terminal & Developer Workflows)

**Feature:** Phase 5 — Developer JARVIS (Controlled Terminal / Shell Tools)  
**Author:** RagavU1430  
**Date:** 2025-11-16  
**Status:** Draft  
**Context:** Follows Phase 4 (File System Intelligence) per PRD roadmap. Enables safe terminal operations for developer workflows.

---

## The Problem

Developers need the assistant to run controlled terminal commands to diagnose issues, run tests, manage Git, and execute build tasks — all within approved working directories. Currently, no terminal capability exists. The PRD lists "Controlled PowerShell", "Command allowlist", "Working-directory restrictions", and "Git status/diff/log/branch/commit" as Phase 5 requirements.

**User pain points:**
- Cannot ask "run my tests and tell me what failed" (PRD user story: "check why my backend is not starting")
- Cannot inspect build logs or run linters through the assistant
- Git operations (status, diff, commit, push) require manual terminal use
- Debugging assistance requires copying/pasting between terminal and chat

---

## Overview

Extend the existing tool system with a **terminal toolset** that operates exclusively within `APPROVED_WORKING_ROOTS` and only allows commands from a configured `COMMAND_ALLOWLIST`. All tools follow the SAFE/CONFIRM/BLOCK risk model, inherit `BaseTool`, and are registered centrally in `dependencies.py`, gated by `enable_terminal_tools` config.

**Scope:** Controlled terminal execution (CONFIRM), command allowlist enforcement, working directory restrictions, Git sub-tools, test/log analysis helpers. No arbitrary shell execution. No sudo/admin commands. No background processes.

---

## Goals

| Goal | Success Criteria |
|------|------------------|
| Execute allowed commands in approved working directories | `execute_command` runs allowlisted commands, returns stdout/stderr/exit_code |
| Git workflow support | `git_status`, `git_diff`, `git_log`, `git_branch`, `git_commit`, `git_push` tools work |
| Test execution | `run_tests` discovers and runs pytest/npm test/cargo test in project root |
| Log analysis | `analyze_logs` extracts errors/warnings from build/test output |
| Working directory restrictions | All operations confined to `APPROVED_WORKING_ROOTS` |
| Command allowlist enforcement | Only commands in `COMMAND_ALLOWLIST` execute; others return `COMMAND_NOT_ALLOWED` |
| Audit logging | Every attempt/result logged with command, args, working_dir, risk, decision, duration |

---

## Non-Goals

- Arbitrary shell command execution (user-provided commands outside allowlist)
- Background/daemon processes
- Sudo/administrative commands
- Interactive terminal sessions (TTY, REPL)
- Network commands (ssh, curl, wget) unless explicitly allowlisted
- File operations outside approved roots (handled by Phase 4 file tools)
- Direct process spawning without allowlist validation

---

## Open Questions

1. **Allowlist format** — JSON array in config? Comma-separated string? Separate file?
2. **Working directory resolution** — Single root or multiple? Relative to project root?
3. **Git push confirmation** — Always CONFIRM, or configurable?
4. **Test framework detection** — Auto-detect (pytest, jest, cargo) or explicit tool per framework?
5. **Output size limits** — Truncate stdout/stderr at configurable bytes?
6. **Timeout handling** — Per-command timeout from config, or tool-specific?
7. **Environment variables** — Allowlist for env vars? Inherit from parent process?
8. **Command chaining** — Support `&&`, `||`, pipes in allowlisted commands?

---

## Technical Plan (Architecture)

### Architecture

```
User Request → Planner → ToolRegistry → Pydantic Validation
    → PermissionEngine (CONFIRM for terminal) → ToolExecutor (timeout, audit)
    → TerminalService.execute() → ToolResult → AI Response
```

All terminal tools inherit `BaseTool`, use Pydantic input schemas, and call a shared `TerminalService` for allowlist validation, working directory checks, and process execution.

### New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `TerminalService` | `app/tools/terminal.py` | Allowlist validation, working directory resolution, safe process execution (async subprocess), output capture/truncation, exit code handling |
| Terminal tools | `app/tools/terminal.py` | `ExecuteCommandTool`, `GitStatusTool`, `GitDiffTool`, `GitLogTool`, `GitBranchTool`, `GitCommitTool`, `GitPushTool`, `RunTestsTool`, `AnalyzeLogsTool` |
| Schemas | `app/tools/terminal.py` | Pydantic models for each tool's input |
| Config additions | `app/config.py` | `enable_terminal_tools`, `approved_working_roots`, `command_allowlist`, `terminal_timeout_seconds`, `max_output_bytes` |
| Registration | `app/dependencies.py` | `register_terminal_tools(registry, settings)` called in `get_tool_registry()` |
| Tests | `apps/backend/tests/test_phase5_terminal.py` | Unit + integration tests for each tool, allowlist, working dir, validation, audit |

### Data Flow

1. **Working directory validation** — every tool input `working_dir` passes through `TerminalService.resolve_working_dir(path)` which:
   - Expands `~`, resolves relative to CWD
   - Verifies path is under at least one `APPROVED_WORKING_ROOTS`
   - Returns `Path` or raises `WorkingDirNotAllowedError`

2. **Command allowlist validation** — `TerminalService.validate_command(cmd, args)` checks:
   - Base command (e.g., `git`, `pytest`, `npm`, `python`) is in `COMMAND_ALLOWLIST`
   - For `git`, subcommand must be in `GIT_ALLOWED_SUBCOMMANDS` (status, diff, log, branch, commit, push)
   - Arguments are validated against allowlist patterns (no `;`, `&`, `|`, `$()`, backticks unless explicitly allowed)
   - Returns validated command list or raises `CommandNotAllowedError`

3. **Risk classification**
   - CONFIRM: `execute_command`, `git_commit`, `git_push`, `run_tests` (can modify state)
   - SAFE: `git_status`, `git_diff`, `git_log`, `git_branch`, `analyze_logs` (read-only)

4. **Execution** — `TerminalService.run_command(cmd, args, working_dir, timeout, max_output)`:
   - Uses `asyncio.create_subprocess_exec` (no shell=True)
   - Captures stdout/stderr with size limit (`max_output_bytes`)
   - Enforces timeout (`terminal_timeout_seconds` config)
   - Returns `{stdout, stderr, exit_code, truncated, duration_ms}`

5. **Audit logging** — `ToolExecutor` logs `{tool, command, args, working_dir, risk, decision, duration_ms, success, exit_code, error_code}`

### Configuration

```python
# app/config.py additions
enable_terminal_tools: bool = False
approved_working_roots: str = ""           # comma-separated, e.g. "C:/Projects,C:/Users/Name/Code"
command_allowlist: str = "git,pytest,python,node,npm,cargo,go,dotnet,make,cmake,ruff,mypy,black"
git_allowed_subcommands: str = "status,diff,log,branch,commit,push"
terminal_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
max_output_bytes: int = Field(default=1_000_000, ge=1024, le=50_000_000)
```

### API Exposure

- `GET /api/v1/tools` — includes terminal tools when enabled
- `POST /api/v1/tools/execute` — executes any terminal tool
- `POST /api/v1/chat` — planner routes developer intents to terminal tools

### Git Sub-tool Design

Each Git operation is a separate tool for explicit risk classification and audit granularity:

| Tool | Risk | Input Schema | Output |
|------|------|--------------|--------|
| `git_status` | SAFE | `working_dir` | `{clean: bool, staged: [], unstaged: [], untracked: []}` |
| `git_diff` | SAFE | `working_dir`, `staged: bool` | `{diff: str, truncated: bool}` |
| `git_log` | SAFE | `working_dir`, `max_entries: int` | `{commits: [{hash, author, date, message}], count: int}` |
| `git_branch` | SAFE | `working_dir` | `{current: str, branches: [str]}` |
| `git_commit` | CONFIRM | `working_dir`, `message: str`, `add_all: bool` | `{hash: str, message: str}` |
| `git_push` | CONFIRM | `working_dir`, `remote: str`, `branch: str`, `force: bool` | `{pushed: bool, remote: str}` |

### Test Tool Design

| Tool | Risk | Input Schema | Output |
|------|------|--------------|--------|
| `run_tests` | CONFIRM | `working_dir`, `framework: "pytest|jest|cargo|auto"`, `args: list[str]` | `{passed: int, failed: int, skipped: int, output: str, truncated: bool, duration_ms: int}` |

Auto-detection checks for `pyproject.toml`/`pytest.ini` (pytest), `package.json` (jest/npm), `Cargo.toml` (cargo), `go.mod` (go test).

### Log Analysis Tool Design

| Tool | Risk | Input Schema | Output |
|------|------|--------------|--------|
| `analyze_logs` | SAFE | `content: str`, `max_findings: int` | `{errors: [{line, context}], warnings: [{line, context}], summary: str}` |

Extracts lines matching error/warning patterns (traceback, ERROR, FAILED, warning, WARN) with surrounding context.

---

## Alternatives Considered

| Alternative | Rejection Reason |
|-------------|------------------|
| Single `terminal_command` tool with free-form command string | Violates allowlist principle; makes schema validation, risk classification, and audit opaque. Rejected by author: explicit tools map cleanly to risk levels and planner keywords. |
| Allow arbitrary commands with user confirmation | Confirmation can be phished/social-engineered; allowlist is the hard capability boundary. Rejected by author: command allowlist is the security boundary. |
| Use `shell=True` with command string | Shell injection risk; argument parsing ambiguity. Rejected by author: `asyncio.create_subprocess_exec` with list args is safer and auditable. |
| Single `git` tool with `operation` enum | Violates single-responsibility; makes risk classification (commit/push vs status/diff) and audit opaque. Rejected by author: separate tools enable SAFE vs CONFIRM distinction. |
| Implement permanent `git_push --force` without extra confirmation | Destructive; force push can rewrite history. Rejected by author: `git_push` requires CONFIRM; `force: true` requires explicit opt-in in tool call. |
| Background/daemon process support | No supervision, orphaned processes, audit gaps. Rejected by author: all commands run with timeout and return results synchronously. |
| Interactive PTY/REPL sessions | Breaks request-response model; no audit trail for interactive input. Rejected by author: tools are stateless, auditable units. |
| Network commands (curl, wget, ssh) in default allowlist | Data exfiltration risk; external network calls should be explicit opt-in. Rejected by author: default allowlist is dev-tool focused only. |
| Environment variable passthrough without allowlist | Secrets leakage (API keys, tokens) into subprocess environment. Rejected by author: env vars require explicit allowlist or inherit-only mode. |
| Command chaining (`&&`, `||`, pipes) in allowlist | Complexity in validation; each subcommand needs allowlist check. Rejected by author: defer to Phase 11 (autonomous agent) for multi-step workflows. |