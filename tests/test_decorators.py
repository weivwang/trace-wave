"""Tests for decorator-based tracing."""
import pytest
import asyncio
from agent_trace.core.tracer import tracer
from agent_trace.core.decorators import trace_agent, trace_tool, trace_llm
from agent_trace.core.models import SpanKind


class TestDecorators:
    def setup_method(self):
        tracer.clear()

    def test_trace_agent_with_name(self):
        @trace_agent("my-agent")
        def agent_fn(query: str) -> str:
            return f"result: {query}"

        with tracer.start_trace("test"):
            result = agent_fn("hello")

        assert result == "result: hello"
        traces = tracer.get_all_traces()
        assert len(traces) >= 1

    def test_trace_agent_without_name(self):
        @trace_agent
        def auto_named_agent(x: int) -> int:
            return x * 2

        with tracer.start_trace("test"):
            result = auto_named_agent(5)

        assert result == 10

    def test_trace_tool(self):
        @trace_tool("calculator")
        def add(a: int, b: int) -> int:
            return a + b

        with tracer.start_trace("test"):
            result = add(2, 3)

        assert result == 5

    def test_trace_llm(self):
        @trace_llm(model="test-model")
        def generate(prompt: str) -> str:
            return "generated text"

        with tracer.start_trace("test"):
            result = generate("hello")

        assert result == "generated text"

    def test_nested_decorators(self):
        @trace_tool("search")
        def search(q: str) -> list:
            return ["result1"]

        @trace_agent("research")
        def research(topic: str) -> str:
            results = search(topic)
            return str(results)

        with tracer.start_trace("test"):
            result = research("AI")

        assert "result1" in result
        trace = tracer.get_all_traces()[-1]
        assert trace.span_count >= 3  # root + agent + tool

    def test_error_propagation(self):
        @trace_agent("failing")
        def failing_agent():
            raise RuntimeError("test error")

        with pytest.raises(RuntimeError, match="test error"):
            with tracer.start_trace("test"):
                failing_agent()

    def test_async_decorator(self):
        @trace_agent("async-agent")
        async def async_agent(query: str) -> str:
            return f"async: {query}"

        async def run():
            with tracer.start_trace("test"):
                return await async_agent("hello")

        result = asyncio.run(run())
        assert result == "async: hello"
