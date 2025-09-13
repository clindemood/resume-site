from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/projects", response_class=FileResponse)
def projects() -> FileResponse:
    return FileResponse(STATIC_DIR / "projects.html")


@app.get("/education", response_class=FileResponse)
def education() -> FileResponse:
    return FileResponse(STATIC_DIR / "education.html")


@app.get("/about", response_class=FileResponse)
def about() -> FileResponse:
    return FileResponse(STATIC_DIR / "about.html")


@app.get("/resume", response_class=FileResponse)
def resume() -> FileResponse:
    return FileResponse(STATIC_DIR / "resume.html")
