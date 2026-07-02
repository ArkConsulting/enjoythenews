# enjoythenews — current state

Live positive-news aggregator (FastAPI + SQLite, stdlib `sqlite3`), deployed on
Hetzner. Also the dogfood test case for a Lovable-like app-generation system and
the `agent/` agent loop.

## Architecture (as documented in CLAUDE.md)
- Three flat modules: `main.py` (routes, startup fetch, `/refresh`), `feeds.py`
  (RSS from hardcoded `SOURCES` via feedparser), `db.py` (single `articles`
  table, `UNIQUE` on `link`, relative `DB_PATH` — run uvicorn from repo root).
- Frontend: single self-contained `src/index.html`, Jinja2 + vanilla JS,
  Tailwind CDN. No HTMX, no partials.
- Versioning = git tags (`v1`, `v2`, …); one `src/`, production runs HEAD of main.
- Support tooling: `ops/` (shell deploy scripts), `tools/` (single-purpose Python
  tools), `designs/` (self-contained HTML template bank for the generator).
- `agent/` agent loop served via `uvicorn agent.main:app --port 8766`; powers
  `/edit/chat`.

## Key decisions / conventions
- Simplest-thing-that-works; avoid frameworks/deps without concrete need.
- Never `rm` — move to `archive/`. Ask before external actions (push/deploy/API).
- All file content in English; conversation may be Norwegian.
- Model sizing: cheapest reliable model per task; local LLMs deferred.

## Known constraints
- Relative `DB_PATH` — start uvicorn from project root.
- Tailwind via CDN (dev only).
- No background scheduler — articles fetched at startup and manual `/refresh` only.

## Open threads
- **No README exists** anywhere in this repo (confirmed via `git ls-files`). A
  2026-07-02 proofread run found nothing to do; docs live in `CLAUDE.md`. If a
  README is wanted, it must be created deliberately — or it belongs in a sibling
  app repo / the funai workspace root.

<!-- folded-through: 20260702-152927 -->
