import re
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from models import Article

SOURCES = [
    {"name": "Positive News", "url": "https://www.positive.news/feed/"},
    {"name": "Good News Network", "url": "https://www.goodnewsnetwork.org/feed/"},
    {"name": "Futurity", "url": "https://www.futurity.org/feed/"},
]


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
        feed = feedparser.parse(source["url"])
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
