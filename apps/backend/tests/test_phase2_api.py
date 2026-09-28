from fastapi.testclient import TestClient

from app.main import app


def test_tools_are_discoverable_and_executable() -> None:
    with TestClient(app) as client:
        discovery = client.get("/api/v1/tools")
        execution = client.post("/api/v1/tools/execute", json={"tool": "memory_usage", "arguments": {}})
        unknown = client.post("/api/v1/tools/execute", json={"tool": "destroy_computer", "arguments": {}})

    assert discovery.status_code == 200
    names = {tool["name"] for tool in discovery.json()["tools"]}
    assert {"system_status", "memory_usage", "current_time"}.issubset(names)
    assert execution.status_code == 200
    assert execution.json()["success"] is True
    assert execution.json()["tool"] == "memory_usage"
    assert unknown.status_code == 200
    assert unknown.json()["error_code"] == "TOOL_NOT_FOUND"


def test_chat_executes_safe_system_request() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/chat", json={"message": "Check my system status."})

    assert response.status_code == 200
    payload = response.json()
    assert payload["tool_results"][0]["tool"] == "system_status"
    assert payload["tool_results"][0]["success"] is True
