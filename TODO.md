# TODO

## Human decisions needed
- [ ] Decide the language rule carve-out: CLAUDE.md says all file content is English, but `src/index.html` and `main.py` (`_timeago`) carry Norwegian user-facing copy ("Akkurat nå", "I går"). If intentional product language, add a user-facing-copy carve-out to CLAUDE.md's Language section; if not, translate the copy. (Human decision — flag, don't act unilaterally.)
- [ ] Decide archive-or-keep for `tools/editor.py`: nothing imports it and `main.py` duplicates its prompt while streaming via `agent/`. If archive: `mv tools/editor.py archive/` and remove its line from CLAUDE.md's tools/ listing. (Human decision.)
- [ ] Confirm whether the hardcoded Norwegian demo content in `src/index.html`'s extra tab sections (~lines 460-465, alongside the Jinja2 loop) is intentional. If not, replace with real template data or remove the sections. (Human decision on intent; implementation can follow in a run.)

## Docs
- [ ] Reword the "Backend serves JSON endpoints" bullet in CLAUDE.md's Frontend pattern section: it reads as a description but the index is server-rendered and `/refresh` returns HTML. Restate it as a guideline for new endpoints (propose the wording, per CLAUDE.md's update rule).

## Harness
- [ ] Make `./.fun/check` layer 2 (no-network GET / smoke) pass in the container: app deps (FastAPI etc.) are not importable there, so three runs in a row have passed layer 1 only. Investigate how the check can install or reach the app's requirements inside the container, or vendor a minimal path so the smoke actually runs.

## Later / operational
- [ ] Background scheduler for feed refresh: articles are currently fetched only at startup and on manual `/refresh`. Design the simplest periodic refresh (e.g. systemd timer hitting `/refresh`, or an in-process asyncio task) consistent with the no-frameworks philosophy; update the Known constraints section when done.
