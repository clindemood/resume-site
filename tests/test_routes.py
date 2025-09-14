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
        "/api/command",
        json={"command": "open overview"},
        headers={"X-CSRF-Token": csrf},
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


def test_rate_limit_exceeded():
    local_client = TestClient(app)
    headers = {"X-Forwarded-For": "203.0.113.1"}
    for _ in range(10):
        resp = local_client.get("/api/start", headers=headers)
        assert resp.status_code == 200
    resp = local_client.get("/api/start", headers=headers)
    assert resp.status_code == 429


def test_command_rate_limit_exceeded():
    local_client = TestClient(app)
    headers = {"X-Forwarded-For": "203.0.113.2"}
    start = local_client.get("/api/start", headers=headers)
    csrf = start.json()["csrf_token"]
    for _ in range(10):
        resp = local_client.post(
            "/api/command",
            json={"command": "open overview"},
            headers={"X-CSRF-Token": csrf, **headers},
        )
        assert resp.status_code == 200
    resp = local_client.post(
        "/api/command",
        json={"command": "open overview"},
        headers={"X-CSRF-Token": csrf, **headers},
    )
    assert resp.status_code == 429


def test_session_limit_evicts_oldest():
    from app import main

    original = main.MAX_SESSIONS
    main.MAX_SESSIONS = 2
    main.sessions.clear()
    local_client = TestClient(main.app)

    s1 = local_client.get("/api/start", headers={"X-Forwarded-For": "198.51.100.1"})
    id1 = s1.cookies["session_id"]
    s2 = local_client.get("/api/start", headers={"X-Forwarded-For": "198.51.100.2"})
    id2 = s2.cookies["session_id"]
    s3 = local_client.get("/api/start", headers={"X-Forwarded-For": "198.51.100.3"})
    id3 = s3.cookies["session_id"]

    assert len(main.sessions) == 2
    assert id1 not in main.sessions
    assert id2 in main.sessions and id3 in main.sessions

    main.sessions.clear()
    main.MAX_SESSIONS = original
