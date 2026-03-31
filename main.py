"""EvalBot CLI — run the multi-agent startup evaluation pipeline."""

from __future__ import annotations

from enum import Enum
import json
import os
import re
import shutil
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, get_args, get_origin

import pdfplumber
from dotenv import load_dotenv

load_dotenv()

from src.docs import load_submission

PROJECT_ROOT = Path(__file__).resolve().parent

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    
    # Background colors
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"


def _colorize(text: str, color: str) -> str:
    """Apply ANSI color to text."""
    return f"{color}{text}{Colors.RESET}"


def _next_generated_id() -> str:
    """Return the next sequential generated ID (generated_1, generated_2, ...)."""
    output_dir = PROJECT_ROOT / "output"
    if not output_dir.exists():
        return "generated_1"
    existing = [
        int(d.name.split("_")[1])
        for d in output_dir.iterdir()
        if d.is_dir() and d.name.startswith("generated_") and d.name.split("_")[1].isdigit()
    ]
    return f"generated_{max(existing) + 1}" if existing else "generated_1"


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


def _extract_text_from_pdf(pdf_path: Path) -> str | None:
    """Extract text from a PDF file. Return None if extraction fails."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n\n".join(text_parts) if text_parts else None
    except Exception:
        return None


AGENT_ROLES = {
    0: "Startup Idea Generator",
    1: "Intake Parser",
    2: "Venture Analyst",
    3: "Market & Competition Analyst",
    4: "Product & Positioning Analyst",
    5: "Founder Fit Analyst",
    6: "Recommendation / Pivot Agent",
    7: "Ranking Committee Agent",
}


def _supports_structured_output(model_name: str) -> bool:
    """Return whether we should use output_pydantic for this model/provider."""
    return not model_name.lower().startswith("minimax/")


def _extract_json_segment(text: str) -> str | None:
    """Extract the first balanced JSON object or array from text."""
    starts = [idx for idx in (text.find("{"), text.find("[")) if idx != -1]
    if not starts:
        return None
    start = min(starts)

    stack: list[str] = []
    in_string = False
    escaped = False

    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch in "{[":
            stack.append(ch)
            continue
        if ch in "}]":
            if not stack:
                return None
            opener = stack.pop()
            if (opener == "{" and ch != "}") or (opener == "[" and ch != "]"):
                return None
            if not stack:
                return text[start : i + 1]

    return None


def _parse_output_to_dict(output_model: Any, raw: str) -> dict[str, Any] | None:
    """Parse LLM raw output into the expected dict, handling fenced JSON and extra prose."""
    def _normalize_for_model(data: dict[str, Any]) -> dict[str, Any]:
        def _unwrap_optional(annotation: Any) -> Any:
            origin = get_origin(annotation)
            if origin is None:
                return annotation
            args = [a for a in get_args(annotation) if a is not type(None)]
            return args[0] if len(args) == 1 else annotation

        def _coerce_rerun_agent(value: Any) -> Any:
            if value is None:
                return None
            if isinstance(value, bool):
                return None if value is False else 1
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                s = value.strip().lower()
                if s in {"", "none", "null", "n/a", "na", "false", "no"}:
                    return None
                if s.isdigit():
                    return int(s)
                # Handles variants like "Agent1", "agent_2", "Agent 3 Parser".
                match = re.search(r"agent\s*[_-]?(\d+)", s)
                if match:
                    return int(match.group(1))
            return value

        def _coerce_str(value: Any, fallback: str = "Not provided") -> str:
            if value is None:
                return fallback
            if isinstance(value, str):
                s = value.strip()
                return s if s else fallback
            return str(value)

        def _clamp_score(field_name: str, value: int) -> int:
            if field_name.startswith("score_"):
                return max(1, min(10, value))
            if field_name in {"clarity_score", "fit_score", "execution_score", "attractiveness_score", "competition_score"}:
                return max(1, min(10, value))
            return value

        def _default_for_field(field_name: str, ann: Any) -> Any:
            origin = get_origin(ann)
            if origin is list:
                return []
            if origin is dict:
                return {}
            if isinstance(ann, type) and issubclass(ann, Enum):
                return next(iter(ann)).value
            if isinstance(ann, type) and ann is int:
                return 5 if "score" in field_name else 0
            if isinstance(ann, type) and ann is float:
                return 0.0
            if isinstance(ann, type) and ann is str:
                return "Not provided"
            if isinstance(ann, type) and hasattr(ann, "model_fields"):
                return _salvage_for_model(ann, {})
            return None

        def _salvage_for_model(model_cls: Any, src: dict[str, Any]) -> dict[str, Any]:
            out: dict[str, Any] = {}
            for f_name, f_info in model_cls.model_fields.items():
                f_ann = _unwrap_optional(f_info.annotation)
                f_origin = get_origin(f_ann)
                has_value = f_name in src and src[f_name] is not None
                raw_value = src.get(f_name) if has_value else None

                if not has_value:
                    if f_info.is_required():
                        out[f_name] = _default_for_field(f_name, f_ann)
                    continue

                if f_name == "rerun_from_agent":
                    out[f_name] = _coerce_rerun_agent(raw_value)
                    continue

                if isinstance(f_ann, type) and issubclass(f_ann, Enum):
                    if isinstance(raw_value, str):
                        raw_val = raw_value.strip()
                        compact = re.sub(r"[^a-z0-9]+", "", raw_val.lower())
                        matched = None
                        for enum_member in f_ann:
                            enum_val = str(enum_member.value)
                            enum_compact = re.sub(r"[^a-z0-9]+", "", enum_val.lower())
                            if raw_val == enum_val or compact == enum_compact:
                                matched = enum_member.value
                                break
                        out[f_name] = matched if matched is not None else next(iter(f_ann)).value
                    else:
                        out[f_name] = next(iter(f_ann)).value
                    continue

                if f_ann is int:
                    out[f_name] = _clamp_score(f_name, _coerce_int(raw_value) if _coerce_int(raw_value) is not None else 0)
                    continue

                if f_ann is float:
                    try:
                        out[f_name] = float(raw_value)
                    except Exception:
                        out[f_name] = 0.0
                    continue

                if f_ann is str:
                    out[f_name] = _coerce_str(raw_value)
                    continue

                if f_origin is list:
                    if isinstance(raw_value, list):
                        out[f_name] = [str(x).strip() for x in raw_value if str(x).strip()]
                    elif isinstance(raw_value, str):
                        lines = [
                            line.strip().lstrip("-*•0123456789. ").strip()
                            for line in raw_value.replace("\r", "").split("\n")
                        ]
                        parts = [p for p in lines if p]
                        if len(parts) <= 1 and "," in raw_value:
                            parts = [p.strip() for p in raw_value.split(",") if p.strip()]
                        out[f_name] = parts
                    else:
                        out[f_name] = [str(raw_value)] if raw_value is not None else []
                    continue

                if isinstance(f_ann, type) and hasattr(f_ann, "model_fields"):
                    if isinstance(raw_value, str):
                        seg = _extract_json_segment(raw_value)
                        candidate = (seg or raw_value).strip()
                        try:
                            parsed_obj = json.loads(candidate)
                        except Exception:
                            parsed_obj = {}
                        if isinstance(parsed_obj, dict):
                            out[f_name] = _salvage_for_model(f_ann, parsed_obj)
                        else:
                            out[f_name] = _salvage_for_model(f_ann, {})
                    elif isinstance(raw_value, dict):
                        out[f_name] = _salvage_for_model(f_ann, raw_value)
                    else:
                        out[f_name] = _salvage_for_model(f_ann, {})
                    continue

                out[f_name] = raw_value

            return out

        def _coerce_int(value: Any) -> Any:
            if isinstance(value, bool):
                return int(value)
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return int(round(value))
            if isinstance(value, str):
                s = value.strip()
                if not s:
                    return value
                # Handles "7", "7.0", "7/10", "Score: 7", etc.
                match = re.search(r"-?\d+(?:\.\d+)?", s)
                if match:
                    try:
                        num = float(match.group(0))
                        return int(round(num))
                    except Exception:
                        return value
            return value

        normalized = dict(data)
        for field_name, field_info in output_model.model_fields.items():
            if field_name not in normalized:
                continue
            value = normalized[field_name]
            if value is None:
                continue

            ann = _unwrap_optional(field_info.annotation)
            ann_origin = get_origin(ann)
            is_list_field = ann_origin is list

            if field_name == "rerun_from_agent":
                normalized[field_name] = _coerce_rerun_agent(value)
                continue

            # Normalize enum values with forgiving case/format matching.
            if isinstance(ann, type) and issubclass(ann, Enum) and isinstance(value, str):
                raw_val = value.strip()
                compact = re.sub(r"[^a-z0-9]+", "", raw_val.lower())
                matched = None
                for enum_member in ann:
                    enum_val = str(enum_member.value)
                    enum_compact = re.sub(r"[^a-z0-9]+", "", enum_val.lower())
                    if raw_val == enum_val or compact == enum_compact:
                        matched = enum_member.value
                        break
                if matched is not None:
                    normalized[field_name] = matched
                    continue

            # Coerce integer-like fields from strings/floats.
            if ann is int:
                normalized[field_name] = _coerce_int(value)
                continue

            # Coerce string fields from non-string values.
            if ann is str and not isinstance(value, str):
                if isinstance(value, (int, float, bool)):
                    normalized[field_name] = str(value)
                    continue
                if isinstance(value, list):
                    normalized[field_name] = "; ".join(str(v).strip() for v in value if str(v).strip())
                    continue
                if isinstance(value, dict):
                    normalized[field_name] = json.dumps(value, default=str)
                    continue

            # If a dict/model field arrives as a JSON string, parse it.
            if ann_origin in {dict} and isinstance(value, str):
                seg = _extract_json_segment(value)
                candidate = (seg or value).strip()
                try:
                    parsed_obj = json.loads(candidate)
                    if isinstance(parsed_obj, dict):
                        normalized[field_name] = parsed_obj
                        continue
                except Exception:
                    pass

            # If a nested model field arrives as a JSON string, parse it to dict first.
            if isinstance(ann, type) and hasattr(ann, "model_fields") and isinstance(value, str):
                seg = _extract_json_segment(value)
                candidate = (seg or value).strip()
                try:
                    parsed_obj = json.loads(candidate)
                    if isinstance(parsed_obj, dict):
                        normalized[field_name] = parsed_obj
                        continue
                except Exception:
                    pass

            if is_list_field:
                if isinstance(value, str):
                    lines = [
                        line.strip().lstrip("-*•0123456789. ").strip()
                        for line in value.replace("\r", "").split("\n")
                    ]
                    parts = [p for p in lines if p]
                    if len(parts) <= 1 and "," in value:
                        parts = [p.strip() for p in value.split(",") if p.strip()]
                    normalized[field_name] = parts if parts else [value.strip()]
                elif isinstance(value, tuple | set):
                    normalized[field_name] = list(value)

        return normalized

    def _salvage_for_model(model_cls: Any, src: dict[str, Any]) -> dict[str, Any]:
        def _unwrap_optional(annotation: Any) -> Any:
            origin = get_origin(annotation)
            if origin is None:
                return annotation
            args = [a for a in get_args(annotation) if a is not type(None)]
            return args[0] if len(args) == 1 else annotation

        def _fallback_for(field_name: str, ann: Any) -> Any:
            origin = get_origin(ann)
            if origin is list:
                return []
            if origin is dict:
                return {}
            if isinstance(ann, type) and issubclass(ann, Enum):
                return next(iter(ann)).value
            if ann is int:
                return 5 if "score" in field_name else 0
            if ann is float:
                return 0.0
            if ann is str:
                return "Not provided"
            if isinstance(ann, type) and hasattr(ann, "model_fields"):
                return _salvage_for_model(ann, {})
            return None

        out: dict[str, Any] = {}
        for field_name, field_info in model_cls.model_fields.items():
            ann = _unwrap_optional(field_info.annotation)
            value = src.get(field_name)

            if value is None:
                if field_info.is_required():
                    out[field_name] = _fallback_for(field_name, ann)
                continue

            if ann is int:
                if isinstance(value, int):
                    out[field_name] = value
                elif isinstance(value, float):
                    out[field_name] = int(round(value))
                elif isinstance(value, str):
                    match = re.search(r"-?\d+(?:\.\d+)?", value)
                    out[field_name] = int(round(float(match.group(0)))) if match else _fallback_for(field_name, ann)
                else:
                    out[field_name] = _fallback_for(field_name, ann)
                if field_name.startswith("score_") or field_name in {
                    "clarity_score", "fit_score", "execution_score", "attractiveness_score", "competition_score"
                }:
                    out[field_name] = max(1, min(10, int(out[field_name])))
                continue

            if ann is float:
                try:
                    out[field_name] = float(value)
                except Exception:
                    out[field_name] = 0.0
                continue

            if ann is str:
                out[field_name] = value.strip() if isinstance(value, str) and value.strip() else str(value)
                continue

            origin = get_origin(ann)
            if origin is list:
                if isinstance(value, list):
                    out[field_name] = [str(v).strip() for v in value if str(v).strip()]
                elif isinstance(value, str):
                    parts = [p.strip() for p in re.split(r"\n|,", value) if p.strip()]
                    out[field_name] = parts
                else:
                    out[field_name] = []
                continue

            if isinstance(ann, type) and issubclass(ann, Enum):
                if isinstance(value, str):
                    compact = re.sub(r"[^a-z0-9]+", "", value.lower())
                    matched = None
                    for enum_member in ann:
                        enum_compact = re.sub(r"[^a-z0-9]+", "", str(enum_member.value).lower())
                        if compact == enum_compact or value == enum_member.value:
                            matched = enum_member.value
                            break
                    out[field_name] = matched if matched is not None else next(iter(ann)).value
                else:
                    out[field_name] = next(iter(ann)).value
                continue

            if isinstance(ann, type) and hasattr(ann, "model_fields"):
                if isinstance(value, dict):
                    out[field_name] = _salvage_for_model(ann, value)
                elif isinstance(value, str):
                    seg = _extract_json_segment(value)
                    if seg:
                        try:
                            parsed_obj = json.loads(seg)
                            out[field_name] = _salvage_for_model(ann, parsed_obj if isinstance(parsed_obj, dict) else {})
                        except Exception:
                            out[field_name] = _salvage_for_model(ann, {})
                    else:
                        out[field_name] = _salvage_for_model(ann, {})
                else:
                    out[field_name] = _salvage_for_model(ann, {})
                continue

            out[field_name] = value

        return out

    candidates: list[str] = [raw.strip()]

    for block in re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, flags=re.IGNORECASE):
        stripped = block.strip()
        if stripped:
            candidates.append(stripped)

    segment = _extract_json_segment(raw)
    if segment:
        candidates.append(segment.strip())

    seen: set[str] = set()
    unique_candidates: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            unique_candidates.append(candidate)

    for candidate in unique_candidates:
        try:
            parsed = output_model.model_validate_json(candidate)
            return parsed.model_dump(mode="json")
        except Exception:
            pass

        try:
            loaded = json.loads(candidate)
            if isinstance(loaded, list) and loaded and isinstance(loaded[0], dict):
                loaded = loaded[0]
            if isinstance(loaded, dict):
                normalized = _normalize_for_model(loaded)
                try:
                    parsed = output_model.model_validate(normalized)
                    return parsed.model_dump(mode="json")
                except Exception:
                    try:
                        salvaged = _salvage_for_model(output_model, normalized)
                        parsed = output_model.model_validate(salvaged)
                        return parsed.model_dump(mode="json")
                    except Exception:
                        continue
        except Exception:
            continue

    return None


def _parse_failure_reason(output_model: Any, raw: str) -> str | None:
    """Return a short reason why raw output failed schema validation."""
    candidates: list[str] = [raw.strip()]

    for block in re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, flags=re.IGNORECASE):
        stripped = block.strip()
        if stripped:
            candidates.append(stripped)

    segment = _extract_json_segment(raw)
    if segment:
        candidates.append(segment.strip())

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)

        # First try JSON string validation directly.
        try:
            output_model.model_validate_json(candidate)
            return None
        except Exception as exc:
            msg = str(exc)

        # Then try loading and validating as dict/list.
        try:
            loaded = json.loads(candidate)
            if isinstance(loaded, list) and loaded and isinstance(loaded[0], dict):
                loaded = loaded[0]
            if isinstance(loaded, dict):
                try:
                    output_model.model_validate(loaded)
                    return None
                except Exception as exc2:
                    msg = str(exc2)
            else:
                msg = "Top-level JSON is not an object."
        except Exception as exc3:
            msg = f"JSON decode error: {exc3}"

        msg = " ".join(msg.split())
        if len(msg) > 220:
            msg = msg[:217] + "..."
        return msg

    return "No JSON object candidate found in model output."


def _repair_output_to_json(agent: Any, output_model: Any, raw: str) -> dict[str, Any] | None:
    """Ask the model to convert its own raw output into strict JSON once parsing fails."""
    from crewai import Crew as _Crew, Task as _Task

    field_names = ", ".join(output_model.model_fields.keys())
    repair_prompt = (
        "Convert the following content into exactly one valid JSON object that matches the target schema.\n"
        "Output ONLY JSON. No markdown, no code fences, no commentary.\n"
        f"Required top-level keys: {field_names}.\n\n"
        "CONTENT TO CONVERT:\n"
        f"{raw}"
    )
    repair_task = _Task(
        description=repair_prompt,
        expected_output="One valid JSON object only.",
        agent=agent,
    )
    repair_crew = _Crew(agents=[agent], tasks=[repair_task], verbose=False)
    repair_result = repair_crew.kickoff()
    return _parse_output_to_dict(output_model, repair_result.raw)


def _default_output_for_model(output_model: Any, reason: str) -> dict[str, Any] | None:
    """Return a deterministic schema-valid fallback payload from model defaults."""
    try:
        payload = output_model.model_validate({}).model_dump(mode="json")
        payload["_schema_fallback"] = True
        payload["_schema_fallback_reason"] = reason
        return payload
    except Exception:
        return None

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
    execution_metrics: dict[str, Any] | None = None,
    is_generation: bool = False,
) -> None:
    """Write batch/generation summary with model table and token/cost breakdown."""
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
    
    # Execution Summary
    if execution_metrics:
        lines.append("## Execution Summary")
        lines.append("")
        metrics = execution_metrics
        lines.append(f"**Outer Rounds**: {metrics.get('outer_rounds', 'N/A')}")
        lines.append(f"**Startups Generated**: {metrics.get('startup_count', 'N/A')}")
        lines.append(f"**Ranking**: {'Yes' if metrics.get('has_ranking') else 'No'}")
        lines.append("")
        
        lines.append("### Inner Loop Details")
        lines.append("")
        max_inner = metrics.get("max_inner_attempts", "N/A")
        total_attempts = metrics.get("total_attempts_made", 0)
        actual_attempts = metrics.get("actual_attempts_per_round", [])
        
        if actual_attempts:
            lines.append(f"**Max Inner Attempts per Round**: {max_inner}")
            lines.append(f"**Total Inner Attempts Made**: {total_attempts}")
            lines.append("")
            lines.append("**Breakdown by Round**:")
            for idx, attempts in enumerate(actual_attempts, 1):
                lines.append(f"  - Round {idx}: {attempts} attempt(s)")
            lines.append("")
        
        total_runs = metrics.get("total_agent_runs", 0)
        lines.append(f"**Total Agent Invocations**: {total_runs}")
        lines.append(f"  - Inner loop (Agents 0,1,2): {sum(a*3 for a in actual_attempts)} invocations")
        lines.append(f"  - Full evaluation (Agents 3-6): {len(actual_attempts)*4} invocations")
        if metrics.get("has_ranking"):
            lines.append(f"  - Ranking (Agent 7): 1 invocation")
        lines.append("")
    
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

    (out_dir / ("generation_summary.md" if is_generation else "batch_summary.md")).write_text("\n".join(lines), encoding="utf-8")


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
    a0 = agent_outputs.get(0) or agent_outputs.get("0") or {}
    a1 = agent_outputs.get(1) or agent_outputs.get("1") or {}
    a2 = agent_outputs.get(2) or agent_outputs.get("2") or {}
    a3 = agent_outputs.get(3) or agent_outputs.get("3") or {}
    a4 = agent_outputs.get(4) or agent_outputs.get("4") or {}
    a5 = agent_outputs.get(5) or agent_outputs.get("5") or {}
    a6 = agent_outputs.get(6) or agent_outputs.get("6") or {}
    tags = agent_outputs.get("_tags") or []
    gen_meta = agent_outputs.get("_gen_meta") or {}

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

    # --- Agent 0: Idea Generation (only if present) ---
    if a0:
        lines.append("## 0. Idea Generation (Agent 0)")
        lines.append("")
        if gen_meta:
            lines.append(f"**Round:** {gen_meta.get('round', 'N/A')} | **Attempt:** {gen_meta.get('attempt', 'N/A')}")
            lines.append("")
        lines.append(f"**Strategy Notes:** {g(a0, 'strategy_notes')}")
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
    execution_metrics: dict[str, Any] | None = None,
    is_generation: bool = False,
    is_batch_mode: bool = False,
) -> Path:
    """Write pipeline results as JSON files.
    
    Output locations:
    - Batch mode: output/Batch/<batch_id>/
    - Generate mode: output/Generated/<batch_id>/
    - Single mode: output/<batch_id>/
    """
    if is_batch_mode:
        out_dir = PROJECT_ROOT / "output" / "Batch" / batch_id
    elif is_generation:
        out_dir = PROJECT_ROOT / "output" / "Generated" / batch_id
    else:
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

    _write_batch_summary(batch_id, out_dir, individual, ranking_usage, execution_metrics, is_generation)

    return out_dir


SCREENING_THRESHOLD = 50  # Weighted score on 0-80 scale
INNER_LOOP_MAX_ATTEMPTS = 5


def _run_candidate_through_screening(
    constraints: dict[str, Any],
    screening_feedback: dict[str, Any] | None,
    prior_evaluation: dict[str, Any] | None,
    prior_score: dict[str, Any] | None,
    round_number: int,
    attempt_number: int,
    force_completely_new_idea: bool,
    current_round: int,
    total_rounds: int,
    inner_attempt: int,
    total_inner_attempts: int,
    candidate_index: int = 1,
) -> dict[str, Any] | None:
    """Run a single candidate through Agent 0 → Agent 1 → Agent 2 (screening phase).
    
    Returns a dict with score, a0, a1, a2 outputs, submission, attempt info, and usage.
    Returns None if the candidate fails to parse at Agent 2.
    """
    from src.pipeline import _compute_weighted_score, _check_reject_signals
    
    # Run Agent 0
    a0_output, a0_usage = _run_single_agent(
        agent_number=0,
        submission_text="",
        agent0_task_kwargs={
            "constraints": constraints,
            "screening_feedback": screening_feedback,
            "prior_evaluation": prior_evaluation,
            "prior_score": prior_score,
            "round_number": round_number,
            "attempt_number": attempt_number,
            "force_completely_new_idea": force_completely_new_idea,
        },
        current_round=current_round,
        total_rounds=total_rounds,
        inner_attempt=inner_attempt,
        total_inner_attempts=total_inner_attempts,
    )
    startup_name = a0_output.get("startup_name", "Generated Startup")
    submission_text = a0_output.get("submission_text", "")
    
    # Run Agent 1 (Intake Parser)
    a1_output, a1_usage = _run_single_agent(
        agent_number=1,
        submission_text=submission_text,
        current_round=current_round,
        total_rounds=total_rounds,
        inner_attempt=inner_attempt,
        total_inner_attempts=total_inner_attempts,
    )
    
    # Run Agent 2 (Venture Analyst)
    a2_output, a2_usage = _run_single_agent(
        agent_number=2,
        submission_text=submission_text,
        prior_context={1: a1_output},
        current_round=current_round,
        total_rounds=total_rounds,
        inner_attempt=inner_attempt,
        total_inner_attempts=total_inner_attempts,
    )
    
    # Check for parse failure
    if a2_output.get("_parse_failed"):
        return None
    
    # Compute weighted score
    weighted_score, score_tier = _compute_weighted_score(a2_output)
    a2_output["weighted_total_score"] = weighted_score
    a2_output["score_tier"] = score_tier
    reject_signals = _check_reject_signals(a2_output)
    a2_output["reject_signals"] = reject_signals
    
    return {
        "score": weighted_score,
        "a0": a0_output,
        "a1": a1_output,
        "a2": a2_output,
        "submission": submission_text,
        "attempt": attempt_number,
        "candidate_index": candidate_index,
        "usage": {0: a0_usage, 1: a1_usage, 2: a2_usage},
    }


def _show_agent_timer(
    agent_number: int,
    model_name: str,
    stop_event: threading.Event,
    current_round: int | None = None,
    total_rounds: int | None = None,
    inner_attempt: int | None = None,
    total_inner_attempts: int | None = None,
) -> None:
    """Show a live-updating elapsed timer for a running agent."""
    role = AGENT_ROLES.get(agent_number, "Unknown")
    start = time.time()
    previous_len = 0

    # Assign a unique color per agent for easy identification
    agent_colors = [
        Colors.BRIGHT_GREEN,   # Agent 0
        Colors.BRIGHT_CYAN,   # Agent 1
        Colors.BRIGHT_MAGENTA, # Agent 2
        Colors.BRIGHT_YELLOW,  # Agent 3
        Colors.BRIGHT_BLUE,    # Agent 4
        Colors.BRIGHT_RED,     # Agent 5
        Colors.BRIGHT_GREEN,   # Agent 6
        Colors.BRIGHT_CYAN,    # Agent 7
    ]
    agent_color = agent_colors[agent_number % len(agent_colors)]

    def _fit_to_terminal(text: str) -> str:
        # Keep the timer on a single terminal row to prevent wrapped "new lines".
        cols = shutil.get_terminal_size(fallback=(120, 24)).columns
        usable = max(20, cols - 1)
        return text[:usable]

    while not stop_event.is_set():
        elapsed = int(time.time() - start)
        mins, secs = divmod(elapsed, 60)
        round_ctx = ""
        inner_ctx = ""
        if current_round is not None and total_rounds is not None:
            round_ctx = f" | Round {current_round}/{total_rounds}"
        if inner_attempt is not None and total_inner_attempts is not None:
            inner_ctx = f" | Inner {inner_attempt}/{total_inner_attempts}"
        
        # Use color for agent number and role
        msg = f"    {_colorize('⏱', Colors.DIM)} {_colorize(f'Agent {agent_number}', agent_color)} ({_colorize(role, Colors.DIM)}) [{model_name}]{round_ctx}{inner_ctx} ... {mins}m {secs}s"
        msg = _fit_to_terminal(msg)
        # Overwrite in-place and erase any leftover chars from the previous tick.
        clear_tail = " " * max(0, previous_len - len(msg))
        sys.stdout.write(f"\r{msg}{clear_tail}")
        sys.stdout.flush()
        previous_len = len(msg)
        time.sleep(1)

    # Clear the timer line once on exit.
    sys.stdout.write("\r" + " " * previous_len + "\r")
    sys.stdout.flush()


def _run_single_agent(
    agent_number: int,
    submission_text: str,
    prior_context: dict[int, Any] | None = None,
    agent0_task_kwargs: dict[str, Any] | None = None,
    current_round: int | None = None,
    total_rounds: int | None = None,
    inner_attempt: int | None = None,
    total_inner_attempts: int | None = None,
) -> tuple[dict, dict]:
    """Run a single agent in a one-agent CrewAI Crew and return (output_dict, usage_dict).

    For Agent 0, pass agent0_task_kwargs with the arguments for create_agent0_task().
    For Agents 1-6, uses the standard create_task().
    """
    from crewai import Crew, Task

    from src.agents import create_agent
    from src.config import get_model_for_agent
    from src.models import AGENT_OUTPUT_MODELS
    from src.tasks import create_agent0_task, create_task

    model_name = get_model_for_agent(agent_number)
    role = AGENT_ROLES.get(agent_number, "Unknown")
    agent = create_agent(agent_number)

    if agent_number == 0:
        task = create_agent0_task(agent=agent, **(agent0_task_kwargs or {}))
    else:
        task = create_task(
            agent_number=agent_number,
            agent=agent,
            submission_text=submission_text,
            prior_context=prior_context,
        )

    # MiniMax can fail with Instructor "multiple tool calls" on structured output.
    if not _supports_structured_output(model_name):
        task = Task(
            description=task.description,
            expected_output=task.expected_output,
            agent=agent,
        )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)

    # Start live timer
    stop_event = threading.Event()
    agent_start = time.time()
    timer_thread = threading.Thread(
        target=_show_agent_timer,
        args=(
            agent_number,
            model_name,
            stop_event,
            current_round,
            total_rounds,
            inner_attempt,
            total_inner_attempts,
        ),
        daemon=True,
    )
    timer_thread.start()

    def _usage_parts(u: Any) -> tuple[int, int, int]:
        return (
            int(getattr(u, "prompt_tokens", 0) or 0),
            int(getattr(u, "completion_tokens", 0) or 0),
            int(getattr(u, "total_tokens", 0) or 0),
        )

    def _kickoff_with_retry(crew_obj: Any, max_retries: int = 3) -> Any:
        """Execute crew.kickoff() with exponential backoff retry for transient network errors."""
        for attempt in range(max_retries):
            try:
                return crew_obj.kickoff()
            except Exception as e:
                exc_msg_l = str(e).lower()
                is_transient = (
                    "connection reset by peer" in exc_msg_l
                    or "connectionerror" in exc_msg_l
                    or "apiconnectionerror" in type(e).__name__.lower()
                    or "readtimeout" in exc_msg_l
                    or "readerror" in type(e).__name__.lower()
                )
                if not is_transient or attempt == max_retries - 1:
                    raise
                wait_secs = 2 ** attempt
                print(f"\n    ⚠ Transient network error for Agent {agent_number} (attempt {attempt + 1}/{max_retries}), retrying in {wait_secs}s...")
                time.sleep(wait_secs)

    usage_acc = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    result = None
    try:
        result = _kickoff_with_retry(crew)
        p, c, t = _usage_parts(result.token_usage)
        usage_acc["prompt_tokens"] += p
        usage_acc["completion_tokens"] += c
        usage_acc["total_tokens"] += t
    except Exception as exc:
        # Some providers (e.g. MiniMax) trigger "multiple tool calls" errors
        # with structured output. Retry without Pydantic output and parse raw.
        exc_msg = str(exc)
        exc_msg_l = exc_msg.lower()
        if (
            "multiple tool calls" in exc_msg_l
            or "instructor does not support multiple tool calls" in exc_msg_l
            or "instructorretryexception" in type(exc).__name__.lower()
        ):
            print(f"\n    ⚠ Structured output failed for Agent {agent_number}, retrying with raw output...")
            task_fallback = Task(
                description=task.description,
                expected_output=task.expected_output,
                agent=agent,
            )
            crew_fallback = Crew(agents=[agent], tasks=[task_fallback], verbose=False)
            result = _kickoff_with_retry(crew_fallback)
            p, c, t = _usage_parts(result.token_usage)
            usage_acc["prompt_tokens"] += p
            usage_acc["completion_tokens"] += c
            usage_acc["total_tokens"] += t
        else:
            raise
    finally:
        stop_event.set()
        timer_thread.join(timeout=2)

    # Report completion time
    duration = time.time() - agent_start
    mins, secs = divmod(int(duration), 60)
    print(f"    ✓ Agent {agent_number} ({role}) completed in {mins}m {secs}s")

    # Extract output
    output_model = AGENT_OUTPUT_MODELS[agent_number]
    if result.pydantic:
        output_dict = result.pydantic.model_dump(mode="json")
    else:
        parsed_dict = _parse_output_to_dict(output_model, result.raw)
        if parsed_dict is not None:
            output_dict = parsed_dict
        else:
            reason = _parse_failure_reason(output_model, result.raw)
            repaired = None
            try:
                repaired = _repair_output_to_json(agent, output_model, result.raw)
            except Exception:
                repaired = None

            if repaired is not None:
                print(f"    ✓ Agent {agent_number} JSON repaired successfully")
                output_dict = repaired
            else:
                print(f"    ⚠ Could not parse Agent {agent_number} output into expected schema; attempting JSON repair...")
                if reason:
                    print(f"    ↳ Parse diagnostic: {reason}")
                # High-impact agents (1, 2, 6): do one strict rerun before giving up.
                if agent_number in {1, 2, 6}:
                    print(f"    ⚠ JSON repair failed for Agent {agent_number}; running strict format rerun...")
                    field_names = ", ".join(output_model.model_fields.keys())
                    strict_task = Task(
                        description=(
                            task.description
                            + "\n\nCRITICAL OUTPUT REQUIREMENT:\n"
                            + "Return EXACTLY one valid JSON object and nothing else.\n"
                            + "Do not include markdown, backticks, commentary, or prose.\n"
                            + f"Required top-level keys: {field_names}.\n"
                            + "All required fields must be present and valid."
                        ),
                        expected_output=task.expected_output,
                        agent=agent,
                    )
                    strict_crew = Crew(agents=[agent], tasks=[strict_task], verbose=False)
                    strict_result = None
                    try:
                        strict_result = strict_crew.kickoff()
                        p, c, t = _usage_parts(strict_result.token_usage)
                        usage_acc["prompt_tokens"] += p
                        usage_acc["completion_tokens"] += c
                        usage_acc["total_tokens"] += t
                    except Exception:
                        strict_result = None

                    strict_parsed = None
                    if strict_result is not None:
                        if strict_result.pydantic:
                            strict_parsed = strict_result.pydantic.model_dump(mode="json")
                        else:
                            strict_parsed = _parse_output_to_dict(output_model, strict_result.raw)
                            if strict_parsed is None:
                                try:
                                    strict_parsed = _repair_output_to_json(agent, output_model, strict_result.raw)
                                except Exception:
                                    strict_parsed = None

                    if strict_parsed is not None:
                        print(f"    ✓ Agent {agent_number} strict rerun produced valid JSON")
                        output_dict = strict_parsed
                    else:
                        print(f"    ⚠ Agent {agent_number} strict rerun also failed")
                        fallback = _default_output_for_model(
                            output_model,
                            reason=f"Agent {agent_number} parse/repair/rerun failed",
                        )
                        if fallback is not None:
                            print(f"    ✓ Agent {agent_number} using deterministic schema fallback")
                            output_dict = fallback
                        else:
                            output_dict = {"raw_output": result.raw, "_parse_failed": True}
                else:
                    print(f"    ⚠ JSON repair failed for Agent {agent_number}")
                    output_dict = {"raw_output": result.raw, "_parse_failed": True}

    # Token usage
    usage_dict = {
        "model": model_name,
        "prompt_tokens": usage_acc["prompt_tokens"],
        "completion_tokens": usage_acc["completion_tokens"],
        "total_tokens": usage_acc["total_tokens"],
    }

    return output_dict, usage_dict


def _parse_generate_args(args: list[str]) -> dict[str, Any]:
    """Parse CLI flags for the generate command into a config dict."""
    from src.config import BEST_OF_N, ENABLE_HALL_OF_FAME, ENABLE_DIMENSION_REASONING
    
    config: dict[str, Any] = {
        "team_size": 1,
        "experience": "Founder starting from scratch without any previous experience to help him",
        "network": None,
        "availability": "100%",
        "locale": "unspecified, assume global",
        "capital": "Very low",
        "traction": "Zero — no customers, no revenue, no prototype",
        "languages": "English",
        "industry": "Unspecified",
        "rounds": 3,
        "name": None,
        # Quick Wins optimizations
        "best_of_n": BEST_OF_N,
        "enable_hall_of_fame": ENABLE_HALL_OF_FAME,
        "enable_dimension_reasoning": ENABLE_DIMENSION_REASONING,
    }

    i = 0
    while i < len(args):
        flag = args[i]
        if flag == "--rounds" and i + 1 < len(args):
            config["rounds"] = int(args[i + 1])
            i += 2
        elif flag == "--team-size" and i + 1 < len(args):
            config["team_size"] = int(args[i + 1])
            i += 2
        elif flag == "--experience" and i + 1 < len(args):
            config["experience"] = args[i + 1]
            i += 2
        elif flag == "--network" and i + 1 < len(args):
            config["network"] = args[i + 1]
            i += 2
        elif flag == "--availability" and i + 1 < len(args):
            config["availability"] = args[i + 1]
            i += 2
        elif flag == "--locale" and i + 1 < len(args):
            config["locale"] = args[i + 1]
            i += 2
        elif flag == "--capital" and i + 1 < len(args):
            config["capital"] = args[i + 1]
            i += 2
        elif flag == "--traction" and i + 1 < len(args):
            config["traction"] = args[i + 1]
            i += 2
        elif flag == "--languages" and i + 1 < len(args):
            config["languages"] = args[i + 1]
            i += 2
        elif flag == "--industry" and i + 1 < len(args):
            config["industry"] = args[i + 1]
            i += 2
        elif flag == "--name" and i + 1 < len(args):
            config["name"] = args[i + 1]
            i += 2
        elif flag == "--best-of-n" and i + 1 < len(args):
            n = int(args[i + 1])
            if not 1 <= n <= 10:
                print(f"Warning: --best-of-n must be between 1 and 10, got {n}. Using default.")
            else:
                config["best_of_n"] = n
            i += 2
        elif flag == "--no-hall-of-fame":
            config["enable_hall_of_fame"] = False
            i += 1
        elif flag == "--no-dimension-reasoning":
            config["enable_dimension_reasoning"] = False
            i += 1
        else:
            print(f"Unknown flag: {flag}")
            i += 1

    return config


def run_generate(config: dict[str, Any]) -> None:
    """Run the generate pipeline with nested inner/outer feedback loops."""
    from src.pipeline import _compute_weighted_score, _check_reject_signals, _compute_tags, StartupEvalPipeline
    from src.db import init_db, create_batch
    from src.models import Recommendation, Verdict

    rounds = config.pop("rounds")
    given_name = config.pop("name")

    # Build founder constraints from remaining config
    constraints: dict[str, Any] = {}
    for key in ["team_size", "experience", "network", "availability", "locale", "capital", "traction", "languages", "industry"]:
        val = config.get(key)
        if val is not None:
            constraints[key] = val

    batch_id = _next_generated_id()
    all_results: dict[str, dict[int, Any]] = {}
    score_progression: list[tuple[str, float, str]] = []

    # Execution metrics tracking
    actual_attempts_per_round: list[int] = []
    total_attempts_made = 0
    
    # Outer loop feedback state
    prior_evaluation: dict[str, Any] | None = None
    prior_score: dict[str, Any] | None = None
    non_strong_positive_streak = 0

    pipeline_start = time.time()

    def _elapsed() -> str:
        e = int(time.time() - pipeline_start)
        mins, secs = divmod(e, 60)
        return f"{mins}m {secs}s"

    print(f"\n{_colorize('#' * 60, Colors.BRIGHT_MAGENTA)}")
    print(f"  {_colorize('EvalBot — Generate Mode', Colors.BRIGHT_CYAN + Colors.BOLD)}")
    print(f"  {_colorize('Batch:', Colors.DIM)} {batch_id} | {_colorize('Rounds:', Colors.DIM)} {rounds}")
    print(f"  {_colorize('Started:', Colors.DIM)} {datetime.now().strftime('%H:%M:%S')}")
    print(f"  {_colorize('Structure:', Colors.DIM)} Each round runs inner loop (Agent 0,1,2) up to {INNER_LOOP_MAX_ATTEMPTS} times,")
    print(f"             then agents 3-6 on best candidate | {_colorize('Screening threshold:', Colors.DIM)} {SCREENING_THRESHOLD}/80")
    print(f"{'#'*60}")
    print(f"\n  Constraints:")
    for k, v in constraints.items():
        print(f"    {k.replace('_', ' ').title()}: {v}")
    print()

    # Load Hall of Fame examples for this batch (if enabled)
    hall_of_fame_examples: list[dict] = []
    if config.get("enable_hall_of_fame", True):
        from src.db import get_top_ideas
        hall_of_fame_examples = get_top_ideas(limit=5, min_score=60)
        if hall_of_fame_examples:
            print(f"  {_colorize('Hall of Fame:', Colors.BRIGHT_CYAN)} Loaded {len(hall_of_fame_examples)} top-scoring examples")
            for i, ex in enumerate(hall_of_fame_examples, 1):
                score = ex.get('weighted_score', 0)
                score_color = Colors.BRIGHT_GREEN if score >= 60 else Colors.BRIGHT_YELLOW
                print(f"    {_colorize(f'{i}.', Colors.DIM)} {ex.get('startup_name', 'Unknown')} ({_colorize(f'Score: {score:.1f}/80', score_color)})")
        else:
            print(f"  {_colorize('Hall of Fame:', Colors.DIM)} No examples yet (need scores >= 60)")
    print()

    for round_num in range(1, rounds + 1):
        print(f"\n{_colorize('=' * 60, Colors.DIM)}")
        streak_info = f"(non-strong-positive streak: {non_strong_positive_streak})" if non_strong_positive_streak > 0 else ""
        print(f"  {_colorize('OUTER ROUND', Colors.BOLD)} {_colorize(f'{round_num}/{rounds}', Colors.BRIGHT_YELLOW)} {streak_info}")
        print(f"  [{_elapsed()} elapsed]")
        print(f"{_colorize('=' * 60, Colors.DIM)}")

        # --- Best-of-N + Inner loop: Generate N candidates, then run screening ---
        best_attempt: dict[str, Any] | None = None
        screening_feedback: dict[str, Any] | None = None
        
        # Extract Best-of-N config
        best_of_n = config.get("best_of_n", 1)
        enable_hall_of_fame = config.get("enable_hall_of_fame", True)
        enable_dimension_reasoning = config.get("enable_dimension_reasoning", True)
        
        # Determine if we need to force a completely new idea (same logic as inner loop)
        force_completely_new_idea = non_strong_positive_streak >= 2 and round_num > 1
        
        # If Best-of-N > 1, generate candidates in parallel using threading
        if best_of_n > 1:
            print(f"\n  {_colorize('⚡ BEST-OF-N', Colors.BRIGHT_CYAN)}: Generating {_colorize(str(best_of_n), Colors.BRIGHT_YELLOW)} candidates in parallel...")
            
            # For Best-of-N, we don't use screening feedback on first pass
            # (it's per-candidate, not cumulative)
            candidates: list[dict[str, Any]] = []
            
            # Import ThreadPoolExecutor for parallel execution
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            # Track which candidates are running
            running_candidates: dict[int, float] = {}  # cand_idx -> start time
            lock = threading.Lock()
            candidate_colors = [Colors.BRIGHT_GREEN, Colors.BRIGHT_MAGENTA, Colors.BRIGHT_CYAN, Colors.BRIGHT_YELLOW, Colors.BRIGHT_BLUE]
            
            def run_single_candidate(cand_idx: int) -> dict[str, Any] | None:
                """Run a single candidate through Agent 0 → 1 → 2."""
                nonlocal running_candidates
                
                # Register this candidate as running
                with lock:
                    running_candidates[cand_idx] = time.time()
                
                try:
                    # Run Agent 0
                    a0_output, a0_usage = _run_single_agent(
                        agent_number=0,
                        submission_text="",
                        agent0_task_kwargs={
                            "constraints": constraints,
                            "screening_feedback": None,  # No feedback on first pass
                            "prior_evaluation": prior_evaluation,
                            "prior_score": prior_score,
                            "round_number": round_num,
                            "attempt_number": cand_idx,
                            "force_completely_new_idea": force_completely_new_idea,
                            "hall_of_fame_examples": hall_of_fame_examples if enable_hall_of_fame else None,
                            "enable_dimension_reasoning": enable_dimension_reasoning,
                        },
                        current_round=round_num,
                        total_rounds=rounds,
                        inner_attempt=cand_idx,
                        total_inner_attempts=best_of_n,
                    )
                    startup_name = a0_output.get("startup_name", f"Generated {cand_idx}")
                    submission_text = a0_output.get("submission_text", "")
                    
                    # Debug: Print Agent 0 output for debugging
                    if not submission_text:
                        print(f"    {_colorize('⚠ DEBUG:', Colors.BRIGHT_RED)} Agent 0 returned empty submission_text!")
                        print(f"       startup_name: {startup_name}")
                        print(f"       full output: {a0_output}")
                    else:
                        print(f"    • {_colorize('[Agent 0: Generator]', Colors.BRIGHT_GREEN)} {_colorize(startup_name, Colors.WHITE)}")
                    
                    # Run Agent 1 (Intake Parser)
                    a1_output, a1_usage = _run_single_agent(
                        agent_number=1,
                        submission_text=submission_text,
                        current_round=round_num,
                        total_rounds=rounds,
                        inner_attempt=cand_idx,
                        total_inner_attempts=best_of_n,
                    )
                    
                    # Run Agent 2 (Venture Analyst)
                    a2_output, a2_usage = _run_single_agent(
                        agent_number=2,
                        submission_text=submission_text,
                        prior_context={1: a1_output},
                        current_round=round_num,
                        total_rounds=rounds,
                        inner_attempt=cand_idx,
                        total_inner_attempts=best_of_n,
                    )
                    
                    # Compute weighted score
                    weighted_score, score_tier = _compute_weighted_score(a2_output)
                    a2_output["weighted_total_score"] = weighted_score
                    a2_output["score_tier"] = score_tier
                    reject_signals = _check_reject_signals(a2_output)
                    a2_output["reject_signals"] = reject_signals
                    
                    return {
                        "score": weighted_score,
                        "a0": a0_output,
                        "a1": a1_output,
                        "a2": a2_output,
                        "submission": submission_text,
                        "attempt": cand_idx,
                        "candidate_index": cand_idx,
                        "usage": {0: a0_usage, 1: a1_usage, 2: a2_usage},
                    }
                except Exception as e:
                    print(f"    {_colorize('⚠', Colors.BRIGHT_RED)} Candidate {cand_idx} failed with error: {e}")
                    return None
                finally:
                    # Remove from running list
                    with lock:
                        if cand_idx in running_candidates:
                            del running_candidates[cand_idx]
            
            # Run candidates in parallel using ThreadPoolExecutor
            print(f"\n  Starting {_colorize(str(best_of_n), Colors.BRIGHT_YELLOW)} parallel workflows...")
            
            def _show_parallel_progress():
                """Show live progress of running parallel candidates."""
                while True:
                    with lock:
                        if not running_candidates:
                            return
                        running = list(running_candidates.keys())
                    
                    if running:
                        elapsed = int(time.time() - list(running_candidates.values())[0])
                        mins, secs = divmod(elapsed, 60)
                        status = ", ".join([f"{c}" for c in running])
                        print(f"\r  {_colorize('▓', Colors.BRIGHT_GREEN)} Running: [{status}] | Elapsed: {mins}m {secs}s", end="")
                        sys.stdout.flush()
                    time.sleep(2)
            
            # Start progress display thread
            progress_thread = threading.Thread(target=_show_parallel_progress, daemon=True)
            progress_thread.start()
            
            with ThreadPoolExecutor(max_workers=best_of_n) as executor:
                futures = {executor.submit(run_single_candidate, idx): idx for idx in range(1, best_of_n + 1)}
                
                for future in as_completed(futures):
                    cand_idx = futures[future]
                    try:
                        candidate = future.result()
                        if candidate is not None:
                            candidates.append(candidate)
                            score = candidate['score']
                            color = Colors.BRIGHT_GREEN if score >= 50 else Colors.BRIGHT_YELLOW if score >= 30 else Colors.BRIGHT_RED
                            print(f"    {_colorize('✓', Colors.BRIGHT_GREEN)} Candidate {cand_idx} → {_colorize(f'Score: {score}/80', color)} ({_colorize(candidate['a2'].get('score_tier', 'N/A'), Colors.BRIGHT_CYAN)})")
                    except Exception as e:
                        print(f"    {_colorize('⚠', Colors.BRIGHT_RED)} Candidate {cand_idx} threw exception: {e}")
            
            # Clear progress line
            print("\r" + " " * 60 + "\r", end="")
            
            # Select best candidate
            if not candidates:
                print(f"\n  {_colorize('✗ No candidates completed successfully!', Colors.BRIGHT_RED)}")
                continue
            
            candidates.sort(key=lambda x: x["score"], reverse=True)
            best_candidate = candidates[0]
            best_attempt = best_candidate
            
            print(f"\n  {_colorize('✓ Best-of-N selected:', Colors.BRIGHT_GREEN)} {best_candidate['a0'].get('startup_name', 'Unknown')}")
            print(f"    Score: {_colorize(str(best_candidate['score']), Colors.BRIGHT_CYAN)}/80")
            
            # If didn't pass screening, set up for retry loop
            if best_candidate["score"] < SCREENING_THRESHOLD:
                screening_feedback = best_candidate["a2"]
                print(f"  {_colorize('└─ ✗ BEST-OF-N FAILED screening', Colors.BRIGHT_RED)} ({best_candidate['score']} < {SCREENING_THRESHOLD})")
                print(f"     {_colorize('↻ Falling back to retry loop...', Colors.BRIGHT_YELLOW)}")
        
        # If best_of_n=1 or Best-of-N failed, run standard retry loop
        if best_of_n == 1 or (best_attempt is not None and best_attempt["score"] < SCREENING_THRESHOLD):
            # Reset best_attempt if Best-of-N failed (to avoid using low-scoring candidate)
            if best_of_n > 1 and best_attempt is not None and best_attempt["score"] < SCREENING_THRESHOLD:
                best_attempt = None
            
            # Continue with retry loop (original logic)
            for attempt in range(1, INNER_LOOP_MAX_ATTEMPTS + 1):
                print(f"\n  {_colorize('┌─', Colors.DIM)} INNER LOOP  {_colorize(f'Attempt {attempt}/{INNER_LOOP_MAX_ATTEMPTS}', Colors.BRIGHT_YELLOW)}  [{_elapsed()}]")

                # If the prior two outer rounds were not strongly positive, force exploration.
                force_completely_new_idea = non_strong_positive_streak >= 2 and round_num > 1
                if force_completely_new_idea and attempt == 1:
                    print(f"    {_colorize('⚠', Colors.BRIGHT_RED)} [{_colorize('FORCED RESTART', Colors.BRIGHT_RED)}]  Generating a completely new direction...")

                # Run Agent 0
                a0_output, a0_usage = _run_single_agent(
                    agent_number=0,
                    submission_text="",
                    agent0_task_kwargs={
                        "constraints": constraints,
                        "screening_feedback": screening_feedback,
                        "prior_evaluation": prior_evaluation,
                        "prior_score": prior_score,
                        "round_number": round_num,
                        "attempt_number": attempt,
                        "force_completely_new_idea": force_completely_new_idea,
                        "hall_of_fame_examples": hall_of_fame_examples if enable_hall_of_fame else None,
                        "enable_dimension_reasoning": enable_dimension_reasoning,
                    },
                    current_round=round_num,
                    total_rounds=rounds,
                    inner_attempt=attempt,
                    total_inner_attempts=INNER_LOOP_MAX_ATTEMPTS,
                )
                startup_name = a0_output.get("startup_name", "Generated Startup")
                submission_text = a0_output.get("submission_text", "")
                if not submission_text:
                    print(f"    {_colorize('⚠ DEBUG:', Colors.BRIGHT_RED)} Agent 0 returned empty submission_text!")
                    print(f"       startup_name: {startup_name}")
                    print(f"       full output: {a0_output}")
                else:
                    print(f"    • {_colorize('[Agent 0: Generator]', Colors.BRIGHT_GREEN)} {_colorize(startup_name, Colors.WHITE)}")
                strategy = a0_output.get("strategy_notes", "")
                if strategy:
                    print(f"      {_colorize('Strategy:', Colors.DIM)} {strategy[:150]}...")

                # Run Agent 1 (Intake Parser)
                a1_output, a1_usage = _run_single_agent(
                    agent_number=1,
                    submission_text=submission_text,
                    current_round=round_num,
                    total_rounds=rounds,
                    inner_attempt=attempt,
                    total_inner_attempts=INNER_LOOP_MAX_ATTEMPTS,
                )
                print(f"    • {_colorize('[Agent 1: Intake Parser]', Colors.BRIGHT_CYAN)} Processing submission...")

                # Run Agent 2 (Venture Analyst)
                a2_output, a2_usage = _run_single_agent(
                    agent_number=2,
                    submission_text=submission_text,
                    prior_context={1: a1_output},
                    current_round=round_num,
                    total_rounds=rounds,
                    inner_attempt=attempt,
                    total_inner_attempts=INNER_LOOP_MAX_ATTEMPTS,
                )
                print(f"    • {_colorize('[Agent 2: Venture Analyst]', Colors.BRIGHT_MAGENTA)} Scoring...")  

                # Do not score unparseable Agent 2 output as 0/N/A.
                if a2_output.get("_parse_failed"):
                    print(f"    {_colorize('⚠', Colors.BRIGHT_RED)} Agent 2 output was not parseable JSON. Skipping scoring for this attempt.")
                    screening_feedback = {
                        "verdict": "Parse Failure",
                        "explanation": (
                            "Agent 2 returned output that could not be parsed into the required schema. "
                            "Return exactly one valid JSON object with all required keys and valid enum values."
                        ),
                    }
                    if attempt < INNER_LOOP_MAX_ATTEMPTS:
                        print(f"  {_colorize('└─ ✗ INVALID Agent 2 output format', Colors.BRIGHT_RED)}")
                        print(f"     {_colorize('↻ Retrying with stricter formatting feedback...', Colors.BRIGHT_YELLOW)}")
                    else:
                        print(f"  {_colorize('└─ ✗ INVALID Agent 2 output format (final inner attempt)', Colors.BRIGHT_RED)}")
                    continue

                # Compute weighted score
                weighted_score, score_tier = _compute_weighted_score(a2_output)
                a2_output["weighted_total_score"] = weighted_score
                a2_output["score_tier"] = score_tier
                reject_signals = _check_reject_signals(a2_output)
                a2_output["reject_signals"] = reject_signals

                # Color the score based on value
                score_color = Colors.BRIGHT_GREEN if weighted_score >= 50 else Colors.BRIGHT_YELLOW if weighted_score >= 30 else Colors.BRIGHT_RED
                tier_color = Colors.BRIGHT_GREEN if score_tier == "Strong Positive" else Colors.BRIGHT_YELLOW if score_tier == "Positive" else Colors.BRIGHT_RED if score_tier == "Negative" else Colors.DIM
                print(f"    • {_colorize(f'Score: {weighted_score}/80', score_color)} ({_colorize(score_tier, tier_color)}) | {_colorize('Verdict:', Colors.DIM)} {a2_output.get('verdict', 'N/A')}")
                if reject_signals:
                    print(f"    → {_colorize('Reject signals:', Colors.BRIGHT_RED)} {', '.join(reject_signals)}")

                # Track best attempt
                current = {
                    "score": weighted_score,
                    "a0": a0_output,
                    "a1": a1_output,
                    "a2": a2_output,
                    "submission": submission_text,
                    "attempt": attempt,
                    "usage": {0: a0_usage, 1: a1_usage, 2: a2_usage},
                }
                if best_attempt is None or weighted_score > best_attempt["score"]:
                    best_attempt = current

                if weighted_score >= SCREENING_THRESHOLD:
                    print(f"  └─ ✓ PASSED screening ({weighted_score} >= {SCREENING_THRESHOLD})")
                    break
                else:
                    print(f"  └─ ✗ FAILED screening ({weighted_score} < {SCREENING_THRESHOLD})")
                    screening_feedback = a2_output
                    if attempt < INNER_LOOP_MAX_ATTEMPTS:
                        print(f"     ↻ Retrying with feedback...")

        if best_attempt is None:
            print("  ERROR: No attempts completed. Skipping round.")
            continue

        actual_attempt = best_attempt["attempt"]
        actual_attempts_per_round.append(actual_attempt)
        total_attempts_made += actual_attempt
        
        if best_attempt["score"] < SCREENING_THRESHOLD:
            print(f"\n  Inner loop exhausted — using best attempt (score {best_attempt['score']}/80)")

        # --- Continue with Agents 3-6 using the best/passing attempt ---
        startup_name = best_attempt["a0"].get("startup_name", "Generated Startup")
        submission_text = best_attempt["submission"]
        used_attempt = best_attempt["attempt"]

        print(f"\n  ──────────────────────────────────────")
        print(f"  Full Evaluation Phase")
        print(f"  {startup_name}")
        print(f"  (Inner attempt {used_attempt}/{INNER_LOOP_MAX_ATTEMPTS}, score {best_attempt['score']}/80)")
        print(f"  Running Agents 3-6...")
        print(f"  ──────────────────────────────────────\n")

        # Build prior context for agents 3-6
        prior_context: dict[int, Any] = {
            1: best_attempt["a1"],
            2: best_attempt["a2"],
        }
        agent_usage = dict(best_attempt["usage"])

        for agent_num in range(3, 7):
            agent_role = AGENT_ROLES.get(agent_num, f"Agent {agent_num}")
            a_output, a_usage = _run_single_agent(
                agent_number=agent_num,
                submission_text=submission_text,
                prior_context=prior_context,
                current_round=round_num,
                total_rounds=rounds,
                inner_attempt=used_attempt,
                total_inner_attempts=INNER_LOOP_MAX_ATTEMPTS,
            )
            print(f"  ✓ [{agent_num}] {agent_role}")
            prior_context[agent_num] = a_output
            agent_usage[agent_num] = a_usage

        # Assemble results
        round_result: dict[int | str, Any] = {
            0: best_attempt["a0"],
            1: best_attempt["a1"],
            2: best_attempt["a2"],
        }
        for agent_num in range(3, 7):
            round_result[agent_num] = prior_context[agent_num]

        # Compute tags
        tags = _compute_tags(round_result)
        round_result["_tags"] = tags
        round_result["_usage"] = agent_usage
        round_result["_gen_meta"] = {
            "round": round_num,
            "attempt": used_attempt,
            "forced_new_idea": force_completely_new_idea,
        }

        # Determine name for this round's results
        base_name = given_name or startup_name
        round_key = f"{_sanitize_filename(base_name)}_r{round_num}"
        all_results[round_key] = round_result

        weighted = best_attempt["score"]
        tier = best_attempt["a2"].get("score_tier", "N/A")
        verdict = best_attempt["a2"].get("verdict", "N/A")
        score_progression.append((round_key, weighted, tier))

        print(f"\n  {'─'*50}")
        print(f"  ✓ OUTER ROUND {round_num} COMPLETE  [{_elapsed()}]")
        print(f"    {startup_name}")
        print(f"    Score: {weighted}/80 ({tier}) | Verdict: {verdict}")
        print(f"  {'─'*50}")

        # Extract Agent 6 feedback for next outer round
        prior_evaluation = prior_context.get(6)
        prior_score = best_attempt["a2"]

        # Strong-positive round resets streak; everything else increments it.
        verdict = str(prior_score.get("verdict", ""))
        recommendation = str((prior_evaluation or {}).get("recommendation", ""))
        is_strong_positive = (
            verdict == Verdict.TOP_VC_CANDIDATE.value
            and recommendation == Recommendation.CONTINUE.value
        )
        if is_strong_positive:
            non_strong_positive_streak = 0
        else:
            non_strong_positive_streak += 1

        # Add to Hall of Fame if score meets threshold
        if config.get("enable_hall_of_fame", True):
            from src.db import insert_to_hall_of_fame
            weighted = best_attempt["score"]
            if weighted >= 60:  # HALL_OF_FAME_MIN_SCORE threshold
                score_tier = best_attempt["a2"].get("score_tier", "Medium")
                insert_to_hall_of_fame(
                    batch_id=batch_id,
                    startup_name=startup_name,
                    weighted_score=weighted,
                    score_tier=score_tier,
                    agent0_output=best_attempt["a0"],
                    agent2_output=best_attempt["a2"],
                )
                print(f"  🏆 Added to Hall of Fame (score: {weighted}/80)")
    else:
        non_strong_positive_streak += 1

    # --- Agent 7: Rank all generated startups ---
    ranking_output = None
    ranking_usage = None
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        print(f"  AGENT 7 — Ranking {len(all_results)} startups  [{_elapsed()}]")
        print(f"{'='*60}\n")

        from crewai import Crew as _Crew
        from src.agents import create_agent as _create_agent
        from src.config import get_model_for_agent as _get_model
        from src.tasks import create_ranking_task

        # Build batch_data in the format create_ranking_task expects
        batch_data = []
        for name, outputs in all_results.items():
            agent_outputs = {k: v for k, v in outputs.items() if isinstance(k, int)}
            batch_data.append({"startup_name": name, "outputs": agent_outputs})

        model_name_7 = _get_model(7)
        agent7 = _create_agent(7)
        ranking_task = create_ranking_task(agent7, batch_data)

        if not _supports_structured_output(model_name_7):
            from crewai import Task as _Task

            ranking_task = _Task(
                description=ranking_task.description,
                expected_output=ranking_task.expected_output,
                agent=agent7,
            )

        crew7 = _Crew(agents=[agent7], tasks=[ranking_task], verbose=False)

        stop_event = threading.Event()
        agent_start = time.time()
        timer_thread = threading.Thread(
            target=_show_agent_timer,
            args=(7, model_name_7, stop_event),
            daemon=True,
        )
        timer_thread.start()

        try:
            try:
                ranking_result = crew7.kickoff()
            except Exception as exc:
                # MiniMax/Instructor may fail structured output on multiple tool calls.
                exc_msg_l = str(exc).lower()
                if (
                    "multiple tool calls" in exc_msg_l
                    or "instructor does not support multiple tool calls" in exc_msg_l
                    or "instructorretryexception" in type(exc).__name__.lower()
                ):
                    from crewai import Task as _Task

                    print("\n    ⚠ Structured ranking output failed, retrying with raw output...")
                    ranking_task_fallback = _Task(
                        description=ranking_task.description,
                        expected_output=ranking_task.expected_output,
                        agent=agent7,
                    )
                    crew7_fallback = _Crew(agents=[agent7], tasks=[ranking_task_fallback], verbose=False)
                    ranking_result = crew7_fallback.kickoff()
                else:
                    raise
        finally:
            stop_event.set()
            timer_thread.join(timeout=2)

        duration = time.time() - agent_start
        mins, secs = divmod(int(duration), 60)
        print(f"    ✓ Agent 7 (Ranking Committee) completed in {mins}m {secs}s")

        from src.models import Agent7Output
        if ranking_result.pydantic:
            ranking_output = ranking_result.pydantic.model_dump(mode="json")
        else:
            try:
                parsed = Agent7Output.model_validate_json(ranking_result.raw)
                ranking_output = parsed.model_dump(mode="json")
            except Exception:
                ranking_output = {"raw_output": ranking_result.raw}

        usage_7 = ranking_result.token_usage
        ranking_usage = {
            7: {
                "model": model_name_7,
                "prompt_tokens": getattr(usage_7, "prompt_tokens", 0),
                "completion_tokens": getattr(usage_7, "completion_tokens", 0),
                "total_tokens": getattr(usage_7, "total_tokens", 0),
            }
        }

        # Print ranking results
        if isinstance(ranking_output, dict) and "ranked_startups" in ranking_output:
            print(f"\n  Ranking:")
            for entry in ranking_output["ranked_startups"]:
                print(f"    #{entry.get('rank', '?')}  {entry.get('name', '?')} — {entry.get('score', '?')} ({entry.get('label', '?')})")
                print(f"        {entry.get('summary', '')}")

    # --- Final summary ---
    total_elapsed = int(time.time() - pipeline_start)
    mins, secs = divmod(total_elapsed, 60)

    print(f"\n\n{'#'*60}")
    print(f"  SCORE PROGRESSION")
    print(f"{'#'*60}\n")
    for name, score, tier in score_progression:
        print(f"  {name}: {score}/80 ({tier})")

    print(f"\n  Total time: {mins}m {secs}s")

    total_agent_runs = sum(attempts * 3 + 4 for attempts in actual_attempts_per_round)
    if ranking_output is not None:
        total_agent_runs += 1
    
    out_dir = export_results(
        batch_id, all_results, ranking_output, ranking_usage,
        execution_metrics={
            "outer_rounds": rounds,
            "max_inner_attempts": INNER_LOOP_MAX_ATTEMPTS,
            "actual_attempts_per_round": actual_attempts_per_round,
            "total_attempts_made": total_attempts_made,
            "total_agent_runs": total_agent_runs,
            "startup_count": len(all_results),
            "has_ranking": ranking_output is not None,
        },
        is_generation=True
    )
    print(f"\n  Results saved to: {out_dir}")


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

    elif mode == "generate":
        gen_config = _parse_generate_args(args[1:])
        run_generate(gen_config)

    elif mode == "hall-of-fame":
        # Hall of Fame management commands
        if len(args) < 2:
            print("Usage: python main.py hall-of-fame <command>")
            print("")
            print("Commands:")
            print("  list                  List all Hall of Fame entries")
            print("  stats                 Show Hall of Fame statistics")
            print("  clear                 Clear all Hall of Fame entries")
            print("  add <name> <score>    Manually add an entry")
            sys.exit(1)
        
        hof_command = args[1]
        
        if hof_command == "list":
            from src.db import get_top_ideas
            entries = get_top_ideas(limit=20, min_score=0)
            if not entries:
                print("Hall of Fame is empty.")
            else:
                print(f"=== Hall of Fame ({len(entries)} entries) ===")
                for i, entry in enumerate(entries, 1):
                    print(f"{i}. {entry.get('startup_name', 'Unknown')}")
                    print(f"   Score: {entry.get('weighted_score', 0):.1f}/80 ({entry.get('score_tier', 'N/A')})")
                    print(f"   Batch: {entry.get('batch_id', 'N/A')}")
                    print()
        elif hof_command == "stats":
            from src.db import get_hall_of_fame_stats
            stats = get_hall_of_fame_stats()
            print("=== Hall of Fame Statistics ===")
            print(f"Total entries: {stats.get('count', 0)}")
            print(f"Average score: {stats.get('avg_score', 0):.1f}/80")
            print(f"Min score: {stats.get('min_score', 0):.1f}/80")
            print(f"Max score: {stats.get('max_score', 0):.1f}/80")
        elif hof_command == "clear":
            from src.db import clear_hall_of_fame
            confirm = input("Are you sure you want to clear all Hall of Fame entries? (yes/no): ")
            if confirm.lower() == "yes":
                clear_hall_of_fame()
                print("Hall of Fame cleared.")
            else:
                print("Cancelled.")
        elif hof_command == "add":
            if len(args) < 4:
                print("Usage: python main.py hall-of-fame add <name> <score>")
                sys.exit(1)
            from src.db import insert_to_hall_of_fame
            name = args[2]
            score = float(args[3])
            tier = "Medium" if score < 70 else "High"
            insert_to_hall_of_fame(
                batch_id="manual",
                startup_name=name,
                weighted_score=score,
                score_tier=tier,
                agent0_output={"startup_name": name},
                agent2_output={"weighted_total_score": score, "score_tier": tier},
            )
            print(f"Added '{name}' to Hall of Fame with score {score}/80")
        else:
            print(f"Unknown command: {hof_command}")
            sys.exit(1)
        return

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
                # Accept any text file in the directory
                all_files = sorted([f for f in subdir.iterdir() if f.is_file() and not f.name.startswith(".")])
                if not all_files:
                    continue
                # Read all text/PDF/DOCX files
                parts = []
                for f in all_files:
                    content = None
                    # Try PDF extraction first for .pdf files
                    if f.suffix.lower() == ".pdf":
                        content = _extract_text_from_pdf(f)
                    elif f.suffix.lower() == ".docx":
                        # Extract text from Word documents
                        try:
                            import docx
                            doc = docx.Document(f)
                            paragraphs = [p.text for p in doc.paragraphs]
                            content = "\n\n".join(paragraphs)
                        except Exception as e:
                            print(f"    ⚠ Could not read {f.name}: {e}")
                    else:
                        # Try reading as text
                        try:
                            content = f.read_text(encoding="utf-8")
                        except (UnicodeDecodeError, IOError):
                            # Skip binary files that aren't PDFs
                            pass
                    if content:
                        parts.append(content)
                if not parts:
                    continue
                combined = "\n\n".join(parts)
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
            is_batch_mode=True,
        )
        print(f"\nResults saved to: {out_dir}")

    else:
        print(f"Unknown mode: {mode}")
        print("Usage:")
        print("  python main.py                     # Process CourseDocs")
        print("  python main.py single <file>       # Process one submission")
        print("  python main.py batch <directory>   # Process multiple + rank")
        print("  python main.py generate [options]  # Generate & evaluate startup ideas")
        print("  python main.py hall-of-fame <cmd>  # Hall of Fame management")
        print("")
        print("Generate options:")
        print("  --rounds N                  Number of outer loop rounds (default: 3)")
        print("  --name NAME                 Base name for output folders")
        print("  --team-size N               Team size (default: 1)")
        print("  --experience TEXT           Founder experience (default: none)")
        print("  --network TEXT              Founder network (default: none)")
        print("  --availability PCT          Availability (default: 100%)")
        print("  --locale TEXT               Location (default: Barcelona, Spain)")
        print("  --capital TEXT              Capital level (default: Very low)")
        print("  --traction TEXT             Current traction (default: zero)")
        print("  --languages TEXT            Languages spoken (default: English)")
        print("  --industry TEXT             Target industry (default: Unspecified)")
        print("")
        print("Optimization options:")
        print("  --best-of-n N               Generate N candidates per attempt (default: 3, range: 1-10)")
        print("  --no-hall-of-fame           Disable hall of fame examples")
        print("  --no-dimension-reasoning    Disable explicit dimension self-evaluation")
        print("")
        print("Hall of Fame commands:")
        print("  list                        List all Hall of Fame entries")
        print("  stats                       Show Hall of Fame statistics")
        print("  clear                       Clear all Hall of Fame entries")
        print("  add <name> <score>          Manually add an entry")
        sys.exit(1)


if __name__ == "__main__":
    main()
