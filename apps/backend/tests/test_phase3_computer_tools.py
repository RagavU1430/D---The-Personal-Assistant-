import pytest

from app.computer.controller import FakeComputerController
from app.security import RiskLevel
from app.tools.computer import register_computer_tools
from app.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_computer_tools_use_structured_allowlisted_actions() -> None:
    controller = FakeComputerController()
    registry = ToolRegistry()
    register_computer_tools(registry, controller)

    opened = await registry.get("open_application").execute({"application": "notepad"})
    rejected = await registry.get("open_application").execute({"application": "arbitrary_executable"})

    assert opened.success is True
    assert opened.data["application"] == "notepad"
    assert rejected.success is False
    assert rejected.error_code == "APPLICATION_NOT_ALLOWED"
    assert controller.calls == [("open_application", {"application": "notepad"})]


@pytest.mark.asyncio
async def test_mouse_keyboard_and_window_tools_validate_inputs() -> None:
    controller = FakeComputerController()
    registry = ToolRegistry()
    register_computer_tools(registry, controller)

    valid = await registry.get("move_mouse").execute({"x": 10, "y": 20})
    invalid = await registry.get("move_mouse").execute({"x": -1, "y": 20})
    key = await registry.get("press_key").execute({"key": "ENTER"})
    bad_key = await registry.get("press_key").execute({"key": "NOT_A_KEY"})

    assert valid.success is True
    assert invalid.error_code == "VALIDATION_ERROR"
    assert key.success is True
    assert bad_key.error_code == "VALIDATION_ERROR"


def test_computer_tools_have_metadata_and_confirmation_policy() -> None:
    registry = ToolRegistry()
    register_computer_tools(registry, FakeComputerController())

    assert registry.metadata("open_application")["category"] == "computer"
    assert registry.get("close_application").risk_level == RiskLevel.CONFIRM
