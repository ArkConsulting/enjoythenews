"""Claude streaming backend for the agent loop."""
import json
import re
from collections.abc import Generator
from dataclasses import dataclass

import anthropic
from dotenv import load_dotenv

load_dotenv()

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


@dataclass
class ParsedResponse:
    message: str
    new_content: str | None


def _parse_html(raw: str) -> ParsedResponse:
    match = re.search(r"```html\n(.*?)```", raw, re.DOTALL)
    if not match:
        return ParsedResponse(message=raw.strip(), new_content=None)
    message = raw[: match.start()].strip() or "Done."
    return ParsedResponse(message=message, new_content=match.group(1))


def stream(
    messages: list[dict],
    system: str,
) -> Generator[str, None, None]:
    """Stream Claude's response as SSE events.

    Yields SSE lines:
      data: {"type": "text", "delta": "..."}
      data: {"type": "done", "message": "...", "new_content": "..." | null}
    """
    full_text = ""
    with _get_client().messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
    ) as s:
        for chunk in s.text_stream:
            full_text += chunk
            yield f"data: {json.dumps({'type': 'text', 'delta': chunk})}\n\n"

    parsed = _parse_html(full_text)
    yield f"data: {json.dumps({'type': 'done', 'message': parsed.message, 'new_content': parsed.new_content})}\n\n"
