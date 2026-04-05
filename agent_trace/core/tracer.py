"""Core tracer that manages spans and traces for AI agent observability.

The :class:`AgentTracer` is the central registry. It owns the lifecycle of
traces and spans, maintains the context-variable stack, emits real-time
events to registered listeners (e.g. the TUI dashboard), and stores
completed traces for later analysis.

Typical usage::

    from agent_trace import tracer

    with tracer.start_trace("research-task") as trace:
        with tracer.start_span("planner", SpanKind.AGENT) as span:
            span.set_input({"query": "research AI"})
            result = plan()
            span.set_output(result)
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from contextlib import contextmanager

from agent_trace.core.models import SpanData, SpanKind, SpanStatus, TraceData
from agent_trace.core.span import Span
from agent_trace.core.context import (
    get_current_span,
    set_current_span,
    reset_current_span,
    get_current_trace,
    set_current_trace,
    reset_current_trace,
)

# Type alias for event listener callbacks
EventListener = Callable[[str, dict[str, Any]], None]


class AgentTracer:
    """Main tracer for AI agent observability.

    The tracer provides two primary context managers:

    * :meth:`start_trace` — begins a top-level trace (creates a root span).
    * :meth:`start_span` — begins a child span within the current trace.

    Both automatically manage the context-variable stack so that nested
    spans are correctly parented, and both emit events to registered
    listeners for real-time dashboard updates.

    Usage::

        from agent_trace import tracer

        with tracer.start_trace("research-task") as trace:
            with tracer.start_span("planner", SpanKind.AGENT) as span:
                span.set_input({"query": "research AI"})
                result = plan()
                span.set_output(result)
    """

    def __init__(self, service_name: str = "traceweave") -> None:
        self.service_name = service_name
        self._traces: dict[str, TraceData] = {}
        self._active_spans: dict[str, Span] = {}
        self._listeners: list[EventListener] = []
        self._lock = threading.Lock()

    # ── Listener management ──────────────────────────────────────────

    def add_listener(self, callback: EventListener) -> None:
        """Add an event listener for real-time updates (used by dashboard)."""
        with self._lock:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def remove_listener(self, callback: EventListener) -> None:
        """Remove a previously registered event listener."""
        with self._lock:
            self._listeners = [ln for ln in self._listeners if ln != callback]

    def _emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Notify all listeners of an event. Errors in listeners are silently ignored."""
        for listener in self._listeners:
            try:
                listener(event_type, data)
            except Exception:
                pass  # Dashboard errors must never break tracing

    # ── Trace lifecycle ──────────────────────────────────────────────

    @contextmanager
    def start_trace(self, name: str, metadata: Optional[dict[str, Any]] = None):
        """Start a new trace (top-level operation).

        Creates a root span of kind :attr:`SpanKind.CHAIN`, sets the
        context variables, and yields the root :class:`Span`. On exit the
        trace is finalized and a ``trace_end`` event is emitted.

        Args:
            name: Human-readable name for the trace.
            metadata: Optional dict of arbitrary metadata to attach.

        Yields:
            The root :class:`Span` for this trace.
        """
        trace_id = uuid.uuid4().hex
        trace_token = set_current_trace(trace_id)

        root_span_data = SpanData(
            trace_id=trace_id,
            name=name,
            kind=SpanKind.CHAIN,
        )

        trace = TraceData(
            trace_id=trace_id,
            name=name,
            start_time=root_span_data.start_time,
            root_span=root_span_data,
            metadata=metadata or {},
        )

        with self._lock:
            self._traces[trace_id] = trace

        root_span = Span(root_span_data, self)
        span_token = set_current_span(root_span)

        self._emit("trace_start", {"trace_id": trace_id, "name": name})

        try:
            yield root_span
        except Exception as e:
            root_span.set_error(e)
            raise
        finally:
            root_span.end()
            trace.end_time = datetime.now(timezone.utc)
            # Restore previous context using proper reset
            reset_current_span(span_token)
            reset_current_trace(trace_token)
            self._emit(
                "trace_end",
                {
                    "trace_id": trace_id,
                    "duration_ms": trace.total_duration_ms,
                    "total_tokens": trace.total_tokens,
                    "total_cost": trace.total_cost,
                    "span_count": trace.span_count,
                },
            )

    # ── Span lifecycle ───────────────────────────────────────────────

    @contextmanager
    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.CUSTOM,
        attributes: Optional[dict[str, Any]] = None,
    ):
        """Start a new span within the current trace.

        Automatically parents the span under the currently active span
        (if any) and updates the context stack. On exit the span is
        finalized and a ``span_end`` event is emitted.

        Args:
            name: Human-readable name for the span.
            kind: The :class:`SpanKind` of operation this span represents.
            attributes: Optional dict of initial attributes.

        Yields:
            The new :class:`Span`.
        """
        parent_span = get_current_span()
        trace_id = get_current_trace() or uuid.uuid4().hex

        span_data = SpanData(
            trace_id=trace_id,
            parent_span_id=parent_span.span_id if parent_span else None,
            name=name,
            kind=kind,
            attributes=attributes or {},
        )

        span = Span(span_data, self)

        # Attach to parent span's children list
        if parent_span:
            parent_span._data.children.append(span_data)

        with self._lock:
            self._active_spans[span_data.span_id] = span

        old_span_token = set_current_span(span)

        self._emit(
            "span_start",
            {
                "trace_id": trace_id,
                "span_id": span_data.span_id,
                "name": name,
                "kind": kind.value,
                "parent_span_id": span_data.parent_span_id,
            },
        )

        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            span.end()
            # Restore previous span context using proper reset
            reset_current_span(old_span_token)

    # ── Internal callbacks ───────────────────────────────────────────

    def _on_span_end(self, span: Span) -> None:
        """Called by :meth:`Span.end` to deregister the span and emit events."""
        with self._lock:
            self._active_spans.pop(span.span_id, None)
        self._emit(
            "span_end",
            {
                "trace_id": span.trace_id,
                "span_id": span.span_id,
                "name": span.name,
                "kind": span.kind.value,
                "status": span._data.status.value,
                "duration_ms": span._data.duration_ms,
                "token_usage": (
                    span._data.token_usage.model_dump()
                    if span._data.token_usage
                    else None
                ),
                "error": span._data.error,
            },
        )

    # ── Queries ──────────────────────────────────────────────────────

    def get_trace(self, trace_id: str) -> Optional[TraceData]:
        """Return a specific trace by ID, or ``None``."""
        return self._traces.get(trace_id)

    def get_all_traces(self) -> list[TraceData]:
        """Return a snapshot of all recorded traces."""
        return list(self._traces.values())

    def clear(self) -> None:
        """Remove all traces and active spans (useful for testing)."""
        with self._lock:
            self._traces.clear()
            self._active_spans.clear()

    def __repr__(self) -> str:
        return (
            f"<AgentTracer service={self.service_name!r} "
            f"traces={len(self._traces)} active_spans={len(self._active_spans)}>"
        )


# Backward-compatible alias
Tracer = AgentTracer

# ── Module-level singleton ───────────────────────────────────────────────
tracer = AgentTracer()
