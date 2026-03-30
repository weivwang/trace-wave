"""Auto-instrumentation for LangChain.

Usage:
    from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

    handler = AgentTraceCallbackHandler()
    llm = ChatOpenAI(callbacks=[handler])

    # Or attach to any chain / agent:
    chain.invoke({"input": "..."}, config={"callbacks": [handler]})
"""
from typing import Any, Optional, Union
from uuid import UUID

from agent_trace.core.models import SpanKind
from agent_trace.core.tracer import tracer


class AgentTraceCallbackHandler:
    """LangChain callback handler that creates traceweave spans.

    Each LangChain *run* (chain, LLM, tool, retriever) is mapped to an
    ``traceweave`` span whose lifetime mirrors the run's start/end/error
    lifecycle.  Token-usage information is extracted from the LLM response
    when available.

    Usage::

        from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

        handler = AgentTraceCallbackHandler()
        chain.invoke({"input": "..."}, config={"callbacks": [handler]})
    """

    def __init__(self) -> None:
        # run_id (str) -> (span, context_manager)
        self._spans: dict[str, tuple[Any, Any]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _start_span(
        self,
        run_id: UUID,
        name: str,
        kind: SpanKind,
        inputs: Optional[dict] = None,
    ) -> None:
        span_ctx = tracer.start_span(name, kind)
        span = span_ctx.__enter__()
        if inputs:
            span.set_input(inputs)
        self._spans[str(run_id)] = (span, span_ctx)

    def _end_span(
        self,
        run_id: UUID,
        outputs: Optional[dict] = None,
        error: Optional[Exception] = None,
    ) -> None:
        key = str(run_id)
        if key in self._spans:
            span, span_ctx = self._spans.pop(key)
            if outputs:
                span.set_output(outputs)
            if error:
                span.set_error(error)
            span_ctx.__exit__(type(error) if error else None, error, None)

    # ------------------------------------------------------------------
    # Chain callbacks
    # ------------------------------------------------------------------

    def on_chain_start(
        self,
        serialized: dict,
        inputs: dict,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        name = serialized.get("name", serialized.get("id", ["chain"])[-1])
        self._start_span(run_id, f"chain.{name}", SpanKind.CHAIN, inputs)

    def on_chain_end(self, outputs: dict, *, run_id: UUID, **kwargs: Any) -> None:
        self._end_span(run_id, outputs)

    def on_chain_error(self, error: Exception, *, run_id: UUID, **kwargs: Any) -> None:
        self._end_span(run_id, error=error)

    # ------------------------------------------------------------------
    # LLM callbacks
    # ------------------------------------------------------------------

    def on_llm_start(
        self,
        serialized: dict,
        prompts: list[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        name = serialized.get("name", "llm")
        self._start_span(run_id, f"llm.{name}", SpanKind.LLM, {"prompts": prompts[:3]})

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs: Any) -> None:
        outputs: dict[str, Any] = {}

        if hasattr(response, "generations"):
            outputs["generations"] = [
                [g.text[:200] for g in gen] for gen in response.generations[:3]
            ]

        # Extract token usage from llm_output when present
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            if token_usage:
                key = str(run_id)
                if key in self._spans:
                    span, _ = self._spans[key]
                    span.set_token_usage(
                        prompt_tokens=token_usage.get("prompt_tokens", 0),
                        completion_tokens=token_usage.get("completion_tokens", 0),
                    )

        self._end_span(run_id, outputs)

    def on_llm_error(self, error: Exception, *, run_id: UUID, **kwargs: Any) -> None:
        self._end_span(run_id, error=error)

    # ------------------------------------------------------------------
    # Tool callbacks
    # ------------------------------------------------------------------

    def on_tool_start(
        self,
        serialized: dict,
        input_str: str,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        name = serialized.get("name", "tool")
        self._start_span(run_id, f"tool.{name}", SpanKind.TOOL, {"input": input_str[:500]})

    def on_tool_end(self, output: str, *, run_id: UUID, **kwargs: Any) -> None:
        self._end_span(run_id, {"output": output[:500]})

    def on_tool_error(self, error: Exception, *, run_id: UUID, **kwargs: Any) -> None:
        self._end_span(run_id, error=error)

    # ------------------------------------------------------------------
    # Agent callbacks (delegated to tool-level spans)
    # ------------------------------------------------------------------

    def on_agent_action(self, action: Any, *, run_id: UUID, **kwargs: Any) -> None:
        pass  # Handled by tool callbacks

    def on_agent_finish(self, finish: Any, *, run_id: UUID, **kwargs: Any) -> None:
        pass

    # ------------------------------------------------------------------
    # Retriever callbacks
    # ------------------------------------------------------------------

    def on_retriever_start(
        self,
        serialized: dict,
        query: str,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        self._start_span(run_id, "retriever", SpanKind.RETRIEVER, {"query": query[:500]})

    def on_retriever_end(self, documents: Any, *, run_id: UUID, **kwargs: Any) -> None:
        self._end_span(run_id, {"doc_count": len(documents)})

    def on_retriever_error(self, error: Exception, *, run_id: UUID, **kwargs: Any) -> None:
        self._end_span(run_id, error=error)
