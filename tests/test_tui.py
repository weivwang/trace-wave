"""Tests for TUI rendering."""
import pytest
from datetime import datetime, timezone
from agent_trace.core.models import SpanData, SpanKind, SpanStatus, TraceData, TokenUsage
from agent_trace.dashboard.tui import (
    format_duration, format_tokens, format_cost, render_trace
)


class TestFormatters:
    def test_format_duration_ms(self):
        assert "500ms" in format_duration(500)

    def test_format_duration_seconds(self):
        result = format_duration(2500)
        assert "2.5s" in result or "2.5" in result

    def test_format_duration_minutes(self):
        result = format_duration(120000)
        assert "2.0m" in result or "2" in result

    def test_format_duration_none(self):
        assert format_duration(None) == "..."

    def test_format_tokens_small(self):
        assert format_tokens(500) == "500"

    def test_format_tokens_large(self):
        assert "1.5k" in format_tokens(1500)

    def test_format_tokens_zero(self):
        assert format_tokens(0) == "-"

    def test_format_cost_zero(self):
        assert format_cost(0) == "-"

    def test_format_cost_small(self):
        result = format_cost(0.005)
        assert "$" in result


class TestRenderTrace:
    def test_render_basic_trace(self):
        root = SpanData(
            name="test", kind=SpanKind.CHAIN,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            status=SpanStatus.OK,
        )
        trace = TraceData(
            trace_id="test", name="test-trace",
            start_time=root.start_time,
            root_span=root,
        )
        panel = render_trace(trace)
        assert panel is not None
