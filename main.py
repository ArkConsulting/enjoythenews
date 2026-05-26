from collections.abc import AsyncGenerator
from datetime import datetime, timezone
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import httpx
from pydantic import BaseModel
import ai
import db
import feeds
import tools.version as version

app = FastAPI()
templates = Jinja2Templates(directory="src")

TEMPLATE_PATH = Path("src/index.html")
UNDO_BUFFER_PATH = TEMPLATE_PATH.with_suffix(".undo_buffer")
AGENT_URL = "http://localhost:8766/chat"
EDITOR_SYSTEM = """You are editing a Jinja2 HTML template for a positive news aggregator called Horisonten.

Rules:
- Preserve all Jinja2 syntax exactly: {{ }}, {% %}, {# #}
- If making changes, end your response with the complete updated file in a fenced html code block.
- Never return partial files or diffs — always the full file.
- If no change is needed, respond conversationally with no code block."""


class ChatRequest(BaseModel):
    message: str


def _timeago(value: str) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value)
        diff = datetime.now(timezone.utc) - dt
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                return "Akkurat nå"
            return f"{hours} time{'r' if hours != 1 else ''} siden"
        if diff.days == 1:
            return "I går"
        if diff.days < 7:
            return f"{diff.days} dager siden"
        return dt.strftime("%-d. %b %Y")
    except Exception:
        return value or ""


templates.env.filters["timeago"] = _timeago


@app.on_event("startup")
def startup():
    db.init()
    _do_refresh()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    articles = db.get_articles(limit=30)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
    })


@app.post("/refresh", response_class=HTMLResponse)
def refresh(request: Request):
    new_count = _do_refresh()
    articles = db.get_articles(limit=30)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "flash": f"{new_count} nye artikler hentet",
    })


@app.get("/edit", response_class=HTMLResponse)
def edit(request: Request):
    return templates.TemplateResponse("edit.html", {
        "request": request,
        "current": version.current_tag(),
        "next_tag": version.next_tag(),
        "tags": version.list_tags(),
        "has_undo": UNDO_BUFFER_PATH.exists(),
    })


@app.post("/edit/chat")
async def edit_chat(body: ChatRequest):
    file_content = TEMPLATE_PATH.read_text()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Current template:\n\n```html\n{file_content}\n```", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": body.message},
            ],
        }
    ]
    return StreamingResponse(
        _proxy_agent(messages, EDITOR_SYSTEM),
        media_type="text/event-stream",
    )


async def _proxy_agent(messages: list[dict], system: str) -> AsyncGenerator[str, None]:
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", AGENT_URL, json={"messages": messages, "system": system}) as resp:
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                event = json.loads(line[6:])
                if event["type"] == "done" and event.get("new_content"):
                    UNDO_BUFFER_PATH.write_text(TEMPLATE_PATH.read_text())
                    TEMPLATE_PATH.write_text(event["new_content"])
                    yield f"data: {json.dumps({'type': 'done', 'changed': True, 'message': event['message']})}\n\n"
                elif event["type"] == "done":
                    yield f"data: {json.dumps({'type': 'done', 'changed': False, 'message': event['message']})}\n\n"
                else:
                    yield line + "\n\n"


@app.post("/edit/undo")
def edit_undo():
    if not UNDO_BUFFER_PATH.exists():
        return {"undone": False}
    previous = UNDO_BUFFER_PATH.read_text()
    UNDO_BUFFER_PATH.write_text(TEMPLATE_PATH.read_text())
    TEMPLATE_PATH.write_text(previous)
    return {"undone": True}


@app.post("/edit/publish")
def edit_publish():
    version.publish()
    return RedirectResponse("/edit", status_code=303)


@app.post("/edit/rollback/{tag}")
def edit_rollback(tag: str):
    version.rollback(tag)
    return RedirectResponse("/edit", status_code=303)


def _do_refresh() -> int:
    raw = feeds.fetch_all()
    new_only = db.filter_new(raw)
    if not new_only:
        return 0
    classified = ai.classify(new_only)
    return db.upsert_articles(classified)
