# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Three things being built simultaneously

This repo is three projects at once. Always keep all three in mind when suggesting approaches:

**1. enjoythenews** — a live positive news aggregator published on the internet (FastAPI + Htmx + SQLite, deployed on Hetzner). Real users, real traffic. Changes here have immediate consequences.

**2. A Lovable-like app generation system** — a platform for generating and iterating on web apps via AI. enjoythenews is both the test case and the first app built with it. Every tool we create here should work for any app, not just enjoythenews.

**3. An agent loop** (`agent/`) — a CLI agent in the spirit of Claude Code and GitHub Copilot CLI. Powers the Lovable system's orchestration layer. Built to be model-agnostic: routes tasks between local models (Ollama) and cloud models (Anthropic API) via LiteLLM. Designed for experimentation with memory, routing, and model selection.

The three reinforce each other: enjoythenews validates the Lovable system, the Lovable system uses the agent loop, and the agent loop is dogfooded while building enjoythenews.

## Core principle: dogfooding

We are building the Lovable-like app generation system *by using it* to build enjoythenews. This means we are simultaneously the producer and the user of the system. Every tool, workflow, and convention we establish gets real-world validation immediately.

Practical consequence: when suggesting how to build a Lovable feature, always frame it in terms of how it would work for enjoythenews first. If it doesn't solve a real problem we have right now, it's premature. enjoythenews is the test case — not a demo, not a toy.

## Philosophy

Prefer the simplest solution that works. Avoid frameworks, abstractions, and dependencies unless they solve a concrete problem. A flat file beats a database, a shell script beats a service, stdlib beats a library.

## Updating this file

When we have discussed an approach and reached agreement on a smart solution, suggest updating CLAUDE.md to capture the decision. Do not update silently — propose the addition and get confirmation first.

## Language

All content must be written in English: code, comments, templates, config, and documentation including CLAUDE.md updates. The user writes in Norwegian — responses and conversation can be in Norwegian, but everything written to files must be in English. This keeps the codebase readable, searchable, and shareable regardless of audience.

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

**2. A Lovable-like app generation system** — built incrementally as reusable tooling alongside enjoythenews. Four components:

### ops/
General-purpose shell scripts for infrastructure and deployment. Not specific to enjoythenews — parameterised so they work for any app on any Hetzner server.
```
ops/
├── server-setup.sh    # install dependencies, clone repo, configure systemd + nginx
├── deploy.sh          # git pull + restart service on remote server
├── ssl-setup.sh       # Certbot SSL for a domain
└── server-status.sh   # check service status and logs
```
These stay as shell scripts because they run on remote servers where the project's Python environment may not exist yet (server-setup.sh *installs* the environment). Shell is the native language of systemctl, nginx, apt, and SSH.

### tools/
Small, self-contained Python modules that the LLM orchestrator calls as discrete tools. Each module does exactly one thing and is usable independently of any LLM. Default to Python — it is consistent with the rest of the codebase, readable by any model, and callable directly from main.py without subprocess indirection. Only use shell if the tool must run outside the Python environment.
```
tools/generate.py     # produce a template from designs/ + user prompt
tools/version.py      # create, list, or check out git tags
tools/preview.py      # start a preview server for a specific version
```
The division of responsibility is strict: **tools execute, Claude understands intent**. A tool never tries to interpret the user's goal; Claude never tries to do what a tool should handle. New capability = new tool. Claude immediately gains access to it without any wiring.

**Model sizing:** use the cheapest model that reliably handles the task. Claude Haiku (or similar small models) for well-defined batch work (e.g. article classification). Large Claude for orchestration, ambiguity resolution, and code generation. Local LLMs are a future optimisation — do not add that complexity until API cost is a real constraint.

### designs/
Design exploration sandbox — also the AI's reference library for generating new apps. Self-contained HTML files — one per variant, no shared code, no dependencies. Organised by site category then variant:
```
designs/
└── news/
    ├── minimal/index.html
    ├── magazine/index.html
    ├── dark/index.html
    ├── horizon/index.html
    └── stripe/index.html
```
Each `index.html` is a complete, browser-openable file with hardcoded example content and Tailwind CDN. These are drafts — not connected to FastAPI. When a design is approved, it is manually converted to Jinja2 templates and moved to `src/`.

AI workflow: give Claude an existing `index.html` as few-shot context, then prompt for a variant. One file = full context = better output. The more variants in `designs/`, the better the generator becomes.

In a Lovable-like flow the user never touches `designs/` — they interact with the live app in `src/`, and `designs/` serves as the template bank Claude draws from when generating.

### Versioning strategy
App versions are git tags (`v1`, `v2`, `v3`). Git is the versioning engine — efficient storage, built-in diff, log, and rollback. Do not implement a parallel manual folder-based versioning system.

There is one `src/` directory. Tags are checkpoints, not parallel deployments. Production always runs `HEAD` of `main`.

**Deploy flow:**
```
[Edit environment]              [Production / Hetzner]

  Make changes in src/
  Preview locally
  "Publish" →
    git commit
    git tag v3
    git push            →→→    git pull + systemctl restart
```

**Rollback:** `git checkout v2 -- src/` + commit + push + pull. Do not check out the entire repo to an old tag in production.

**Edit environment:** the `/edit` page is where new versions are created. The first implementation is prompt-based — the user describes a change, Claude updates `src/`, and the user can preview before publishing. Direct in-browser code editing is a later addition.

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
