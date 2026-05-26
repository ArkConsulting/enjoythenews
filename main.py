from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import ai
import db
import feeds
import tools.editor as editor
import tools.version as version

app = FastAPI()
templates = Jinja2Templates(directory="src")

TEMPLATE_PATH = Path("src/index.html")


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
    })


@app.post("/edit/chat")
def edit_chat(body: ChatRequest):
    file_content = TEMPLATE_PATH.read_text()
    result = editor.chat(body.message, file_content)
    if result.new_content is not None:
        TEMPLATE_PATH.write_text(result.new_content)
    return {"message": result.message, "changed": result.new_content is not None}


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
