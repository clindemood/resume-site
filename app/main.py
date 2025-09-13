import json
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Load room data
ROOMS_PATH = Path(__file__).parent / "rooms.json"
with ROOMS_PATH.open() as f:
    rooms = json.load(f)

# Serve static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# In-memory session store
sessions: dict[str, dict] = {}

def describe_room(key: str) -> str:
    room = rooms[key]
    exits = ", ".join(room.get("exits", {}).keys())
    return f"{room['name']}\n{room['description']}\nExits: {exits}"

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

@app.get("/api/start")
def start():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"current_room": "entrance", "inventory": []}
    return {"session_id": session_id, "text": describe_room("entrance")}

@app.post("/api/command")
async def command(payload: dict):
    session_id = payload.get("session_id")
    cmd = payload.get("command", "").strip().lower()
    state = sessions.get(session_id)
    if not state:
        return {"text": "Invalid session."}

    current = state["current_room"]
    text = ""

    if cmd in {"look", "l"}:
        text = describe_room(current)
    elif cmd.startswith("go "):
        direction = cmd.split(maxsplit=1)[1]
        destination = rooms[current]["exits"].get(direction)
        if destination:
            state["current_room"] = destination
            text = describe_room(destination)
        else:
            text = "You can't go that way."
    elif cmd in {"inventory", "i"}:
        inv = state["inventory"]
        text = "You are carrying: " + (", ".join(inv) if inv else "nothing.")
    elif cmd == "help":
        text = "Commands: look, go <direction>, inventory, map, examine <item>"
    elif cmd == "map":
        text = "Rooms: " + ", ".join(room["name"] for room in rooms.values())
    elif cmd.startswith("examine "):
        item = cmd.split(maxsplit=1)[1]
        text = f"You see nothing special about the {item}."
    else:
        text = "Unknown command."

    return {"text": text}

