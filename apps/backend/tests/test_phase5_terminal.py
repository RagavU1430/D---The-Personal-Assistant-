"""
Phase 5 Test Suite — Developer JARVIS (TerminalService + 9 tools)
Tests: security boundaries, command allowlist, shell injection, git subcommands,
       tool execution, auto-detection, log analysis, timeout, intent routing.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from app.agent.intents import Intent, detect_intent
from app.agent.planner import Planner
from app.config import Settings
from app.tools.registry import ToolRegistry
from app.tools.terminal import (
    AnalyzeLogsTool,
    CommandNotAllowedError,
    GitCommitTool,
    GitDiffTool,
    GitLogTool,
    GitPushTool,
    GitStatusTool,
    ShellInjectionError,
    TerminalService,
    WorkingDirNotAllowedError,
    _detect_test_framework,
    register_terminal_tools,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def approved_dir(tmp_path: Path) -> Path:
    d = tmp_path / "approved_project"
    d.mkdir()
    return d.resolve()


@pytest.fixture
def outside_dir(tmp_path: Path) -> Path:
    d = tmp_path / "outside"
    d.mkdir()
    return d.resolve()


@pytest.fixture
def terminal_settings(approved_dir: Path) -> Settings:
    return Settings(
        enable_terminal_tools=True,
        approved_working_roots=str(approved_dir),
        command_allowlist="git,pytest,python,node,npm,cargo,go,ruff,mypy",
        git_allowed_subcommands="status,diff,log,branch,commit,push",
        terminal_timeout_seconds=5.0,
        max_output_bytes=1_000_000,
    )


@pytest.fixture
def service(terminal_settings: Settings) -> TerminalService:
    return TerminalService(terminal_settings)


@pytest.fixture
def git_repo(approved_dir: Path) -> Path:
    """Create a minimal git repository inside approved_dir."""
    loop = asyncio.get_event_loop()

    async def _init() -> None:
        proc = await asyncio.create_subprocess_exec("git", "init", cwd=str(approved_dir))
        await proc.communicate()
        proc2 = await asyncio.create_subprocess_exec(
            "git", "config", "user.email", "test@test.com", cwd=str(approved_dir)
        )
        await proc2.communicate()
        proc3 = await asyncio.create_subprocess_exec(
            "git", "config", "user.name", "Test", cwd=str(approved_dir)
        )
        await proc3.communicate()

    loop.run_until_complete(_init())
    return approved_dir


# ---------------------------------------------------------------------------
# Test 1: Working directory validation and traversal rejection
# ---------------------------------------------------------------------------


def test_working_dir_traversal_rejection(service: TerminalService, approved_dir: Path, outside_dir: Path) -> None:
    sub = approved_dir / "sub"
    sub.mkdir()
    resolved = service.resolve_working_dir(str(sub))
    assert resolved == sub

    resolved2 = service.resolve_working_dir(str(approved_dir))
    assert resolved2 == approved_dir

    with pytest.raises(WorkingDirNotAllowedError):
        service.resolve_working_dir(str(outside_dir))

    # Traversal attempt
    traversal = str(approved_dir / ".." / ".." / "etc")
    with pytest.raises(WorkingDirNotAllowedError):
        service.resolve_working_dir(traversal)


def test_no_approved_roots_raises(outside_dir: Path) -> None:
    s = Settings(enable_terminal_tools=True, approved_working_roots="")
    svc = TerminalService(s)
    with pytest.raises(WorkingDirNotAllowedError, match="No approved working roots"):
        svc.resolve_working_dir(str(outside_dir))


# ---------------------------------------------------------------------------
# Test 2: Command allowlist enforcement
# ---------------------------------------------------------------------------


def test_command_allowlist_enforcement(service: TerminalService) -> None:
    for cmd, args in [("git", ["status"]), ("pytest", []), ("python", ["-V"]), ("ruff", ["check"])]:
        c, _ = service.validate_command(cmd, args)
        assert c == cmd

    for cmd in ["curl", "powershell", "cmd", "bash", "rm", "del", "format", "ssh", "wget"]:
        with pytest.raises(CommandNotAllowedError):
            service.validate_command(cmd, [])


# ---------------------------------------------------------------------------
# Test 3: Shell injection operator rejection
# ---------------------------------------------------------------------------


def test_shell_injection_operator_rejection(service: TerminalService) -> None:
    dangerous: list[list[str]] = [
        ["; rm -rf /"],
        ["&& del C:\\Windows"],
        ["| cat /etc/passwd"],
        ["`whoami`"],
        ["$(id)"],
        ["> /tmp/out"],
        ["file.txt && evil"],
        ["arg1", "arg2 || bad"],
    ]
    for args in dangerous:
        with pytest.raises(ShellInjectionError):
            service._sanitize_args(args)

    service._sanitize_args(["--check", ".", "-v", "my-file.txt"])


# ---------------------------------------------------------------------------
# Test 4: Git subcommand allowlist
# ---------------------------------------------------------------------------


def test_git_subcommand_allowlist(service: TerminalService) -> None:
    for sub in ["status", "diff", "log", "branch", "commit", "push"]:
        cmd, args = service.validate_command("git", [sub])
        assert cmd == "git"
        assert args[0] == sub

    for sub in ["filter-branch", "credential", "config", "clone", "init"]:
        with pytest.raises(CommandNotAllowedError):
            service.validate_command("git", [sub])

    with pytest.raises(CommandNotAllowedError, match="subcommand"):
        service.validate_command("git", [])


# ---------------------------------------------------------------------------
# Test 5: GitStatus — SAFE risk and correct output shape
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_git_status_safe_execution(service: TerminalService, git_repo: Path) -> None:
    tool = GitStatusTool(service)
    assert tool.risk_level.value == "safe"

    result = await tool.execute({"working_dir": str(git_repo)})
    assert result.success is True
    assert result.data is not None
    for key in ("clean", "branch", "staged", "unstaged", "untracked"):
        assert key in result.data


# ---------------------------------------------------------------------------
# Test 6: GitDiff and GitLog shapes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_git_diff_shape(service: TerminalService, git_repo: Path) -> None:
    tool = GitDiffTool(service)
    assert tool.risk_level.value == "safe"
    result = await tool.execute({"working_dir": str(git_repo), "staged": False})
    assert result.success is True
    for key in ("diff", "files_changed", "truncated"):
        assert key in result.data


@pytest.mark.asyncio
async def test_git_log_shape(service: TerminalService, git_repo: Path) -> None:
    tool = GitLogTool(service)
    assert tool.risk_level.value == "safe"
    # Need at least one commit for git log to work
    proc = await asyncio.create_subprocess_exec("git", "commit", "--allow-empty", "-m", "initial", cwd=str(git_repo))
    await proc.communicate()
    result = await tool.execute({"working_dir": str(git_repo), "max_entries": 5})
    assert result.success is True
    assert "commits" in result.data
    assert "count" in result.data
    assert result.data["count"] >= 1


# ---------------------------------------------------------------------------
# Test 7: GitCommit / GitPush — CONFIRM risk
# ---------------------------------------------------------------------------


def test_git_commit_risk_confirm(service: TerminalService) -> None:
    assert GitCommitTool(service).risk_level.value == "confirm"
    assert GitPushTool(service).risk_level.value == "confirm"


@pytest.mark.asyncio
async def test_git_commit_injection_in_message(service: TerminalService, approved_dir: Path) -> None:
    tool = GitCommitTool(service)
    result = await tool.execute({"working_dir": str(approved_dir), "message": "fix: hello; rm -rf /", "add_all": False})
    assert result.success is False
    assert result.error_code == "INJECTION_DETECTED"


# ---------------------------------------------------------------------------
# Test 8: RunTests — auto-detection
# ---------------------------------------------------------------------------


def test_run_tests_auto_detection_pytest(approved_dir: Path) -> None:
    for f in approved_dir.iterdir():
        f.unlink()
    (approved_dir / "pyproject.toml").write_text("[tool.pytest.ini_options]")
    cmd, _ = _detect_test_framework(approved_dir)
    assert cmd == "pytest"


def test_run_tests_auto_detection_cargo(approved_dir: Path) -> None:
    for f in approved_dir.iterdir():
        f.unlink()
    (approved_dir / "Cargo.toml").write_text('[package]\nname = "myapp"')
    cmd, args = _detect_test_framework(approved_dir)
    assert cmd == "cargo"
    assert "test" in args


def test_run_tests_auto_detection_go(approved_dir: Path) -> None:
    for f in approved_dir.iterdir():
        f.unlink()
    (approved_dir / "go.mod").write_text("module myapp\n\ngo 1.21")
    cmd, args = _detect_test_framework(approved_dir)
    assert cmd == "go"
    assert "./..." in args


def test_run_tests_auto_detection_npm(approved_dir: Path) -> None:
    for f in approved_dir.iterdir():
        f.unlink()
    (approved_dir / "package.json").write_text('{"name":"app","scripts":{"test":"jest"}}')
    cmd, _ = _detect_test_framework(approved_dir)
    assert cmd == "npm"


# ---------------------------------------------------------------------------
# Test 9: AnalyzeLogs — pattern extraction
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyze_logs_extraction() -> None:
    tool = AnalyzeLogsTool()
    assert tool.risk_level.value == "safe"

    sample_log = (
        "INFO Starting server\n"
        "WARNING: deprecated config key detected\n"
        "ERROR: Connection refused at port 8001\n"
        "Traceback (most recent call last):\n"
        "  File \"main.py\", line 42, in run\n"
        "    raise ValueError(\"bad input\")\n"
        "ValueError: bad input\n"
        "INFO: Server stopped\n"
        "CRITICAL: Database unreachable"
    )

    result = await tool.execute({"content": sample_log, "max_findings": 25})
    assert result.success is True
    data = result.data
    assert len(data["errors"]) >= 1
    assert len(data["warnings"]) >= 1
    assert len(data["tracebacks"]) >= 1


# ---------------------------------------------------------------------------
# Test 10: Command timeout
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_command_timeout(service: TerminalService, approved_dir: Path) -> None:
    result = await service.run_command(
        "python",
        ["-c", "import time; time.sleep(60)"],
        approved_dir,
        timeout=0.5,
    )
    assert result.exit_code == -1
    assert result.truncated is True
    assert "timed out" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Test 11: Planner routes + intent detection + registration
# ---------------------------------------------------------------------------


def test_planner_routes_git_status(terminal_settings: Settings) -> None:
    registry = register_terminal_tools(ToolRegistry(), terminal_settings)
    plan = Planner(registry).plan("git status")
    assert plan.steps[0].tool == "git_status"


def test_planner_routes_run_tests(terminal_settings: Settings) -> None:
    registry = register_terminal_tools(ToolRegistry(), terminal_settings)
    plan = Planner(registry).plan("run tests")
    assert plan.steps[0].tool == "run_tests"


def test_intent_detection_terminal() -> None:
    for msg in ["git status", "run tests", "what branch", "show git diff", "recent commits", "git commit"]:
        assert detect_intent(msg) == Intent.TERMINAL_ACTION, f"Expected TERMINAL_ACTION for: {msg!r}"


def test_terminal_tools_disabled_by_default() -> None:
    s = Settings(enable_terminal_tools=False)
    registry = register_terminal_tools(ToolRegistry(), s)
    for name in ["git_status", "run_tests", "execute_command", "analyze_logs"]:
        assert not registry.exists(name)


def test_terminal_tools_enabled(terminal_settings: Settings) -> None:
    registry = register_terminal_tools(ToolRegistry(), terminal_settings)
    expected = ["git_status", "git_diff", "git_log", "git_branch",
                "git_commit", "git_push", "run_tests", "analyze_logs", "execute_command"]
    for name in expected:
        assert registry.exists(name), f"Expected tool '{name}' to be registered"
