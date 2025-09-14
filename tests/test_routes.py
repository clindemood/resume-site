from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200


def test_projects_returns_200():
    response = client.get("/projects")
    assert response.status_code == 200


def test_api_resume_returns_200():
    response = client.get("/api/resume")
    assert response.status_code == 200


def test_education_returns_200():
    response = client.get("/education")
    assert response.status_code == 200


def test_about_returns_200():
    response = client.get("/about")
    assert response.status_code == 200


def test_resume_returns_200():
    response = client.get("/resume")
    assert response.status_code == 200


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_api_start_and_command_flow():
    start_resp = client.get("/api/start")
    assert start_resp.status_code == 200
    data = start_resp.json()
    assert "csrf_token" in data
    csrf = data["csrf_token"]
    assert "session_id" in start_resp.cookies

    open_resp = client.post(
        "/api/command", json={"command": "open overview"}, headers={"X-CSRF-Token": csrf}
    )
    assert open_resp.status_code == 200
    assert "Name:" in open_resp.json()["text"]

    next_resp = client.post(
        "/api/command", json={"command": "next"}, headers={"X-CSRF-Token": csrf}
    )
    assert next_resp.status_code == 200
    assert "Name:" in next_resp.json()["text"]

    invalid_resp = client.post(
        "/api/command", json={"command": "999"}, headers={"X-CSRF-Token": csrf}
    )
    assert invalid_resp.status_code == 200
    assert invalid_resp.json()["text"] == "Unknown id."


def test_prune_sessions_removes_old():
    from app.main import SESSION_TTL, prune_sessions, sessions
    import time

    old_id = "expired"
    sessions[old_id] = {"_ts": time.time() - (SESSION_TTL + 1)}
    prune_sessions()
    assert old_id not in sessions
