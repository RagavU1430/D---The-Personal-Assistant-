import pytest

from app.computer.controller import FakeComputerController
from app.tools.computer import register_computer_tools
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_computer_actions_go_through_executor_and_emergency_stop() -> None:
    controller = FakeComputerController()
    registry = ToolRegistry()
    register_computer_tools(registry, controller)
    executor = ToolExecutor(registry)

    result = await executor.execute("open_application", {"application": "notepad"})
    controller.emergency_stop()
    stopped = await executor.execute("open_application", {"application": "notepad"})

    assert result.success is True
    assert stopped.error_code == "COMPUTER_CONTROL_DISABLED"
    assert len(controller.calls) == 1


@pytest.mark.asyncio
async def test_confirmation_tool_never_reaches_controller() -> None:
    controller = FakeComputerController()
    registry = ToolRegistry()
    register_computer_tools(registry, controller)

    result = await ToolExecutor(registry).execute("close_application", {"title": "Notepad"})

    assert result.error_code == "CONFIRMATION_REQUIRED"
    assert controller.calls == []
