"""Zero-config decorators for tracing AI agent operations.

Usage:
    from agent_trace import trace_agent, trace_tool, trace_llm

    @trace_agent("researcher")
    def research(query: str) -> str:
        return do_research(query)

    @trace_tool("web-search")
    def search(query: str) -> list[str]:
        return web_search(query)

    @trace_llm(model="claude-3-opus")
    def generate(prompt: str) -> str:
        return call_llm(prompt)
"""
import functools
import inspect
from contextlib import contextmanager
from typing import Any, Callable, Optional, TypeVar

from agent_trace.core.models import SpanKind
from agent_trace.core.context import get_current_trace
from agent_trace.core.tracer import tracer as default_tracer

F = TypeVar("F", bound=Callable[..., Any])


@contextmanager
def _auto_span(name: str, kind: SpanKind, attributes: Optional[dict] = None):
    """Context manager that auto-creates a trace if none is active.

    When called outside an existing trace, uses ``start_trace`` to create
    a root trace+span.  When called inside a trace, uses ``start_span``
    to create a nested child span.
    """
    if get_current_trace() is None:
        # No active trace — create a new root trace
        with default_tracer.start_trace(name, metadata=attributes) as span:
            # The root span kind defaults to CHAIN; override it
            span._data.kind = kind
            if attributes:
                span._data.attributes.update(attributes)
            yield span
    else:
        # Already inside a trace — create a child span
        with default_tracer.start_span(name, kind, attributes=attributes) as span:
            yield span


def trace_agent(
    name: Optional[str] = None,
    *,
    attributes: Optional[dict] = None,
    capture_input: bool = True,
    capture_output: bool = True,
) -> Callable[[F], F]:
    """Decorator to trace an agent function.

    Can be used with or without parentheses::

        @trace_agent("planner")
        def plan(task: str) -> str: ...

        @trace_agent  # auto-detects name from function
        def plan(task: str) -> str: ...

    Args:
        name: Span name (defaults to the function name).
        attributes: Optional dict of initial span attributes.
        capture_input: Whether to record function arguments.
        capture_output: Whether to record the return value.
    """

    def decorator(func: F) -> F:
        span_name = name if isinstance(name, str) else func.__name__

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with _auto_span(span_name, SpanKind.AGENT, attributes) as span:
                if capture_input:
                    span.set_input(_capture_args(func, args, kwargs))
                try:
                    result = func(*args, **kwargs)
                    if capture_output:
                        span.set_output(_serialize_output(result))
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with _auto_span(span_name, SpanKind.AGENT, attributes) as span:
                if capture_input:
                    span.set_input(_capture_args(func, args, kwargs))
                try:
                    result = await func(*args, **kwargs)
                    if capture_output:
                        span.set_output(_serialize_output(result))
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    # Handle @trace_agent (without parens) and @trace_agent("name")
    if callable(name):
        func = name
        name = None
        return decorator(func)
    return decorator


def trace_tool(
    name: Optional[str] = None,
    *,
    attributes: Optional[dict] = None,
    capture_input: bool = True,
    capture_output: bool = True,
) -> Callable[[F], F]:
    """Decorator to trace a tool function.

    Usage::

        @trace_tool("web-search")
        def search(query: str) -> list: ...

        @trace_tool
        def calculator(expression: str) -> float: ...

    Args:
        name: Span name (defaults to the function name).
        attributes: Optional dict of initial span attributes.
        capture_input: Whether to record function arguments.
        capture_output: Whether to record the return value.
    """

    def decorator(func: F) -> F:
        span_name = name if isinstance(name, str) else func.__name__

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with _auto_span(span_name, SpanKind.TOOL, attributes) as span:
                if capture_input:
                    span.set_input(_capture_args(func, args, kwargs))
                try:
                    result = func(*args, **kwargs)
                    if capture_output:
                        span.set_output(_serialize_output(result))
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with _auto_span(span_name, SpanKind.TOOL, attributes) as span:
                if capture_input:
                    span.set_input(_capture_args(func, args, kwargs))
                try:
                    result = await func(*args, **kwargs)
                    if capture_output:
                        span.set_output(_serialize_output(result))
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    if callable(name):
        func = name
        name = None
        return decorator(func)
    return decorator


def trace_llm(
    name: Optional[str] = None,
    *,
    model: Optional[str] = None,
    attributes: Optional[dict] = None,
    capture_input: bool = True,
    capture_output: bool = True,
) -> Callable[[F], F]:
    """Decorator to trace an LLM call with token tracking.

    Automatically attempts to extract token usage from the return value
    if the result has a ``usage`` attribute (e.g. OpenAI / Anthropic
    response objects) or a ``"usage"`` dict key.

    Usage::

        @trace_llm(model="claude-3-opus")
        def generate(prompt: str) -> str: ...

        @trace_llm
        def chat(messages: list) -> dict: ...

    Args:
        name: Span name (defaults to the function name).
        model: Model name to record on the span (e.g. ``"gpt-4"``).
        attributes: Optional dict of initial span attributes.
        capture_input: Whether to record function arguments.
        capture_output: Whether to record the return value.
    """

    def decorator(func: F) -> F:
        span_name = name if isinstance(name, str) else func.__name__

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            attrs = {**(attributes or {})}
            if model:
                attrs["model"] = model
            with _auto_span(span_name, SpanKind.LLM, attrs) as span:
                if model:
                    span._data.model_name = model
                if capture_input:
                    span.set_input(_capture_args(func, args, kwargs))
                try:
                    result = func(*args, **kwargs)
                    if capture_output:
                        span.set_output(_serialize_output(result))
                    # Try to extract token usage from result
                    _try_extract_usage(span, result)
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            attrs = {**(attributes or {})}
            if model:
                attrs["model"] = model
            with _auto_span(span_name, SpanKind.LLM, attrs) as span:
                if model:
                    span._data.model_name = model
                if capture_input:
                    span.set_input(_capture_args(func, args, kwargs))
                try:
                    result = await func(*args, **kwargs)
                    if capture_output:
                        span.set_output(_serialize_output(result))
                    _try_extract_usage(span, result)
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    if callable(name):
        func = name
        name = None
        return decorator(func)
    return decorator


# ── Internal helpers ──────────────────────────────────────────────────────


def _capture_args(func: Callable, args: tuple, kwargs: dict) -> dict:
    """Capture function arguments as a serializable dict."""
    try:
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return {k: _serialize_output(v) for k, v in bound.arguments.items()}
    except Exception:
        return {
            "args": [str(a) for a in args],
            "kwargs": {k: str(v) for k, v in kwargs.items()},
        }


def _serialize_output(value: Any) -> Any:
    """Best-effort serialization of output values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_serialize_output(v) for v in value[:50]]  # Limit list size
    if isinstance(value, dict):
        return {str(k): _serialize_output(v) for k, v in list(value.items())[:50]}
    try:
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "__dict__"):
            return {
                k: str(v) for k, v in value.__dict__.items() if not k.startswith("_")
            }
    except Exception:
        pass
    return str(value)[:1000]


def _try_extract_usage(span: Any, result: Any) -> None:
    """Try to extract token usage from LLM response objects.

    Supports both attribute-style (``result.usage``) and dict-style
    (``result["usage"]``) access, covering OpenAI, Anthropic, and
    similar SDK response shapes.
    """
    usage = None
    if hasattr(result, "usage"):
        usage = result.usage
    elif isinstance(result, dict) and "usage" in result:
        usage = result["usage"]

    if usage is None:
        return

    prompt_tokens = getattr(usage, "prompt_tokens", 0) or (
        usage.get("prompt_tokens", 0) if isinstance(usage, dict) else 0
    )
    completion_tokens = getattr(usage, "completion_tokens", 0) or (
        usage.get("completion_tokens", 0) if isinstance(usage, dict) else 0
    )
    if prompt_tokens or completion_tokens:
        span.set_token_usage(
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens
        )
