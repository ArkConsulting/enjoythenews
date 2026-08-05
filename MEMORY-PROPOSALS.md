# Memory proposals

Durable learnings appended by unattended runs. Review and fold into CLAUDE.md /
patterns as appropriate.

## 20260805-095943 — two proposed CLAUDE.md edits (per the update rule: propose, don't apply)

1. **Frontend pattern section — reword the "Backend serves JSON endpoints" bullet.**
   It reads as a description but is false as one: the index is server-rendered and
   `/refresh` returns a full HTML page. Proposed replacement (a guideline for new
   endpoints):

   > - Full pages are server-rendered Jinja2; new dynamic endpoints return JSON for
   >   the page's JS to fetch and render. Never HTML partials/fragments over the wire.

2. **Known constraints section — the "No background scheduler" bullet is now stale.**
   This run added an in-process asyncio task in `main.py` that refreshes feeds every
   hour (`REFRESH_INTERVAL`). Proposed replacement:

   > - Feed refresh is periodic in-process: an asyncio task in `main.py` runs every
   >   hour (`REFRESH_INTERVAL`), in addition to startup and manual `/refresh`. No
   >   external scheduler; the task dies with the process.
