"""Orchestration for the EvalBot multi-agent pipeline."""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from crewai import Crew

from .agents import create_agent
from .config import MAX_ITERATIONS, get_model_for_agent
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

    def __init__(self, batch_id: str | None = None):
        self.state = PipelineState(
            batch_id=batch_id or f"batch-{uuid.uuid4().hex[:8]}",
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
                result = crew.kickoff()
            finally:
                stop_event.set()
                counter_thread.join(timeout=2)
            
            # Record agent timing
            agent_duration = time.time() - agent_start
            agent_timings[agent_num] = agent_duration
            mins, secs = divmod(int(agent_duration), 60)
            print(f"  ✓ Agent {agent_num} completed in {mins}m {secs}s")

            # Extract Pydantic output
            output_model = AGENT_OUTPUT_MODELS[agent_num]
            if result.pydantic:
                pydantic_output = result.pydantic
            else:
                # Fallback: try to parse from raw text
                try:
                    pydantic_output = output_model.model_validate_json(result.raw)
                except Exception:
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
    batch_id: str | None = None,
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
    batch_id: str | None = None,
) -> dict:
    """Run agents 1-6 for each startup, then Agent 7 ranking."""
    bid = batch_id or f"batch-{uuid.uuid4().hex[:8]}"

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

    agent = create_agent(7)
    task = create_ranking_task(agent, batch_data)
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
        ranking_result = crew.kickoff()
    finally:
        stop_event.set()
        counter_thread.join(timeout=2)
    
    # Record Agent 7 timing
    agent_duration = time.time() - agent_start
    mins, secs = divmod(int(agent_duration), 60)
    print(f"  ✓ Agent 7 completed in {mins}m {secs}s")

    ranking_output = None
    if ranking_result.pydantic:
        ranking_output = ranking_result.pydantic.model_dump(mode="json")
    else:
        try:
            from .models import Agent7Output

            parsed = Agent7Output.model_validate_json(ranking_result.raw)
            ranking_output = parsed.model_dump(mode="json")
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

    return {"individual": all_results, "ranking": ranking_output}
