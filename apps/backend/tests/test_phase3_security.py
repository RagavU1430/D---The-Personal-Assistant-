import pytest

from app.computer.controller import FakeComputerController
from app.tools.computer import register_computer_tools
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool", "arguments", "error_code"),
    [
        ("open_application", {"application": "powershell"}, "APPLICATION_NOT_ALLOWED"),
        ("type_text", {"text": "secret-password"}, "CONFIRMATION_REQUIRED"),
        ("move_mouse", {"x": 999999, "y": 20}, "VALIDATION_ERROR"),
        ("raw_shell", {"command": "whoami"}, "TOOL_NOT_FOUND"),
    ],
)
async def test_unsafe_computer_requests_are_rejected(tool: str, arguments: dict, error_code: str) -> None:
    registry = ToolRegistry()
    register_computer_tools(registry, FakeComputerController())
    result = await ToolExecutor(registry).execute(tool, arguments)
    assert result.error_code == error_code
