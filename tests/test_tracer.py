"""Tests for the core tracer."""
import pytest
from agent_trace.core.tracer import AgentTracer
from agent_trace.core.models import SpanKind, SpanStatus
from agent_trace.core.context import get_current_span, get_current_trace


class TestAgentTracer:
    def setup_method(self):
        self.tracer = AgentTracer("test-service")

    def test_start_trace(self):
        with self.tracer.start_trace("test-trace") as root:
            assert root is not None
            assert root.name == "test-trace"

        traces = self.tracer.get_all_traces()
        assert len(traces) == 1
        assert traces[0].name == "test-trace"

    def test_nested_spans(self):
        with self.tracer.start_trace("test") as root:
            with self.tracer.start_span("agent", SpanKind.AGENT) as agent:
                with self.tracer.start_span("tool", SpanKind.TOOL) as tool:
                    tool.set_attribute("key", "value")

        trace = self.tracer.get_all_traces()[-1]
        assert trace.span_count >= 3

    def test_span_error_handling(self):
        with pytest.raises(ValueError):
            with self.tracer.start_trace("error-test") as root:
                with self.tracer.start_span("failing", SpanKind.TOOL) as span:
                    raise ValueError("test error")

        trace = self.tracer.get_all_traces()[-1]
        # The root span should have error status
        assert trace.root_span.status == SpanStatus.ERROR

    def test_context_propagation(self):
        with self.tracer.start_trace("ctx-test") as root:
            current = get_current_span()
            assert current is not None

            trace_id = get_current_trace()
            assert trace_id is not None

        # After context exit, should be clean
        assert get_current_span() is None

    def test_event_listeners(self):
        events = []

        def listener(event_type, data):
            events.append((event_type, data))

        self.tracer.add_listener(listener)

        with self.tracer.start_trace("listener-test") as root:
            with self.tracer.start_span("child", SpanKind.TOOL) as span:
                pass

        self.tracer.remove_listener(listener)

        event_types = [e[0] for e in events]
        assert "trace_start" in event_types
        assert "span_start" in event_types
        assert "span_end" in event_types
        assert "trace_end" in event_types

    def test_clear(self):
        with self.tracer.start_trace("test"):
            pass

        assert len(self.tracer.get_all_traces()) > 0
        self.tracer.clear()
        assert len(self.tracer.get_all_traces()) == 0

    def test_token_usage_tracking(self):
        with self.tracer.start_trace("token-test") as root:
            with self.tracer.start_span("llm", SpanKind.LLM) as span:
                span.set_token_usage(
                    prompt_tokens=100,
                    completion_tokens=50,
                    model="test-model",
                    prompt_cost_per_1k=0.01,
                    completion_cost_per_1k=0.03,
                )

        trace = self.tracer.get_all_traces()[-1]
        assert trace.total_tokens == 150
        assert trace.total_cost > 0
