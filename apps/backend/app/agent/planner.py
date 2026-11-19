from __future__ import annotations

import re
from typing import Any

from app.tools.registry import ToolRegistry

from .schemas import AgentPlan, PlanStep


class Planner:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def create_plan(self, goal: str, *, tool: str | None = None, arguments: dict[str, Any] | None = None) -> AgentPlan:
        step = PlanStep(
            id="step-1",
            description=goal,
            action_type="tool" if tool else "respond",
            tool=tool,
            arguments=arguments or {},
        )
        return AgentPlan(goal=goal, steps=[step])

    def plan(self, request: str) -> AgentPlan:  # noqa: C901
        text = request.strip()
        lowered = text.lower()

        # ----------------------------------------------------------------
        # System tools
        # ----------------------------------------------------------------
        system_mappings = (
            (("system status", "system information", "check my system"), "system_status"),
            (("ram", "memory"), "memory_usage"),
            (("cpu", "processor"), "cpu_usage"),
            (("disk", "storage"), "disk_usage"),
            (("what time", "current time", "time is it"), "current_time"),
            (("health", "healthy"), "jarvis_health"),
            (("screenshot", "screen capture", "capture my screen"), "take_screenshot"),
            (("active window", "current window", "what window"), "get_active_window"),
        )
        for keywords, tool_name in system_mappings:
            if any(k in lowered for k in keywords) and self.registry.exists(tool_name):
                return self.create_plan(text, tool=tool_name)

        # ----------------------------------------------------------------
        # Application tools
        # ----------------------------------------------------------------
        if any(k in lowered for k in ("open vs code", "open vscode", "launch vscode", "open code", "code editor")):
            if self.registry.exists("open_application"):
                return self.create_plan(text, tool="open_application", arguments={"application": "vscode"})

        if any(k in lowered for k in ("open file explorer", "open explorer", "file explorer")):
            if self.registry.exists("open_application"):
                return self.create_plan(text, tool="open_application", arguments={"application": "file_explorer"})

        # ----------------------------------------------------------------
        # Phase 5 — Terminal / Developer JARVIS tools
        # ----------------------------------------------------------------
        _wd = "."

        if self.registry.exists("git_status") and any(
            k in lowered for k in ("git status", "git state", "check repo", "repo status")
        ):
            return self.create_plan(text, tool="git_status", arguments={"working_dir": _wd})

        if self.registry.exists("git_diff") and any(
            k in lowered for k in ("git diff", "show diff", "what changed", "what did i change", "show changes")
        ):
            staged = "staged" in lowered or "--staged" in lowered
            return self.create_plan(text, tool="git_diff", arguments={"working_dir": _wd, "staged": staged})

        if self.registry.exists("git_log") and any(
            k in lowered for k in ("git log", "recent commits", "commit history", "last commits", "show commits")
        ):
            return self.create_plan(text, tool="git_log", arguments={"working_dir": _wd, "max_entries": 10})

        if self.registry.exists("git_branch") and any(
            k in lowered for k in ("git branch", "what branch", "current branch", "which branch", "list branches")
        ):
            return self.create_plan(text, tool="git_branch", arguments={"working_dir": _wd})

        if self.registry.exists("git_commit") and any(
            k in lowered for k in ("git commit", "commit with message", "stage and commit", "commit changes")
        ):
            match = re.search(r'["\'](.+?)["\']', text)
            msg = match.group(1) if match else "chore: update"
            add_all = "all" in lowered or " -a" in lowered
            return self.create_plan(
                text,
                tool="git_commit",
                arguments={"working_dir": _wd, "message": msg, "add_all": add_all},
            )

        if self.registry.exists("git_push") and any(
            k in lowered for k in ("git push", "push to remote", "push my changes", "push changes")
        ):
            return self.create_plan(text, tool="git_push", arguments={"working_dir": _wd, "remote": "origin"})

        if self.registry.exists("run_tests") and any(
            k in lowered for k in ("run tests", "run pytest", "run my tests", "test my code", "execute tests")
        ):
            return self.create_plan(text, tool="run_tests", arguments={"working_dir": _wd, "framework": "auto"})

        if self.registry.exists("analyze_logs") and any(
            k in lowered for k in (
                "analyze log", "analyze error", "explain error", "diagnose log", "analyze this error"
            )
        ):
            return self.create_plan(text, tool="analyze_logs", arguments={"content": text})

        if self.registry.exists("execute_command") and any(
            k in lowered for k in (
                "run ruff", "run mypy", "run black", "run make", "run cmake", "run command", "execute command"
            )
        ):
            parts = text.split()
            # Handle "run command python --version" pattern
            if "run command" in lowered:
                idx = lowered.index("run command")
                remainder = text[idx + len("run command"):].strip()
                parts = remainder.split()
            elif "execute command" in lowered:
                idx = lowered.index("execute command")
                remainder = text[idx + len("execute command"):].strip()
                parts = remainder.split()
            else:
                cmd = parts[1] if len(parts) > 1 else "ruff"
                extra = parts[2:] if len(parts) > 2 else []
                return self.create_plan(
                    text,
                    tool="execute_command",
                    arguments={"command": cmd, "args": extra, "working_dir": _wd},
                )

            if parts:
                cmd = parts[0]
                extra = parts[1:] if len(parts) > 1 else []
                return self.create_plan(
                    text,
                    tool="execute_command",
                    arguments={"command": cmd, "args": extra, "working_dir": _wd},
                )

        # ----------------------------------------------------------------
        # Phase 4 — File System Intelligence tools
        # ----------------------------------------------------------------
        if self.registry.exists("search_files") and any(
            k in lowered for k in ("search file", "search for", "find all", "find files", "find my")
        ):
            pattern = "*.py" if "python" in lowered else ("*.txt" if "text" in lowered or ".txt" in lowered else "*")
            for w in text.split():
                if "." in w and not w.startswith("http") and not w.endswith("?"):
                    pattern = w.strip("',\":")
                    break
            return self.create_plan(text, tool="search_files", arguments={"pattern": pattern})

        if self.registry.exists("read_file") and any(
            lowered.startswith(k) or f" {k}" in lowered for k in ("read file", "read ", "inspect file", "show file")
        ):
            path = ""
            for token in text.split():
                if "." in token and not token.startswith("http") and token.lower() != "read":
                    path = token.strip("',\":?")
                    break
            return self.create_plan(text, tool="read_file", arguments={"path": path or "config.py"})

        if self.registry.exists("list_large_files") and any(
            k in lowered for k in ("large files", "biggest files", "huge files", "large file")
        ):
            return self.create_plan(text, tool="list_large_files", arguments={"threshold_mb": 50})

        if self.registry.exists("find_duplicates") and any(
            k in lowered for k in ("duplicate files", "find duplicates", "detect duplicates", "duplicates")
        ):
            return self.create_plan(text, tool="find_duplicates", arguments={"min_size_mb": 1})

        if self.registry.exists("organize_directory") and any(
            k in lowered for k in (
                "organize directory", "organize folder", "organize my downloads", "organize files", "organize"
            )
        ):
            return self.create_plan(text, tool="organize_directory", arguments={"root": ".", "dry_run": True})

        if self.registry.exists("compress_directory") and any(
            k in lowered for k in ("compress directory", "compress folder", "zip folder", "zip directory")
        ):
            return self.create_plan(
                text,
                tool="compress_directory",
                arguments={"source": ".", "destination": "archive.zip"},
            )

        if self.registry.exists("rename_file") and "rename" in lowered:
            return self.create_plan(text, tool="rename_file")

        if self.registry.exists("copy_file") and "copy" in lowered:
            return self.create_plan(text, tool="copy_file")

        if self.registry.exists("move_file") and "move" in lowered and "recycle" not in lowered:
            return self.create_plan(text, tool="move_file")

        if self.registry.exists("write_file") and any(k in lowered for k in ("write file", "create file", "write to")):
            return self.create_plan(text, tool="write_file")

        if self.registry.exists("move_to_recycle_bin") and any(
            k in lowered for k in ("recycle bin", "delete file", "recycle file", "remove file")
        ):
            return self.create_plan(text, tool="move_to_recycle_bin")

        return self.create_plan(text)

    def validate_plan(self, plan: AgentPlan) -> AgentPlan:
        for step in plan.steps:
            if step.action_type == "tool":
                if not step.tool:
                    raise ValueError("Tool steps require a tool name.")
                if not self.registry.exists(step.tool):
                    raise ValueError(f"Tool '{step.tool}' is not registered.")
        return plan
