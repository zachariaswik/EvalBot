"""Retry and fallback utilities for LLM API calls."""

from __future__ import annotations

import signal
import time
from dataclasses import dataclass
from functools import partial
from threading import Thread
from typing import Any, Callable, TypedDict

from .config import (
    AGENT_TIMEOUT,
    FALLBACK_MODEL,
    RECOVERY_CHECK_INTERVAL,
    RECOVERY_COOLDOWN,
    RETRY_ATTEMPTS,
    RETRY_BASE_DELAY,
    TOTAL_STARTUP_TIMEOUT,
    get_fallback_model_for_agent,
)


class RetryResult(TypedDict):
    """Result of retry execution with metadata."""
    result: Any
    intended_model: str
    actual_model: str
    retry_count: int
    fallback_occurred: bool
    recovery_occurred: bool
    error_type: str | None


class AgentTimeoutError(Exception):
    """Raised when an agent exceeds the configured AGENT_TIMEOUT."""
    pass


class StartupTimeoutError(Exception):
    """Raised when a startup exceeds the TOTAL_STARTUP_TIMEOUT budget."""
    def __init__(self, elapsed: float, limit: float, message: str | None = None):
        self.elapsed = elapsed
        self.limit = limit
        self.message = message or (
            f"Startup exceeded time limit: {int(elapsed)}s elapsed (limit: {int(limit)}s). "
            f"All model retries failed."
        )
        super().__init__(self.message)


@dataclass
class FallbackState:
    """Tracks fallback model usage and recovery attempts."""
    active: bool = False
    primary_model: str | None = None
    fallback_count: int = 0
    last_failure_time: float = 0.0
    consecutive_successes: int = 0


# Global fallback state (persists across agent executions in a batch)
_fallback_state = FallbackState()

# Global startup timer - records when the first agent started for this startup
_startup_start_time: float | None = None


def reset_fallback_state() -> None:
    """Reset fallback state (call at start of new batch)."""
    global _fallback_state, _startup_start_time
    _fallback_state = FallbackState()
    _startup_start_time = None


def should_attempt_recovery() -> bool:
    """Check if we should try switching back to primary model."""
    if not _fallback_state.active:
        return False
    
    # Need enough consecutive successes
    if _fallback_state.consecutive_successes < RECOVERY_CHECK_INTERVAL:
        return False
    
    # Need to wait for cooldown period
    elapsed = time.time() - _fallback_state.last_failure_time
    return elapsed >= RECOVERY_COOLDOWN


def _execute_with_timeout(func: Callable[[], Any], timeout: int | None) -> Any:
    """Execute a function with a timeout limit using a background thread.
    
    Args:
        func: Function to execute
        timeout: Maximum seconds to allow (None to disable timeout)
    
    Returns:
        Function result
    
    Raises:
        AgentTimeoutError: If execution exceeds timeout limit
    """
    if timeout is None:
        return func()
    
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e
    
    thread = Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        # Thread is still running - it timed out
        raise AgentTimeoutError(
            f"Agent execution exceeded timeout limit of {timeout} seconds"
        )
    
    if exception[0] is not None:
        raise exception[0]
    
    return result[0]


def execute_with_retry(
    func: Callable[[], Any],
    model_name: str,
    agent_number: int,
    silent: bool = True,
) -> RetryResult:
    """
    Execute a function with retry logic and automatic fallback.
    
    Args:
        func: Function to execute (typically crew.kickoff)
        model_name: Primary model being used
        agent_number: Agent number (for logging)
        silent: If True, suppress error messages during retries
    
    Returns:
        RetryResult dict with result and execution metadata
    
    Raises:
        Last exception if all retries and fallback fail
        StartupTimeoutError: If total startup time exceeds TOTAL_STARTUP_TIMEOUT
    """
    global _fallback_state, _startup_start_time
    
    # Record start time on first call for this startup
    if _startup_start_time is None:
        _startup_start_time = time.time()
    
    # Get the appropriate fallback model for this agent
    fallback_model = get_fallback_model_for_agent(agent_number)
    
    # Track metadata for this execution
    retry_count = 0
    fallback_occurred = False
    recovery_occurred = False
    error_type = None
    
    # Determine which model to use
    if should_attempt_recovery():
        attempt_model = _fallback_state.primary_model
        recovery_attempt = True
        if not silent:
            print(f"    ↻ Attempting recovery to primary model...")
    elif _fallback_state.active:
        attempt_model = fallback_model
        recovery_attempt = False
    else:
        attempt_model = model_name
        recovery_attempt = False
    
    last_error = None
    
    # Check if we've already exceeded total startup timeout before even trying
    elapsed = time.time() - _startup_start_time
    if elapsed >= TOTAL_STARTUP_TIMEOUT:
        raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)
    
    # Try with current model (primary or fallback)
    for attempt in range(RETRY_ATTEMPTS):
        try:
            # Wrap with AGENT_TIMEOUT to enforce max execution time
            result = _execute_with_timeout(func, AGENT_TIMEOUT)
            
            # Success! Update fallback state
            if recovery_attempt:
                # Successfully recovered to primary model
                if not silent:
                    print(f"    ✓ Recovered to primary model")
                _fallback_state.active = False
                _fallback_state.consecutive_successes = 0
                recovery_occurred = True
            elif _fallback_state.active:
                # Successful fallback execution
                _fallback_state.consecutive_successes += 1
            
            return {
                "result": result,
                "intended_model": model_name,
                "actual_model": attempt_model,
                "retry_count": retry_count,
                "fallback_occurred": fallback_occurred,
                "recovery_occurred": recovery_occurred,
                "error_type": error_type,
            }
            
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Capture error type for logging
            if not error_type:
                if isinstance(e, AgentTimeoutError):
                    error_type = "agent_timeout"
                elif "timeout" in error_str or "timed out" in error_str:
                    error_type = "timeout"
                elif "connection" in error_str or "reset" in error_str:
                    error_type = "connection_reset"
                elif any(code in error_str for code in ["502", "503", "504"]):
                    error_type = "server_error"
                else:
                    error_type = "other"
            
            # Check if this is a retryable error (connection error only)
            is_connection_error = any(
                err in error_str
                for err in [
                    "connection", "reset", "errno 54", "errno 60",
                    "apiconnectionerror", "readtimeout", "invalid response"
                ]
            )
            
            # Connection errors are retryable; timeouts fail fast (switch model)
            is_retryable = is_connection_error
            
            if not is_retryable:
                # AgentTimeoutError or other non-connection error - fail fast, don't retry
                raise
            
            # Connection error - attempt retry with backoff
            retry_count += 1
            
            # Check if we've exceeded total startup timeout before retrying
            elapsed = time.time() - _startup_start_time
            if elapsed >= TOTAL_STARTUP_TIMEOUT:
                raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)
            
            if attempt < RETRY_ATTEMPTS - 1:
                delay = RETRY_BASE_DELAY ** (attempt + 1)
                if not silent:
                    print(f"    ↻ Retrying... ({attempt + 1}/{RETRY_ATTEMPTS})")
                time.sleep(delay)
            else:
                # Exhausted retries on current model
                break
    
    # All retries failed - try fallback if available
    if fallback_model and not recovery_attempt and attempt_model != fallback_model:
        # Check if we've exceeded total startup timeout before trying fallback
        elapsed = time.time() - _startup_start_time
        if elapsed >= TOTAL_STARTUP_TIMEOUT:
            raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)
        
        if not silent:
            print(f"    ⚠ Switching to fallback model ({fallback_model})")
        
        # Activate fallback state
        if not _fallback_state.active:
            _fallback_state.active = True
            _fallback_state.primary_model = model_name
            _fallback_state.last_failure_time = time.time()
        
        _fallback_state.fallback_count += 1
        _fallback_state.consecutive_successes = 0
        fallback_occurred = True
        
        # Try with fallback model (with retries, since it's the last resort)
        fallback_retry_count = 0
        for fallback_attempt in range(RETRY_ATTEMPTS):
            try:
                # Check total startup timeout before each fallback attempt
                elapsed = time.time() - _startup_start_time
                if elapsed >= TOTAL_STARTUP_TIMEOUT:
                    raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)
                
                result = _execute_with_timeout(func, AGENT_TIMEOUT)
                return {
                    "result": result,
                    "intended_model": model_name,
                    "actual_model": fallback_model,
                    "retry_count": retry_count + fallback_retry_count,
                    "fallback_occurred": fallback_occurred,
                    "recovery_occurred": recovery_occurred,
                    "error_type": error_type,
                }
            except Exception as fallback_error:
                fallback_retry_count += 1
                fallback_error_str = str(fallback_error).lower()
                
                # Check if this is a retryable error (connection error only)
                is_connection_error = any(
                    err in fallback_error_str
                    for err in [
                        "connection", "reset", "errno 54", "errno 60",
                        "apiconnectionerror", "readtimeout", "invalid response"
                    ]
                )
                
                # Connection errors are retryable; timeouts fail fast (no more retries)
                is_retryable = is_connection_error
                
                if not is_retryable:
                    # AgentTimeoutError or other non-connection error - fail fast
                    raise
                
                # Check total startup timeout before retrying fallback
                elapsed = time.time() - _startup_start_time
                if elapsed >= TOTAL_STARTUP_TIMEOUT:
                    raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)
                
                if fallback_attempt < RETRY_ATTEMPTS - 1:
                    delay = RETRY_BASE_DELAY ** (fallback_attempt + 1)
                    if not silent:
                        print(f"    ↻ Fallback retry... ({fallback_attempt + 1}/{RETRY_ATTEMPTS})")
                    time.sleep(delay)
                else:
                    if not silent:
                        print(f"    ✗ Fallback model also failed after {RETRY_ATTEMPTS} attempts")
                    raise fallback_error
    
    # No fallback available or recovery attempt failed
    if recovery_attempt:
        if not silent:
            print(f"    ✗ Recovery failed, continuing with fallback")
        _fallback_state.consecutive_successes = 0
        # Will use fallback on next execution
    
    raise last_error


def get_fallback_stats() -> dict[str, Any]:
    """Get current fallback state statistics."""
    return {
        "fallback_active": _fallback_state.active,
        "primary_model": _fallback_state.primary_model,
        "fallback_count": _fallback_state.fallback_count,
        "consecutive_successes": _fallback_state.consecutive_successes,
        "seconds_since_failure": int(time.time() - _fallback_state.last_failure_time) if _fallback_state.last_failure_time > 0 else 0,
    }
