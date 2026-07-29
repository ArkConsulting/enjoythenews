# enjoythenews — current state

Live positive-news aggregator (FastAPI + SQLite, stdlib `sqlite3`), deployed on
Hetzner. Also the dogfood test case for a Lovable-like app-generation system and
the `agent/` agent loop (`uvicorn agent.main:app --port 8766`, powers `/edit/chat`).
Architecture, conventions, and versioning are documented in CLAUDE.md — it is
deliberately the repo's **only** top-level doc (no README, now stated in its intro).

## Where things stand
- Feed fetching: bounded 10s timeout (`FEED_TIMEOUT`, module constant) via stdlib
  `urllib`, bytes handed to `feedparser.parse()` — never a URL. Now documented in
  CLAUDE.md; detailed rationale lives as code comments at `feeds.py:15-26`.
- `DB_PATH` is absolute, anchored to `db.py`'s directory — app works from any cwd;
  DB file stays at repo root. CLAUDE.md updated accordingly (stale claims removed).
- **MEMORY-PROPOSALS.md is empty** — the 2026-07-15 graduation run folded both
  pending bullets (no-README rule, feedparser timeout constraint) into CLAUDE.md.

## Key decisions (recent runs)
- Feedparser learning NOT lifted to `patterns/`: no other workspace app uses RSS.
  Candidate to lift if a second app ever fetches feeds.
- CLAUDE.md carries only the concise always-on constraint; code comments remain
  the detailed reference (avoids duplicating rationale in two places).

## Known constraints
- Tailwind via CDN (dev only).
- No background scheduler — articles fetched at startup and manual `/refresh` only.

## Open threads
- **Stale CLAUDE.md claim:** Architecture says `feeds.py` "returns plain dicts",
  but it actually returns `models.Article` instances (`feeds.py:40-60`,
  `models.py`). Out of scope for the graduation run; needs a memory proposal or
  human edit.
- `./.fun/check` verified layer 1 only (py_compile) in the last run; the
  network-less GET / smoke was skipped because app deps weren't importable in
  that environment. Full check unverified since.

<!-- folded-through: 20260715-171639 -->
