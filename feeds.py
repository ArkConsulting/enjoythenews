import re
import urllib.request
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from models import Article

SOURCES = [
    {"name": "Positive News", "url": "https://www.positive.news/feed/"},
    {"name": "Good News Network", "url": "https://www.goodnewsnetwork.org/feed/"},
    {"name": "Futurity", "url": "https://www.futurity.org/feed/"},
]

# Per-feed network timeout (seconds). feedparser.parse() fetches the URL itself
# with no timeout, so a slow/unreachable source can hang startup and /refresh
# indefinitely. We fetch the bytes ourselves with a bounded timeout and hand the
# content to feedparser, keeping stdlib as the only network dependency.
FEED_TIMEOUT = 10


def _fetch(url: str) -> bytes:
    # A browser-like User-Agent avoids feeds that reject the default urllib agent.
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (enjoythenews)"})
    with urllib.request.urlopen(req, timeout=FEED_TIMEOUT) as resp:
        return resp.read()


def _parse_date(entry) -> str:
    try:
        return parsedate_to_datetime(entry.published).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_all() -> list[Article]:
    articles = []
    for source in SOURCES:
        try:
            content = _fetch(source["url"])
        except Exception as exc:
            # One slow or unreachable feed must not block the others.
            print(f"feeds: skipping {source['name']}: {exc}")
            continue
        feed = feedparser.parse(content)
        for entry in feed.entries:
            summary = _strip_html(entry.get("summary", ""))
            articles.append(Article(
                title=entry.get("title", "").strip(),
                link=entry.get("link", ""),
                summary=summary[:300] + "..." if len(summary) > 300 else summary,
                published=_parse_date(entry),
                author=entry.get("author", ""),
                source=source["name"],
            ))
    return articles
