"""EvalBot CLI — run the multi-agent startup evaluation pipeline."""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from src.docs import load_submission

PROJECT_ROOT = Path(__file__).resolve().parent


def _ensure_supported_python() -> None:
    """CrewAI stack used by this project is not compatible with Python 3.14+."""
    if sys.version_info < (3, 14):
        return

    py313 = PROJECT_ROOT / ".venv313" / "bin" / "python"

    if py313.exists() and Path(sys.executable).resolve() != py313.resolve():
        print("Python 3.14 detected; re-launching with .venv313 for compatibility...\n")
        os.execv(str(py313), [str(py313), str(Path(__file__).resolve()), *sys.argv[1:]])

    print("EvalBot currently requires Python 3.13 or earlier.")
    print("Create .venv313 and run with: .venv313/bin/python main.py")
    sys.exit(1)


def _extract_startup_name(text: str) -> str:
    """Try to extract a startup name from submission text, fall back to generic."""
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:80]
    return "Unknown Startup"


def _sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()


def export_results(
    batch_id: str,
    individual: dict[str, dict[int, Any]],
    ranking: dict[str, Any] | None = None,
) -> Path:
    """Write pipeline results as JSON files to output/<batch_id>/."""
    out_dir = PROJECT_ROOT / "output" / batch_id
    out_dir.mkdir(parents=True, exist_ok=True)

    for startup_name, agent_outputs in individual.items():
        filename = _sanitize_filename(startup_name) + ".json"
        (out_dir / filename).write_text(
            json.dumps(agent_outputs, indent=2, default=str),
            encoding="utf-8",
        )

    if ranking is not None:
        (out_dir / "ranking.json").write_text(
            json.dumps(ranking, indent=2, default=str),
            encoding="utf-8",
        )

    return out_dir


def main() -> None:
    _ensure_supported_python()
    from src.pipeline import run_batch, run_single

    args = sys.argv[1:]

    if not args:
        # Default: process CourseDocs
        print("No arguments — processing CourseDocs as a single submission.\n")
        submission = load_submission()
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"
        result = run_single(
            startup_name="CourseDocs Startup",
            submission_text=submission,
            batch_id=batch_id,
        )
        print("\n\nFINAL RESULTS")
        print("=" * 60)
        for agent_num in sorted(k for k in result.keys() if isinstance(k, int)):
            print(f"\n--- Agent {agent_num} ---")
            print(json.dumps(result[agent_num], indent=2, default=str))
        if "_tags" in result:
            print(f"\n--- Tags ---")
            print(json.dumps(result["_tags"], indent=2, default=str))

        out_dir = export_results(batch_id, {"CourseDocs Startup": result})
        print(f"\nResults saved to: {out_dir}")
        return

    mode = args[0]

    if mode == "single":
        if len(args) < 2:
            print("Usage: python main.py single <submission_file>")
            sys.exit(1)
        path = Path(args[1])
        if not path.exists():
            print(f"File not found: {path}")
            sys.exit(1)
        submission = load_submission(path)
        name = _extract_startup_name(submission)
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"
        result = run_single(startup_name=name, submission_text=submission, batch_id=batch_id)
        print("\n\nFINAL RESULTS")
        print("=" * 60)
        for agent_num in sorted(result.keys()):
            print(f"\n--- Agent {agent_num} ---")
            print(json.dumps(result[agent_num], indent=2, default=str))

        out_dir = export_results(batch_id, {name: result})
        print(f"\nResults saved to: {out_dir}")

    elif mode == "batch":
        if len(args) < 2:
            print("Usage: python main.py batch <directory>")
            sys.exit(1)
        folder = Path(args[1])
        if not folder.is_dir():
            print(f"Not a directory: {folder}")
            sys.exit(1)

        submissions: dict[str, str] = {}
        subdirs = sorted([d for d in folder.iterdir() if d.is_dir() and not d.name.startswith(".")])
        if subdirs:
            # New structure: each subfolder is one startup
            for subdir in subdirs:
                md_files = sorted(subdir.glob("*.md"))
                if not md_files:
                    continue
                combined = "\n\n".join(f.read_text(encoding="utf-8") for f in md_files)
                submissions[subdir.name] = combined
        else:
            # Legacy: .md files directly in the folder
            for f in sorted(folder.glob("*.md")):
                text = f.read_text(encoding="utf-8")
                name = _extract_startup_name(text)
                submissions[name] = text

        if not submissions:
            print(f"No startup submissions found in {folder}")
            sys.exit(1)

        print(f"Found {len(submissions)} submissions: {list(submissions.keys())}\n")
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"
        result = run_batch(submissions, batch_id=batch_id)

        print("\n\nINDIVIDUAL RESULTS")
        print("=" * 60)
        for name, outputs in result["individual"].items():
            print(f"\n{'#'*40}")
            print(f"  {name}")
            print(f"{'#'*40}")
            for agent_num in sorted(k for k in outputs.keys() if isinstance(k, int)):
                print(f"\n--- Agent {agent_num} ---")
                print(json.dumps(outputs[agent_num], indent=2, default=str))
            if "_tags" in outputs:
                print(f"\n--- Tags ---")
                print(json.dumps(outputs["_tags"], indent=2, default=str))

        if result["ranking"]:
            print("\n\nCOHORT RANKING")
            print("=" * 60)
            print(json.dumps(result["ranking"], indent=2, default=str))

        out_dir = export_results(batch_id, result["individual"], result["ranking"])
        print(f"\nResults saved to: {out_dir}")

    else:
        print(f"Unknown mode: {mode}")
        print("Usage:")
        print("  python main.py                     # Process CourseDocs")
        print("  python main.py single <file>       # Process one submission")
        print("  python main.py batch <directory>   # Process multiple + rank")
        sys.exit(1)


if __name__ == "__main__":
    main()
