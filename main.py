"""EvalBot CLI — run the multi-agent startup evaluation pipeline."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from src.docs import load_submission

PROJECT_ROOT = Path(__file__).resolve().parent


def _next_batch_id() -> str:
    """Return the next sequential batch ID (batch_1, batch_2, ...)."""
    output_dir = PROJECT_ROOT / "output"
    if not output_dir.exists():
        return "batch_1"
    existing = [
        int(d.name.split("_")[1])
        for d in output_dir.iterdir()
        if d.is_dir() and d.name.startswith("batch_") and d.name.split("_")[1].isdigit()
    ]
    return f"batch_{max(existing) + 1}" if existing else "batch_1"


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


AGENT_ROLES = {
    1: "Intake Parser",
    2: "Venture Analyst",
    3: "Market & Competition Analyst",
    4: "Product & Positioning Analyst",
    5: "Founder Fit Analyst",
    6: "Recommendation / Pivot Agent",
    7: "Ranking Committee Agent",
}

# Pricing per million tokens: {model_prefix: (input_$/M, output_$/M)}
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "anthropic/claude-haiku-4-5": (1.00, 5.00),
    "anthropic/claude-sonnet-4-6": (3.00, 15.00),
    "anthropic/claude-opus-4-6": (15.00, 75.00),
    "anthropic/claude-sonnet-4-20250514": (3.00, 15.00),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "o3-mini": (1.10, 4.40),
    "minimax/MiniMax-M2.5": (0.30, 1.20),
}


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost from model name and token counts."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0
    input_rate, output_rate = pricing
    return (prompt_tokens * input_rate + completion_tokens * output_rate) / 1_000_000


def _write_batch_summary(
    batch_id: str,
    out_dir: Path,
    individual: dict[str, dict[int, Any]],
    ranking_usage: dict[int, dict] | None = None,
) -> None:
    """Write batch_summary.md with model table and token/cost breakdown."""
    # Aggregate usage across all startups per agent
    aggregated: dict[int, dict] = {}
    for _name, outputs in individual.items():
        usage_data = outputs.get("_usage", {})
        for agent_num, info in usage_data.items():
            agent_num = int(agent_num)
            if agent_num not in aggregated:
                aggregated[agent_num] = {
                    "model": info["model"],
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                }
            aggregated[agent_num]["prompt_tokens"] += info["prompt_tokens"]
            aggregated[agent_num]["completion_tokens"] += info["completion_tokens"]
            aggregated[agent_num]["total_tokens"] += info["total_tokens"]

    # Add Agent 7 usage if present
    if ranking_usage:
        for agent_num, info in ranking_usage.items():
            agent_num = int(agent_num)
            aggregated[agent_num] = {
                "model": info["model"],
                "prompt_tokens": info["prompt_tokens"],
                "completion_tokens": info["completion_tokens"],
                "total_tokens": info["total_tokens"],
            }

    lines = [f"# Batch Summary — {batch_id}", ""]

    # Models table
    lines.append("## Models Used")
    lines.append("")
    lines.append("| Agent | Role                           | Model                              |")
    lines.append("|-------|--------------------------------|------------------------------------|")
    for agent_num in sorted(aggregated.keys()):
        role = AGENT_ROLES.get(agent_num, "Unknown")
        model = aggregated[agent_num]["model"]
        lines.append(f"| {agent_num}     | {role:<30} | {model:<34} |")
    lines.append("")

    # Token usage & cost table
    lines.append("## Token Usage & Cost")
    lines.append("")
    lines.append("| Agent | Prompt Tokens | Completion Tokens | Total Tokens | Cost     |")
    lines.append("|-------|---------------|-------------------|--------------|----------|")
    total_cost = 0.0
    for agent_num in sorted(aggregated.keys()):
        info = aggregated[agent_num]
        cost = _estimate_cost(info["model"], info["prompt_tokens"], info["completion_tokens"])
        total_cost += cost
        lines.append(
            f"| {agent_num}     | {info['prompt_tokens']:,}".ljust(22)
            + f"| {info['completion_tokens']:,}".ljust(22)
            + f"| {info['total_tokens']:,}".ljust(15)
            + f"| ${cost:.3f}".ljust(11) + "|"
        )
    lines.append(
        f"| **Total** |               |                   |              | **${total_cost:.2f}** |"
    )
    lines.append("")

    (out_dir / "batch_summary.md").write_text("\n".join(lines), encoding="utf-8")


def _fmt_list(items: list | str | None, bullet: str = "- ") -> str:
    """Format a list or string as bulleted markdown lines."""
    if not items:
        return f"{bullet}N/A"
    if isinstance(items, str):
        return f"{bullet}{items}"
    return "\n".join(f"{bullet}{item}" for item in items)


def _write_startup_report(
    startup_name: str, agent_outputs: dict[int | str, Any], path: Path
) -> None:
    """Write a human-readable markdown report for a single startup."""
    a1 = agent_outputs.get(1) or agent_outputs.get("1") or {}
    a2 = agent_outputs.get(2) or agent_outputs.get("2") or {}
    a3 = agent_outputs.get(3) or agent_outputs.get("3") or {}
    a4 = agent_outputs.get(4) or agent_outputs.get("4") or {}
    a5 = agent_outputs.get(5) or agent_outputs.get("5") or {}
    a6 = agent_outputs.get(6) or agent_outputs.get("6") or {}
    tags = agent_outputs.get("_tags") or []

    def g(d: dict, key: str, fallback: str = "N/A") -> str:
        v = d.get(key)
        return str(v) if v is not None else fallback

    lines: list[str] = []

    # Header
    lines.append(f"# {startup_name}")
    lines.append("")
    if a1.get("one_line_description"):
        lines.append(f"> {a1['one_line_description']}")
        lines.append("")

    verdict = g(a2, "verdict")
    weighted = g(a2, "weighted_total_score")
    tier = g(a2, "score_tier")
    recommendation = g(a6, "recommendation")
    lines.append(f"**Verdict:** {verdict} | **Score:** {weighted}/80 ({tier}) | **Recommendation:** {recommendation}")
    lines.append("")

    if tags:
        lines.append("**Tags:** " + ", ".join(f"`{t}`" for t in tags))
        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Agent 1: Startup Brief ---
    lines.append("## 1. Startup Brief (Agent 1)")
    lines.append("")
    for field, label in [
        ("problem", "Problem"),
        ("solution", "Solution"),
        ("target_customer", "Target Customer"),
        ("buyer", "Buyer"),
        ("market", "Market"),
        ("business_model", "Business Model"),
        ("competitors", "Competitors"),
        ("traction", "Traction"),
        ("team", "Team"),
        ("why_now", "Why Now"),
        ("vision", "Vision"),
        ("unfair_advantage", "Unfair Advantage"),
        ("risks", "Risks"),
    ]:
        lines.append(f"- **{label}:** {g(a1, field)}")

    missing = a1.get("missing_info")
    if missing:
        lines.append(f"- **Missing Info:**")
        for item in (missing if isinstance(missing, list) else [missing]):
            lines.append(f"  - {item}")

    inconsistencies = a1.get("inconsistencies")
    if inconsistencies:
        lines.append(f"- **Inconsistencies:**")
        for item in (inconsistencies if isinstance(inconsistencies, list) else [inconsistencies]):
            lines.append(f"  - {item}")

    lines.append(f"- **Clarity Score:** {g(a1, 'clarity_score')}/10")
    lines.append("")

    # --- Agent 2: Venture Analysis ---
    lines.append("## 2. Venture Analysis (Agent 2)")
    lines.append("")
    lines.append(f"**Summary:** {g(a2, 'summary')}")
    lines.append("")

    lines.append("### Scores")
    lines.append("")
    lines.append("| Category | Score |")
    lines.append("|----------|-------|")
    score_fields = [
        ("score_problem_severity", "Problem Severity"),
        ("score_market_size", "Market Size"),
        ("score_differentiation", "Differentiation"),
        ("score_customer_clarity", "Customer Clarity"),
        ("score_founder_insight", "Founder Insight"),
        ("score_business_model", "Business Model"),
        ("score_moat_potential", "Moat Potential"),
        ("score_venture_potential", "Venture Potential"),
        ("score_competition_difficulty", "Competition Difficulty"),
        ("score_execution_feasibility", "Execution Feasibility"),
    ]
    for field, label in score_fields:
        lines.append(f"| {label} | {g(a2, field)}/10 |")
    lines.append(f"| **Total** | **{g(a2, 'total_score')}** |")
    lines.append("")
    lines.append(f"**Weighted Total:** {weighted}/80 — {tier}")
    lines.append("")

    swot = a2.get("swot") or {}
    if swot:
        lines.append("### SWOT")
        lines.append("")
        for category in ["strengths", "weaknesses", "opportunities", "threats"]:
            items = swot.get(category, [])
            lines.append(f"- **{category.title()}:**")
            for item in (items if isinstance(items, list) else [items] if items else []):
                lines.append(f"  - {item}")
        lines.append("")

    reject = a2.get("reject_signals")
    if reject:
        lines.append("**Reject Signals:** " + ", ".join(str(s) for s in reject))
        lines.append("")

    lines.append(f"**Verdict:** {verdict}")
    lines.append("")
    lines.append(f"**Explanation:** {g(a2, 'explanation')}")
    lines.append("")

    # --- Agent 3: Market & Competition ---
    lines.append("## 3. Market & Competition (Agent 3)")
    lines.append("")
    for field, label in [
        ("market_category", "Market Category"),
        ("size_class", "Market Size"),
        ("trend", "Trend"),
        ("direct_competitors", "Direct Competitors"),
        ("indirect_competitors", "Indirect Competitors"),
        ("big_tech_risk", "Big Tech Risk"),
        ("crowdedness", "Crowdedness"),
        ("wedge", "Wedge"),
    ]:
        lines.append(f"- **{label}:** {g(a3, field)}")
    lines.append(f"- **Attractiveness Score:** {g(a3, 'attractiveness_score')}/10")
    lines.append(f"- **Competition Score:** {g(a3, 'competition_score')}/10")
    lines.append(f"- **Conclusion:** {g(a3, 'conclusion')}")
    lines.append("")

    # --- Agent 4: Product & Positioning ---
    lines.append("## 4. Product & Positioning (Agent 4)")
    lines.append("")
    for field, label in [
        ("product_reality", "Product Reality"),
        ("value_prop", "Value Prop"),
        ("killer_feature", "Killer Feature"),
        ("why_care", "Why Care"),
        ("why_not_care", "Why Not Care"),
        ("feature_vs_company", "Feature vs Company"),
        ("wrapper_risk", "Wrapper Risk"),
        ("wedge", "Wedge"),
        ("moat", "Moat"),
        ("positioning", "Positioning"),
        ("six_month_focus", "6-Month Focus"),
    ]:
        lines.append(f"- **{label}:** {g(a4, field)}")
    lines.append("")

    # --- Agent 5: Founder Fit ---
    lines.append("## 5. Founder Fit (Agent 5)")
    lines.append("")
    for field, label in [
        ("founder_fit", "Founder Fit"),
        ("domain", "Domain"),
        ("technical", "Technical"),
        ("distribution", "Distribution"),
        ("strategy", "Strategy"),
        ("ambition", "Ambition"),
        ("execution", "Execution"),
    ]:
        lines.append(f"- **{label}:** {g(a5, field)}")

    missing_roles = a5.get("missing_roles")
    if missing_roles:
        lines.append("- **Missing Roles:**")
        for role in (missing_roles if isinstance(missing_roles, list) else [missing_roles]):
            lines.append(f"  - {role}")

    risks_5 = a5.get("risks")
    if risks_5:
        lines.append("- **Risks:**")
        for risk in (risks_5 if isinstance(risks_5, list) else [risks_5]):
            lines.append(f"  - {risk}")

    lines.append(f"- **Fit Score:** {g(a5, 'fit_score')}/10 | **Execution Score:** {g(a5, 'execution_score')}/10")
    lines.append(f"- **Conclusion:** {g(a5, 'conclusion')}")
    lines.append("")

    # --- Agent 6: Recommendation ---
    lines.append("## 6. Recommendation (Agent 6)")
    lines.append("")
    lines.append(f"**Recommendation:** {recommendation}")
    lines.append("")
    lines.append(f"**Target Customer Segment:** {g(a6, 'customer_segment')}")
    lines.append("")
    lines.append(f"**Wedge:** {g(a6, 'wedge')}")
    lines.append("")

    remove = a6.get("remove")
    if remove:
        lines.append("### Stop Doing")
        lines.append("")
        lines.append(_fmt_list(remove))
        lines.append("")

    emphasize = a6.get("emphasize")
    if emphasize:
        lines.append("### Start Emphasizing")
        lines.append("")
        lines.append(_fmt_list(emphasize))
        lines.append("")

    pivots = a6.get("pivots")
    if pivots:
        lines.append("### Pivot Options")
        lines.append("")
        if isinstance(pivots, list):
            for i, p in enumerate(pivots, 1):
                lines.append(f"{i}. {p}")
        else:
            lines.append(f"1. {pivots}")
        lines.append("")

    if a6.get("positioning_rewrite"):
        lines.append("### Positioning Rewrite")
        lines.append("")
        lines.append(g(a6, "positioning_rewrite"))
        lines.append("")

    if a6.get("thirty_day_plan"):
        lines.append("### 30-Day Plan")
        lines.append("")
        lines.append(g(a6, "thirty_day_plan"))
        lines.append("")

    if a6.get("ninety_day_plan"):
        lines.append("### 90-Day Plan")
        lines.append("")
        lines.append(g(a6, "ninety_day_plan"))
        lines.append("")

    if a6.get("mistake_to_avoid"):
        lines.append("### Mistake to Avoid")
        lines.append("")
        lines.append(g(a6, "mistake_to_avoid"))
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def export_results(
    batch_id: str,
    individual: dict[str, dict[int, Any]],
    ranking: dict[str, Any] | None = None,
    ranking_usage: dict[int, dict] | None = None,
) -> Path:
    """Write pipeline results as JSON files to output/<batch_id>/."""
    out_dir = PROJECT_ROOT / "output" / batch_id
    out_dir.mkdir(parents=True, exist_ok=True)

    for startup_name, agent_outputs in individual.items():
        safe_name = _sanitize_filename(startup_name)
        startup_dir = out_dir / safe_name
        startup_dir.mkdir(parents=True, exist_ok=True)
        (startup_dir / f"{safe_name}.json").write_text(
            json.dumps(agent_outputs, indent=2, default=str),
            encoding="utf-8",
        )
        _write_startup_report(startup_name, agent_outputs, startup_dir / f"{safe_name}.md")

    if ranking is not None:
        (out_dir / "ranking.json").write_text(
            json.dumps(ranking, indent=2, default=str),
            encoding="utf-8",
        )

    _write_batch_summary(batch_id, out_dir, individual, ranking_usage)

    return out_dir


def main() -> None:
    _ensure_supported_python()
    from src.pipeline import run_batch, run_single

    args = sys.argv[1:]

    if not args:
        # Default: process CourseDocs
        print("No arguments — processing CourseDocs as a single submission.\n")
        submission = load_submission()
        batch_id = _next_batch_id()
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
        batch_id = _next_batch_id()
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
        batch_id = _next_batch_id()
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

        out_dir = export_results(
            batch_id, result["individual"], result["ranking"], result.get("ranking_usage"),
        )
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
