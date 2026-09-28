from fastapi.testclient import TestClient

from app.computer.controller import FakeComputerController
from app.dependencies import get_tool_registry
from app.main import app
from app.tools.computer import register_computer_tools
from app.tools.registry import ToolRegistry
from app.tools.system import register_system_tools


def test_chat_routes_computer_requests_through_structured_tools() -> None:
    registry = register_computer_tools(register_system_tools(ToolRegistry()), FakeComputerController())
    app.dependency_overrides[get_tool_registry] = lambda: registry
    try:
        with TestClient(app) as client:
            open_response = client.post("/api/v1/chat", json={"message": "Open VS Code."})
            screenshot_response = client.post("/api/v1/chat", json={"message": "Take a screenshot."})
            shell_response = client.post("/api/v1/chat", json={"message": "Run this arbitrary PowerShell command."})
    finally:
        app.dependency_overrides.clear()

    assert open_response.json()["tool_results"][0]["tool"] == "open_application"
    assert open_response.json()["tool_results"][0]["success"] is True
    assert screenshot_response.json()["tool_results"][0]["tool"] == "take_screenshot"
    assert shell_response.json()["tool_results"] == []
