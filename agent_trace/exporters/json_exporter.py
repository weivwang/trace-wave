"""Export traces to JSON format."""
import json
import orjson
from pathlib import Path
from typing import Union
from agent_trace.core.models import TraceData


def export_json(trace: TraceData, path: Union[str, Path, None] = None) -> str:
    """Export a trace to JSON format.

    Args:
        trace: The trace to export
        path: Optional file path. If None, returns JSON string.

    Returns:
        JSON string or file path
    """
    data = trace.model_dump(mode="json")
    json_bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2)

    if path:
        path = Path(path)
        path.write_bytes(json_bytes)
        return str(path)

    return json_bytes.decode()


def export_json_multi(traces: list[TraceData], path: Union[str, Path, None] = None) -> str:
    """Export multiple traces to JSON."""
    data = [t.model_dump(mode="json") for t in traces]
    json_bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2)

    if path:
        path = Path(path)
        path.write_bytes(json_bytes)
        return str(path)

    return json_bytes.decode()
