# enjoythenews — current state

Live positive-news aggregator (FastAPI + SQLite, stdlib `sqlite3`), deployed on
Hetzner. Also the dogfood test case for a Lovable-like app-generation system and
the `agent/` agent loop (`uvicorn agent.main:app --port 8766`, powers `/edit/chat`).
Architecture, conventions, and versioning live in CLAUDE.md — deliberately the
repo's **only** top-level doc (no README).

## Where things stand
- **`./.fun/check` now passes BOTH layers in the container** (run
  20260804-140710, check PASS, reviewer LGTM): layer 1 `py_compile` over all
  tracked `.py`, layer 2 self-provisions a deps venv (cached per
  `requirements.txt` hash, allowlisted PyPI hosts) and runs the in-process
  no-network smoke — `GET /` returned 200 with rendered HTML. This closes the
  long-standing "layer 2 honestly skipped" thread; the 2026-08-04
  self-provisioning work is verified end-to-end.
- **CLAUDE.md freshly audited** (run 20260731-145043, check PASS): every claim
  checked against code; ~10 stale claims fixed and a duplicated intro merged.
  Vision/strategy statements left untouched.
- Feed fetching: bounded 10s timeout (`FEED_TIMEOUT`) via stdlib `urllib`,
  bytes handed to `feedparser.parse()` — never a URL. Rationale at
  `feeds.py:15-26`.
- `DB_PATH` is absolute, anchored to `db.py`'s directory — works from any cwd.
- **MEMORY-PROPOSALS.md is empty** (last graduation 2026-07-15).

## Key decisions (recent runs)
- Audit kept CLAUDE.md's safety/gate rules and all vision statements; no git
  tags yet is consistent with the versioning strategy, not a finding.
- Feedparser learning NOT lifted to `patterns/`: no other workspace app uses
  RSS. Candidate to lift if a second app ever fetches feeds.
- CLAUDE.md carries only concise always-on constraints; code comments remain
  the detailed reference.

## Open threads (human calls flagged by the audit)
- **Language rule vs Norwegian UI copy**: templates rule says English, but
  `src/index.html` and `main.py` (`_timeago`) carry Norwegian user-facing copy
  ("Akkurat nå", "I går") — rule may need a user-facing-copy carve-out.
- **`tools/editor.py` appears dead**: nothing imports it; `main.py` duplicates
  its prompt and streams via `agent/`. Archive-or-keep is a human decision.
- `src/index.html` has hardcoded Norwegian demo content in extra tab sections
  (~lines 460-465) alongside the Jinja2 loop — intentional?
- "Backend serves JSON endpoints" reads as guideline, not description (index is
  server-rendered; `/refresh` returns HTML) — consider rewording.

<!-- folded-through: 20260804-140710 -->
