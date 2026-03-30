"""View saved trace files in the terminal."""
import json
from rich.console import Console
from agent_trace.core.models import TraceData
from agent_trace.dashboard.tui import print_trace


def view_trace_file(path: str):
    """Load and display a trace from a JSON file."""
    console = Console()

    try:
        with open(path) as f:
            data = json.load(f)

        if isinstance(data, list):
            for trace_data in data:
                trace = TraceData.model_validate(trace_data)
                print_trace(trace)
        else:
            trace = TraceData.model_validate(data)
            print_trace(trace)
    except Exception as e:
        console.print(f"[red]Error loading trace: {e}[/red]")
