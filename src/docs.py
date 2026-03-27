"""Load startup submission documents from CourseDocs or an arbitrary path."""

from __future__ import annotations

from pathlib import Path

from .config import COURSE_DOCS_DIR


def load_submission(source: Path | None = None) -> str:
    """Read all .md files from *source* (default: CourseDocs/) and return
    concatenated text suitable as input for Agent 1."""
    folder = source or COURSE_DOCS_DIR
    if folder.is_file():
        return folder.read_text(encoding="utf-8")

    md_files = sorted(folder.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md files found in {folder}")

    parts: list[str] = []
    for f in md_files:
        parts.append(f"# {f.stem}\n\n{f.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(parts)
