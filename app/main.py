"""Minimal resume API with basic open/show navigation."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "resume.json"

with DATA_PATH.open() as f:
    RESUME: Dict[str, Any] = json.load(f)


def get_last_updated() -> str:
    git = shutil.which("git")
    if git:
        try:
            result = subprocess.run(
                [git, "log", "-1", "--format=%cs", str(DATA_PATH)],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, OSError):
            pass
    return datetime.fromtimestamp(DATA_PATH.stat().st_mtime).strftime("%Y-%m-%d")


RESUME.setdefault("meta", {})["last_updated"] = get_last_updated()

STATIC_DIR = APP_DIR / "static"

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

ITEMS_PER_PAGE = 5


def format_date(value: str | None, short: bool = False) -> str:
    if not value:
        return "Present"
    try:
        dt = datetime.strptime(value, "%Y-%m")
        month, day = dt.month, 1
    except ValueError:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            month, day = dt.month, dt.day
        except ValueError:
            return value
    year = dt.year % 100 if short else dt.year
    return f"{month}/{day}/{year}"


def strip_scheme(url: str | None) -> str:
    if not url:
        return ""
    url = url.replace("https://", "").replace("http://", "")
    if url.startswith("www."):
        url = url[4:]
    return url


def format_overview() -> str:
    o = RESUME.get("overview", {})
    lines = [
        f"Name: {o.get('name')} | {o.get('title')} | {o.get('location')}",
        (
            f"Email: {o.get('email')} | Web: {strip_scheme(o.get('web'))} | "
            f"LinkedIn: {strip_scheme(o.get('linkedin'))} | GitHub: {strip_scheme(o.get('github'))}"
        ),
        f"Summary: {o.get('summary')}",
    ]
    return "\n".join(lines)


def render_details(section: str, item: Dict[str, Any]) -> str:
    if section == "experience":
        lines = [
            f"Company: {item['company']}",
            f"Role: {item['role']}",
            f"Dates: {format_date(item['start'])} - {format_date(item.get('end'), True)}",
            "Highlights:",
        ]
        lines.extend([f"- {b}" for b in item.get("bullets", [])])
        if tech := item.get("tech"):
            lines.append("Tech: " + ", ".join(tech))
        return "\n".join(lines)
    if section == "projects":
        lines = [f"Name: {item['name']}"]
        if start := item.get("start"):
            lines.append(f"Date: {format_date(start)}")
        lines.append(f"Role: {item.get('role', '')}")
        if repo := item.get("repo"):
            lines.append(f"Repo: {repo}")
        if tech := item.get("tech"):
            lines.append("Tech: " + ", ".join(tech))
        if bullets := item.get("bullets"):
            lines.append("Details:")
            lines.extend([f"- {b}" for b in bullets])
        if outcome := item.get("outcome"):
            lines.append(f"Outcome: {outcome}")
        return "\n".join(lines)
    if section == "skills":
        return f"{item['name']} ({item.get('level')})"
    if section == "education":
        return f"{item['degree']} at {item['institution']} ({item['year']})"
    if section == "certifications":
        parts = [item.get("name", "")]
        details = []
        if issuer := item.get("issuer"):
            details.append(issuer)
        if issued := item.get("issued"):
            details.append(f"Issued {format_date(issued)}")
        if expires := item.get("expires"):
            details.append(f"Expires {format_date(expires)}")
        if cred := item.get("credential_id"):
            details.append(f"ID {cred}")
        if details:
            parts.append(" – " + " · ".join(details))
        return "".join(parts)
    return ""


def list_section(section: str, *, expand: bool = False, page: int = 1) -> str:
    items: List[Dict[str, Any]] = RESUME.get(section, [])
    if not isinstance(items, list):
        if section == "overview":
            return format_overview()
        raise HTTPException(status_code=404, detail="Unknown section")

    total_pages = max(1, (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = items[start:end]

    lines: List[str] = []
    for idx, item in enumerate(page_items, start=start + 1):
        if section == "experience":
            base = (
                f"[{idx}] {item['company']} | {item['role']} | "
                f"{format_date(item['start'])} - {format_date(item.get('end'), True)} | {item['location']}"
            )
        elif section == "projects":
            if item.get("start"):
                base = f"[{idx}] {format_date(item['start'])} - {item['name']}"
            else:
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
    lines.append(f"Page {page}/{total_pages}")
    return "\n".join(lines)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/resume")
def get_resume() -> Dict[str, Any]:
    return RESUME


@app.get("/api/open/{section}")
def api_open(section: str, expand: bool = False, page: int = 1) -> Dict[str, str]:
    text = list_section(section, expand=expand, page=page)
    return {"text": text}


@app.get("/api/show/{section}/{item_id}")
def api_show(section: str, item_id: int) -> Dict[str, str]:
    items = RESUME.get(section, [])
    if not isinstance(items, list) or item_id < 1 or item_id > len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    text = render_details(section, items[item_id - 1])
    return {"text": text}
