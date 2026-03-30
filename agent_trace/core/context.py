"""Context management for trace propagation across agent calls.

Uses :mod:`contextvars` so that each thread and async task gets its own
span stack, enabling correct parent-child relationships even with
concurrent agents. This is the mechanism that allows nested
``start_span`` calls to automatically link to their parent.

Usage (internal — most callers should use :class:`AgentTracer` directly)::

    from agent_trace.core.context import get_current_span, set_current_span

    token = set_current_span(my_span)
    # ... nested code sees my_span via get_current_span() ...
    reset_current_span(token)
"""
from __future__ import annotations

import contextvars
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agent_trace.core.span import Span

# ── Context variables ────────────────────────────────────────────────────
_current_span: contextvars.ContextVar[Optional[Span]] = contextvars.ContextVar(
    "current_span", default=None
)
_current_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_trace_id", default=None
)


# ── Public helpers ───────────────────────────────────────────────────────

def get_current_span() -> Optional[Span]:
    """Return the currently active span, or ``None`` if outside a trace."""
    return _current_span.get()


def set_current_span(span: Optional[Span]) -> contextvars.Token:
    """Set the currently active span and return a reset token.

    The returned :class:`contextvars.Token` can be passed to
    :func:`reset_current_span` to restore the previous value.
    """
    return _current_span.set(span)


def reset_current_span(token: contextvars.Token) -> None:
    """Restore the span context variable to its value before the given token."""
    _current_span.reset(token)


def get_current_trace() -> Optional[str]:
    """Return the currently active trace ID, or ``None``."""
    return _current_trace_id.get()


def set_current_trace(trace_id: Optional[str]) -> contextvars.Token:
    """Set the currently active trace ID and return a reset token."""
    return _current_trace_id.set(trace_id)


def reset_current_trace(token: contextvars.Token) -> None:
    """Restore the trace context variable to its value before the given token."""
    _current_trace_id.reset(token)
