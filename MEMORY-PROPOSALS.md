# Memory proposals

Durable learnings appended by unattended runs. Review and fold into CLAUDE.md /
patterns as appropriate.

- The `enjoythenews` repo has **no README.md** (no README of any name). Repo-level
  documentation lives in `CLAUDE.md`. A task to "proofread README.md" has no target
  here — confirm the requester didn't mean the funai workspace root or a sibling repo.

- `feedparser.parse(url)` fetches the URL itself with **no network timeout** — a slow
  or unreachable feed hangs the caller forever. Stdlib-first fix: fetch bytes with
  `urllib.request.urlopen(req, timeout=N)` (a browser-like User-Agent avoids feeds
  that reject the default urllib agent), then pass the raw content to
  `feedparser.parse()`, which happily parses already-fetched bytes. No threads,
  signals, or extra deps needed. See `feeds.py` `_fetch()` / `FEED_TIMEOUT`.
