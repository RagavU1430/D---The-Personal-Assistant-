# Design Document: Phase 4 — File System Intelligence

**Feature:** Phase 4 — File System Intelligence  
**Author:** RagavU1430  
**Date:** 2025-11-15  
**Status:** Draft  
**Context:** Follows Phase 3 (Computer Control) per PRD roadmap

---

## The Problem

Users need the assistant to find, read, organize, and safely modify files in approved directories. Currently, only `move_to_recycle_bin` exists (gated behind `enable_file_tools: false`). There is no ability to search, read, create, copy, move, rename, or compress files — all of which are prerequisites for developer workflows (Phase 5), browser downloads (Phase 6), and memory/RAG ingestion (Phases 7–8).

**User pain points:**
- Cannot ask "find my latest project report and summarize it" (PRD user story)
- Cannot organize project folders or detect duplicates/large files
- File operations require manual shell or explorer use, breaking the natural-language flow

---

## Overview

Extend the existing tool system (`BaseTool`, `ToolRegistry`, `ToolExecutor`, permission engine, audit logger) with a **file toolset** that operates exclusively within `APPROVED_FILE_ROOTS`. All tools are registered centrally in `dependencies.py`, gated by `enable_file_tools` config, and follow the SAFE/CONFIRM/BLOCK risk model.

**Scope:** Read-only tools (SAFE) + mutating tools (CONFIRM). No permanent deletion. No operations outside approved roots. No shell interpolation.

---

## Goals

| Goal | Success Criteria |
|------|------------------|
| Search files by name/pattern/content | `search_files` returns matching paths under approved roots |
| Read file contents (text, code, docs) | `read_file` returns content with size/encoding metadata |
| Create/write files | `write_file` creates new files (CONFIRM if overwriting) |
| Copy/move/rename files | `copy_file`, `move_file`, `rename_file` with CONFIRM |
| Compress directories | `compress_directory` creates zip/tar (CONFIRM) |
| Detect large files | `list_large_files` returns files > threshold |
| Detect duplicates | `find_duplicates` returns groups by content hash |
| Organize folders | `organize_directory` moves files by extension/date (CONFIRM) |
| Protected directories | Configurable `PROTECTED_FILE_ROOTS` blocks mutating ops |
| Audit logging | Every attempt/result logged with path, risk, decision, duration |

---

## Non-Goals

- Permanent deletion (recycle bin only)
- Operations outside `APPROVED_FILE_ROOTS`
- Shell command execution (Phase 5)
- Binary file editing (read-only for non-text)
- Network filesystem mounts (local only)
- Recursive directory deletion

---

## Technical Plan

### Architecture

```
User Request → Planner → ToolRegistry → Pydantic Validation
    → PermissionEngine (SAFE/CONFIRM/BLOCK) → ToolExecutor (timeout, audit)
    → FileTool.execute() → ToolResult → AI Response
```

All file tools inherit `BaseTool`, use Pydantic input schemas, and call a shared `FileSystemService` for path validation and operations.

### New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `FileSystemService` | `app/tools/filesystem.py` | Path validation, approved/protected root checks, safe path resolution, common operations (read, write, copy, move, hash, zip) |
| File tools | `app/tools/files.py` | `SearchFilesTool`, `ReadFileTool`, `WriteFileTool`, `CopyFileTool`, `MoveFileTool`, `RenameFileTool`, `CompressDirectoryTool`, `ListLargeFilesTool`, `FindDuplicatesTool`, `OrganizeDirectoryTool` |
| Schemas | `app/tools/files.py` (or `app/computer/schemas.py` style) | Pydantic models for each tool's input |
| Config additions | `app/config.py` | `enable_file_tools`, `approved_file_roots`, `protected_file_roots`, `max_file_size_mb`, `large_file_threshold_mb` |
| Registration | `app/dependencies.py` | `register_file_tools(registry, settings)` called in `get_tool_registry()` |
| Tests | `apps/backend/tests/test_phase4_files.py` | Unit + integration tests for each tool, permission, validation, audit |

### Data Flow

1. **Path validation** — every tool input path passes through `FileSystemService.resolve_approved(path)` which:
   - Expands `~`, resolves relative to CWD
   - Verifies path is under at least one `APPROVED_FILE_ROOTS`
   - Verifies path is NOT under any `PROTECTED_FILE_ROOTS` (for mutating tools)
   - Returns `Path` or raises `PathNotAllowedError`

2. **Risk classification**
   - SAFE: `search_files`, `read_file`, `list_large_files`, `find_duplicates`
   - CONFIRM: `write_file`, `copy_file`, `move_file`, `rename_file`, `compress_directory`, `organize_directory`

3. **Execution** — `ToolExecutor` enforces timeout (config `tool_timeout_seconds`), normalizes `ToolResult`, logs audit event with `{tool, path, risk, decision, duration_ms, success, error_code}`

### Configuration

```python
# app/config.py additions
enable_file_tools: bool = False
approved_file_roots: str = ""           # comma-separated, e.g. "C:/Projects,C:/Users/Name/Documents"
protected_file_roots: str = ""          # comma-separated, e.g. "C:/Projects/.git,C:/Windows"
max_file_size_mb: int = 100             # reject reads/writes above this
large_file_threshold_mb: int = 50       # for list_large_files
```

### API Exposure

- `GET /api/v1/tools` — includes file tools when enabled
- `POST /api/v1/tools/execute` — executes any file tool
- `POST /api/v1/chat` — planner routes file-related intents to file tools

---

## Alternatives Considered

| Alternative | Rejection Reason |
|-------------|------------------|
| Single `file_action` tool with `operation` enum | Violates single-responsibility; makes schema validation, risk classification, and audit opaque. Rejected by author: explicit tools map cleanly to risk levels and planner keywords. |
| Allow operations outside approved roots with confirmation | Security model requires hard boundary; confirmation can be phished. Rejected by author: approved roots are the capability boundary. |
| Use `pathlib` directly in each tool without service | Duplicates validation logic; harder to test and audit. Rejected by author: shared service centralizes path safety. |
| Implement permanent `delete_file` tool | PRD explicitly says "permanent deletion is not implemented." Recycle bin is the only deletion path. |
| Shell out to `cp`/`mv`/`rsync`/`7z` | Shell interpolation risk; Windows portability. Rejected by author: pure Python (`shutil`, `zipfile`, `hashlib`) is sufficient and auditable. |

---

## Detailed Implementation

### Files to Create

| File | Rationale |
|------|-----------|
| `apps/backend/app/tools/filesystem.py` | Shared service: path validation, approved/protected root logic, safe read/write/copy/move/hash/zip. All file tools depend on this. |
| `apps/backend/app/tools/files.py` (extend) | Add 10 new tool classes + Pydantic schemas. Reuses `move_to_recycle_bin` scaffolding. |
| `apps/backend/app/config.py` (modify) | Add `enable_file_tools`, `approved_file_roots`, `protected_file_roots`, `max_file_size_mb`, `large_file_threshold_mb`. |
| `apps/backend/app/dependencies.py` (modify) | Import and call `register_file_tools` in `get_tool_registry()`. |
| `apps/backend/app/agent/planner.py` (modify) | Add keyword mappings for file intents: "find", "search", "read", "open file", "create", "write", "copy", "move", "rename", "compress", "zip", "large files", "duplicates", "organize". |
| `apps/backend/tests/test_phase4_files.py` (create) | Test each tool: success, validation error, path not allowed, protected root, confirmation required, timeout, audit log entry. Mirror `test_recycle_bin.py` patterns. |
| `apps/backend/tests/test_phase4_integration.py` (create) | End-to-end chat flow tests: "find all .py files", "read config.py", "create notes.txt", "organize Downloads". |

### Files to Modify

| File | Change |
|------|--------|
| `apps/backend/app/tools/__init__.py` | Export new tool classes if needed |
| `docs/TOOLS.md` | Document all 10 new tools with schemas, risk levels, examples |
| `docs/SECURITY.md` | Update file handling section: approved roots, protected roots, CONFIRM gating, audit |
| `README.md` | Update "Current phase" to reflect Phase 4 progress |

### Tool Specifications

#### 1. `search_files` (SAFE)
```python
class SearchFilesInput(BaseModel):
    pattern: str = Field(min_length=1, max_length=256)  # glob or regex
    root: str | None = None  # optional subdirectory under approved roots
    recursive: bool = True
    max_results: int = Field(default=100, ge=1, le=1000)
```
Returns: `{"matches": [{"path": str, "size": int, "modified": iso_timestamp}, ...]}`

#### 2. `read_file` (SAFE)
```python
class ReadFileInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)
    max_bytes: int = Field(default=1_000_000, ge=1, le=10_000_000)
    encoding: str = "utf-8"
```
Returns: `{"path": str, "content": str, "size": int, "encoding": str, "truncated": bool}`

#### 3. `write_file` (CONFIRM)
```python
class WriteFileInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)
    content: str
    encoding: str = "utf-8"
    overwrite: bool = False
```
Returns: `{"path": str, "bytes_written": int, "created": bool}`

#### 4. `copy_file` (CONFIRM)
```python
class CopyFileInput(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)
    overwrite: bool = False
```

#### 5. `move_file` (CONFIRM)
```python
class MoveFileInput(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)
    overwrite: bool = False
```

#### 6. `rename_file` (CONFIRM)
```python
class RenameFileInput(BaseModel):
    path: str = Field(min_length=1, max_length=4096)
    new_name: str = Field(min_length=1, max_length=256, pattern=r"^[^<>:\"/\\|?*\x00-\x1F]+$")
```

#### 7. `compress_directory` (CONFIRM)
```python
class CompressDirectoryInput(BaseModel):
    source: str = Field(min_length=1, max_length=4096)
    destination: str = Field(min_length=1, max_length=4096)  # .zip or .tar.gz
    format: Literal["zip", "tar.gz"] = "zip"
```

#### 8. `list_large_files` (SAFE)
```python
class ListLargeFilesInput(BaseModel):
    root: str | None = None
    threshold_mb: int = Field(default=50, ge=1, le=10000)
    max_results: int = Field(default=50, ge=1, le=500)
```
Returns: `{"files": [{"path": str, "size_mb": float}, ...]}`

#### 9. `find_duplicates` (SAFE)
```python
class FindDuplicatesInput(BaseModel):
    root: str | None = None
    min_size_mb: int = Field(default=1, ge=0, le=1000)
    max_groups: int = Field(default=20, ge=1, le=100)
```
Returns: `{"groups": [{"hash": str, "size_mb": float, "files": [str, ...]}, ...]}`

#### 10. `organize_directory` (CONFIRM)
```python
class OrganizeDirectoryInput(BaseModel):
    root: str = Field(min_length=1, max_length=4096)
    by: Literal["extension", "date", "size"] = "extension"
    dry_run: bool = True
```
Returns: `{"plan": [{"source": str, "destination": str}, ...], "executed": bool}`

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Path traversal via `../` or symlinks | `resolve_approved()` uses `Path.resolve(strict=False)` and verifies `approved_root in requested.parents` |
| Symlink escape outside approved roots | `resolve()` follows symlinks; parent check catches escape |
| Large file DoS (memory exhaustion) | `max_file_size_mb` config + streaming reads for `read_file` |
| Zip bombs / decompression bombs | `compress_directory` only creates; no extraction tool. Size validated before write. |
| Race conditions (TOCTOU) | Operations are atomic where possible (`shutil.move`, `os.replace`); audit logs capture actual result |
| Protected root bypass | Mutating tools check `PROTECTED_FILE_ROOTS` in addition to `APPROVED_FILE_ROOTS` |
| Confirmation fatigue | SAFE tools auto-execute; only mutating tools require CONFIRM. UI can batch confirmations. |

---

## Acceptance Criteria

1. `enable_file_tools=true` + `approved_file_roots` set → `GET /api/v1/tools` lists 11 file tools (10 new + recycle bin)
2. `search_files` finds files by glob/regex under approved roots, rejects outside paths
3. `read_file` returns text content with metadata, truncates at `max_bytes`
4. `write_file` creates new file, requires CONFIRM if `overwrite=true` or file exists
5. `copy_file`/`move_file`/`rename_file` require CONFIRM, respect protected roots
6. `compress_directory` creates zip/tar.gz, requires CONFIRM
7. `list_large_files` returns files > threshold with sizes
8. `find_duplicates` groups by SHA-256 content hash
9. `organize_directory` with `dry_run=true` returns plan; `dry_run=false` executes with CONFIRM
10. All tools emit audit log entries with path, risk, decision, duration, success/error_code
11. Planner routes "find all python files" → `search_files`, "read config.py" → `read_file`, "organize my downloads" → `organize_directory`
12. Tests pass: `pytest apps/backend/tests/test_phase4_files.py apps/backend/tests/test_phase4_integration.py -v`

---

## Dependencies

- **Runtime:** `shutil`, `zipfile`, `tarfile`, `hashlib`, `pathlib` (stdlib) — no new deps
- **Test:** `pytest-asyncio` (already added in Phase 3 commit)
- **Config:** Requires `APPROVED_FILE_ROOTS` set in `.env` for tools to be usable

---

## Rollout Plan

1. Implement `FileSystemService` + tool classes + schemas
2. Add config fields + registration in `dependencies.py`
3. Extend planner with file intent keywords
4. Write unit tests for each tool (validation, permission, path checks)
5. Write integration tests for chat flow
6. Update docs (TOOLS.md, SECURITY.md, README.md)
7. Verify `pytest` + `ruff` + `mypy` pass
8. Commit and push

---

## Open Questions

1. **Encoding detection** — Should `read_file` auto-detect encoding (chardet) or require explicit `encoding` param? Current design: default UTF-8, explicit override.
2. **Binary file handling** — `read_file` on binary returns base64? Current design: reject with error if decoding fails; user can use `search_files` to locate, then external tool.
3. **`organize_directory` default behavior** — `dry_run=true` by default (safe), requires explicit `dry_run=false` + CONFIRM to execute.
4. **Max recursion depth for `search_files`** — Add `max_depth` param? Current design: no limit, but `max_results` caps output.
5. **Parallel execution** — `ToolExecutor.execute_plan` runs sequentially. File tools are I/O bound; could add `asyncio.gather` for independent steps. Defer to Phase 11 (autonomous agent).

---

*End of design draft. Ready for review and approval to proceed to implementation.*