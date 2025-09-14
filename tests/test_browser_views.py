import threading
import time
import pytest
import uvicorn

from app.main import app

pytest.importorskip("playwright")
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.1)
    yield
    server.should_exit = True
    thread.join()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            pytest.skip("Chromium browser not installed")
        yield browser
        browser.close()


def test_resume_page(server, browser):
    page = browser.new_page()
    page.goto("http://127.0.0.1:8000/resume")
    page.wait_for_selector("#resume-container h1")
    assert "Chad Lindemood" in page.text_content("#resume-container")
    page.close()


def test_projects_page(server, browser):
    page = browser.new_page()
    page.goto("http://127.0.0.1:8000/projects")
    page.wait_for_selector("#projects-list li")
    assert "Resume Creation Lab" in page.text_content("#projects-list")
    page.close()


def test_education_page(server, browser):
    page = browser.new_page()
    page.goto("http://127.0.0.1:8000/education")
    page.wait_for_selector("#education-list li")
    assert "Western Governors University" in page.text_content("#education-list")
    page.close()
