"""Export traces to Chrome Trace Event format for chrome://tracing visualization."""
import json
from pathlib import Path
from typing import Union
from agent_trace.core.models import SpanData, TraceData


def _span_to_chrome_events(span: SpanData, pid: int = 1) -> list[dict]:
    """Convert a span to Chrome Trace Event format."""
    events = []

    start_us = int(span.start_time.timestamp() * 1_000_000)
    duration_us = int(span.duration_ms * 1000) if span.duration_ms else 0

    # Duration event
    events.append({
        "name": span.name,
        "cat": span.kind.value,
        "ph": "X",  # Complete event
        "ts": start_us,
        "dur": duration_us,
        "pid": pid,
        "tid": span.trace_id[:8],
        "args": {
            "kind": span.kind.value,
            "status": span.status.value,
            "span_id": span.span_id,
            **({"model": span.model_name} if span.model_name else {}),
            **({"tokens": span.token_usage.total_tokens} if span.token_usage else {}),
            **({"error": span.error} if span.error else {}),
        }
    })

    # Add events as instant events
    for event in span.events:
        events.append({
            "name": event.name,
            "cat": "event",
            "ph": "i",
            "ts": int(event.timestamp.timestamp() * 1_000_000),
            "pid": pid,
            "tid": span.trace_id[:8],
            "s": "t",
            "args": event.attributes,
        })

    # Recurse into children
    for child in span.children:
        events.extend(_span_to_chrome_events(child, pid))

    return events


def export_chrome(trace: TraceData, path: Union[str, Path, None] = None) -> str:
    """Export trace to Chrome Trace Event format.

    Open the output file at chrome://tracing for interactive visualization.
    """
    events = _span_to_chrome_events(trace.root_span)

    output = json.dumps({"traceEvents": events}, indent=2)

    if path:
        path = Path(path)
        path.write_text(output)
        return str(path)

    return output
