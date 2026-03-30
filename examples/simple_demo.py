"""Minimal traceweave example — perfect for the README.

Run: python examples/simple_demo.py
"""
from agent_trace import tracer, trace_agent, trace_tool
from agent_trace.core.models import SpanKind
from agent_trace.dashboard.tui import print_trace


@trace_tool("calculator")
def add(a: int, b: int) -> int:
    return a + b


@trace_agent("math-agent")
def math_agent(question: str) -> int:
    # Simulate LLM reasoning
    with tracer.start_span("reasoning", SpanKind.LLM) as span:
        span.set_token_usage(prompt_tokens=100, completion_tokens=50, model="gpt-4")
        span.set_input({"question": question})
        span.set_output({"answer": "I need to add 2 and 3"})
    result = add(2, 3)
    return result


with tracer.start_trace("math-task"):
    answer = math_agent("What is 2 + 3?")

print(f"Answer: {answer}")
print()
print_trace(tracer.get_all_traces()[-1])
