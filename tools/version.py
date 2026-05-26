"""Git tag versioning tool. Each public function maps to one operation."""
import subprocess
from dataclasses import dataclass


@dataclass
class TagInfo:
    name: str
    date: str


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def list_tags() -> list[TagInfo]:
    """Return all vN tags, newest first."""
    output = _git("tag", "--list", "v[0-9]*", "--sort=-version:refname", "--format=%(refname:short) %(creatordate:short)")
    if not output:
        return []
    tags = []
    for line in output.splitlines():
        parts = line.split(maxsplit=1)
        tags.append(TagInfo(name=parts[0], date=parts[1] if len(parts) > 1 else ""))
    return tags


def current_tag() -> str:
    """Return the latest vN tag, or 'unreleased' if none exist."""
    output = _git("tag", "--list", "v[0-9]*", "--sort=-version:refname")
    lines = [l for l in output.splitlines() if l]
    return lines[0] if lines else "unreleased"


def next_tag() -> str:
    """Return what the next publish tag would be (does not create it)."""
    tag = current_tag()
    if tag == "unreleased":
        return "v1"
    return f"v{int(tag[1:]) + 1}"


def publish() -> str:
    """Create the next sequential vN tag. Returns the new tag name."""
    tag = next_tag()
    _git("tag", tag)
    return tag


def rollback(tag: str) -> None:
    """Restore src/ to the state at <tag> and commit."""
    _git("checkout", tag, "--", "src/")
    _git("commit", "-m", f"rollback: restore src/ to {tag}")
