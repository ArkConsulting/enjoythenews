# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language

All file content (code, comments, templates, config) must be written in English, regardless of the language used in the prompt.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (must be run from project root)
uvicorn main:app --reload --port 8765

# Quick smoke test without a running server
python3 -c "from fastapi.testclient import TestClient; from main import app; r = TestClient(app).get('/'); print(r.status_code, len(r.text))"
```

## Architecture

Three flat modules + Jinja2 templates. No subdirectory nesting.

**Request flow:**
1. `main.py` — FastAPI routes. On startup: `db.init()` then `feeds.fetch_all()` → `db.upsert_articles()`. The `/refresh` POST endpoint repeats this on demand.
2. `feeds.py` — Fetches RSS from three hardcoded sources (`SOURCES` list) using `feedparser`. Returns plain dicts with keys: `title`, `link`, `summary`, `published`, `author`, `source`.
3. `db.py` — SQLite via stdlib `sqlite3` (not async). Single table `articles` with `UNIQUE` on `link` for deduplication. `DB_PATH = "enjoythenews.db"` is relative, so the server must be started from project root.

**Frontend pattern:**
- `templates/base.html` — full page shell with Tailwind CDN and Htmx CDN loaded
- `templates/index.html` — extends base; renders source filter tabs + `#article-list` div
- `templates/partials/articles.html` — renders article cards + "Last flere" button; used both by full-page render (via `{% include %}`) and by the Htmx `/articles` GET endpoint for infinite scroll

Htmx "Last flere" swaps `beforeend` into `#article-list` using `GET /articles?offset=N&source=X`. The partial only renders the button when exactly 30 articles are returned (signals more may exist).

## Adding news sources

Edit `SOURCES` in `feeds.py`. Each source needs `name` and `url` (RSS). The source name is used as a filter key in the UI and as a color key in `templates/partials/articles.html` (`source_colors` dict) — add a color entry there too.

## Known constraints

- `DB_PATH` is relative — always start uvicorn from the project root, not a subdirectory.
- Tailwind is loaded via CDN (fine for development; switch to CLI build for production).
- No background scheduler — articles are only fetched at startup and on manual refresh.
