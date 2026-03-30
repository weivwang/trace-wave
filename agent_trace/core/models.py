"""Core data models for traceweave.

Pydantic v2 models representing the fundamental building blocks of the
tracing system: spans, traces, token usage, and events. These models
form the data layer that all other components build upon.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SpanKind(str, Enum):
    """The type of operation a span represents.

    Each kind maps to a logical component in an AI agent pipeline:
    - AGENT: An autonomous agent performing reasoning and actions.
    - TOOL: An external tool invocation (search, calculator, API call, etc.).
    - LLM: A direct call to a language model.
    - CHAIN: A sequential composition of steps (e.g. LangChain chain).
    - RETRIEVER: A retrieval operation (vector DB lookup, document fetch).
    - CUSTOM: Any user-defined operation that doesn't fit the above.
    """

    AGENT = "agent"
    TOOL = "tool"
    LLM = "llm"
    CHAIN = "chain"
    RETRIEVER = "retriever"
    CUSTOM = "custom"


class SpanStatus(str, Enum):
    """Current lifecycle status of a span."""

    RUNNING = "running"
    OK = "ok"
    ERROR = "error"


class TokenUsage(BaseModel):
    """Token usage and cost information for an LLM call.

    Tracks both raw token counts and optional per-1k-token pricing so that
    the total cost can be computed automatically.
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Cost estimation
    prompt_cost_per_1k: float = 0.0
    completion_cost_per_1k: float = 0.0

    @property
    def total_cost(self) -> float:
        """Compute the total cost based on token counts and per-1k prices."""
        return (
            self.prompt_tokens * self.prompt_cost_per_1k / 1000
            + self.completion_tokens * self.completion_cost_per_1k / 1000
        )


class SpanEvent(BaseModel):
    """A timestamped event attached to a span.

    Events capture discrete occurrences during span execution, such as
    exceptions, retries, tool invocations, or user-defined milestones.
    """

    name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    attributes: dict[str, Any] = Field(default_factory=dict)


class SpanData(BaseModel):
    """A single span in a trace — represents one unit of work.

    Spans form a tree structure via ``parent_span_id`` and ``children``.
    Each span records timing, status, optional token usage, and arbitrary
    attributes for maximum observability.
    """

    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: Optional[str] = None
    name: str
    kind: SpanKind
    status: SpanStatus = SpanStatus.RUNNING
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: Optional[datetime] = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    events: list[SpanEvent] = Field(default_factory=list)
    token_usage: Optional[TokenUsage] = None
    model_name: Optional[str] = None
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error: Optional[str] = None
    children: list[SpanData] = Field(default_factory=list)

    @property
    def duration_ms(self) -> Optional[float]:
        """Duration in milliseconds, or ``None`` if the span hasn't ended."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    model_config = {
        "arbitrary_types_allowed": True,
        "protected_namespaces": (),
    }


class TraceData(BaseModel):
    """A complete trace — a tree of spans representing one agent execution.

    The trace is anchored by a ``root_span`` and provides aggregate
    properties for total tokens, cost, duration, and span count computed
    by recursively walking the span tree.
    """

    trace_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    root_span: SpanData
    metadata: dict[str, Any] = Field(default_factory=dict)

    # ── Aggregate properties ──────────────────────────────────────────

    @property
    def total_tokens(self) -> int:
        """Recursively sum all token usage across every span."""
        return self._sum_tokens(self.root_span)

    def _sum_tokens(self, span: SpanData) -> int:
        total = span.token_usage.total_tokens if span.token_usage else 0
        for child in span.children:
            total += self._sum_tokens(child)
        return total

    @property
    def total_cost(self) -> float:
        """Recursively sum all cost across every span."""
        return self._sum_cost(self.root_span)

    def _sum_cost(self, span: SpanData) -> float:
        cost = span.token_usage.total_cost if span.token_usage else 0.0
        for child in span.children:
            cost += self._sum_cost(child)
        return cost

    @property
    def total_duration_ms(self) -> Optional[float]:
        """Total duration of the trace, derived from the root span."""
        return self.root_span.duration_ms

    @property
    def span_count(self) -> int:
        """Total number of spans in the trace tree."""
        return self._count_spans(self.root_span)

    def _count_spans(self, span: SpanData) -> int:
        count = 1
        for child in span.children:
            count += self._count_spans(child)
        return count

    model_config = {
        "arbitrary_types_allowed": True,
        "protected_namespaces": (),
    }