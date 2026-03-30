"""CLI for traceweave: AI Agent Observability.

Provides commands for launching dashboards, viewing traces, exporting
data, and running demos.

Usage::

    traceweave dashboard --port 8420
    traceweave tui
    traceweave view trace.json
    traceweave export trace.json --format chrome -o trace.chrome.json
    traceweave demo
"""
import click
import json
import sys


@click.group()
@click.version_option(version="0.1.0", prog_name="traceweave")
def main():
    """🔍 traceweave: Distributed tracing and observability for AI agents."""
    pass


@main.command()
@click.option("--port", default=8420, help="Port for the dashboard server")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
def dashboard(port: int, host: str):
    """Launch the web dashboard for trace visualization."""
    from agent_trace.dashboard.server import run_server

    click.echo(f"🔍 traceweave dashboard starting at http://{host}:{port}")
    run_server(host=host, port=port)


@main.command()
@click.option("--port", default=8420, help="Port for the TUI dashboard")
def tui(port: int):
    """Launch the terminal UI dashboard."""
    from agent_trace.dashboard.tui import run_tui

    run_tui(port=port)


@main.command()
@click.argument("trace_file", type=click.Path(exists=True))
def view(trace_file: str):
    """View a saved trace file in the terminal."""
    from agent_trace.dashboard.trace_viewer import view_trace_file

    view_trace_file(trace_file)


@main.command()
@click.argument("trace_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "fmt",
    default="json",
    type=click.Choice(["json", "otlp", "chrome"]),
)
@click.option("--output", "-o", default=None, help="Output file path")
def export(trace_file: str, fmt: str, output: str):
    """Export traces to different formats."""
    from agent_trace.exporters.export import export_trace

    result = export_trace(trace_file, fmt, output)
    click.echo(f"✅ Exported to {result}")


@main.command()
def demo():
    """Run a demo to see traceweave in action."""
    from agent_trace.examples.demo_runner import run_demo

    run_demo()


if __name__ == "__main__":
    main()
