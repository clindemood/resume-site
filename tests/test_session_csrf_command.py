from fastapi.testclient import TestClient
from app import main


def test_session_expires_after_ttl():
    client = TestClient(main.app)
    start = client.get("/api/start", headers={"X-Forwarded-For": "198.51.100.99"})
    csrf = start.json()["csrf_token"]
    sid = start.cookies["session_id"]
    # make session appear expired
    main.sessions[sid]["_ts"] -= main.SESSION_TTL + 1
    main.prune_sessions()
    resp = client.post(
        "/api/command",
        json={"command": "help"},
        headers={"X-CSRF-Token": csrf},
    )
    assert resp.status_code == 400


def test_csrf_token_must_match():
    client = TestClient(main.app)
    client.get("/api/start", headers={"X-Forwarded-For": "198.51.100.98"})
    resp = client.post(
        "/api/command",
        json={"command": "help"},
        headers={"X-CSRF-Token": "bad-token"},
    )
    assert resp.status_code == 403


def test_invalid_command_parsing_returns_400():
    client = TestClient(main.app)
    start = client.get("/api/start", headers={"X-Forwarded-For": "198.51.100.97"})
    csrf = start.json()["csrf_token"]
    resp = client.post(
        "/api/command",
        json={"command": "open 'unterminated"},
        headers={"X-CSRF-Token": csrf},
    )
    assert resp.status_code == 400
