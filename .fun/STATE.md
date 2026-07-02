# enjoythenews — current state

Live positive-news aggregator (FastAPI + SQLite, stdlib `sqlite3`), deployed on
Hetzner. Also the dogfood test case for a Lovable-like app-generation system and
the `agent/` agent loop.

## Architecture (as documented in CLAUDE.md)
- Three flat modules: `main.py` (routes, startup fetch, `/refresh`), `feeds.py`
  (RSS from hardcoded `SOURCES` via feedparser), `db.py` (single `articles`
  table, `UNIQUE` on `link`).
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

## Feed fetching
- Each RSS source is fetched with a bounded **10s timeout** (`FEED_TIMEOUT`) via
  stdlib `urllib.request.urlopen`, then handed to `feedparser.parse()` as bytes
  (feedparser is now a pure parser, no network). Stdlib-first — no `requests`,
  threads, or signals. One slow/unreachable feed is logged and skipped; the rest
  still populate the DB. Timeout is a module constant, not env-configurable.

## Database path
- `DB_PATH` is now absolute, anchored to `db.py`'s directory via
  `str(Path(__file__).resolve().parent / "enjoythenews.db")`. The app works from
  any cwd; the DB file stays at repo root (where `db.py` lives). Kept as `str`,
  `.resolve()`'d for a normalized path.

## Known constraints
- Tailwind via CDN (dev only).
- No background scheduler — articles fetched at startup and manual `/refresh` only.

## Open threads
- CLAUDE.md still says uvicorn must run from repo root (Architecture line +
  "Known constraints" `DB_PATH` bullet) — now stale after the cwd-independent
  fix. Flagged in MEMORY-PROPOSALS.md; a human must edit CLAUDE.md (off-limits
  to agents).
- **No README exists** anywhere in this repo. A 2026-07-02 proofread found
  nothing to do; docs live in `CLAUDE.md`. Create one only if deliberately wanted.

<!-- folded-through: 20260702-175724 -->
