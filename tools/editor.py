"""LLM-powered Jinja2 template editor."""
import json
import re
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

_SYSTEM = """You are editing a Jinja2 HTML template for a positive news aggregator called Horisonten.

Rules:
- Preserve all Jinja2 syntax exactly: {{ }}, {% %}, {# #}
- If making changes, end your response with the complete updated file in a fenced html code block.
- Never return partial files or diffs — always the full file.
- If no change is needed, respond conversationally with no code block."""

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


@dataclass
class EditResult:
    message: str
    new_content: str | None


def chat(user_message: str, file_content: str) -> EditResult:
    """Send user_message + current file to Claude. Returns response text and optionally the updated file."""
    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=[
            {
                "type": "text",
                "text": _SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Current template:\n\n```html\n{file_content}\n```",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": user_message,
                    },
                ],
            }
        ],
    )

    return _parse_response(response.content[0].text)


def stream_chat(user_message: str, file_content: str, output_path: Path | None = None) -> Generator[str, None, None]:
    """Stream Claude's response as SSE. Writes updated file when done if output_path is given."""
    full_text = ""
    with _get_client().messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": f"Current template:\n\n```html\n{file_content}\n```", "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": user_message},
            ],
        }],
    ) as stream:
        for chunk in stream.text_stream:
            full_text += chunk
            yield f"data: {json.dumps({'type': 'text', 'delta': chunk})}\n\n"

    result = _parse_response(full_text)
    if result.new_content is not None and output_path is not None:
        output_path.write_text(result.new_content)

    yield f"data: {json.dumps({'type': 'done', 'changed': result.new_content is not None, 'message': result.message})}\n\n"


def _parse_response(raw: str) -> EditResult:
    match = re.search(r"```html\n(.*?)```", raw, re.DOTALL)
    if not match:
        return EditResult(message=raw.strip(), new_content=None)
    message = raw[: match.start()].strip() or "Done."
    return EditResult(message=message, new_content=match.group(1))
