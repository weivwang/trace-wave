"""Lightweight web dashboard server for traceweave."""
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional
from agent_trace.core.tracer import tracer as default_tracer


DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔍 traceweave Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --text-dim: #7d8590; --accent: #58a6ff;
    --green: #3fb950; --red: #f85149; --yellow: #d29922;
    --purple: #bc8cff; --cyan: #39d353;
  }
  body { font-family: 'SF Mono', 'Cascadia Code', monospace; background: var(--bg); color: var(--text); padding: 20px; }

  .header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
  .header h1 { font-size: 24px; background: linear-gradient(135deg, var(--accent), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .header .badge { background: var(--surface); border: 1px solid var(--border); padding: 4px 12px; border-radius: 16px; font-size: 12px; color: var(--text-dim); }

  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
  .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
  .stat-card .label { font-size: 12px; color: var(--text-dim); margin-bottom: 4px; }
  .stat-card .value { font-size: 28px; font-weight: bold; }
  .stat-card .value.tokens { color: var(--accent); }
  .stat-card .value.cost { color: var(--green); }
  .stat-card .value.duration { color: var(--yellow); }
  .stat-card .value.spans { color: var(--purple); }

  .trace-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 16px; }
  .trace-title { font-size: 16px; font-weight: bold; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }

  .span-tree { padding-left: 0; }
  .span-node { margin: 4px 0; }
  .span-row { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-radius: 6px; cursor: pointer; transition: background 0.2s; }
  .span-row:hover { background: rgba(255,255,255,0.05); }
  .span-icon { font-size: 16px; width: 24px; text-align: center; }
  .span-name { font-weight: 600; }
  .span-name.agent { color: var(--cyan); }
  .span-name.tool { color: var(--yellow); }
  .span-name.llm { color: var(--purple); }
  .span-name.chain { color: var(--accent); }

  .span-bar-container { flex: 1; display: flex; align-items: center; gap: 8px; min-width: 200px; }
  .span-bar { height: 8px; border-radius: 4px; min-width: 4px; transition: width 0.3s; }
  .span-bar.agent { background: var(--cyan); }
  .span-bar.tool { background: var(--yellow); }
  .span-bar.llm { background: linear-gradient(90deg, var(--purple), var(--accent)); }
  .span-bar.chain { background: var(--accent); }
  .span-bar.error { background: var(--red); }

  .span-meta { font-size: 12px; color: var(--text-dim); white-space: nowrap; }
  .span-children { padding-left: 24px; border-left: 1px solid var(--border); margin-left: 11px; }

  .status-ok { color: var(--green); }
  .status-error { color: var(--red); }
  .status-running { color: var(--yellow); animation: pulse 1s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

  .empty-state { text-align: center; padding: 60px 20px; color: var(--text-dim); }
  .empty-state code { display: block; background: var(--bg); padding: 16px; border-radius: 8px; margin-top: 16px; text-align: left; max-width: 400px; margin-left: auto; margin-right: auto; font-size: 13px; }

  .error-badge { background: rgba(248,81,73,0.1); color: var(--red); padding: 2px 8px; border-radius: 4px; font-size: 11px; }
</style>
</head>
<body>

<div class="header">
  <h1>🔍 traceweave</h1>
  <span class="badge">v0.1.0</span>
  <span class="badge" id="trace-count">0 traces</span>
  <span class="badge status-running" id="status">● Live</span>
</div>

<div class="stats">
  <div class="stat-card"><div class="label">Total Duration</div><div class="value duration" id="total-duration">-</div></div>
  <div class="stat-card"><div class="label">Total Spans</div><div class="value spans" id="total-spans">0</div></div>
  <div class="stat-card"><div class="label">Total Tokens</div><div class="value tokens" id="total-tokens">0</div></div>
  <div class="stat-card"><div class="label">Total Cost</div><div class="value cost" id="total-cost">$0.00</div></div>
</div>

<div id="traces-container">
  <div class="empty-state">
    <p>Waiting for traces...</p>
    <code>from agent_trace import tracer, trace_agent

@trace_agent
def my_agent(query):
    ...</code>
  </div>
</div>

<script>
const KIND_ICONS = {agent:'🤖', tool:'🔧', llm:'🧠', chain:'🔗', retriever:'📚', custom:'⚡'};
const STATUS_ICONS = {running:'🔄', ok:'✅', error:'❌'};

function formatDuration(ms) {
  if (!ms) return '...';
  if (ms < 1000) return ms.toFixed(0) + 'ms';
  if (ms < 60000) return (ms/1000).toFixed(1) + 's';
  return (ms/60000).toFixed(1) + 'm';
}
function formatTokens(t) { return t < 1000 ? t.toString() : (t/1000).toFixed(1) + 'k'; }
function formatCost(c) { return c < 0.01 ? '$' + c.toFixed(4) : '$' + c.toFixed(2); }

function renderSpan(span, maxDuration) {
  const icon = KIND_ICONS[span.kind] || '⚡';
  const status = STATUS_ICONS[span.status] || '❓';
  const duration = span.duration_ms || 0;
  const barWidth = maxDuration > 0 ? Math.max(4, (duration / maxDuration) * 100) : 4;
  const tokens = span.token_usage ? span.token_usage.total_tokens : 0;
  const cost = span.token_usage ? (span.token_usage.prompt_tokens * span.token_usage.prompt_cost_per_1k / 1000 + span.token_usage.completion_tokens * span.token_usage.completion_cost_per_1k / 1000) : 0;
  const barClass = span.status === 'error' ? 'error' : span.kind;
  const errorHtml = span.error ? `<span class="error-badge">${span.error}</span>` : '';
  const modelHtml = span.model_name ? `<span class="span-meta">(${span.model_name})</span>` : '';

  let html = `<div class="span-node">
    <div class="span-row">
      <span class="span-icon">${status}</span>
      <span class="span-icon">${icon}</span>
      <span class="span-name ${span.kind}">${span.name}</span>
      ${modelHtml}
      <div class="span-bar-container">
        <div class="span-bar ${barClass}" style="width:${barWidth}%"></div>
      </div>
      <span class="span-meta">${formatDuration(duration)}</span>
      <span class="span-meta">${tokens > 0 ? formatTokens(tokens) + ' tok' : ''}</span>
      <span class="span-meta">${cost > 0 ? formatCost(cost) : ''}</span>
      ${errorHtml}
    </div>`;

  if (span.children && span.children.length > 0) {
    html += '<div class="span-children">';
    for (const child of span.children) {
      html += renderSpan(child, maxDuration);
    }
    html += '</div>';
  }

  html += '</div>';
  return html;
}

function sumTokens(span) {
  let t = span.token_usage ? span.token_usage.total_tokens : 0;
  for (const c of (span.children || [])) t += sumTokens(c);
  return t;
}

function sumCost(span) {
  let c = span.token_usage ? (span.token_usage.prompt_tokens * span.token_usage.prompt_cost_per_1k / 1000 + span.token_usage.completion_tokens * span.token_usage.completion_cost_per_1k / 1000) : 0;
  for (const ch of (span.children || [])) c += sumCost(ch);
  return c;
}

function countSpans(span) {
  let n = 1;
  for (const c of (span.children || [])) n += countSpans(c);
  return n;
}

function renderTraces(traces) {
  const container = document.getElementById('traces-container');
  if (!traces.length) return;

  let totalDuration = 0, totalSpans = 0, totalTokens = 0, totalCost = 0;
  let html = '';

  for (const trace of traces) {
    const dur = trace.root_span.duration_ms || 0;
    const spans = countSpans(trace.root_span);
    const tokens = sumTokens(trace.root_span);
    const cost = sumCost(trace.root_span);
    totalDuration += dur; totalSpans += spans; totalTokens += tokens; totalCost += cost;

    html += `<div class="trace-panel">
      <div class="trace-title">📍 ${trace.name} <span class="span-meta">id: ${trace.trace_id.substring(0,8)}...</span></div>
      ${renderSpan(trace.root_span, dur)}
    </div>`;
  }

  container.innerHTML = html;
  document.getElementById('trace-count').textContent = traces.length + ' traces';
  document.getElementById('total-duration').textContent = formatDuration(totalDuration);
  document.getElementById('total-spans').textContent = totalSpans;
  document.getElementById('total-tokens').textContent = formatTokens(totalTokens);
  document.getElementById('total-cost').textContent = formatCost(totalCost);
}

// Poll for updates
async function poll() {
  try {
    const res = await fetch('/api/traces');
    const data = await res.json();
    renderTraces(data);
  } catch(e) {}
  setTimeout(poll, 1000);
}
poll();
</script>
</body>
</html>'''


class DashboardHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the traceweave web dashboard."""

    tracer = None

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        elif self.path == '/api/traces':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            traces = self.tracer.get_all_traces() if self.tracer else []
            data = [t.model_dump(mode="json") for t in traces]
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logs


def run_server(host: str = "127.0.0.1", port: int = 8420, tracer=None):
    """Start the web dashboard server."""
    _tracer = tracer or default_tracer
    DashboardHandler.tracer = _tracer

    server = HTTPServer((host, port), DashboardHandler)
    print(f"🔍 traceweave dashboard: http://{host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        print("\nDashboard stopped.")
