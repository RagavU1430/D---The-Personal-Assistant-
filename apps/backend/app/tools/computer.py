from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel, ValidationError

from ..computer.controller import ComputerController
from ..computer.schemas import (
    ApplicationInput,
    EmptyComputerInput,
    HotkeyInput,
    KeyInput,
    MouseInput,
    TypeTextInput,
    WindowInput,
)
from ..config import settings
from ..security import RiskLevel
from .base import BaseTool, ToolResult
from .registry import ToolRegistry


class ComputerTool(BaseTool):
    category = "computer"

    def __init__(self, controller: ComputerController) -> None:
        self.controller = controller

    def _parse(self, arguments: Any) -> BaseModel | ToolResult:
        try:
            return self.input_schema.model_validate(arguments)
        except ValidationError:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="VALIDATION_ERROR",
                message="Invalid computer action arguments.",
            )

    async def _run(self, action: str, arguments: BaseModel | dict[str, Any], **kwargs: Any) -> ToolResult:
        try:
            if isinstance(arguments, dict):
                arguments = self.input_schema.model_validate(arguments)
            data = await getattr(self.controller, action)(**kwargs)
            return ToolResult(success=True, tool=self.name, data=data, message=f"{self.name} completed.")
        except ValidationError:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="VALIDATION_ERROR",
                message="Invalid computer action arguments.",
            )
        except Exception as exc:
            error_code = "COMPUTER_CONTROL_DISABLED" if not self.controller.enabled else "COMPUTER_ACTION_ERROR"
            return ToolResult(success=False, tool=self.name, error_code=error_code, message=str(exc))


class OpenApplicationTool(ComputerTool):
    name = "open_application"
    description = "Open an approved application by its configured name."
    input_schema = ApplicationInput
    risk_level = RiskLevel.SAFE

    async def execute(self, arguments: ApplicationInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(ApplicationInput, parsed)
        executable = settings.application_map.get(parsed.application)
        if not executable:
            return ToolResult(
                success=False,
                tool=self.name,
                error_code="APPLICATION_NOT_ALLOWED",
                message="Application is not allowlisted.",
            )
        return await self._run("open_application", parsed, application=parsed.application, executable=executable)


class CloseApplicationTool(ComputerTool):
    name = "close_application"
    description = "Close a window after explicit user confirmation."
    input_schema = WindowInput
    risk_level = RiskLevel.CONFIRM

    async def execute(self, arguments: WindowInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(WindowInput, parsed)
        return await self._run("close_application", parsed, title=parsed.title)


class WindowActionTool(ComputerTool):
    action = "focus_window"
    input_schema = WindowInput

    async def execute(self, arguments: WindowInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(WindowInput, parsed)
        return await self._run(self.action, parsed, title=parsed.title)


class FocusWindowTool(WindowActionTool):
    name = "focus_window"
    description = "Focus an existing window by title."


class MinimizeWindowTool(WindowActionTool):
    name = "minimize_window"
    description = "Minimize an existing window by title."
    action = "minimize_window"


class MaximizeWindowTool(WindowActionTool):
    name = "maximize_window"
    description = "Maximize an existing window by title."
    action = "maximize_window"


class MoveMouseTool(ComputerTool):
    name = "move_mouse"
    description = "Move the mouse to a validated screen coordinate."
    input_schema = MouseInput

    async def execute(self, arguments: MouseInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(MouseInput, parsed)
        return await self._run("move_mouse", parsed, x=parsed.x, y=parsed.y)


class ClickTool(ComputerTool):
    name = "click"
    description = "Click a validated screen coordinate."
    input_schema = MouseInput

    async def execute(self, arguments: MouseInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(MouseInput, parsed)
        return await self._run("click", parsed, x=parsed.x, y=parsed.y)


class DoubleClickTool(ClickTool):
    name = "double_click"
    description = "Double-click a validated screen coordinate."

    async def execute(self, arguments: MouseInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(MouseInput, parsed)
        return await self._run("click", parsed, x=parsed.x, y=parsed.y, double=True)


class TypeTextTool(ComputerTool):
    name = "type_text"
    description = "Type user-provided text into the focused application after confirmation."
    input_schema = TypeTextInput
    risk_level = RiskLevel.CONFIRM

    async def execute(self, arguments: TypeTextInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(TypeTextInput, parsed)
        return await self._run("type_text", parsed, text=parsed.text)


class PressKeyTool(ComputerTool):
    name = "press_key"
    description = "Press one approved keyboard key."
    input_schema = KeyInput

    async def execute(self, arguments: KeyInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(KeyInput, parsed)
        return await self._run("press_key", parsed, key=parsed.key)


class HotkeyTool(ComputerTool):
    name = "hotkey"
    description = "Press a short sequence of approved keyboard keys."
    input_schema = HotkeyInput

    async def execute(self, arguments: HotkeyInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        parsed = cast(HotkeyInput, parsed)
        return await self._run("hotkey", parsed, keys=parsed.keys)


class ScreenshotTool(ComputerTool):
    name = "take_screenshot"
    description = "Capture one on-demand temporary desktop screenshot."
    input_schema = EmptyComputerInput

    async def execute(self, arguments: EmptyComputerInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        return await self._run("screenshot", parsed)


class ActiveWindowTool(ComputerTool):
    name = "get_active_window"
    description = "Return basic information about the active window."
    input_schema = EmptyComputerInput

    async def execute(self, arguments: EmptyComputerInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        return await self._run("get_active_window", parsed)


class ListWindowsTool(ComputerTool):
    name = "list_windows"
    description = "Return basic visible window information."
    input_schema = EmptyComputerInput

    async def execute(self, arguments: EmptyComputerInput | dict[str, Any]) -> ToolResult:
        parsed = self._parse(arguments)
        if isinstance(parsed, ToolResult):
            return parsed
        return await self._run("list_windows", parsed)


def register_computer_tools(registry: ToolRegistry, controller: ComputerController) -> ToolRegistry:
    if not settings.enable_computer_control:
        return registry
    for tool in (
        OpenApplicationTool(controller), CloseApplicationTool(controller), FocusWindowTool(controller),
        MinimizeWindowTool(controller), MaximizeWindowTool(controller), MoveMouseTool(controller),
        ClickTool(controller), DoubleClickTool(controller), TypeTextTool(controller), PressKeyTool(controller),
        HotkeyTool(controller), ScreenshotTool(controller), ActiveWindowTool(controller), ListWindowsTool(controller),
    ):
        registry.register(tool)
    return registry
