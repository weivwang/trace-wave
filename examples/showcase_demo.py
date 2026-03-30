#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  🔍 traceweave — Showcase Demo                                  ║
║                                                                  ║
║  A real-world AI startup workflow: from customer email to        ║
║  automated response, with multi-agent collaboration, RAG,       ║
║  tool calls, error handling, retries, and cost tracking.        ║
║                                                                  ║
║  No API keys needed — everything is simulated.                  ║
║                                                                  ║
║  Run:  python examples/showcase_demo.py                         ║
╚══════════════════════════════════════════════════════════════════╝
"""
import time
import random
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from agent_trace import tracer, trace_agent, trace_tool
from agent_trace.core.models import SpanKind
from agent_trace.dashboard.tui import print_trace, render_trace, render_multi_trace
from agent_trace.exporters.json_exporter import export_json

console = Console()


# ═══════════════════════════════════════════════════════════════════
#  🔧 Tools — Simulated external services
# ═══════════════════════════════════════════════════════════════════

@trace_tool("email-reader")
def read_email(email_id: str) -> dict:
    """Read an email from inbox."""
    time.sleep(random.uniform(0.1, 0.2))
    return {
        "id": email_id,
        "from": "john@acmecorp.com",
        "subject": "Urgent: Production API returning 500 errors",
        "body": (
            "Hi Support,\n\n"
            "Our production integration has been returning 500 errors "
            "since 2pm UTC. We're on the Enterprise plan and this is "
            "blocking our release. Error: 'rate_limit_exceeded'. "
            "Can you please look into this ASAP?\n\n"
            "Ticket: ACME-4521\nPriority: P0\n\nThanks,\nJohn"
        ),
        "priority": "high",
        "timestamp": "2026-03-31T14:23:00Z",
    }


@trace_tool("vector-search")
def vector_search(query: str, top_k: int = 3) -> list[dict]:
    """Search knowledge base via vector similarity."""
    time.sleep(random.uniform(0.2, 0.4))
    return [
        {
            "doc_id": "kb-1042",
            "title": "Rate Limiting — Troubleshooting Guide",
            "content": "When users hit rate_limit_exceeded, check: 1) Current plan limits 2) Burst quota 3) API key tier...",
            "score": 0.94,
        },
        {
            "doc_id": "kb-0887",
            "title": "Enterprise Plan — Rate Limits",
            "content": "Enterprise plan: 10,000 RPM, 1M tokens/day. Burst: 2x for 60s. Contact support for temporary increases...",
            "score": 0.89,
        },
        {
            "doc_id": "kb-1205",
            "title": "500 Error Codes — Internal Reference",
            "content": "500 errors with rate_limit_exceeded indicate the account has exceeded allocated quota. Resolution: ...",
            "score": 0.85,
        },
    ]


@trace_tool("sql-query")
def query_customer_db(customer_email: str) -> dict:
    """Query customer database for account info."""
    time.sleep(random.uniform(0.1, 0.3))
    return {
        "customer_id": "cust_8a3f2b",
        "company": "Acme Corp",
        "plan": "enterprise",
        "api_calls_today": 12847,
        "daily_limit": 10000,
        "status": "rate_limited",
        "account_health": "at_risk",
        "mrr": 4500,
    }


@trace_tool("slack-notify")
def send_slack_notification(channel: str, message: str) -> bool:
    """Send notification to Slack channel."""
    time.sleep(random.uniform(0.1, 0.2))
    return True


@trace_tool("ticket-update")
def update_ticket(ticket_id: str, status: str, notes: str) -> bool:
    """Update support ticket in system."""
    time.sleep(random.uniform(0.1, 0.2))
    return True


@trace_tool("rate-limit-override")
def apply_rate_limit_override(customer_id: str, new_limit: int, duration_hours: int) -> dict:
    """Apply temporary rate limit increase for a customer."""
    time.sleep(random.uniform(0.2, 0.4))
    return {
        "override_id": "ovr_x9k2m",
        "customer_id": customer_id,
        "new_limit": new_limit,
        "expires_at": "2026-04-01T14:23:00Z",
        "status": "applied",
    }


@trace_tool("send-email")
def send_email(to: str, subject: str, body: str) -> bool:
    """Send email response to customer."""
    time.sleep(random.uniform(0.2, 0.3))
    return True


@trace_tool("sentiment-api")
def analyze_sentiment(text: str) -> dict:
    """Analyze customer sentiment (external API, sometimes fails)."""
    time.sleep(random.uniform(0.3, 0.5))
    # Simulate occasional API failure
    if random.random() < 0.6:
        raise ConnectionError("Sentiment API timeout after 5000ms")
    return {"sentiment": "frustrated", "urgency": 0.92, "churn_risk": 0.78}


# ═══════════════════════════════════════════════════════════════════
#  🧠 LLM Calls — Simulated with realistic token tracking
# ═══════════════════════════════════════════════════════════════════

def llm_call(name: str, prompt: str, model: str = "claude-4-sonnet",
             system: str = None) -> str:
    """Simulate an LLM API call with token & cost tracking."""
    with tracer.start_span(name, SpanKind.LLM) as span:
        span._data.model_name = model
        span.set_input({"prompt": prompt[:300], "system": system[:100] if system else None})

        # Simulate varying latency based on model
        latency_map = {
            "claude-4-sonnet": (0.4, 1.0),
            "claude-4-opus": (0.8, 2.0),
            "gpt-4o": (0.3, 0.8),
            "claude-4-haiku": (0.1, 0.3),
        }
        lo, hi = latency_map.get(model, (0.3, 0.8))
        time.sleep(random.uniform(lo, hi))

        # Realistic token counts
        prompt_tokens = len(prompt.split()) * 2 + random.randint(100, 500)
        completion_tokens = random.randint(150, 800)

        cost_map = {
            "claude-4-sonnet": (0.003, 0.015),
            "claude-4-opus": (0.015, 0.075),
            "gpt-4o": (0.005, 0.015),
            "claude-4-haiku": (0.00025, 0.00125),
        }
        p_cost, c_cost = cost_map.get(model, (0.003, 0.015))

        span.set_token_usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=model,
            prompt_cost_per_1k=p_cost,
            completion_cost_per_1k=c_cost,
        )

        response = f"[{name} response for model {model}]"
        span.set_output({"response": response[:200]})
        return response


# ═══════════════════════════════════════════════════════════════════
#  🤖 Agents — Multi-agent support pipeline
# ═══════════════════════════════════════════════════════════════════

@trace_agent("triage-agent")
def triage_agent(email: dict) -> dict:
    """Classify and prioritize incoming support email."""
    # Analyze email with fast model for classification
    classification = llm_call(
        "classify-email",
        f"Classify this support email:\nSubject: {email['subject']}\n"
        f"Body: {email['body']}\n\n"
        "Return: category, priority, requires_human, suggested_team",
        model="claude-4-haiku",
    )

    # Try sentiment analysis (may fail — demonstrates error handling)
    sentiment = None
    try:
        sentiment = analyze_sentiment(email["body"])
    except ConnectionError:
        # Retry once with backoff
        time.sleep(0.2)
        try:
            sentiment = analyze_sentiment(email["body"])
        except ConnectionError:
            # Log and continue without sentiment — graceful degradation
            sentiment = {"sentiment": "unknown", "urgency": 0.8, "churn_risk": 0.5}

    return {
        "category": "api_error",
        "priority": "P0",
        "requires_human": False,
        "team": "platform",
        "sentiment": sentiment,
    }


@trace_agent("research-agent")
def research_agent(email: dict, triage: dict) -> dict:
    """Research the issue using knowledge base and customer data."""
    # RAG: Search knowledge base
    kb_results = vector_search(
        f"rate_limit_exceeded 500 error enterprise plan"
    )

    # Query customer database
    customer = query_customer_db(email["from"])

    # Deep analysis with RAG context
    analysis = llm_call(
        "analyze-issue",
        f"Customer issue: {email['body']}\n\n"
        f"Knowledge base results:\n{kb_results}\n\n"
        f"Customer data: {customer}\n\n"
        "Analyze root cause and suggest resolution.",
        model="claude-4-sonnet",
        system="You are a senior support engineer. Be thorough.",
    )

    return {
        "root_cause": "Customer exceeded daily API limit (12,847/10,000)",
        "customer": customer,
        "kb_articles": [r["doc_id"] for r in kb_results],
        "recommendation": "temporary_limit_increase",
        "analysis": analysis,
    }


@trace_agent("resolution-agent")
def resolution_agent(research: dict) -> dict:
    """Execute the resolution plan."""
    customer = research["customer"]

    # Apply rate limit override
    override = apply_rate_limit_override(
        customer_id=customer["customer_id"],
        new_limit=20000,
        duration_hours=24,
    )

    # Update ticket
    update_ticket(
        ticket_id="ACME-4521",
        status="in_progress",
        notes=f"Applied temp limit increase to 20K RPM. Override: {override['override_id']}",
    )

    # Notify internal team
    send_slack_notification(
        channel="#support-escalations",
        message=f"🚨 P0 resolved: Acme Corp (${customer['mrr']}/mo MRR) "
                f"rate limited. Temp override applied: {override['override_id']}",
    )

    return {
        "actions_taken": [
            "rate_limit_increased_to_20k",
            "ticket_updated",
            "slack_notified",
        ],
        "override": override,
    }


@trace_agent("response-agent")
def response_agent(email: dict, research: dict, resolution: dict) -> str:
    """Draft and send customer response."""
    # Generate personalized response
    draft = llm_call(
        "draft-response",
        f"Write a professional support response.\n"
        f"Customer: {email['from']} (Enterprise plan)\n"
        f"Issue: Rate limiting causing 500 errors\n"
        f"Root cause: Exceeded 10K daily limit at 12.8K calls\n"
        f"Resolution: Temp increase to 20K for 24h\n"
        f"Tone: Empathetic, proactive, professional",
        model="claude-4-opus",
        system="You write world-class customer support emails.",
    )

    # Quality check with a different model
    review = llm_call(
        "review-response",
        f"Review this customer email for:\n"
        f"1. Accuracy of technical details\n"
        f"2. Appropriate tone for frustrated Enterprise customer\n"
        f"3. Clear next steps\n\nDraft: {draft}",
        model="claude-4-sonnet",
    )

    # Send the email
    send_email(
        to=email["from"],
        subject=f"Re: {email['subject']} [ACME-4521]",
        body=draft,
    )

    # Final ticket update
    update_ticket(
        ticket_id="ACME-4521",
        status="resolved",
        notes="Customer response sent. Temp limit increase applied for 24h.",
    )

    return draft


# ═══════════════════════════════════════════════════════════════════
#  🚀 Main — Orchestrate the full pipeline
# ═══════════════════════════════════════════════════════════════════

def print_header():
    header = Text()
    header.append("🔍 traceweave", style="bold cyan")
    header.append(" — AI Support Agent Showcase\n", style="bold white")
    header.append(
        "Simulating a full AI-powered customer support pipeline:\n"
        "Email → Triage → Research (RAG) → Resolution → Response\n\n"
        "Features demonstrated:\n",
        style="dim",
    )
    header.append("  ✦ ", style="cyan")
    header.append("Multi-agent orchestration (4 specialized agents)\n", style="white")
    header.append("  ✦ ", style="yellow")
    header.append("8 tool calls (DB, vector search, Slack, email, etc.)\n", style="white")
    header.append("  ✦ ", style="magenta")
    header.append("5 LLM calls across 3 models with cost tracking\n", style="white")
    header.append("  ✦ ", style="red")
    header.append("Error handling & retry (sentiment API failure)\n", style="white")
    header.append("  ✦ ", style="green")
    header.append("RAG pipeline with vector similarity search\n", style="white")

    console.print(Panel(header, border_style="cyan", box=box.DOUBLE))
    console.print()


def print_step(icon: str, msg: str):
    console.print(f"  {icon}  {msg}", highlight=False)


def main():
    print_header()

    with tracer.start_trace(
        "customer-support-pipeline",
        metadata={
            "trigger": "incoming_email",
            "customer": "Acme Corp",
            "ticket": "ACME-4521",
        },
    ) as root:
        root.set_attribute("pipeline", "support-automation")

        # Step 1: Read email
        print_step("📨", "Reading incoming email...")
        email = read_email("msg_9x2k4")
        console.print(f"      [dim]From: {email['from']} | Subject: {email['subject']}[/dim]")

        # Step 2: Triage
        print_step("🏷️ ", "Triaging with AI (classification + sentiment)...")
        triage = triage_agent(email)
        console.print(f"      [dim]Category: {triage['category']} | Priority: {triage['priority']} | Sentiment: {triage['sentiment']['sentiment']}[/dim]")

        # Step 3: Research
        print_step("🔬", "Researching issue (RAG + customer DB)...")
        research = research_agent(email, triage)
        console.print(f"      [dim]Root cause: {research['root_cause']}[/dim]")

        # Step 4: Resolve
        print_step("⚡", "Executing resolution actions...")
        resolution = resolution_agent(research)
        console.print(f"      [dim]Actions: {', '.join(resolution['actions_taken'])}[/dim]")

        # Step 5: Respond
        print_step("✉️ ", "Drafting & sending customer response...")
        response = response_agent(email, research, resolution)
        console.print(f"      [dim]Response sent to {email['from']}[/dim]")

    console.print()

    # ── Print the trace ───────────────────────────────────────────
    traces = tracer.get_all_traces()
    for trace in traces:
        print_trace(trace)

    # ── Print summary stats ───────────────────────────────────────
    trace = traces[-1]
    console.print()
    summary = Panel(
        f"[bold]Pipeline completed in {trace.total_duration_ms/1000:.1f}s[/bold]\n\n"
        f"  🤖 Agents:     4 (triage → research → resolution → response)\n"
        f"  🔧 Tools:     {sum(1 for _ in _count_by_kind(trace.root_span, SpanKind.TOOL))} calls (email, DB, vector search, Slack, ticket)\n"
        f"  🧠 LLM calls: {sum(1 for _ in _count_by_kind(trace.root_span, SpanKind.LLM))} across 3 models\n"
        f"  📊 Tokens:    {trace.total_tokens:,}\n"
        f"  💰 Cost:      ${trace.total_cost:.4f}\n"
        f"  ❌ Errors:    {sum(1 for _ in _count_errors(trace.root_span))} (gracefully handled)\n\n"
        f"[dim]Install:[/dim] pip install traceweave\n"
        f"[dim]GitHub:[/dim]  https://github.com/traceweave/traceweave",
        title="[bold cyan]📊 Pipeline Summary[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
    )
    console.print(summary)

    # ── Export trace ──────────────────────────────────────────────
    output_path = export_json(trace, "showcase_trace.json")
    console.print(f"\n  [dim]Trace exported to: {output_path}[/dim]")
    console.print(f"  [dim]View in Chrome:    Open chrome://tracing → Load showcase_trace.json[/dim]")
    console.print()


def _count_by_kind(span, kind):
    """Recursively yield spans of a given kind."""
    if span.kind == kind:
        yield span
    for child in span.children:
        yield from _count_by_kind(child, kind)


def _count_errors(span):
    """Recursively yield spans with errors."""
    if span.error:
        yield span
    for child in span.children:
        yield from _count_errors(child)


if __name__ == "__main__":
    main()
