# Security

D - The Personal Assistant treats all model and external output as untrusted data. Tool names and arguments are accepted only through the registry and Pydantic schemas, then passed through the permission engine and `ToolExecutor`. There is no direct model path to shell, arbitrary Python execution, unrestricted filesystem mutation, browser automation, or raw process control.

`SAFE` tools can run automatically, `CONFIRM` tools return a confirmation contract without execution, and `BLOCK` tools are rejected. Every execution attempt is audit logged with tool, risk, decision, result, duration, and error code; sensitive argument values are redacted.

## Permission Model

- `SAFE`: Low-risk operations with no approval required (e.g., `system_status`, `search_files`, `read_file`, `list_large_files`, `find_duplicates`).
- `CONFIRM`: Mutating or stateful actions requiring explicit user approval (e.g., `write_file`, `copy_file`, `move_file`, `rename_file`, `compress_directory`, `organize_directory`, `close_application`, `move_to_recycle_bin`).
- `BLOCK`: Prohibited actions (arbitrary shell commands, path traversal, operations outside approved roots).

## Phase 3 Computer Control Governance

Computer control is strictly bounded and allowlisted:
* Applications are selected by configured alias names, never executable paths from model output.
* Mouse coordinates and keyboard keys are validated against strict allowlists.
* Text entry, window closing, and destructive operations require confirmation.
* An emergency killswitch disables controller actions instantly until explicitly resumed.
* Windows startup uses the legitimate per-user Startup folder only.

## Phase 4 File System Intelligence Security

File tools are guarded by multi-layered security controls:
* **Approved File Roots:** All paths must resolve within `APPROVED_FILE_ROOTS`. Directory traversal (`..`), symlink escapes, and root drive targets outside approved paths trigger `PATH_NOT_ALLOWED`.
* **Protected File Roots:** Mutating tools check `PROTECTED_FILE_ROOTS` (e.g. `.git/`, system directories) and reject operations with `PATH_PROTECTED`.
* **Safe Reversible Deletion:** Hard deletions (`rmdir`, `unlink`) are disabled; only reversible moves to the Windows Recycle Bin via `SHFileOperationW` (`FOF_ALLOWUNDO`) are permitted under confirmation.
* **Denial-of-Service Mitigations:** File reads and writes enforce `max_file_size_mb` guards (default 100 MB). Compression tools validate destination paths and output size limits.
* **Audit Trail:** Every file operation logs `{tool, path, risk, decision, duration_ms, success, error_code}` with secret redaction.

## Secret Handling

Secrets are loaded from environment configuration (`.env`) and excluded from Git. Logs automatically redact fields containing keys, tokens, passwords, and secrets.
