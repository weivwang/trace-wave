"""Beautiful terminal UI for traceweave visualization using Rich."""
import time
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress_bar import ProgressBar
from rich.columns import Columns
from rich import box

from agent_trace.core.models import SpanData, SpanKind, SpanStatus, TraceData


# Color scheme
COLORS = {
    SpanKind.AGENT: "bold cyan",
    SpanKind.TOOL: "bold yellow",
    SpanKind.LLM: "bold magenta",
    SpanKind.CHAIN: "bold blue",
    SpanKind.RETRIEVER: "bold green",
    SpanKind.CUSTOM: "bold white",
}

STATUS_ICONS = {
    SpanStatus.RUNNING: "🔄",
    SpanStatus.OK: "✅",
    SpanStatus.ERROR: "❌",
}

KIND_ICONS = {
    SpanKind.AGENT: "🤖",
    SpanKind.TOOL: "🔧",
    SpanKind.LLM: "🧠",
    SpanKind.CHAIN: "🔗",
    SpanKind.RETRIEVER: "📚",
    SpanKind.CUSTOM: "⚡",
}


def format_duration(ms: Optional[float]) -> str:
    if ms is None:
        return "..."
    if ms < 1000:
        return f"{ms:.0f}ms"
    elif ms < 60000:
        return f"{ms/1000:.1f}s"
    else:
        return f"{ms/60000:.1f}m"


def format_tokens(tokens: int) -> str:
    if tokens == 0:
        return "-"
    if tokens < 1000:
        return str(tokens)
    return f"{tokens/1000:.1f}k"


def format_cost(cost: float) -> str:
    if cost == 0:
        return "-"
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"


def _build_span_tree(span: SpanData, tree: Tree, max_duration: float) -> None:
    """Recursively build a rich Tree from span data."""
    icon = KIND_ICONS.get(span.kind, "⚡")
    status = STATUS_ICONS.get(span.status, "❓")
    color = COLORS.get(span.kind, "white")

    duration_str = format_duration(span.duration_ms)
    tokens_str = format_tokens(span.token_usage.total_tokens if span.token_usage else 0)
    cost_str = format_cost(span.token_usage.total_cost if span.token_usage else 0.0)

    # Build the waterfall bar
    bar_width = 20
    if span.duration_ms and max_duration > 0:
        bar_fill = int((span.duration_ms / max_duration) * bar_width)
        bar_fill = max(1, min(bar_fill, bar_width))
    else:
        bar_fill = 1

    bar_char = "█"
    bar_empty = "░"

    if span.status == SpanStatus.ERROR:
        bar_color = "red"
    elif span.status == SpanStatus.RUNNING:
        bar_color = "yellow"
    else:
        bar_color = COLORS.get(span.kind, "white").replace("bold ", "")

    waterfall = f"[{bar_color}]{bar_char * bar_fill}[/{bar_color}][dim]{bar_empty * (bar_width - bar_fill)}[/dim]"

    # Model badge
    model_badge = f" [dim]({span.model_name})[/dim]" if span.model_name else ""

    # Error indicator
    error_text = f" [red]⚠ {span.error}[/red]" if span.error else ""

    label = (
        f"{status} {icon} [{color}]{span.name}[/{color}]{model_badge}"
        f"  {waterfall} {duration_str}"
        f"  [dim]tokens:[/dim] {tokens_str}"
        f"  [dim]cost:[/dim] {cost_str}"
        f"{error_text}"
    )

    branch = tree.add(label)

    for child in span.children:
        _build_span_tree(child, branch, max_duration)


def render_trace(trace: TraceData) -> Panel:
    """Render a single trace as a Rich Panel with tree visualization."""
    max_duration = trace.total_duration_ms or 1.0

    tree = Tree(
        f"[bold white]📍 Trace: {trace.name}[/bold white]"
        f"  [dim]id={trace.trace_id[:8]}...[/dim]"
    )

    _build_span_tree(trace.root_span, tree, max_duration)

    # Summary stats
    summary = Table(box=None, show_header=False, padding=(0, 2))
    summary.add_column("key", style="dim")
    summary.add_column("value", style="bold")

    summary.add_row("⏱  Duration", format_duration(trace.total_duration_ms))
    summary.add_row("🔢 Spans", str(trace.span_count))
    summary.add_row("📊 Tokens", format_tokens(trace.total_tokens))
    summary.add_row("💰 Cost", format_cost(trace.total_cost))

    layout = Table.grid(padding=(1, 0))
    layout.add_row(tree)
    layout.add_row(Panel(summary, title="[bold]Summary[/bold]", border_style="dim", box=box.ROUNDED))

    return Panel(
        layout,
        title=f"[bold cyan]🔍 traceweave[/bold cyan]",
        subtitle=f"[dim]{trace.start_time.strftime('%H:%M:%S')}[/dim]",
        border_style="cyan",
        box=box.DOUBLE,
    )


def render_multi_trace(traces: list[TraceData]) -> Layout:
    """Render multiple traces with an overview panel."""
    layout = Layout()

    # Overview table
    overview = Table(
        title="[bold]📋 Traces Overview[/bold]",
        box=box.ROUNDED,
        border_style="cyan",
    )
    overview.add_column("#", style="dim", width=4)
    overview.add_column("Name", style="bold cyan")
    overview.add_column("Status", width=8)
    overview.add_column("Duration", width=10)
    overview.add_column("Spans", width=8)
    overview.add_column("Tokens", width=10)
    overview.add_column("Cost", width=10)

    for i, trace in enumerate(traces):
        status = STATUS_ICONS.get(trace.root_span.status, "❓")
        overview.add_row(
            str(i + 1),
            trace.name,
            status,
            format_duration(trace.total_duration_ms),
            str(trace.span_count),
            format_tokens(trace.total_tokens),
            format_cost(trace.total_cost),
        )

    return overview


class TraceDashboard:
    """Live-updating terminal dashboard for agent traces."""

    def __init__(self, tracer=None):
        from agent_trace.core.tracer import tracer as default_tracer
        self.tracer = tracer or default_tracer
        self.console = Console()
        self._live: Optional[Live] = None

    def _render(self) -> Panel:
        traces = self.tracer.get_all_traces()

        if not traces:
            return Panel(
                "[dim]Waiting for traces...[/dim]\n\n"
                "[cyan]Instrument your code with:[/cyan]\n"
                "  from agent_trace import tracer, trace_agent\n\n"
                "  @trace_agent\n"
                "  def my_agent(query): ...",
                title="[bold cyan]🔍 traceweave dashboard[/bold cyan]",
                border_style="cyan",
                box=box.DOUBLE,
            )

        # Show the most recent trace in detail
        latest_trace = traces[-1]
        trace_panel = render_trace(latest_trace)

        if len(traces) > 1:
            overview = render_multi_trace(traces)
            grid = Table.grid(padding=(1, 0))
            grid.add_row(overview)
            grid.add_row(trace_panel)
            return Panel(grid, title="[bold cyan]🔍 traceweave dashboard[/bold cyan]", border_style="cyan", box=box.DOUBLE)

        return trace_panel

    def start(self):
        """Start the live dashboard."""
        self.tracer.add_listener(self._on_event)
        self._live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=4,
            screen=False,
        )
        self._live.start()

    def stop(self):
        """Stop the live dashboard."""
        if self._live:
            self._live.stop()
        self.tracer.remove_listener(self._on_event)

    def update(self):
        """Force a dashboard update."""
        if self._live:
            self._live.update(self._render())

    def _on_event(self, event_type: str, data: dict):
        self.update()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


def print_trace(trace: TraceData):
    """Print a trace to the terminal (non-live, single shot)."""
    console = Console()
    console.print(render_trace(trace))


def run_tui(port: int = 8420):
    """Run the TUI dashboard."""
    console = Console()
    console.print("[bold cyan]🔍 traceweave TUI Dashboard[/bold cyan]")
    console.print("[dim]Listening for traces...[/dim]\n")

    dashboard = TraceDashboard()
    dashboard.start()

    try:
        while True:
            time.sleep(0.25)
    except KeyboardInterrupt:
        dashboard.stop()
        console.print("\n[dim]Dashboard stopped.[/dim]")
