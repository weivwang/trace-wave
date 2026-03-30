"""Active Span that acts as a context manager for tracing agent operations.

A :class:`Span` wraps a :class:`~agent_trace.core.models.SpanData` with a
rich mutation API and context-manager support so callers can write::

    with tracer.start_span("my-agent", SpanKind.AGENT) as span:
        span.set_attribute("model", "claude-3")
        result = do_work()
        span.set_output(result)

The span automatically records timing, captures exceptions, and notifies
the parent :class:`~agent_trace.core.tracer.AgentTracer` on completion.
"""
from __future__ import annotations

import traceback
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional

from agent_trace.core.models import SpanData, SpanKind, SpanStatus, SpanEvent, TokenUsage

if TYPE_CHECKING:
    from agent_trace.core.tracer import AgentTracer


class Span:
    """A span represents a single operation within a trace.

    Usage::

        with tracer.start_span("my-agent", SpanKind.AGENT) as span:
            span.set_attribute("model", "claude-3")
            result = do_work()
            span.set_output(result)
    """

    __slots__ = ("_data", "_tracer", "_children", "_finished")

    def __init__(self, data: SpanData, tracer: AgentTracer) -> None:
        self._data = data
        self._tracer = tracer
        self._children: list[Span] = []
        self._finished = False

    # ── Read-only properties ──────────────────────────────────────────

    @property
    def span_id(self) -> str:
        return self._data.span_id

    @property
    def trace_id(self) -> str:
        return self._data.trace_id

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def kind(self) -> SpanKind:
        return self._data.kind

    @property
    def data(self) -> SpanData:
        return self._data

    # ── Mutators (fluent API — each returns self) ─────────────────────

    def set_attribute(self, key: str, value: Any) -> Span:
        """Set an arbitrary key-value attribute on this span."""
        self._data.attributes[key] = value
        return self

    def set_input(self, input_data: Any) -> Span:
        """Record the input payload for this span."""
        self._data.input_data = input_data
        return self

    def set_output(self, output_data: Any) -> Span:
        """Record the output / return value for this span."""
        self._data.output_data = output_data
        return self

    def set_token_usage(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        model: Optional[str] = None,
        prompt_cost_per_1k: float = 0.0,
        completion_cost_per_1k: float = 0.0,
    ) -> Span:
        """Record LLM token usage and optional cost information.

        Args:
            prompt_tokens: Number of tokens in the prompt / input.
            completion_tokens: Number of tokens in the completion / output.
            model: Optional model name (e.g. ``"gpt-4"``).
            prompt_cost_per_1k: Cost per 1 000 prompt tokens (USD).
            completion_cost_per_1k: Cost per 1 000 completion tokens (USD).
        """
        self._data.token_usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            prompt_cost_per_1k=prompt_cost_per_1k,
            completion_cost_per_1k=completion_cost_per_1k,
        )
        if model:
            self._data.model_name = model
        return self

    def add_event(self, name: str, attributes: Optional[dict[str, Any]] = None) -> Span:
        """Append a timestamped event to this span.

        Events are useful for recording discrete milestones such as retries,
        cache hits, or intermediate tool invocations.
        """
        self._data.events.append(
            SpanEvent(
                name=name,
                attributes=attributes or {},
            )
        )
        self._tracer._emit("span_event", {"span_id": self.span_id, "event": name})
        return self

    def set_error(self, error: Exception) -> Span:
        """Mark this span as errored and record full exception details.

        Sets the status to :attr:`SpanStatus.ERROR`, stores a human-readable
        error string, and appends an ``exception`` event with the full
        traceback.
        """
        self._data.status = SpanStatus.ERROR
        self._data.error = f"{type(error).__name__}: {str(error)}"
        self._data.events.append(
            SpanEvent(
                name="exception",
                attributes={
                    "exception.type": type(error).__name__,
                    "exception.message": str(error),
                    "exception.stacktrace": traceback.format_exc(),
                },
            )
        )
        return self

    # ── Lifecycle ─────────────────────────────────────────────────────

    def end(self, status: Optional[SpanStatus] = None) -> None:
        """Finish this span, record the end time, and notify the tracer.

        If no explicit *status* is given and the span is still
        :attr:`SpanStatus.RUNNING`, it is automatically marked as
        :attr:`SpanStatus.OK`.

        This method is idempotent — calling it multiple times is safe.
        """
        if self._finished:
            return
        self._finished = True
        self._data.end_time = datetime.now(UTC)
        if status:
            self._data.status = status
        elif self._data.status == SpanStatus.RUNNING:
            self._data.status = SpanStatus.OK
        self._tracer._on_span_end(self)

    # Alias for backward compatibility
    finish = end

    # ── Context manager protocol ──────────────────────────────────────

    def __enter__(self) -> Span:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_val is not None:
            self.set_error(exc_val)
        self.end()
        return False  # Never suppress exceptions

    # ── Dunder helpers ────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"<Span name={self._data.name!r} kind={self._data.kind.value} "
            f"status={self._data.status.value}>"
        )
