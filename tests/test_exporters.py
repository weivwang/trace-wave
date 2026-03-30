"""Tests for exporters."""
import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from agent_trace.core.models import SpanData, SpanKind, SpanStatus, TraceData, TokenUsage
from agent_trace.exporters.json_exporter import export_json, export_json_multi
from agent_trace.exporters.chrome_exporter import export_chrome


@pytest.fixture
def sample_trace():
    now = datetime.now(timezone.utc)
    child = SpanData(
        name="llm-call", kind=SpanKind.LLM,
        model_name="test-model",
        token_usage=TokenUsage(
            prompt_tokens=100, completion_tokens=50, total_tokens=150,
            prompt_cost_per_1k=0.01, completion_cost_per_1k=0.03,
        ),
        start_time=now,
        end_time=now,
        status=SpanStatus.OK,
    )
    root = SpanData(
        name="root", kind=SpanKind.CHAIN,
        start_time=now,
        end_time=now,
        status=SpanStatus.OK,
        children=[child],
    )
    return TraceData(
        trace_id="test-trace-id",
        name="test-trace",
        start_time=root.start_time,
        end_time=root.end_time,
        root_span=root,
    )


class TestJsonExporter:
    def test_export_string(self, sample_trace):
        result = export_json(sample_trace)
        data = json.loads(result)
        assert data["name"] == "test-trace"
        assert data["trace_id"] == "test-trace-id"

    def test_export_file(self, sample_trace, tmp_path):
        path = tmp_path / "trace.json"
        export_json(sample_trace, path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["name"] == "test-trace"

    def test_export_multi(self, sample_trace):
        result = export_json_multi([sample_trace, sample_trace])
        data = json.loads(result)
        assert len(data) == 2


class TestChromeExporter:
    def test_export_string(self, sample_trace):
        result = export_chrome(sample_trace)
        data = json.loads(result)
        assert "traceEvents" in data
        assert len(data["traceEvents"]) >= 2  # root + child

    def test_event_format(self, sample_trace):
        result = export_chrome(sample_trace)
        data = json.loads(result)
        event = data["traceEvents"][0]
        assert "name" in event
        assert "ph" in event
        assert event["ph"] == "X"  # Complete event
        assert "ts" in event
        assert "dur" in event
