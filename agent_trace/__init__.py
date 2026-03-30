"""traceweave: Distributed tracing and observability for AI agents."""

__version__ = "0.1.0"

from agent_trace.core.models import (
    SpanKind,
    SpanStatus,
    TokenUsage,
    SpanEvent,
    SpanData,
    TraceData,
)
from agent_trace.core.span import Span
from agent_trace.core.context import get_current_span, get_current_trace
from agent_trace.core.tracer import AgentTracer, tracer
from agent_trace.core.decorators import trace_agent, trace_tool, trace_llm

__all__ = [
    "__version__",
    # Models
    "SpanKind",
    "SpanStatus",
    "TokenUsage",
    "SpanEvent",
    "SpanData",
    "TraceData",
    # Span
    "Span",
    # Context
    "get_current_span",
    "get_current_trace",
    # Tracer
    "AgentTracer",
    "tracer",
    # Decorators
    "trace_agent",
    "trace_tool",
    "trace_llm",
]
