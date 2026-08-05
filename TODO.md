# TODO

## Human decisions needed
- [ ] Decide the language rule carve-out: CLAUDE.md says all file content is English, but `src/index.html` and `main.py` (`_timeago`) carry Norwegian user-facing copy ("Akkurat nå", "I går"). If intentional product language, add a user-facing-copy carve-out to CLAUDE.md's Language section; if not, translate the copy. (Human decision — flag, don't act unilaterally.)
- [ ] Decide archive-or-keep for `tools/editor.py`: nothing imports it and `main.py` duplicates its prompt while streaming via `agent/`. If archive: `mv tools/editor.py archive/` and remove its line from CLAUDE.md's tools/ listing. (Human decision.)
- [ ] Confirm whether the hardcoded Norwegian demo content in `src/index.html`'s extra tab sections (~lines 460-465, alongside the Jinja2 loop) is intentional. If not, replace with real template data or remove the sections. (Human decision on intent; implementation can follow in a run.)

## Docs
- [x] Reword the "Backend serves JSON endpoints" bullet in CLAUDE.md's Frontend pattern section — done 2026-08-05: wording proposed in MEMORY-PROPOSALS.md (runs must not edit CLAUDE.md); apply via `fun memory rules` or by hand after review.

## Harness
- [x] Make `./.fun/check` layer 2 (no-network GET / smoke) pass in the container — done 2026-08-04: when the deps aren't importable, the check now provisions them itself into a venv cached under `~/.cache/fun-check/enjoythenews-<requirements-hash>` (built once per `requirements.txt` change; the container firewall already allowlists pypi.org + files.pythonhosted.org). Reused across runs and worktrees; a failed build removes the partial venv and degrades to the old honest skip (exit 0). Verified: host direct, container first build, container cache hit (~1s), and the skip path.

## Later / operational
- [x] Background scheduler for feed refresh — done 2026-08-05: in-process asyncio task in `main.py` (`_periodic_refresh`, hourly via `REFRESH_INTERVAL`, `asyncio.to_thread` so the sync fetch never blocks the loop; cancelled on shutdown). Chosen over a systemd timer so dev and prod behave identically with zero server config. The matching Known-constraints update is proposed in MEMORY-PROPOSALS.md (runs must not edit CLAUDE.md).
