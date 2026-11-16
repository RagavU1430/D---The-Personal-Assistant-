from __future__ import annotations

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

    def plan(self, request: str) -> AgentPlan:
        text = request.strip()
        lowered = text.lower()

        mappings = (
            (("system status", "system information", "check my system"), "system_status"),
            (("ram", "memory"), "memory_usage"),
            (("cpu", "processor"), "cpu_usage"),
            (("disk", "storage"), "disk_usage"),
            (("what time", "current time", "time is it"), "current_time"),
            (("health", "healthy"), "jarvis_health"),
            (("screenshot", "screen capture", "capture my screen"), "take_screenshot"),
            (("active window", "current window", "what window"), "get_active_window"),
        )
        for keywords, tool_name in mappings:
            if any(keyword in lowered for keyword in keywords) and self.registry.exists(tool_name):
                return self.create_plan(text, tool=tool_name)

        if any(
            keyword in lowered
            for keyword in ("open vs code", "open vscode", "launch vscode", "open code", "code editor")
        ):
            tool_name = "open_application"
            if self.registry.exists(tool_name):
                return self.create_plan(text, tool=tool_name, arguments={"application": "vscode"})

        if any(keyword in lowered for keyword in ("open file explorer", "open explorer", "file explorer")):
            tool_name = "open_application"
            if self.registry.exists(tool_name):
                return self.create_plan(text, tool=tool_name, arguments={"application": "file_explorer"})

        # File intelligence tools (Phase 4)
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

        organize_keywords = (
            "organize directory", "organize folder", "organize my downloads", "organize files", "organize"
        )
        if self.registry.exists("organize_directory") and any(k in lowered for k in organize_keywords):
            return self.create_plan(text, tool="organize_directory", arguments={"root": ".", "dry_run": True})

        if self.registry.exists("compress_directory") and any(
            k in lowered for k in ("compress directory", "compress folder", "zip folder", "zip directory")
        ):
            dest_args = {"source": ".", "destination": "archive.zip"}
            return self.create_plan(text, tool="compress_directory", arguments=dest_args)

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

        if any(keyword in lowered for keyword in ("delete", "remove", "rename")):
            tool_name = "file_action"
            if self.registry.exists(tool_name):
                return self.create_plan(text, tool=tool_name)

        if any(keyword in lowered for keyword in ("run", "execute", "shell", "command")):
            tool_name = "terminal_command"
            if self.registry.exists(tool_name):
                return self.create_plan(text, tool=tool_name)

        return self.create_plan(text)

    def validate_plan(self, plan: AgentPlan) -> AgentPlan:
        for step in plan.steps:
            if step.action_type == "tool":
                if not step.tool:
                    raise ValueError("Tool steps require a tool name.")
                if not self.registry.exists(step.tool):
                    raise ValueError(f"Tool '{step.tool}' is not registered.")
        return plan
