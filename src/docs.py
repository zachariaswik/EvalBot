"""Load startup submission documents from CourseDocs or an arbitrary path."""

from __future__ import annotations

from pathlib import Path

from .config import COURSE_DOCS_DIR


def load_submission(source: Path | None = None) -> str:
    """Read all .md files from *source* (default: CourseDocs/) and return
    concatenated text suitable as input for Agent 1.
    
    For PDF files, returns a file reference that Agent 1 (Claude) can read directly.
    """
    folder = source or COURSE_DOCS_DIR
    if folder.is_file():
        # Single file case
        if folder.suffix.lower() == ".pdf":
            # Return PDF file reference for Claude to read directly
            return f"[PDF_FILE: {folder.absolute()}]"
        return folder.read_text(encoding="utf-8")

    # Directory case: look for .md or .pdf files
    md_files = sorted(folder.glob("*.md"))
    pdf_files = sorted(folder.glob("*.pdf"))
    
    if not md_files and not pdf_files:
        raise FileNotFoundError(f"No .md or .pdf files found in {folder}")

    parts: list[str] = []
    
    # Handle markdown files
    for f in md_files:
        parts.append(f"# {f.stem}\n\n{f.read_text(encoding='utf-8')}")
    
    # Handle PDF files - pass as file references
    for f in pdf_files:
        parts.append(f"[PDF_FILE: {f.absolute()}]")
    
    return "\n\n---\n\n".join(parts)
