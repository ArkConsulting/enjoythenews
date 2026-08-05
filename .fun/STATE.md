# enjoythenews — current state

Live positive-news aggregator (FastAPI + SQLite, stdlib `sqlite3`), deployed on
Hetzner. Also the dogfood test case for a Lovable-like app-generation system and
the `agent/` agent loop (`uvicorn agent.main:app --port 8766`, powers `/edit/chat`).
Architecture, conventions, and versioning live in CLAUDE.md — deliberately the
repo's **only** top-level doc (no README).

## Where things stand
- **Periodic feed refresh now implemented** (run 20260805-095943, check PASS,
  reviewer/gate LGTM): `main.py` runs `_periodic_refresh()` as an asyncio task
  started at startup, sleeping `REFRESH_INTERVAL` (hourly, constant) before
  each pass, then calling the existing `_do_refresh()` via `asyncio.to_thread`
  so sync urllib/Anthropic work never blocks the event loop; cancelled on a
  new shutdown handler. Sleep-first design means `.fun/check`'s smoke never
  triggers a real network fetch.
- **Two CLAUDE.md rewordings proposed, not yet applied**, in
  MEMORY-PROPOSALS.md: (1) the Frontend-pattern "Backend serves JSON
  endpoints" bullet reworded into a guideline for new endpoints, (2) the
  Known-constraints "No background scheduler" bullet, now stale given the
  refresh feature above. CLAUDE.md itself is untouched (runs must not edit it
  directly) — until `fun memory rules` applies these, CLAUDE.md still
  contradicts the code on background scheduling.
- **`./.fun/check` passes both layers in the container** (run 20260804-140710):
  layer 1 `py_compile` over tracked `.py`, layer 2 self-provisions a deps venv
  and runs the in-process no-network smoke (`GET /` → 200).
- **CLAUDE.md freshly audited** (run 20260731-145043): ~10 stale claims fixed;
  vision/strategy statements left untouched.
- Feed fetching: bounded 10s timeout (`FEED_TIMEOUT`) via stdlib `urllib`,
  bytes handed to `feedparser.parse()` — never a URL. Rationale at
  `feeds.py:15-26`.
- `DB_PATH` is absolute, anchored to `db.py`'s directory — works from any cwd.
- **MEMORY-PROPOSALS.md now holds the two rewordings above** (last graduation
  2026-07-15, then empty until this run).

## Key decisions (recent runs)
- In-process asyncio task chosen over a systemd timer for the refresh: works
  identically in dev/prod, zero ops config, stdlib-only, consistent with the
  no-frameworks philosophy.
- Audit kept CLAUDE.md's safety/gate rules and all vision statements; no git
  tags yet is consistent with the versioning strategy, not a finding.
- Feedparser learning NOT lifted to `patterns/`: no other workspace app uses
  RSS. Candidate to lift if a second app ever fetches feeds.

## Open threads (human calls)
- Apply or reject the two pending MEMORY-PROPOSALS.md rewordings (`fun memory
  rules`).
- **Language rule vs Norwegian UI copy**: templates rule says English, but
  `src/index.html` and `main.py` (`_timeago`) carry Norwegian user-facing copy
  ("Akkurat nå", "I går") — rule may need a user-facing-copy carve-out.
- **`tools/editor.py` appears dead**: nothing imports it; `main.py` duplicates
  its prompt and streams via `agent/`. Archive-or-keep is a human decision.
- `src/index.html` has hardcoded Norwegian demo content in extra tab sections
  (~lines 460-465) alongside the Jinja2 loop — intentional?
- `REFRESH_INTERVAL` is a hardcoded constant (3600s) — make env-configurable
  only if a real need appears.

<!-- folded-through: 20260805-095943 -->
