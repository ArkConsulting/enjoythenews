# enjoythenews roadmap

Forward-looking direction for this repo's three intertwined projects.
Always-on rules and architecture live in `CLAUDE.md` (the repo's only
top-level doc); the working backlog in `TODO.md`; the run-to-run state
digest in `.fun/STATE.md`.

## The three projects (see CLAUDE.md for the full framing)

1. **enjoythenews** — the live positive-news aggregator (FastAPI + SQLite,
   Hetzner). Real users; changes have immediate consequences.
2. **The Lovable-like app-generation system** — built incrementally as
   reusable tooling (`ops/`, `tools/`, `designs/`), with enjoythenews as its
   first generated-and-iterated app.
3. **The agent loop** (`agent/`) — the CLI agent powering the system's
   orchestration; dogfooded while building enjoythenews.

Everything below serves the dogfooding principle: a feature earns its place
by solving a real enjoythenews problem now, not a hypothetical one.

## Direction per component

- **Edit environment (`/edit`)** — the page where new versions are created.
  Current implementation is prompt-based: describe a change, Claude updates
  `src/`, preview before publishing. Later: direct in-browser code editing.
  Publishing stays git-native (commit + tag `vN` + push → pull + restart);
  no parallel versioning system.
- **Agent loop (`agent/`)** — model-agnostic routing is the goal: local
  models (Ollama) and cloud models via LiteLLM. The current backend
  (`agent/claude.py`) streams to the Anthropic API only. Local LLMs are an
  optimisation to take when API cost becomes a real constraint, not before.
- **Design bank (`designs/`)** — grows as the AI's few-shot reference
  library: more self-contained variants → better generation. Approved
  designs get converted to Jinja2 in `src/` by hand.
- **The live app** — no background scheduler yet (articles fetch at startup
  and on manual refresh); a scheduler is the natural next operational step
  when freshness matters more than simplicity.

## Standing tensions to resolve (tracked in TODO.md)

The 2026-07-31 CLAUDE.md audit flagged decisions only a human can make —
the English-only rule vs Norwegian user-facing copy, whether `tools/editor.py`
is dead, hardcoded demo content in `src/index.html`. These live as backlog
items, not roadmap direction.
