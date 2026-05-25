from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import ai
import db
import feeds

app = FastAPI()
templates = Jinja2Templates(directory="src")


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


def _do_refresh() -> int:
    raw = feeds.fetch_all()
    new_only = db.filter_new(raw)
    if not new_only:
        return 0
    classified = ai.classify(new_only)
    return db.upsert_articles(classified)
