"""Orchestration for the EvalBot multi-agent pipeline."""

from __future__ import annotations

from enum import Enum
import json
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, get_args, get_origin

from crewai import Crew, Task

from .agents import create_agent
from .config import CRITICAL_FIELDS, MAX_ITERATIONS, QUALITY_GATE_THRESHOLD, get_model_for_agent
from .db import (
    create_batch,
    get_all_batch_outputs,
    init_db,
    invalidate_outputs_from,
    log_feedback,
    store_agent_output,
    update_startup_status,
    upsert_startup,
)
from .models import AGENT_OUTPUT_MODELS, FeedbackMixin
from .tasks import create_ranking_task, create_task


def _is_instructor_multi_tool_error(exc: Exception) -> bool:
    """Detect known Instructor/CrewAI structured-output failures from some models."""
    msg = str(exc).lower()
    exc_type = type(exc).__name__.lower()
    return (
        "multiple tool calls" in msg
        or "instructor does not support multiple tool calls" in msg
        or "instructorretryexception" in exc_type
    )


def _supports_structured_output(model_name: str) -> bool:
    """Return whether output_pydantic should be used with this provider/model."""
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
    """Parse LLM raw output into expected dict, handling fenced JSON and extra prose."""
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
                match = re.search(r"agent\s*[_-]?(\d+)", s)
                if match:
                    return int(match.group(1))
            return value

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
                match = re.search(r"-?\d+(?:\.\d+)?", s)
                if match:
                    try:
                        return int(round(float(match.group(0))))
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

            if ann is int:
                normalized[field_name] = _coerce_int(value)
                continue

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


def _default_output_for_model(output_model: Any, reason: str) -> dict[str, Any] | None:
    """Return a deterministic schema-valid fallback payload from model defaults."""
    try:
        payload = output_model.model_validate({}).model_dump(mode="json")
        payload["_schema_fallback"] = True
        payload["_schema_fallback_reason"] = reason
        return payload
    except Exception:
        return None


def _compute_weighted_score(output_dict: dict) -> tuple[float, str]:
    """Compute the weighted total score and tier from Agent 2 output."""
    weighted = (
        output_dict.get("score_problem_severity", 0) * 0.20
        + output_dict.get("score_market_size", 0) * 0.20
        + output_dict.get("score_differentiation", 0) * 0.15
        + output_dict.get("score_founder_insight", 0) * 0.15
        + output_dict.get("score_moat_potential", 0) * 0.10
        + output_dict.get("score_business_model", 0) * 0.10
        + output_dict.get("score_venture_potential", 0) * 0.10
    ) * 8  # Scale to 0-80 range

    if weighted >= 64:
        tier = "Top tier"
    elif weighted >= 52:
        tier = "Strong"
    elif weighted >= 40:
        tier = "Medium"
    elif weighted >= 28:
        tier = "Weak"
    else:
        tier = "Reject"

    return round(weighted, 2), tier


def _check_reject_signals(output_dict: dict) -> list[str]:
    """Check for hard reject signals from Agent 2 scores."""
    signal_map = {
        "score_problem_severity": "No real pain",
        "score_market_size": "Tiny market",
        "score_customer_clarity": "No clear buyer",
        "score_founder_insight": "Weak founder understanding",
        "score_differentiation": "No differentiation / no wedge",
    }
    signals = []
    for field, label in signal_map.items():
        if output_dict.get(field, 10) <= 3:
            signals.append(label)
    return signals


def _compute_tags(agent_outputs: dict[int, Any]) -> list[str]:
    """Compute automatic tags from all agent outputs."""
    tags: list[str] = []

    # Score-based tags from Agent 2
    a2 = agent_outputs.get(2, {})
    if a2:
        if a2.get("score_market_size", 0) >= 7:
            tags.append("large_market")
        elif a2.get("score_market_size", 10) <= 3:
            tags.append("small_market")

        if a2.get("score_moat_potential", 0) >= 7:
            tags.append("strong_moat")
        elif a2.get("score_moat_potential", 10) <= 3:
            tags.append("no_moat")

        if a2.get("score_founder_insight", 0) >= 7:
            tags.append("strong_founder_fit")
        elif a2.get("score_founder_insight", 10) <= 3:
            tags.append("weak_founder_fit")

        if a2.get("score_differentiation", 0) >= 7:
            tags.append("good_wedge")
        elif a2.get("score_differentiation", 10) <= 3:
            tags.append("no_wedge")

        if a2.get("score_customer_clarity", 10) <= 3:
            tags.append("unclear_buyer")

        # Verdict-based tags
        verdict = a2.get("verdict", "")
        if verdict == "Feature, Not a Company":
            tags.append("feature_not_company")
        if verdict == "AI Wrapper With Weak Moat":
            tags.append("wrapper_risk")

    # Agent 4 tags
    a4 = agent_outputs.get(4, {})
    if a4 and a4.get("wrapper_risk") == "high" and "wrapper_risk" not in tags:
        tags.append("wrapper_risk")

    # Agent 3 tags
    a3 = agent_outputs.get(3, {})
    if a3:
        if a3.get("size_class") == "small" and "small_market" not in tags:
            tags.append("small_market")
        crowdedness = a3.get("crowdedness", "")
        if isinstance(crowdedness, str) and "crowded" in crowdedness.lower():
            tags.append("crowded_market")

    return tags


@dataclass
class PipelineState:
    batch_id: str = ""
    startup_name: str = ""
    submission_text: str = ""
    current_agent: int = 1
    iteration: int = 0
    agent_outputs: dict[int, Any] = field(default_factory=dict)
    completed: bool = False


class StartupEvalPipeline:
    """Run agents 1-6 sequentially with feedback-loop support."""

    def __init__(self, batch_id: str):
        self.state = PipelineState(
            batch_id=batch_id,
        )

    def _show_live_counter(self, agent_num: int, stop_event: threading.Event) -> None:
        """Show a live-updating counter at the bottom of output, ticking every second."""
        start = time.time()
        while not stop_event.is_set():
            elapsed = int(time.time() - start)
            mins, secs = divmod(elapsed, 60)
            # Use \r to overwrite the same line
            print(f"\r    ⏱ Agent {agent_num} running... {mins}m {secs}s", end="", flush=True)
            time.sleep(1)
        # Clear the line when done
        print("\r" + " " * 50 + "\r", end="", flush=True)

    def kickoff(self) -> dict[int, Any]:
        """Core while-loop running agents 1-6 with feedback jumps."""
        init_db()
        create_batch(self.state.batch_id)
        upsert_startup(
            self.state.batch_id,
            self.state.startup_name,
            self.state.submission_text,
        )
        update_startup_status(self.state.batch_id, self.state.startup_name, "in_progress")

        # Track feedback reason and rerun flag
        pending_feedback_reason: str | None = None
        pending_is_rerun: bool = False
        start_time = datetime.now()
        agent_timings: dict[int, float] = {}  # Track per-agent execution time
        agent_usage: dict[int, dict] = {}  # Track per-agent token usage

        while self.state.current_agent <= 6 and self.state.iteration < MAX_ITERATIONS:
            self.state.iteration += 1
            agent_num = self.state.current_agent
            is_rerun = pending_is_rerun
            model_name = get_model_for_agent(agent_num, is_rerun=is_rerun)
            elapsed = datetime.now() - start_time
            elapsed_str = f"{elapsed.seconds // 60}m {elapsed.seconds % 60}s"
            completed = len([k for k in self.state.agent_outputs.keys() if k < agent_num])
            print(f"\n{'='*60}")
            print(f"  [Progress {completed}/6] Agent {agent_num}/6 | Iteration {self.state.iteration}"
                  f" | Elapsed: {elapsed_str}")
            print(f"  Model: {model_name}{' (re-run)' if is_rerun else ''}")
            print(f"{'='*60}\n")

            feedback_reason = pending_feedback_reason
            pending_feedback_reason = None
            pending_is_rerun = False

            # Build prior context from stored outputs
            prior_context = dict(self.state.agent_outputs)

            # Create agent and task — is_rerun may select a different model
            agent = create_agent(agent_num, is_rerun=is_rerun)
            task = create_task(
                agent_number=agent_num,
                agent=agent,
                submission_text=self.state.submission_text,
                prior_context=prior_context if agent_num > 1 else None,
                feedback_reason=feedback_reason,
            )

            if not _supports_structured_output(model_name):
                task = Task(
                    description=task.description,
                    expected_output=task.expected_output,
                    agent=agent,
                )

            # Run single-agent crew with live counter
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            print(f"  ⏱ Agent {agent_num} starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Start live counter thread
            stop_event = threading.Event()
            agent_start = time.time()
            counter_thread = threading.Thread(
                target=self._show_live_counter,
                args=(agent_num, stop_event),
                daemon=True
            )
            counter_thread.start()
            
            try:
                try:
                    result = crew.kickoff()
                except Exception as exc:
                    if _is_instructor_multi_tool_error(exc):
                        print(
                            f"\n  ⚠ Structured output failed for Agent {agent_num}; "
                            "retrying with raw output..."
                        )
                        task_fallback = Task(
                            description=task.description,
                            expected_output=task.expected_output,
                            agent=agent,
                        )
                        crew_fallback = Crew(agents=[agent], tasks=[task_fallback], verbose=True)
                        result = crew_fallback.kickoff()
                    else:
                        raise
            finally:
                stop_event.set()
                counter_thread.join(timeout=2)
            
            # Record agent timing
            agent_duration = time.time() - agent_start
            agent_timings[agent_num] = agent_duration
            mins, secs = divmod(int(agent_duration), 60)
            print(f"  ✓ Agent {agent_num} completed in {mins}m {secs}s")

            # Capture token usage
            usage = result.token_usage
            agent_usage[agent_num] = {
                "model": model_name,
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }

            # Extract Pydantic output
            output_model = AGENT_OUTPUT_MODELS[agent_num]
            if result.pydantic:
                pydantic_output = result.pydantic
            else:
                # Fallback: try to parse from raw text
                parsed_dict = _parse_output_to_dict(output_model, result.raw)
                if parsed_dict is not None:
                    pydantic_output = output_model.model_validate(parsed_dict)
                else:
                    print(f"  WARNING: Could not parse Agent {agent_num} output into Pydantic model")
                    pydantic_output = None

            if pydantic_output:
                output_dict = pydantic_output.model_dump(mode="json")
            else:
                output_dict = {"raw_output": result.raw}

            # Store in state and DB
            self.state.agent_outputs[agent_num] = output_dict
            store_agent_output(
                batch_id=self.state.batch_id,
                startup_name=self.state.startup_name,
                agent_number=agent_num,
                output_json=json.dumps(output_dict, default=str),
                iteration=self.state.iteration,
            )

            # --- Post-agent checks ---

            # Quality gate after Agent 1
            if agent_num == 1 and pydantic_output:
                missing = output_dict.get("missing_info", [])
                missing_critical = [f for f in CRITICAL_FIELDS if any(f in m.lower() for m in missing)]
                if len(missing_critical) >= QUALITY_GATE_THRESHOLD:
                    print(f"\n  {'!'*50}")
                    print(f"  ⚠ QUALITY GATE WARNING: {len(missing_critical)} critical fields missing")
                    print(f"  Missing: {', '.join(missing_critical)}")
                    print(f"  Raw missing_info from Agent 1: {missing}")
                    print(f"  {'!'*50}\n")

            # Weighted scoring + reject signals after Agent 2
            if agent_num == 2 and pydantic_output:
                weighted_score, score_tier = _compute_weighted_score(output_dict)
                output_dict["weighted_total_score"] = weighted_score
                output_dict["score_tier"] = score_tier
                self.state.agent_outputs[agent_num] = output_dict  # update with new fields

                print(f"\n  Weighted Score: {weighted_score}/80 — {score_tier}")

                reject_signals = _check_reject_signals(output_dict)
                output_dict["reject_signals"] = reject_signals
                if len(reject_signals) >= 3:
                    print(f"\n  {'!'*50}")
                    print(f"  ⛔ HARD REJECT SIGNALS ({len(reject_signals)} detected):")
                    for sig in reject_signals:
                        print(f"     - {sig}")
                    print(f"  {'!'*50}\n")

            # Check for feedback loop (agents 2-6 only)
            if pydantic_output and isinstance(pydantic_output, FeedbackMixin):
                rerun_from = pydantic_output.rerun_from_agent
                rerun_reason = pydantic_output.rerun_reason
                if rerun_from is not None and 1 <= rerun_from < agent_num:
                    print(f"\n  FEEDBACK LOOP: Agent {agent_num} requests re-run from Agent {rerun_from}")
                    print(f"  Reason: {rerun_reason}\n")

                    log_feedback(
                        batch_id=self.state.batch_id,
                        startup_name=self.state.startup_name,
                        from_agent=agent_num,
                        to_agent=rerun_from,
                        reason=rerun_reason or "",
                        iteration=self.state.iteration,
                    )

                    # Invalidate outputs from the target agent onward
                    invalidate_outputs_from(
                        self.state.batch_id,
                        self.state.startup_name,
                        rerun_from,
                    )
                    # Clear in-memory outputs from target onward
                    for k in list(self.state.agent_outputs.keys()):
                        if k >= rerun_from:
                            del self.state.agent_outputs[k]

                    # Jump back with feedback context
                    self.state.current_agent = rerun_from
                    pending_feedback_reason = rerun_reason
                    pending_is_rerun = True
                    continue

            # Advance to next agent
            print(f"  Agent {agent_num} completed successfully.")
            self.state.current_agent = agent_num + 1

        # Compute automatic tags from all agent outputs
        tags = _compute_tags(self.state.agent_outputs)
        self.state.agent_outputs["_tags"] = tags
        self.state.agent_outputs["_usage"] = agent_usage
        if tags:
            print(f"\n  Tags: {', '.join(tags)}")

        self.state.completed = True
        update_startup_status(self.state.batch_id, self.state.startup_name, "completed")
        elapsed = datetime.now() - start_time
        elapsed_str = f"{elapsed.seconds // 60}m {elapsed.seconds % 60}s"
        print(f"\n{'='*60}")
        print(f"  ✓ Pipeline completed for: {self.state.startup_name}")
        print(f"  Total iterations: {self.state.iteration} | Total elapsed: {elapsed_str}")
        print(f"{'='*60}")
        
        # Display per-agent timings summary
        print(f"\n  Per-Agent Execution Times:")
        for agent_num in sorted(agent_timings.keys()):
            mins, secs = divmod(int(agent_timings[agent_num]), 60)
            print(f"    Agent {agent_num}: {mins}m {secs}s")
        print()
        
        return dict(self.state.agent_outputs)


def run_single(
    startup_name: str,
    submission_text: str,
    batch_id: str,
) -> dict[int, Any]:
    """Run the pipeline for a single startup submission."""
    pipeline = StartupEvalPipeline(batch_id=batch_id)
    pipeline.state.startup_name = startup_name
    pipeline.state.submission_text = submission_text
    return pipeline.kickoff()


def _show_live_counter_agent7(stop_event: threading.Event) -> None:
    """Show a live-updating counter for Agent 7, ticking every second."""
    start = time.time()
    while not stop_event.is_set():
        elapsed = int(time.time() - start)
        mins, secs = divmod(elapsed, 60)
        # Use \r to overwrite the same line
        print(f"\r    ⏱ Agent 7 running... {mins}m {secs}s", end="", flush=True)
        time.sleep(1)
    # Clear the line when done
    print("\r" + " " * 50 + "\r", end="", flush=True)


def run_batch(
    submissions: dict[str, str],
    batch_id: str,
) -> dict:
    """Run agents 1-6 for each startup, then Agent 7 ranking."""
    bid = batch_id

    # Run agents 1-6 for each startup
    all_results: dict[str, dict] = {}
    for name, text in submissions.items():
        print(f"\n{'#'*60}")
        print(f"  Processing: {name}")
        print(f"{'#'*60}")
        result = run_single(name, text, batch_id=bid)
        all_results[name] = result

    # Run Agent 7 — ranking across the cohort
    print(f"\n{'#'*60}")
    print(f"  Running Agent 7: Cohort Ranking")
    print(f"{'#'*60}\n")

    init_db()
    batch_data = get_all_batch_outputs(bid)

    if len(batch_data) < 1:
        print("  No batch data available for ranking.")
        return {"individual": all_results, "ranking": None}

    model_name_7 = get_model_for_agent(7)
    agent = create_agent(7)
    task = create_ranking_task(agent, batch_data)
    if not _supports_structured_output(model_name_7):
        task = Task(
            description=task.description,
            expected_output=task.expected_output,
            agent=agent,
        )
    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    
    print(f"  ⏱ Agent 7 starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Start live counter thread for Agent 7
    stop_event = threading.Event()
    agent_start = time.time()
    counter_thread = threading.Thread(
        target=_show_live_counter_agent7,
        args=(stop_event,),
        daemon=True
    )
    counter_thread.start()
    
    try:
        try:
            ranking_result = crew.kickoff()
        except Exception as exc:
            if _is_instructor_multi_tool_error(exc):
                print("\n  ⚠ Structured ranking output failed; retrying with raw output...")
                ranking_task_fallback = Task(
                    description=task.description,
                    expected_output=task.expected_output,
                    agent=agent,
                )
                crew_fallback = Crew(agents=[agent], tasks=[ranking_task_fallback], verbose=True)
                ranking_result = crew_fallback.kickoff()
            else:
                raise
    finally:
        stop_event.set()
        counter_thread.join(timeout=2)
    
    # Record Agent 7 timing
    agent_duration = time.time() - agent_start
    mins, secs = divmod(int(agent_duration), 60)
    print(f"  ✓ Agent 7 completed in {mins}m {secs}s")

    # Capture Agent 7 token usage
    usage_7 = ranking_result.token_usage
    agent7_usage = {
        7: {
            "model": model_name_7,
            "prompt_tokens": getattr(usage_7, "prompt_tokens", 0),
            "completion_tokens": getattr(usage_7, "completion_tokens", 0),
            "total_tokens": getattr(usage_7, "total_tokens", 0),
        }
    }

    ranking_output = None
    if ranking_result.pydantic:
        ranking_output = ranking_result.pydantic.model_dump(mode="json")
    else:
        try:
            from .models import Agent7Output

            parsed_dict = _parse_output_to_dict(Agent7Output, ranking_result.raw)
            if parsed_dict is not None:
                ranking_output = parsed_dict
            else:
                ranking_output = {"raw_output": ranking_result.raw}
        except Exception:
            ranking_output = {"raw_output": ranking_result.raw}

    # Store ranking output
    store_agent_output(
        batch_id=bid,
        startup_name="__cohort__",
        agent_number=7,
        output_json=json.dumps(ranking_output, default=str),
        iteration=1,
    )

    return {"individual": all_results, "ranking": ranking_output, "ranking_usage": agent7_usage}
