import sqlite3
from contextlib import contextmanager
from dataclasses import asdict

from models import Article

DB_PATH = "enjoythenews.db"


def init():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                summary TEXT,
                published TEXT,
                author TEXT,
                source TEXT,
                fetched_at TEXT DEFAULT (datetime('now'))
            )
        """)
        # migrations: add columns introduced after initial schema
        for col, typedef in [("category", "TEXT"), ("score", "REAL")]:
            try:
                conn.execute(f"ALTER TABLE articles ADD COLUMN {col} {typedef}")
            except sqlite3.OperationalError:
                pass  # column already exists


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row_to_article(row) -> Article:
    return Article(
        title=row["title"],
        link=row["link"],
        source=row["source"] or "",
        summary=row["summary"] or "",
        published=row["published"] or "",
        author=row["author"] or "",
        category=row["category"] or "",
        score=float(row["score"] or 0.0),
    )


def filter_new(articles: list[Article]) -> list[Article]:
    """Return only articles whose link is not already in the database."""
    if not articles:
        return []
    links = [a.link for a in articles]
    placeholders = ",".join("?" * len(links))
    with connect() as conn:
        existing = {
            r["link"]
            for r in conn.execute(
                f"SELECT link FROM articles WHERE link IN ({placeholders})", links
            ).fetchall()
        }
    return [a for a in articles if a.link not in existing]


def upsert_articles(articles: list[Article]) -> int:
    new_count = 0
    with connect() as conn:
        for a in articles:
            try:
                conn.execute(
                    """INSERT INTO articles
                       (title, link, summary, published, author, source, category, score)
                       VALUES (:title, :link, :summary, :published, :author, :source, :category, :score)""",
                    asdict(a),
                )
                new_count += 1
            except sqlite3.IntegrityError:
                pass  # duplicate link, skip
    return new_count


def get_articles(limit: int = 30, offset: int = 0, source: str | None = None) -> list[Article]:
    with connect() as conn:
        if source:
            rows = conn.execute(
                "SELECT * FROM articles WHERE source = ? ORDER BY published DESC LIMIT ? OFFSET ?",
                (source, limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM articles ORDER BY published DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [_row_to_article(r) for r in rows]


def get_sources() -> list[str]:
    with connect() as conn:
        rows = conn.execute("SELECT DISTINCT source FROM articles ORDER BY source").fetchall()
        return [r["source"] for r in rows]
