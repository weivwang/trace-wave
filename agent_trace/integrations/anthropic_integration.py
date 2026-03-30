"""Auto-instrumentation for Anthropic SDK.

Usage:
    from agent_trace.integrations.anthropic_integration import instrument_anthropic
    instrument_anthropic()

    client = anthropic.Anthropic()
    response = client.messages.create(...)  # auto-traced
"""
import functools
from typing import Any

from agent_trace.core.models import SpanKind
from agent_trace.core.tracer import tracer

# Model pricing (per 1K tokens) — approximate as of 2026
MODEL_COSTS: dict[str, tuple[float, float]] = {
    "claude-3-opus": (0.015, 0.075),
    "claude-3-sonnet": (0.003, 0.015),
    "claude-3-haiku": (0.00025, 0.00125),
    "claude-3.5-sonnet": (0.003, 0.015),
    "claude-3.5-haiku": (0.0008, 0.004),
    "claude-4-opus": (0.015, 0.075),
    "claude-4-sonnet": (0.003, 0.015),
}

# Sentinels to track original methods for uninstrumentation
_original_create = None
_original_async_create = None


def _get_cost(model: str) -> tuple[float, float]:
    """Look up (prompt, completion) cost per 1K tokens for *model*."""
    for key, cost in MODEL_COSTS.items():
        if key in model:
            return cost
    return (0.003, 0.015)  # default to sonnet-class pricing


def instrument_anthropic() -> None:
    """Patch Anthropic SDK to auto-trace all API calls.

    Both the synchronous ``Messages.create`` and the asynchronous
    ``AsyncMessages.create`` methods are monkey-patched so that every
    call is wrapped in an ``traceweave`` span.

    Raises:
        ImportError: If the ``anthropic`` package is not installed.
    """
    global _original_create, _original_async_create

    try:
        import anthropic
        import anthropic.resources.messages
    except ImportError:
        raise ImportError("anthropic package required: pip install traceweave[anthropic]")

    # Guard against double-instrumentation
    if _original_create is not None:
        return

    _original_create = anthropic.resources.messages.Messages.create

    @functools.wraps(_original_create)
    def traced_create(self: Any, *args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])

        with tracer.start_span(f"anthropic.{model}", SpanKind.LLM) as span:
            span._data.model_name = model
            span.set_input({
                "model": model,
                "message_count": len(messages),
                "max_tokens": kwargs.get("max_tokens"),
                "system": str(kwargs.get("system", ""))[:200] if kwargs.get("system") else None,
            })

            try:
                response = _original_create(self, *args, **kwargs)

                if hasattr(response, "usage"):
                    prompt_cost, completion_cost = _get_cost(model)
                    span.set_token_usage(
                        prompt_tokens=getattr(response.usage, "input_tokens", 0),
                        completion_tokens=getattr(response.usage, "output_tokens", 0),
                        model=model,
                        prompt_cost_per_1k=prompt_cost,
                        completion_cost_per_1k=completion_cost,
                    )

                if hasattr(response, "content") and response.content:
                    text = (
                        response.content[0].text
                        if hasattr(response.content[0], "text")
                        else str(response.content[0])
                    )
                    span.set_output({"content": text[:500]})

                return response
            except Exception as e:
                span.set_error(e)
                raise

    anthropic.resources.messages.Messages.create = traced_create

    # Patch async variant ------------------------------------------------------
    try:
        _original_async_create = anthropic.resources.messages.AsyncMessages.create

        @functools.wraps(_original_async_create)
        async def traced_async_create(self: Any, *args: Any, **kwargs: Any) -> Any:
            model = kwargs.get("model", "unknown")

            with tracer.start_span(f"anthropic.{model}", SpanKind.LLM) as span:
                span._data.model_name = model
                span.set_input({"model": model})

                try:
                    response = await _original_async_create(self, *args, **kwargs)

                    if hasattr(response, "usage"):
                        prompt_cost, completion_cost = _get_cost(model)
                        span.set_token_usage(
                            prompt_tokens=getattr(response.usage, "input_tokens", 0),
                            completion_tokens=getattr(response.usage, "output_tokens", 0),
                            model=model,
                            prompt_cost_per_1k=prompt_cost,
                            completion_cost_per_1k=completion_cost,
                        )

                    return response
                except Exception as e:
                    span.set_error(e)
                    raise

        anthropic.resources.messages.AsyncMessages.create = traced_async_create
    except Exception:
        pass  # async patching is best-effort


def uninstrument_anthropic() -> None:
    """Remove Anthropic instrumentation and restore original methods."""
    global _original_create, _original_async_create

    try:
        import anthropic
        import anthropic.resources.messages
    except ImportError:
        return

    if _original_create is not None:
        anthropic.resources.messages.Messages.create = _original_create
        _original_create = None

    if _original_async_create is not None:
        anthropic.resources.messages.AsyncMessages.create = _original_async_create
        _original_async_create = None
