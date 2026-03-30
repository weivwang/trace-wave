"""Main export dispatcher."""
import json
from pathlib import Path
from agent_trace.core.models import TraceData


def export_trace(trace_file: str, fmt: str = "json", output: str = None) -> str:
    """Export a trace file to the specified format."""
    with open(trace_file) as f:
        data = json.load(f)

    trace = TraceData.model_validate(data)

    if output is None:
        stem = Path(trace_file).stem
        output = f"{stem}.{fmt}"

    if fmt == "json":
        from agent_trace.exporters.json_exporter import export_json
        return export_json(trace, output)
    elif fmt == "chrome":
        from agent_trace.exporters.chrome_exporter import export_chrome
        return export_chrome(trace, output)
    elif fmt == "otlp":
        # Future: OpenTelemetry export
        raise NotImplementedError("OTLP export coming soon")
    else:
        raise ValueError(f"Unknown format: {fmt}")
