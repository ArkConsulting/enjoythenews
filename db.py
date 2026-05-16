import sqlite3
from contextlib import contextmanager

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


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_articles(articles: list[dict]) -> int:
    new_count = 0
    with connect() as conn:
        for a in articles:
            try:
                conn.execute(
                    """INSERT INTO articles (title, link, summary, published, author, source)
                       VALUES (:title, :link, :summary, :published, :author, :source)""",
                    a,
                )
                new_count += 1
            except sqlite3.IntegrityError:
                pass  # duplicate link, skip
    return new_count


def get_articles(limit: int = 30, offset: int = 0, source: str | None = None) -> list[dict]:
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
        return [dict(r) for r in rows]


def get_sources() -> list[str]:
    with connect() as conn:
        rows = conn.execute("SELECT DISTINCT source FROM articles ORDER BY source").fetchall()
        return [r["source"] for r in rows]
