"""🔍 traceweave Demo: Multi-Agent Research Team

This demo simulates a 3-agent research team to showcase traceweave's
tracing capabilities. No API keys required!

Run: python examples/multi_agent_demo.py
"""
import time
import random
from agent_trace import tracer, trace_agent, trace_tool, trace_llm
from agent_trace.core.models import SpanKind
from agent_trace.dashboard.tui import print_trace


# ── Simulated tools ──────────────────────────────────────────────────────


@trace_tool("web-search")
def web_search(query: str) -> list[str]:
    """Simulate a web search."""
    time.sleep(random.uniform(0.3, 0.8))
    return [
        f"Result 1 for '{query}': Recent advances in...",
        f"Result 2 for '{query}': A comprehensive survey of...",
        f"Result 3 for '{query}': Breaking: New research shows...",
    ]


@trace_tool("arxiv-search")
def arxiv_search(query: str) -> list[str]:
    """Simulate an ArXiv search."""
    time.sleep(random.uniform(0.2, 0.5))
    return [
        f"[2026.01234] {query}: A Novel Approach",
        f"[2026.05678] Scaling {query} with Transformers",
    ]


@trace_tool("summarize-document")
def summarize_doc(doc: str) -> str:
    """Simulate document summarization."""
    time.sleep(random.uniform(0.1, 0.3))
    return f"Summary: {doc[:100]}..."


# ── Simulated LLM calls ─────────────────────────────────────────────────


def simulate_llm_call(
    name: str, prompt: str, model: str = "claude-3-sonnet"
) -> str:
    """Simulate an LLM call with realistic token tracking."""
    with tracer.start_span(name, SpanKind.LLM) as span:
        span._data.model_name = model
        span.set_input({"prompt": prompt[:200]})

        # Simulate latency
        time.sleep(random.uniform(0.5, 1.5))

        prompt_tokens = random.randint(500, 2000)
        completion_tokens = random.randint(200, 1000)

        # Cost estimation (realistic pricing)
        cost_map = {
            "claude-3-sonnet": (0.003, 0.015),
            "claude-3-opus": (0.015, 0.075),
            "gpt-4": (0.03, 0.06),
        }
        prompt_cost, completion_cost = cost_map.get(model, (0.003, 0.015))

        span.set_token_usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=model,
            prompt_cost_per_1k=prompt_cost,
            completion_cost_per_1k=completion_cost,
        )

        response = (
            f"Based on my analysis of the provided information, "
            f"here are the key findings regarding the topic..."
        )
        span.set_output({"response": response})
        return response


# ── Agent definitions ────────────────────────────────────────────────────


@trace_agent("planner")
def planner_agent(task: str) -> dict:
    """Plan the research approach."""
    plan = simulate_llm_call(
        "plan-generation",
        f"Create a research plan for: {task}",
        "claude-3-sonnet",
    )
    return {
        "queries": [
            f"{task} latest developments",
            f"{task} benchmark comparisons",
            f"{task} practical applications",
        ],
        "plan": plan,
    }


@trace_agent("researcher")
def researcher_agent(queries: list[str]) -> list[str]:
    """Execute research based on plan."""
    all_results = []
    for query in queries:
        web_results = web_search(query)
        arxiv_results = arxiv_search(query)
        all_results.extend(web_results + arxiv_results)

    # Analyze results with LLM
    analysis = simulate_llm_call(
        "analyze-results",
        f"Analyze these {len(all_results)} research results and identify "
        f"key themes, contradictions, and novel insights...",
        "claude-3-sonnet",
    )
    all_results.append(analysis)
    return all_results


@trace_agent("writer")
def writer_agent(research: list[str]) -> str:
    """Write the final report."""
    # Summarize key documents first
    for doc in research[:3]:
        summarize_doc(doc)

    # Generate final report
    report = simulate_llm_call(
        "write-report",
        f"Write a comprehensive report based on {len(research)} sources. "
        f"Include an executive summary, key findings, and recommendations...",
        "claude-3-opus",
    )
    return report


@trace_agent("reviewer")
def reviewer_agent(report: str) -> str:
    """Review and improve the report."""
    review = simulate_llm_call(
        "review-report",
        f"Review this report for accuracy, completeness, and clarity. "
        f"Flag any unsupported claims: {report[:200]}",
        "claude-3-sonnet",
    )
    return review


# ── Main entry point ─────────────────────────────────────────────────────


def main():
    print("🔍 traceweave Demo: Multi-Agent Research Team")
    print("=" * 50)
    print()
    print("Simulating a 4-agent pipeline:")
    print("  📋 Planner  → plans the research approach")
    print("  🔬 Researcher → searches web + ArXiv")
    print("  ✍️  Writer   → drafts the report")
    print("  📝 Reviewer  → reviews for quality")
    print()

    with tracer.start_trace(
        "multi-agent-research",
        metadata={"topic": "AI agents", "team_size": 4},
    ) as root:
        root.set_attribute("task_type", "research")

        # Step 1: Plan
        print("📋 Planning research approach...")
        plan = planner_agent("AI agent frameworks 2026")

        # Step 2: Research
        print("🔬 Researching (3 queries, web + ArXiv)...")
        research = researcher_agent(plan["queries"])

        # Step 3: Write
        print("✍️  Writing report...")
        report = writer_agent(research)

        # Step 4: Review
        print("📝 Reviewing report...")
        review = reviewer_agent(report)

    # Print the beautiful trace
    print()
    traces = tracer.get_all_traces()
    for trace in traces:
        print_trace(trace)

    print()
    print("💡 Try the web dashboard:  traceweave dashboard")
    print("💡 Export to Chrome:       traceweave export trace.json --format chrome")


if __name__ == "__main__":
    main()
