import json
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Load virtual filesystem data
FS_PATH = Path(__file__).parent / "filesystem.json"
with FS_PATH.open() as f:
    FS = json.load(f)


def get_node(path: list[str]) -> dict | None:
    """Traverse the filesystem dictionary following ``path``."""
    node = FS
    for part in path:
        node = node.get("children", {}).get(part)
        if not node:
            return None
    return node


def list_dir(path: list[str]) -> str:
    node = get_node(path)
    if not node or node.get("type") != "dir":
        return "Not a directory."
    items = []
    for name, child in sorted(node.get("children", {}).items()):
        items.append(name + ("/" if child.get("type") == "dir" else ""))
    return "\n".join(items)


# Serve static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# In-memory session store
sessions: dict[str, dict] = {}


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


@app.get("/api/start")
def start():
    """Start a new CLI session."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"cwd": []}
    text = (
        "Welcome to the resume CLI. Type 'help' for commands."
    )
    return {"session_id": session_id, "text": text}


@app.post("/api/command")
async def command(payload: dict):
    session_id = payload.get("session_id")
    cmd = payload.get("command", "").strip()
    state = sessions.get(session_id)
    if not state:
        return {"text": "Invalid session."}

    cwd = state["cwd"]
    text = ""

    if cmd == "ls":
        text = list_dir(cwd)
    elif cmd.startswith("cd "):
        arg = cmd.split(maxsplit=1)[1]
        if arg == "..":
            if cwd:
                cwd.pop()
            text = list_dir(cwd)
        elif arg == "/":
            state["cwd"] = []
            text = list_dir(state["cwd"])
        else:
            node = get_node(cwd)
            child = node.get("children", {}).get(arg) if node else None
            if child and child.get("type") == "dir":
                cwd.append(arg)
                text = list_dir(cwd)
            else:
                text = "Not a directory."
    elif cmd == "pwd":
        text = "/" + "/".join(cwd)
    elif cmd.startswith("cat "):
        filename = cmd.split(maxsplit=1)[1]
        node = get_node(cwd)
        child = node.get("children", {}).get(filename) if node else None
        if child and child.get("type") == "file":
            text = child.get("content", "")
        else:
            text = "No such file."
    elif cmd == "help":
        text = "Commands: ls, cd <dir>, cd .., pwd, cat <file>, help"
    else:
        text = "Unknown command."

    return {"text": text}

