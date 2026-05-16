from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import db
import feeds

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    db.init()
    _do_refresh()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, source: str | None = None):
    articles = db.get_articles(limit=30, source=source)
    sources = db.get_sources()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "sources": sources,
        "active_source": source,
    })


@app.get("/articles", response_class=HTMLResponse)
def load_more(
    request: Request,
    offset: int = Query(0),
    source: str | None = Query(None),
):
    articles = db.get_articles(limit=30, offset=offset, source=source)
    return templates.TemplateResponse("partials/articles.html", {
        "request": request,
        "articles": articles,
        "offset": offset + 30,
        "source": source,
    })


@app.post("/refresh", response_class=HTMLResponse)
def refresh(request: Request):
    new_count = _do_refresh()
    articles = db.get_articles(limit=30)
    sources = db.get_sources()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "sources": sources,
        "active_source": None,
        "flash": f"{new_count} nye artikler hentet",
    })


def _do_refresh() -> int:
    articles = feeds.fetch_all()
    return db.upsert_articles(articles)
