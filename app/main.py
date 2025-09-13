"""Interactive resume CLI backend.

This module implements a small web API used by a browser based
"terminal".  It exposes a handful of endpoints that provide the
behaviour of the command set described in the user instructions.
The implementation is intentionally lightweight; the goal is to
provide an approachable demonstration rather than a fully fledged
resume management system.
"""

from __future__ import annotations

import json
import shlex
import uuid
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "resume.json"

with DATA_PATH.open() as f:
    RESUME: Dict[str, Any] = json.load(f)

STATIC_DIR = APP_DIR / "static"

# ---------------------------------------------------------------------------
# FastAPI setup
# ---------------------------------------------------------------------------

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

# Each session keeps track of the current section view, pagination state,
# and auxiliary data such as expanded items or user notes.
sessions: Dict[str, Dict[str, Any]] = {}

ITEMS_PER_PAGE = 3

# ---------------------------------------------------------------------------
# Helper formatting utilities
# ---------------------------------------------------------------------------

def format_overview() -> str:
    o = RESUME.get("overview", {})
    lines = [
        f"Name: {o.get('name')} | {o.get('title')} | {o.get('location')}",
        f"Email: {o.get('email')} | Web: {o.get('web')} | LinkedIn: {o.get('linkedin')}",
        f"Summary: {o.get('summary')}",
    ]
    return "\n".join(lines)


def list_section(state: Dict[str, Any], section: str, *, expand: bool = False, page: int = 1) -> str:
    """Return a textual representation for ``section``.

    The state is updated with pagination information so that commands like
    ``next``/``prev`` can operate on the last view.
    """

    items: List[Dict[str, Any]] = RESUME.get(section, [])
    if not isinstance(items, list):
        if section == "overview":
            state["current_section"] = section
            state["last_items"] = {}
            state["page"] = 1
            return format_overview()
        return "Unknown section."

    total_pages = max(1, (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = items[start:end]

    state["current_section"] = section
    state["page"] = page
    state["last_items"] = {str(i): item for i, item in enumerate(page_items, start=start + 1)}

    lines: List[str] = []
    for idx, item in state["last_items"].items():
        if section == "experience":
            base = f"[{idx}] {item['company']} | {item['role']} | {item['start']}–{item.get('end', 'Present')} | {item['location']}"
        elif section == "projects":
            base = f"[{idx}] {item['name']}"
        elif section == "skills":
            base = f"[{idx}] {item['name']} ({item.get('level')})"
        elif section == "education":
            base = f"[{idx}] {item['institution']} | {item['degree']} | {item['year']}"
        else:
            base = f"[{idx}] {item.get('name', 'item')}"
        lines.append(base)
        if expand:
            lines.append(render_details(section, item))
    lines.append(f"Page {page}/{total_pages} • use 'show <id>' or 'expand <id>'")
    return "\n".join(lines)


def render_details(section: str, item: Dict[str, Any]) -> str:
    if section == "experience":
        lines = [
            f"Company: {item['company']}",
            f"Role: {item['role']}",
            f"Dates: {item['start']} → {item.get('end', 'Present')}",
            "Highlights:",
        ]
        lines.extend([f"- {b}" for b in item.get("bullets", [])])
        if tech := item.get("tech"):
            lines.append("Tech: " + ", ".join(tech))
        return "\n".join(lines)
    if section == "projects":
        lines = [f"Name: {item['name']}", f"Role: {item['role']}" ]
        if repo := item.get("repo"):
            lines.append(f"Repo: {repo}")
        if tech := item.get("tech"):
            lines.append("Tech: " + ", ".join(tech))
        if outcome := item.get("outcome"):
            lines.append(f"Outcome: {outcome}")
        return "\n".join(lines)
    if section == "skills":
        return f"{item['name']} ({item.get('level')})"
    if section == "education":
        return f"{item['degree']} at {item['institution']} ({item['year']})"
    if section == "certifications":
        return item.get("name", "")
    return ""


def search_resume(query: str, section: str | None = None) -> List[str]:
    query = query.lower()
    sections = [section] if section else [k for k, v in RESUME.items() if isinstance(v, list)]
    results: List[str] = []
    for sec in sections:
        items = RESUME.get(sec, [])
        for item in items:
            blob = json.dumps(item).lower()
            if query in blob:
                label = item.get("company") or item.get("name") or str(item.get("id"))
                results.append(f"[{sec}] {label}")
    return results

# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def handle_command(state: Dict[str, Any], cmd: str) -> Dict[str, Any]:
    """Return response dict for ``cmd`` executed in ``state``."""

    if not cmd:
        return {"text": ""}

    parts = shlex.split(cmd)
    command = parts[0]
    args = parts[1:]

    # Allow using just the numeric id to show an item
    if command.isdigit() and not args:
        item = state.get("last_items", {}).get(command)
        if not item:
            return {"text": "Unknown id."}
        section = state.get("current_section")
        return {"text": render_details(section, item)}

    # Basic navigation -----------------------------------------------------
    if command == "help":
        return {"text": HELP_TEXT if not args else COMMAND_HELP.get(args[0], "No help available.")}

    if command == "open" and args:
        section = args[0]
        expand = "--expand" in args
        page = 1
        if "--page" in args:
            try:
                idx = args.index("--page")
                page = int(args[idx + 1])
            except (ValueError, IndexError):
                pass
        text = list_section(state, section, expand=expand, page=page)
        state.setdefault("history", []).append(cmd)
        return {"text": text}

    if command == "show" and args:
        item = state.get("last_items", {}).get(args[0])
        if not item:
            return {"text": "Unknown id."}
        section = state.get("current_section")
        return {"text": render_details(section, item)}

    if command in {"next", "prev"}:
        section = state.get("current_section")
        if not section:
            return {"text": "Nothing to paginate."}
        page = state.get("page", 1) + (1 if command == "next" else -1)
        text = list_section(state, section, page=page)
        return {"text": text}

    if command == "back":
        hist = state.get("history", [])
        if len(hist) > 1:
            hist.pop()  # remove current
            prev = hist.pop()
            return handle_command(state, prev)
        state.clear()
        return {"text": ""}

    # Discovery -----------------------------------------------------------
    if command == "search" and args:
        section = None
        if "--in" in args:
            try:
                idx = args.index("--in")
                section = args[idx + 1]
            except IndexError:
                pass
        query = args[0]
        hits = search_resume(query, section)
        if not hits:
            return {"text": "No matches."}
        return {"text": "\n".join(hits)}

    if command == "filter" and args:
        # Very small filter implementation: filter <section> field=value
        sec = args[0] if args[0] in RESUME else state.get("current_section")
        exprs = args[1:] if sec == args[0] else args
        items = RESUME.get(sec, [])
        if not isinstance(items, list):
            return {"text": "Unknown section."}
        results = items
        for expr in exprs:
            if "=" in expr:
                field, value = expr.split("=", 1)
                field = field.strip()
                value = value.strip()
                results = [i for i in results if str(i.get(field, "")).lower() == value.lower()]
        lines = []
        for item in results:
            label = item.get("company") or item.get("name")
            lines.append(label)
        return {"text": "Matches: " + ", ".join(lines) if lines else "No matches."}

    if command == "timeline":
        sec = "experience"
        if "--section" in args:
            try:
                idx = args.index("--section")
                sec = args[idx + 1]
            except IndexError:
                pass
        items = RESUME.get(sec, [])
        lines = [
            " → ".join(
                f"{i.get('start')}–{i.get('end', 'Present')} {i.get('company', i.get('name'))}" for i in items
            )
        ]
        return {"text": "".join(lines)}

    if command == "certifications":
        expand = "--expand" in args
        page = 1
        if "--page" in args:
            try:
                idx = args.index("--page")
                page = int(args[idx + 1])
            except (ValueError, IndexError):
                pass
        text = list_section(state, "certifications", expand=expand, page=page)
        state.setdefault("history", []).append(cmd)
        return {"text": text}

    if command == "skills":
        level = None
        tags: List[str] | None = None
        if "--level" in args:
            try:
                level = args[args.index("--level") + 1]
            except IndexError:
                pass
        if "--tag" in args:
            try:
                tags = [t.strip() for t in args[args.index("--tag") + 1].split(",")]
            except IndexError:
                pass
        skills = RESUME.get("skills", [])
        out = []
        for s in skills:
            if level and s.get("level") != level:
                continue
            if tags and not set(tags) & set(s.get("tags", [])):
                continue
            out.append(f"{s['name']} ({s.get('level')})")
        return {"text": " • ".join(out) if out else "No skills match."}

    if command == "contact":
        o = RESUME.get("overview", {})
        return {"text": f"Email: {o.get('email')} | Phone: (N/A) | Web: {o.get('web')}"}

    if command == "copy" and args:
        field = args[0]
        o = RESUME.get("overview", {})
        value = o.get(field)
        if not value:
            return {"text": "Unknown field."}
        return {"text": f"Copied {field}: {value}"}

    if command == "share":
        return {"text": "Public link: https://example.com/r/jordan-patel/engineering"}

    if command == "download":
        filename = "resume.txt"
        if "--filename" in args:
            try:
                filename = args[args.index("--filename") + 1]
            except IndexError:
                pass
        return {"text": f"Download started: {filename}"}

    if command == "versions":
        versions = RESUME.get("versions", [])
        if "--list" in args or not args:
            return {"text": " • ".join(versions) + f" • last_updated: {RESUME['meta']['last_updated']}"}
        if "--diff" in args:
            return {"text": "Diff not implemented."}

    if command == "tags":
        tags = state.setdefault("tags", {})
        if "--list" in args:
            listing = [f"{k}: {', '.join(v)}" for k, v in tags.items()]
            return {"text": "\n".join(listing) if listing else "No tags."}
        if "--add" in args:
            try:
                idx = args.index("--add")
                id_, tag = args[idx + 1], args[idx + 2]
                tags.setdefault(id_, []).append(tag)
                return {"text": f"Tag '{tag}' added to {id_}."}
            except IndexError:
                return {"text": "Usage: tags --add <id> <tag>"}
        if "--remove" in args:
            try:
                idx = args.index("--remove")
                id_, tag = args[idx + 1], args[idx + 2]
                if tag in tags.get(id_, []):
                    tags[id_].remove(tag)
                return {"text": f"Tag '{tag}' removed from {id_}."}
            except IndexError:
                return {"text": "Usage: tags --remove <id> <tag>"}
        return {"text": "Usage: tags --list|--add|--remove"}

    if command == "notes":
        notes = state.setdefault("notes", {})
        if "--add" in args:
            try:
                idx = args.index("--add")
                id_, text = args[idx + 1], args[idx + 2]
                notes.setdefault(id_, []).append(text)
                return {"text": "Note added."}
            except IndexError:
                return {"text": "Usage: notes --add <id> 'text'"}
        if "--show" in args:
            try:
                idx = args.index("--show")
                id_ = args[idx + 1]
                return {"text": " | ".join(notes.get(id_, [])) or "No notes."}
            except IndexError:
                return {"text": "Usage: notes --show <id>"}
        return {"text": "Usage: notes --add|--show"}

    if command == "print":
        mode = "compact"
        if "--detailed" in args:
            mode = "detailed"
        return {"text": f"Printing in {mode} mode..."}

    if command == "theme" and args:
        theme = args[0]
        state["theme"] = theme
        return {"text": f"Theme set to {theme}."}

    if command == "about":
        meta = RESUME.get("meta", {})
        return {
            "text": f"Resume data from {meta.get('data_source')} • last_updated: {meta.get('last_updated')}"
        }

    if command == "clear":
        return {"text": "", "clear": True}

    if command == "quit":
        return {"text": "Goodbye."}

    return {"text": "Unknown command."}

# ---------------------------------------------------------------------------
# Help text
# ---------------------------------------------------------------------------

HELP_TEXT = (
    "Available commands:\n"
    "  open <section> [--expand] [--page N]  — show a section\n"
    "  show <id> or <id>                    — show an item from the last listing\n"
    "  next | prev                          — paginate through the current section\n"
    "  back                                 — return to previous view\n"
    "  search <query> [--in <section>]      — full-text search\n"
    "  filter [section] field=value         — filter items\n"
    "  timeline                             — show experience timeline\n"
    "  certifications [--expand] [--page N] — list certifications\n"
    "  skills [--level L] [--tag t1,t2]     — list skills\n"
    "  contact                              — show contact info\n"
    "  copy <field>                         — copy a field\n"
    "  share                                — show public link\n"
    "  download [--filename name]           — download resume\n"
    "  versions [--list|--diff]             — resume versions\n"
    "  tags --list|--add|--remove           — manage tags\n"
    "  notes --add|--show                   — manage notes\n"
    "  print [--detailed]                   — print resume\n"
    "  theme <name>                         — set theme\n"
    "  about                                — show resume metadata\n"
    "  clear                                — clear screen\n"
    "  quit                                 — exit the game\n"
    "Type 'help <command>' for more details."
)

COMMAND_HELP = {
    "open": "open <section> [--expand] [--page N] — show a section.",
    "show": "show <id> — open one item by its ID from the last listing. You can also type the id number directly.",
    "search": "search <query> [--in <section>] — full-text search.",
    "certifications": "certifications [--expand] [--page N] — list certifications.",
}

# ---------------------------------------------------------------------------
# HTTP routes
# ---------------------------------------------------------------------------

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


@app.get("/api/resume")
def get_resume() -> Dict[str, Any]:
    return RESUME


@app.get("/api/start")
def start() -> Dict[str, Any]:
    """Start a new CLI session."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {}
    variants = " • ".join(RESUME.get("versions", []))
    text = (
        "Short usage hint: type 'help' or 'open overview'\n"
        f"Last updated: {RESUME['meta']['last_updated']} | Available variants: {variants}"
    )
    return {"session_id": session_id, "text": text}


@app.post("/api/command")
async def command(payload: Dict[str, Any]) -> Dict[str, Any]:
    session_id = payload.get("session_id")
    cmd = payload.get("command", "").strip()
    state = sessions.get(session_id)
    if state is None:
        return {"text": "Invalid session."}
    return handle_command(state, cmd)
