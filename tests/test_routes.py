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
