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