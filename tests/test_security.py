import importlib
import os

from fastapi.testclient import TestClient


def test_security_headers_present():
    from app.main import app

    client = TestClient(app)
    response = client.get("/")
    headers = response.headers
    assert headers["Strict-Transport-Security"] == "max-age=63072000; includeSubDomains"
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"


def test_cors_respects_allowed_origins():
    os.environ["ALLOWED_ORIGINS"] = "https://allowed.example"
    import app.main as main
    importlib.reload(main)

    client = TestClient(main.app)
    response = client.get("/", headers={"Origin": "https://allowed.example"})
    assert response.headers["access-control-allow-origin"] == "https://allowed.example"

    # cleanup
    del os.environ["ALLOWED_ORIGINS"]
    importlib.reload(main)
