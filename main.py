"""EvalBot CLI — run the multi-agent startup evaluation pipeline."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.docs import load_submission


def _ensure_supported_python() -> None:
    """CrewAI stack used by this project is not compatible with Python 3.14+."""
    if sys.version_info < (3, 14):
        return

    project_root = Path(__file__).resolve().parent
    py313 = project_root / ".venv313" / "bin" / "python"

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


def main() -> None:
    _ensure_supported_python()
    from src.pipeline import run_batch, run_single

    args = sys.argv[1:]

    if not args:
        # Default: process CourseDocs
        print("No arguments — processing CourseDocs as a single submission.\n")
        submission = load_submission()
        result = run_single(
            startup_name="CourseDocs Startup",
            submission_text=submission,
        )
        print("\n\nFINAL RESULTS")
        print("=" * 60)
        for agent_num in sorted(result.keys()):
            print(f"\n--- Agent {agent_num} ---")
            print(json.dumps(result[agent_num], indent=2, default=str))
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
        result = run_single(startup_name=name, submission_text=submission)
        print("\n\nFINAL RESULTS")
        print("=" * 60)
        for agent_num in sorted(result.keys()):
            print(f"\n--- Agent {agent_num} ---")
            print(json.dumps(result[agent_num], indent=2, default=str))

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
        result = run_batch(submissions)

        print("\n\nINDIVIDUAL RESULTS")
        print("=" * 60)
        for name, outputs in result["individual"].items():
            print(f"\n{'#'*40}")
            print(f"  {name}")
            print(f"{'#'*40}")
            for agent_num in sorted(outputs.keys()):
                print(f"\n--- Agent {agent_num} ---")
                print(json.dumps(outputs[agent_num], indent=2, default=str))

        if result["ranking"]:
            print("\n\nCOHORT RANKING")
            print("=" * 60)
            print(json.dumps(result["ranking"], indent=2, default=str))

    else:
        print(f"Unknown mode: {mode}")
        print("Usage:")
        print("  python main.py                     # Process CourseDocs")
        print("  python main.py single <file>       # Process one submission")
        print("  python main.py batch <directory>   # Process multiple + rank")
        sys.exit(1)


if __name__ == "__main__":
    main()
