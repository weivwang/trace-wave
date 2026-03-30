"""Tests for traceweave data models."""
import pytest
from datetime import datetime, timezone, timedelta
from agent_trace.core.models import (
    SpanKind, SpanStatus, TokenUsage, SpanEvent, SpanData, TraceData
)


class TestTokenUsage:
    def test_default_values(self):
        usage = TokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_total_cost(self):
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            prompt_cost_per_1k=0.003,
            completion_cost_per_1k=0.015,
        )
        expected = 1000 * 0.003 / 1000 + 500 * 0.015 / 1000
        assert abs(usage.total_cost - expected) < 1e-10

    def test_zero_cost(self):
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        assert usage.total_cost == 0.0


class TestSpanData:
    def test_creation(self):
        span = SpanData(name="test", kind=SpanKind.AGENT)
        assert span.name == "test"
        assert span.kind == SpanKind.AGENT
        assert span.status == SpanStatus.RUNNING
        assert span.trace_id  # auto-generated
        assert span.span_id  # auto-generated

    def test_duration(self):
        now = datetime.now(timezone.utc)
        span = SpanData(
            name="test", kind=SpanKind.TOOL,
            start_time=now,
            end_time=now + timedelta(seconds=1.5),
        )
        assert span.duration_ms is not None
        assert abs(span.duration_ms - 1500.0) < 1.0

    def test_duration_none_when_not_ended(self):
        span = SpanData(name="test", kind=SpanKind.TOOL)
        assert span.duration_ms is None

    def test_children(self):
        parent = SpanData(name="parent", kind=SpanKind.CHAIN)
        child = SpanData(name="child", kind=SpanKind.TOOL)
        parent.children.append(child)
        assert len(parent.children) == 1
        assert parent.children[0].name == "child"


class TestTraceData:
    def test_total_tokens(self):
        child = SpanData(
            name="llm", kind=SpanKind.LLM,
            token_usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )
        root = SpanData(
            name="root", kind=SpanKind.CHAIN,
            token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            children=[child],
        )
        trace = TraceData(
            trace_id="test", name="test",
            start_time=datetime.now(timezone.utc),
            root_span=root,
        )
        assert trace.total_tokens == 150

    def test_span_count(self):
        child1 = SpanData(name="c1", kind=SpanKind.TOOL)
        child2 = SpanData(name="c2", kind=SpanKind.LLM)
        root = SpanData(name="root", kind=SpanKind.CHAIN, children=[child1, child2])
        trace = TraceData(
            trace_id="test", name="test",
            start_time=datetime.now(timezone.utc),
            root_span=root,
        )
        assert trace.span_count == 3

    def test_total_cost(self):
        child = SpanData(
            name="llm", kind=SpanKind.LLM,
            token_usage=TokenUsage(
                prompt_tokens=1000, completion_tokens=500, total_tokens=1500,
                prompt_cost_per_1k=0.003, completion_cost_per_1k=0.015,
            ),
        )
        root = SpanData(name="root", kind=SpanKind.CHAIN, children=[child])
        trace = TraceData(
            trace_id="test", name="test",
            start_time=datetime.now(timezone.utc),
            root_span=root,
        )
        expected = 1000 * 0.003 / 1000 + 500 * 0.015 / 1000
        assert abs(trace.total_cost - expected) < 1e-10
