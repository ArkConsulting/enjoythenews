import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime

SOURCES = [
    {"name": "Positive News", "url": "https://www.positive.news/feed/"},
    {"name": "Good News Network", "url": "https://www.goodnewsnetwork.org/feed/"},
    {"name": "Futurity", "url": "https://www.futurity.org/feed/"},
]


def _parse_date(entry) -> str:
    try:
        return parsedate_to_datetime(entry.published).isoformat()
    except Exception:
        return datetime.utcnow().isoformat()


def _strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_all() -> list[dict]:
    articles = []
    for source in SOURCES:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries:
            summary = _strip_html(entry.get("summary", ""))
            articles.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                "published": _parse_date(entry),
                "author": entry.get("author", ""),
                "source": source["name"],
            })
    return articles
