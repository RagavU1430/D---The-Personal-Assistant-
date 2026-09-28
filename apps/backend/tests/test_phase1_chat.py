from fastapi.testclient import TestClient

from app.main import app


def test_chat_endpoint_accepts_prompt_and_returns_response() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/chat", json={"message": "Hello Jarvis"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"]
    assert payload["state"] in {"COMPLETED", "THINKING", "PLANNING", "EXECUTING"}


def test_chat_endpoint_handles_action_request() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/chat", json={"message": "Open VS Code."})

    assert response.status_code == 200
    payload = response.json()
    assert payload["plan"] is not None
    assert payload["plan"]["goal"]
