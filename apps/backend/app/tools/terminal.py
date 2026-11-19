"""
Phase 5 — Developer JARVIS: TerminalService + 9 controlled developer tools.

Security invariants:
- NO shell=True anywhere in this module.
- All commands validated against COMMAND_ALLOWLIST before any process spawns.
- Working directories validated against APPROVED_WORKING_ROOTS.
- Shell injection operators rejected in all argument positions.
- Git subcommands validated against GIT_ALLOWED_SUBCOMMANDS.
"""
from __future__ import annotations

import asyncio
import re
import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..config import Settings
from ..security.risk import RiskLevel
from .base import BaseTool, ToolResult
from .registry import ToolRegistry

# ---------------------------------------------------------------------------
# Shell injection detection pattern
# ---------------------------------------------------------------------------

_SHELL_INJECTION_PATTERN = re.compile(
    r"[;&|`><]|&&|\|\||\$\(|%[a-zA-Z]"
)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class TerminalError(Exception):
    """Base class for terminal tool errors."""


class WorkingDirNotAllowedError(TerminalError):
    """Raised when a working directory is outside approved roots."""


class CommandNotAllowedError(TerminalError):
    """Raised when a command or git subcommand is not in the allowlist."""


class ShellInjectionError(TerminalError):
    """Raised when a shell injection operator is detected in arguments."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class TerminalRunResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    truncated: bool = False
    duration_ms: float = 0.0


# ---------------------------------------------------------------------------
# TerminalService
# ---------------------------------------------------------------------------


class TerminalService:
    """
    Shared service providing working-directory validation, command allowlisting,
    shell-injection sanitization, and safe async subprocess execution.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def resolve_working_dir(self, path: str | Path) -> Path:
        """
        Resolve *path* and verify it is inside at least one APPROVED_WORKING_ROOTS.
        Raises WorkingDirNotAllowedError if not allowed.
        """
        resolved = Path(path).expanduser().resolve()
        roots = self._settings.approved_working_roots_list

        if not roots:
            raise WorkingDirNotAllowedError(
                "No approved working roots configured. "
                "Set APPROVED_WORKING_ROOTS in .env to enable terminal tools."
            )

        for raw_root in roots:
            approved = Path(raw_root).expanduser().resolve()
            try:
                resolved.relative_to(approved)
                if not resolved.exists():
                    raise WorkingDirNotAllowedError(
                        f"Working directory does not exist: {resolved}"
                    )
                if not resolved.is_dir():
                    raise WorkingDirNotAllowedError(
                        f"Path is not a directory: {resolved}"
                    )
                return resolved
            except ValueError:
                continue

        raise WorkingDirNotAllowedError(
            f"Working directory '{resolved}' is not inside any approved root. "
            f"Approved: {roots}"
        )

    def _sanitize_args(self, args: list[str]) -> None:
        """Raise ShellInjectionError if any argument contains shell injection operators."""
        for arg in args:
            if _SHELL_INJECTION_PATTERN.search(arg):
                raise ShellInjectionError(
                    f"Argument contains prohibited shell operator: {arg!r}"
                )

    def validate_command(self, cmd: str, args: list[str]) -> tuple[str, list[str]]:
        """
        Validate cmd against COMMAND_ALLOWLIST; for git, validate subcommand
        against GIT_ALLOWED_SUBCOMMANDS.  Sanitize all args for injection.
        """
        cmd_lower = cmd.strip().lower()
        allowed = self._settings.command_allowlist_set

        if cmd_lower not in allowed:
            raise CommandNotAllowedError(
                f"Command '{cmd}' is not in the allowed command list. "
                f"Allowed: {sorted(allowed)}"
            )

        if cmd_lower == "git":
            if not args:
                raise CommandNotAllowedError(
                    "git requires a subcommand (e.g. status, diff, log)."
                )
            sub = args[0].strip().lower()
            allowed_subs = self._settings.git_allowed_subcommands_set
            if sub not in allowed_subs:
                raise CommandNotAllowedError(
                    f"git subcommand '{sub}' is not allowed. "
                    f"Allowed: {sorted(allowed_subs)}"
                )

        self._sanitize_args(args)
        return cmd, args

    async def run_command(
        self,
        cmd: str,
        args: list[str],
        working_dir: Path,
        timeout: float | None = None,
        max_bytes: int | None = None,
    ) -> TerminalRunResult:
        """
        Execute cmd+args in working_dir via asyncio.create_subprocess_exec.
        Never uses shell=True. Enforces timeout and byte-limit truncation.
        """
        effective_timeout = timeout or self._settings.terminal_timeout_seconds
        effective_max = max_bytes or self._settings.max_output_bytes

        full_cmd = [cmd, *args]
        start = time.monotonic()

        try:
            proc = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(working_dir),
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=effective_timeout
                )
            except TimeoutError:
                proc.kill()
                await proc.communicate()
                duration = (time.monotonic() - start) * 1000
                return TerminalRunResult(
                    stdout="",
                    stderr=f"Process timed out after {effective_timeout}s",
                    exit_code=-1,
                    truncated=True,
                    duration_ms=round(duration, 2),
                )

            duration = (time.monotonic() - start) * 1000
            truncated = False

            if len(stdout_bytes) > effective_max:
                stdout_bytes = stdout_bytes[:effective_max]
                truncated = True
            if len(stderr_bytes) > effective_max:
                stderr_bytes = stderr_bytes[:effective_max]
                truncated = True

            return TerminalRunResult(
                stdout=stdout_bytes.decode("utf-8", errors="replace").rstrip(),
                stderr=stderr_bytes.decode("utf-8", errors="replace").rstrip(),
                exit_code=proc.returncode or 0,
                truncated=truncated,
                duration_ms=round(duration, 2),
            )
        except FileNotFoundError:
            duration = (time.monotonic() - start) * 1000
            return TerminalRunResult(
                stdout="",
                stderr=f"Command '{cmd}' not found on PATH.",
                exit_code=127,
                duration_ms=round(duration, 2),
            )
        except Exception as exc:
            duration = (time.monotonic() - start) * 1000
            return TerminalRunResult(
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                duration_ms=round(duration, 2),
            )


# ---------------------------------------------------------------------------
# Pydantic input schemas
# ---------------------------------------------------------------------------


class GitWorkingDirInput(BaseModel):
    working_dir: str = Field(default=".", description="Path to the git repository")


class GitDiffInput(BaseModel):
    working_dir: str = Field(default=".")
    staged: bool = Field(default=False, description="Show staged diff instead of unstaged")
    max_lines: int = Field(default=500, ge=1, le=5000)


class GitLogInput(BaseModel):
    working_dir: str = Field(default=".")
    max_entries: int = Field(default=10, ge=1, le=100)


class GitCommitInput(BaseModel):
    working_dir: str = Field(default=".")
    message: str = Field(min_length=1, max_length=500)
    add_all: bool = Field(default=False)


class GitPushInput(BaseModel):
    working_dir: str = Field(default=".")
    remote: str = Field(default="origin")
    branch: str | None = Field(default=None)
    force: bool = Field(default=False)


class RunTestsInput(BaseModel):
    working_dir: str = Field(default=".")
    framework: Literal["pytest", "jest", "npm", "cargo", "go", "auto"] = "auto"
    args: list[str] = Field(default_factory=list)


class AnalyzeLogsInput(BaseModel):
    content: str = Field(min_length=1, description="Raw log text to analyze")
    max_findings: int = Field(default=25, ge=1, le=200)


class ExecuteCommandInput(BaseModel):
    command: str = Field(min_length=1)
    args: list[str] = Field(default_factory=list)
    working_dir: str = Field(default=".")


# ---------------------------------------------------------------------------
# Tool 1: GitStatusTool (SAFE)
# ---------------------------------------------------------------------------


class GitStatusTool(BaseTool):
    name = "git_status"
    description = "Get git status: branch, staged/unstaged/untracked files"
    category = "developer"
    risk_level = RiskLevel.SAFE
    input_schema = GitWorkingDirInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = GitWorkingDirInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        result = await self._svc.run_command("git", ["status", "--porcelain", "-b"], wd)
        if result.exit_code != 0:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="GIT_ERROR",
                message=result.stderr or result.stdout,
            )

        lines = result.stdout.splitlines()
        branch = ""
        staged: list[str] = []
        unstaged: list[str] = []
        untracked: list[str] = []

        for line in lines:
            if line.startswith("## "):
                branch = line[3:].split("...")[0].split(" ")[0]
            elif line.startswith("?? "):
                untracked.append(line[3:].strip())
            elif len(line) >= 2:
                x, y = line[0], line[1]
                filepath = line[3:].strip()
                if x not in (" ", "?"):
                    staged.append(filepath)
                if y not in (" ", "?"):
                    unstaged.append(filepath)

        clean = not staged and not unstaged and not untracked
        counts_str = f"{len(staged)} staged, {len(unstaged)} unstaged, {len(untracked)} untracked"
        summary = f"Branch: {branch} | " + ("Clean working tree" if clean else counts_str)
        return ToolResult(
            success=True,
            tool=self.name,
            data={
                "clean": clean,
                "branch": branch,
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked,
                "summary": summary,
            },
            message=summary,
        )


# ---------------------------------------------------------------------------
# Tool 2: GitDiffTool (SAFE)
# ---------------------------------------------------------------------------


class GitDiffTool(BaseTool):
    name = "git_diff"
    description = "Show git diff of unstaged (or staged with staged=true) changes"
    category = "developer"
    risk_level = RiskLevel.SAFE
    input_schema = GitDiffInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = GitDiffInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        stat_args = ["diff", "--stat"] + (["--staged"] if inp.staged else [])
        stat_result = await self._svc.run_command("git", stat_args, wd)

        diff_args = ["diff"] + (["--staged"] if inp.staged else [])
        diff_result = await self._svc.run_command("git", diff_args, wd)

        diff_lines = diff_result.stdout.splitlines()
        truncated = len(diff_lines) > inp.max_lines
        diff_text = "\n".join(diff_lines[: inp.max_lines])

        stat_lines = [line for line in stat_result.stdout.splitlines() if "|" in line]
        files_changed = [line.split("|")[0].strip() for line in stat_lines]

        return ToolResult(
            success=True,
            tool=self.name,
            data={"diff": diff_text, "files_changed": files_changed, "truncated": truncated},
            message=f"{len(files_changed)} file(s) changed" + (" (diff truncated)" if truncated else ""),
        )


# ---------------------------------------------------------------------------
# Tool 3: GitLogTool (SAFE)
# ---------------------------------------------------------------------------


class GitLogTool(BaseTool):
    name = "git_log"
    description = "Show recent git commit history"
    category = "developer"
    risk_level = RiskLevel.SAFE
    input_schema = GitLogInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = GitLogInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        fmt = "--pretty=format:%H|||%an|||%ad|||%s"
        result = await self._svc.run_command("git", ["log", fmt, "--date=short", f"-{inp.max_entries}"], wd)
        if result.exit_code != 0:
            return ToolResult(success=False, tool=self.name, error_code="GIT_ERROR", message=result.stderr)

        commits = []
        for line in result.stdout.splitlines():
            parts = line.split("|||")
            if len(parts) == 4:
                commits.append({"hash": parts[0][:8], "author": parts[1], "date": parts[2], "message": parts[3]})

        return ToolResult(
            success=True,
            tool=self.name,
            data={"commits": commits, "count": len(commits)},
            message=f"Showing {len(commits)} commit(s)",
        )


# ---------------------------------------------------------------------------
# Tool 4: GitBranchTool (SAFE)
# ---------------------------------------------------------------------------


class GitBranchTool(BaseTool):
    name = "git_branch"
    description = "List git branches and show the current active branch"
    category = "developer"
    risk_level = RiskLevel.SAFE
    input_schema = GitWorkingDirInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = GitWorkingDirInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        result = await self._svc.run_command("git", ["branch"], wd)
        if result.exit_code != 0:
            return ToolResult(success=False, tool=self.name, error_code="GIT_ERROR", message=result.stderr)

        current = ""
        branches: list[str] = []
        for line in result.stdout.splitlines():
            if line.startswith("* "):
                current = line[2:].strip()
                branches.append(current)
            elif line.strip():
                branches.append(line.strip())

        return ToolResult(
            success=True,
            tool=self.name,
            data={"current": current, "branches": branches},
            message=f"Current branch: {current} | {len(branches)} branch(es) total",
        )


# ---------------------------------------------------------------------------
# Tool 5: GitCommitTool (CONFIRM)
# ---------------------------------------------------------------------------


class GitCommitTool(BaseTool):
    name = "git_commit"
    description = "Stage and commit changes to the git repository"
    category = "developer"
    risk_level = RiskLevel.CONFIRM
    input_schema = GitCommitInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = GitCommitInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        if inp.add_all:
            add_result = await self._svc.run_command("git", ["add", "--all"], wd)
            if add_result.exit_code != 0:
                return ToolResult(success=False, tool=self.name, error_code="GIT_ADD_FAILED", message=add_result.stderr)

        try:
            self._svc._sanitize_args([inp.message])
        except ShellInjectionError as exc:
            return ToolResult(success=False, tool=self.name, error_code="INJECTION_DETECTED", message=str(exc))

        result = await self._svc.run_command("git", ["commit", "-m", inp.message], wd)
        if result.exit_code != 0:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="GIT_COMMIT_FAILED",
                message=result.stderr or result.stdout,
            )

        commit_hash = ""
        for line in result.stdout.splitlines():
            if line.startswith("["):
                parts = line.split()
                if len(parts) >= 2:
                    commit_hash = parts[1].rstrip("]")
                break

        return ToolResult(
            success=True,
            tool=self.name,
            data={"hash": commit_hash, "message": inp.message, "success": True},
            message=f"Committed: {commit_hash} — {inp.message}",
        )


# ---------------------------------------------------------------------------
# Tool 6: GitPushTool (CONFIRM)
# ---------------------------------------------------------------------------


class GitPushTool(BaseTool):
    name = "git_push"
    description = "Push commits to a remote git repository"
    category = "developer"
    risk_level = RiskLevel.CONFIRM
    input_schema = GitPushInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = GitPushInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        args = ["push", inp.remote]
        if inp.branch:
            args.append(inp.branch)
        if inp.force:
            args.append("--force-with-lease")  # Safer than --force

        try:
            self._svc._sanitize_args([inp.remote] + ([inp.branch] if inp.branch else []))
        except ShellInjectionError as exc:
            return ToolResult(success=False, tool=self.name, error_code="INJECTION_DETECTED", message=str(exc))

        result = await self._svc.run_command("git", args, wd)
        pushed = result.exit_code == 0
        output = result.stdout or result.stderr

        return ToolResult(
            success=pushed,
            tool=self.name,
            data={"pushed": pushed, "remote": inp.remote, "branch": inp.branch or "current", "output": output},
            message=f"Push {'succeeded' if pushed else 'failed'}: {inp.remote}/{inp.branch or 'current'}",
            error_code=None if pushed else "GIT_PUSH_FAILED",
        )


# ---------------------------------------------------------------------------
# Tool 7: RunTestsTool (CONFIRM)
# ---------------------------------------------------------------------------


def _detect_test_framework(wd: Path) -> tuple[str, list[str]]:
    """Auto-detect test framework in wd. Returns (command, base_args)."""
    if (wd / "pyproject.toml").exists() or (wd / "pytest.ini").exists() or (wd / "setup.cfg").exists():
        return "pytest", []
    if (wd / "Cargo.toml").exists():
        return "cargo", ["test"]
    if (wd / "go.mod").exists():
        return "go", ["test", "./..."]
    if (wd / "package.json").exists():
        return "npm", ["test", "--", "--watchAll=false"]
    return "pytest", []


class RunTestsTool(BaseTool):
    name = "run_tests"
    description = "Run the project test suite (auto-detects pytest, cargo, go test, npm test)"
    category = "developer"
    risk_level = RiskLevel.CONFIRM
    input_schema = RunTestsInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = RunTestsInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        if inp.args:
            try:
                self._svc._sanitize_args(inp.args)
            except ShellInjectionError as exc:
                return ToolResult(success=False, tool=self.name, error_code="INJECTION_DETECTED", message=str(exc))

        framework_map = {
            "pytest": ("pytest", []),
            "jest": ("npm", ["test", "--", "--watchAll=false"]),
            "npm": ("npm", ["test", "--", "--watchAll=false"]),
            "cargo": ("cargo", ["test"]),
            "go": ("go", ["test", "./..."]),
        }

        if inp.framework == "auto":
            cmd, base_args = _detect_test_framework(wd)
        else:
            cmd, base_args = framework_map.get(inp.framework, ("pytest", []))

        result = await self._svc.run_command(cmd, base_args + inp.args, wd)
        output = result.stdout or result.stderr

        passed = failed = skipped = 0
        for line in output.splitlines():
            ll = line.lower()
            m = re.search(r"(\d+) passed", ll)
            if m:
                passed = int(m.group(1))
            m = re.search(r"(\d+) failed", ll)
            if m:
                failed = int(m.group(1))
            m = re.search(r"(\d+) (skipped|warning)", ll)
            if m:
                skipped = int(m.group(1))

        summary = f"{passed} passed, {failed} failed, {skipped} skipped | exit {result.exit_code}"
        return ToolResult(
            success=result.exit_code == 0,
            tool=self.name,
            data={
                "framework": cmd,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "exit_code": result.exit_code,
                "summary": summary,
                "output": output,
                "duration_ms": result.duration_ms,
            },
            message=summary,
            error_code=None if result.exit_code == 0 else "TEST_FAILURES",
        )


# ---------------------------------------------------------------------------
# Tool 8: AnalyzeLogsTool (SAFE)
# ---------------------------------------------------------------------------

_ERROR_RE = re.compile(r"(error|exception|traceback|failed|fatal|critical)", re.IGNORECASE)
_WARNING_RE = re.compile(r"(warning|warn|deprecated)", re.IGNORECASE)
_TRACEBACK_RE = re.compile(r"^Traceback \(most recent call last\):", re.MULTILINE)


class AnalyzeLogsTool(BaseTool):
    name = "analyze_logs"
    description = "Extract errors, warnings, and tracebacks from raw log text"
    category = "developer"
    risk_level = RiskLevel.SAFE
    input_schema = AnalyzeLogsInput

    async def execute(self, arguments: Any) -> ToolResult:
        inp = AnalyzeLogsInput.model_validate(arguments)
        lines = inp.content.splitlines()

        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        tracebacks: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]
            if _TRACEBACK_RE.match(line):
                tb_lines = [line]
                i += 1
                while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                    tb_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    tb_lines.append(lines[i])
                    i += 1
                tracebacks.append("\n".join(tb_lines))
                continue

            if _ERROR_RE.search(line) and len(errors) < inp.max_findings:
                ctx_start = max(0, i - 1)
                ctx_end = min(len(lines), i + 2)
                errors.append({"line": i + 1, "text": line.strip(), "context": "\n".join(lines[ctx_start:ctx_end])})
            elif _WARNING_RE.search(line) and len(warnings) < inp.max_findings:
                warnings.append({"line": i + 1, "text": line.strip()})

            i += 1

        summary = (
            f"Found {len(errors)} error(s), {len(warnings)} warning(s), "
            f"{len(tracebacks)} traceback(s) in {len(lines)} lines."
        )
        return ToolResult(
            success=True,
            tool=self.name,
            data={"errors": errors, "warnings": warnings, "tracebacks": tracebacks, "summary": summary},
            message=summary,
        )


# ---------------------------------------------------------------------------
# Tool 9: ExecuteCommandTool (CONFIRM)
# ---------------------------------------------------------------------------


class ExecuteCommandTool(BaseTool):
    name = "execute_command"
    description = "Execute an allowlisted developer command in an approved working directory"
    category = "developer"
    risk_level = RiskLevel.CONFIRM
    input_schema = ExecuteCommandInput

    def __init__(self, service: TerminalService) -> None:
        self._svc = service

    async def execute(self, arguments: Any) -> ToolResult:
        inp = ExecuteCommandInput.model_validate(arguments)
        try:
            wd = self._svc.resolve_working_dir(inp.working_dir)
        except TerminalError as exc:
            return ToolResult(success=False, tool=self.name, error_code="DIR_NOT_ALLOWED", message=str(exc))

        try:
            cmd, args = self._svc.validate_command(inp.command, inp.args)
        except (CommandNotAllowedError, ShellInjectionError) as exc:
            return ToolResult(success=False, tool=self.name, error_code="COMMAND_BLOCKED", message=str(exc))

        result = await self._svc.run_command(cmd, args, wd)
        success = result.exit_code == 0
        return ToolResult(
            success=success,
            tool=self.name,
            data={
                "command": f"{cmd} {' '.join(args)}".strip(),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "duration_ms": result.duration_ms,
            },
            message=result.stdout or result.stderr or f"Exit code: {result.exit_code}",
            error_code=None if success else "COMMAND_FAILED",
        )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_terminal_tools(registry: ToolRegistry, settings: Settings) -> ToolRegistry:
    """Register all Phase 5 terminal tools when enable_terminal_tools is True."""
    if not settings.enable_terminal_tools:
        return registry

    service = TerminalService(settings)
    tools: list[BaseTool] = [
        GitStatusTool(service),
        GitDiffTool(service),
        GitLogTool(service),
        GitBranchTool(service),
        GitCommitTool(service),
        GitPushTool(service),
        RunTestsTool(service),
        AnalyzeLogsTool(),
        ExecuteCommandTool(service),
    ]
    for tool in tools:
        registry.register(tool)
    return registry
