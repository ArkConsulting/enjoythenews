import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = ["science", "health", "nature", "society", "technology", "animals", "space"]

_PROMPT = """You are filtering news articles for a positive news aggregator.

For each article, determine:
- positive: true if genuinely good, uplifting, or constructive news; false otherwise
- category: one of {categories}
- score: positivity score from 0.0 to 1.0

Articles:
{articles}

Respond with a JSON array, one object per article, in the same order:
[{{"index": 0, "positive": true, "category": "science", "score": 0.92}}, ...]

Respond with ONLY the JSON array, no other text."""

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
    return _client


def classify(articles: list[dict]) -> list[dict]:
    """Filter and classify articles. Returns only positive ones with category and score added."""
    if not articles:
        return []

    results = []
    for i in range(0, len(articles), 20):
        batch = articles[i : i + 20]
        try:
            results.extend(_classify_batch(batch))
        except Exception:
            pass  # skip batch on API failure; articles will be retried on next refresh

    return [a for a in results if a.get("positive")]


def _classify_batch(articles: list[dict]) -> list[dict]:
    items = [
        {"index": i, "title": a["title"], "summary": a.get("summary", "")[:200]}
        for i, a in enumerate(articles)
    ]
    prompt = _PROMPT.format(
        categories=CATEGORIES,
        articles=json.dumps(items, ensure_ascii=False),
    )
    message = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    classifications = json.loads(message.content[0].text)
    merged = []
    for c in classifications:
        article = dict(articles[c["index"]])
        article["category"] = c.get("category", "")
        article["score"] = float(c.get("score", 0.0))
        article["positive"] = bool(c.get("positive", False))
        merged.append(article)
    return merged
