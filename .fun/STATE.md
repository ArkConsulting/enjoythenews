# enjoythenews — current state

Live positive-news aggregator (FastAPI + SQLite, stdlib `sqlite3`), deployed on
Hetzner. Also the dogfood test case for a Lovable-like app-generation system and
the `agent/` agent loop (`uvicorn agent.main:app --port 8766`, powers `/edit/chat`).
Architecture, conventions, and versioning are documented in CLAUDE.md — it is
deliberately the repo's **only** top-level doc (no README, stated in its intro).

## Where things stand
- Feed fetching: bounded 10s timeout (`FEED_TIMEOUT`, module constant) via stdlib
  `urllib`, bytes handed to `feedparser.parse()` — never a URL. Documented in
  CLAUDE.md; detailed rationale lives as code comments at `feeds.py:15-26`.
- `DB_PATH` is absolute, anchored to `db.py`'s directory — app works from any cwd;
  DB file stays at repo root.
- **MEMORY-PROPOSALS.md is empty** — the 2026-07-15 graduation run folded both
  pending bullets (no-README rule, feedparser timeout constraint) into CLAUDE.md.
- Run 20260730-084401 was a harness smoke test (created a one-line README on
  explicit request); its artifacts were archived afterward — repo back to the
  no-README rule.

## Key decisions (recent runs)
- Feedparser learning NOT lifted to `patterns/`: no other workspace app uses RSS.
  Candidate to lift if a second app ever fetches feeds.
- CLAUDE.md carries only the concise always-on constraint; code comments remain
  the detailed reference (avoids duplicating rationale in two places).

## Open threads
- **Stale CLAUDE.md claim:** Architecture says `feeds.py` "returns plain dicts",
  but it returns `models.Article` instances (`feeds.py:40-60`, `models.py`).
  Needs a memory proposal or human edit.
- `./.fun/check` keeps passing on layer 1 only (py_compile); layer 2 (no-network
  GET / smoke) skipped in the last two runs — app deps not importable there.

<!-- folded-through: 20260730-084401 -->
