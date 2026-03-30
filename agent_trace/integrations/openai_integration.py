"""Auto-instrumentation for OpenAI SDK.

Usage:
    from agent_trace.integrations.openai_integration import instrument_openai
    instrument_openai()

    # Now all OpenAI calls are automatically traced!
    client = openai.OpenAI()
    response = client.chat.completions.create(...)  # auto-traced
"""
import functools
from typing import Any

from agent_trace.core.models import SpanKind
from agent_trace.core.tracer import tracer

# Model pricing (per 1K tokens) — approximate as of 2026
MODEL_COSTS: dict[str, tuple[float, float]] = {
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-4": (0.03, 0.06),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    "o1": (0.015, 0.06),
    "o1-mini": (0.003, 0.012),
    "o3-mini": (0.0011, 0.0044),
}

# Sentinels to track original methods for uninstrumentation
_original_create = None
_original_async_create = None


def _get_cost(model: str) -> tuple[float, float]:
    """Look up (prompt, completion) cost per 1K tokens for *model*."""
    for key, cost in MODEL_COSTS.items():
        if key in model:
            return cost
    return (0.01, 0.03)  # conservative default


def _truncated_messages(messages: list[dict], max_messages: int = 5, max_chars: int = 200) -> list[dict]:
    """Return a compact representation of the first *max_messages* messages."""
    return [
        {
            "role": m.get("role", ""),
            "content": str(m.get("content", ""))[:max_chars],
        }
        for m in messages[:max_messages]
    ]


def instrument_openai() -> None:
    """Patch OpenAI SDK to auto-trace all API calls.

    Both the synchronous ``Completions.create`` and the asynchronous
    ``AsyncCompletions.create`` methods are monkey-patched so that every
    call is wrapped in an ``traceweave`` span.

    Raises:
        ImportError: If the ``openai`` package is not installed.
    """
    global _original_create, _original_async_create

    try:
        import openai
        import openai.resources.chat.completions
    except ImportError:
        raise ImportError("openai package required: pip install traceweave[openai]")

    # Guard against double-instrumentation
    if _original_create is not None:
        return

    _original_create = openai.resources.chat.completions.Completions.create

    @functools.wraps(_original_create)
    def traced_create(self: Any, *args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])

        with tracer.start_span(f"openai.{model}", SpanKind.LLM) as span:
            span._data.model_name = model
            span.set_input({
                "model": model,
                "messages": _truncated_messages(messages),
                "temperature": kwargs.get("temperature"),
                "max_tokens": kwargs.get("max_tokens"),
            })

            try:
                response = _original_create(self, *args, **kwargs)

                # Extract usage
                if hasattr(response, "usage") and response.usage:
                    prompt_cost, completion_cost = _get_cost(model)
                    span.set_token_usage(
                        prompt_tokens=response.usage.prompt_tokens or 0,
                        completion_tokens=response.usage.completion_tokens or 0,
                        model=model,
                        prompt_cost_per_1k=prompt_cost,
                        completion_cost_per_1k=completion_cost,
                    )

                # Extract output
                if hasattr(response, "choices") and response.choices:
                    content = response.choices[0].message.content
                    span.set_output({"content": content[:500] if content else None})

                return response
            except Exception as e:
                span.set_error(e)
                raise

    openai.resources.chat.completions.Completions.create = traced_create

    # Also patch async variant -------------------------------------------------
    try:
        _original_async_create = openai.resources.chat.completions.AsyncCompletions.create

        @functools.wraps(_original_async_create)
        async def traced_async_create(self: Any, *args: Any, **kwargs: Any) -> Any:
            model = kwargs.get("model", "unknown")
            messages = kwargs.get("messages", [])

            with tracer.start_span(f"openai.{model}", SpanKind.LLM) as span:
                span._data.model_name = model
                span.set_input({"model": model, "message_count": len(messages)})

                try:
                    response = await _original_async_create(self, *args, **kwargs)

                    if hasattr(response, "usage") and response.usage:
                        prompt_cost, completion_cost = _get_cost(model)
                        span.set_token_usage(
                            prompt_tokens=response.usage.prompt_tokens or 0,
                            completion_tokens=response.usage.completion_tokens or 0,
                            model=model,
                            prompt_cost_per_1k=prompt_cost,
                            completion_cost_per_1k=completion_cost,
                        )

                    if hasattr(response, "choices") and response.choices:
                        span.set_output({
                            "content": str(response.choices[0].message.content)[:500],
                        })

                    return response
                except Exception as e:
                    span.set_error(e)
                    raise

        openai.resources.chat.completions.AsyncCompletions.create = traced_async_create
    except Exception:
        pass  # async patching is best-effort


def uninstrument_openai() -> None:
    """Remove OpenAI instrumentation and restore original methods."""
    global _original_create, _original_async_create

    try:
        import openai
        import openai.resources.chat.completions
    except ImportError:
        return

    if _original_create is not None:
        openai.resources.chat.completions.Completions.create = _original_create
        _original_create = None

    if _original_async_create is not None:
        openai.resources.chat.completions.AsyncCompletions.create = _original_async_create
        _original_async_create = None
