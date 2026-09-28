from fastapi.testclient import TestClient

from app.main import app


def test_computer_status_and_stop_resume_api() -> None:
    with TestClient(app) as client:
        status = client.get("/api/v1/computer/status")
        stop = client.post("/api/v1/computer/stop")
        stopped = client.get("/api/v1/computer/status")
        resume = client.post("/api/v1/computer/resume")

    assert status.status_code == 200
    assert "computer_control" in status.json()
    assert stop.json()["computer_control"] is False
    assert stopped.json()["computer_control"] is False
    assert resume.json()["computer_control"] is True


def test_windows_and_active_window_api_are_structured() -> None:
    with TestClient(app) as client:
        windows = client.get("/api/v1/windows")
        active = client.get("/api/v1/computer/active-window")

    assert windows.status_code == 200
    assert isinstance(windows.json()["windows"], list)
    assert active.status_code == 200
    assert "window" in active.json()
