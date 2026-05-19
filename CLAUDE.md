# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Philosophy

Prefer the simplest solution that works. Avoid frameworks, abstractions, and dependencies unless they solve a concrete problem. A flat file beats a database, a shell script beats a service, stdlib beats a library.

## Language

All file content (code, comments, templates, config) must be written in English, regardless of the language used in the prompt.

## Deleting files

Never delete files with rm. Move them to archive/ instead:
```bash
mv somefile.py archive/
```
This keeps files recoverable without relying on git history.

## External actions

Always ask for confirmation before actions that affect external systems: GitHub, git push, deployments, external APIs, and anything that cannot be undone locally.

## What we are building

This repo serves two purposes in parallel:

**1. enjoythenews** — a live positive news aggregator (FastAPI + Htmx + SQLite), deployed on Hetzner.

**2. A Lovable-like app generation system** — built incrementally as reusable tooling alongside enjoythenews. Three components:

### designs/
Design exploration sandbox. Self-contained HTML files — one per variant, no shared code, no dependencies. Organised by site category then variant:
```
designs/
└── news/
    ├── minimal/index.html
    ├── magazine/index.html
    └── dark/index.html
```
Each `index.html` is a complete, browser-openable file with hardcoded example content and Tailwind CDN. These are drafts — not connected to FastAPI. When a design is approved, it is manually converted to Jinja2 templates and moved to `src/`.

AI workflow: give Claude an existing `index.html` as few-shot context, then prompt for a variant. One file = full context = better output.

### ops/
General-purpose shell scripts for infrastructure and deployment. Not specific to enjoythenews — parameterised so they work for any app on any Hetzner server.
```
ops/
├── server-setup.sh    # install dependencies, clone repo, configure systemd + nginx
├── deploy.sh          # git pull + restart service on remote server
├── ssl-setup.sh       # Certbot SSL for a domain
└── server-status.sh   # check service status and logs
```

### Versioning strategy
App versions are git tags (`v1`, `v2`, `v3`). Git is used programmatically as the versioning engine — efficient storage (diffs only), built-in diff, log, and checkout. Future GUI reads `git log` to list versions, checks out to a temp directory for preview, and uses `git checkout <tag>` for rollback. Do not implement a parallel manual folder-based versioning system.

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
- `src/base.html` — full page shell with Tailwind CDN and Htmx CDN loaded
- `src/index.html` — extends base; renders source filter tabs + `#article-list` div
- `src/partials/articles.html` — renders article cards + "Last flere" button; used both by full-page render (via `{% include %}`) and by the Htmx `/articles` GET endpoint for infinite scroll

Htmx "Last flere" swaps `beforeend` into `#article-list` using `GET /articles?offset=N&source=X`. The partial only renders the button when exactly 30 articles are returned (signals more may exist).

## Adding news sources

Edit `SOURCES` in `feeds.py`. Each source needs `name` and `url` (RSS). The source name is used as a filter key in the UI and as a color key in `src/partials/articles.html` (`source_colors` dict) — add a color entry there too.

## Known constraints

- `DB_PATH` is relative — always start uvicorn from the project root, not a subdirectory.
- Tailwind is loaded via CDN (fine for development; switch to CLI build for production).
- No background scheduler — articles are only fetched at startup and on manual refresh.
