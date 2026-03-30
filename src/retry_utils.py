"""Retry and fallback utilities for LLM API calls."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from .config import (
    FALLBACK_MODEL,
    RECOVERY_CHECK_INTERVAL,
    RECOVERY_COOLDOWN,
    RETRY_ATTEMPTS,
    RETRY_BASE_DELAY,
)


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


def reset_fallback_state() -> None:
    """Reset fallback state (call at start of new batch)."""
    global _fallback_state
    _fallback_state = FallbackState()


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


def execute_with_retry(
    func: Callable[[], Any],
    model_name: str,
    agent_number: int,
    silent: bool = True,
) -> Any:
    """
    Execute a function with retry logic and automatic fallback.
    
    Args:
        func: Function to execute (typically crew.kickoff)
        model_name: Primary model being used
        agent_number: Agent number (for logging)
        silent: If True, suppress error messages during retries
    
    Returns:
        Result from successful execution
    
    Raises:
        Last exception if all retries and fallback fail
    """
    global _fallback_state
    
    # Determine which model to use
    if should_attempt_recovery():
        attempt_model = _fallback_state.primary_model
        recovery_attempt = True
        if not silent:
            print(f"    ↻ Attempting recovery to primary model...")
    elif _fallback_state.active:
        attempt_model = FALLBACK_MODEL
        recovery_attempt = False
    else:
        attempt_model = model_name
        recovery_attempt = False
    
    last_error = None
    
    # Try with current model (primary or fallback)
    for attempt in range(RETRY_ATTEMPTS):
        try:
            result = func()
            
            # Success! Update fallback state
            if recovery_attempt:
                # Successfully recovered to primary model
                if not silent:
                    print(f"    ✓ Recovered to primary model")
                _fallback_state.active = False
                _fallback_state.consecutive_successes = 0
            elif _fallback_state.active:
                # Successful fallback execution
                _fallback_state.consecutive_successes += 1
            
            return result
            
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Check if this is a retryable error
            is_connection_error = any(
                err in error_str
                for err in [
                    "connection", "reset", "timeout", "timed out",
                    "502", "503", "504", "errno 54", "errno 60",
                    "apiconnectionerror", "readtimeout"
                ]
            )
            
            if not is_connection_error:
                # Non-retryable error, raise immediately
                raise
            
            # Connection error - attempt retry
            if attempt < RETRY_ATTEMPTS - 1:
                delay = RETRY_BASE_DELAY ** (attempt + 1)
                if not silent:
                    print(f"    ↻ Retrying... ({attempt + 1}/{RETRY_ATTEMPTS})")
                time.sleep(delay)
            else:
                # Exhausted retries on current model
                break
    
    # All retries failed - try fallback if available
    if FALLBACK_MODEL and not recovery_attempt and attempt_model != FALLBACK_MODEL:
        if not silent:
            print(f"    ⚠ Switching to fallback model ({FALLBACK_MODEL})")
        
        # Activate fallback state
        if not _fallback_state.active:
            _fallback_state.active = True
            _fallback_state.primary_model = model_name
            _fallback_state.last_failure_time = time.time()
        
        _fallback_state.fallback_count += 1
        _fallback_state.consecutive_successes = 0
        
        # Try with fallback model (no retries, fail fast)
        try:
            result = func()
            return result
        except Exception as fallback_error:
            if not silent:
                print(f"    ✗ Fallback model also failed")
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
