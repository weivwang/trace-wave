#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  🔍 traceweave × DeepSeek Agent — Real-World Demo                  ║
║                                                                      ║
║  A real AI agent powered by DeepSeek API, fully instrumented with   ║
║  traceweave for observability. Every LLM call, tool execution,      ║
║  and agent reasoning step is traced and visualized.                  ║
║                                                                      ║
║  Features:                                                           ║
║    ✦ Real DeepSeek API calls (not simulated)                        ║
║    ✦ 4 tools: shell, file_read, file_write, python_exec            ║
║    ✦ Full trace tree with token usage & cost tracking               ║
║    ✦ Beautiful terminal visualization via Rich                      ║
║    ✦ JSON trace export for further analysis                         ║
║                                                                      ║
║  Based on: github.com/weivwang/llm-agent-learn                     ║
║                                                                      ║
║  Run:  python examples/deepseek_agent_demo.py                       ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import subprocess
import sys
import tempfile

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from agent_trace import tracer, trace_tool
from agent_trace.core.models import SpanKind
from agent_trace.dashboard.tui import print_trace
from agent_trace.exporters.json_exporter import export_json

console = Console()

# ═══════════════════════════════════════════════════════════════════
#  ⚙️  Configuration — Fill in your API key here
# ═══════════════════════════════════════════════════════════════════

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your token")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"
MAX_TURN = 20

# DeepSeek pricing (per 1K tokens, USD)
# https://api-docs.deepseek.com/quick_start/pricing
PROMPT_COST_PER_1K = 0.00014     # ¥0.001/千tokens ≈ $0.00014
COMPLETION_COST_PER_1K = 0.00028  # ¥0.002/千tokens ≈ $0.00028


# ═══════════════════════════════════════════════════════════════════
#  🔧 Tools — Traced with @trace_tool
# ═══════════════════════════════════════════════════════════════════

@trace_tool("shell-exec")
def shell_exec(command: str) -> str:
    """Execute a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout
        if result.stderr:
            output += f"\nStderr: {result.stderr}"
        if result.returncode != 0:
            output += f"\nReturn code: {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error: {e}"


@trace_tool("file-read")
def file_read(file_path: str) -> str:
    """Read the contents of a file at the given path."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


@trace_tool("file-write")
def file_write(file_path: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return "File written successfully"
    except Exception as e:
        return f"Error: {e}"


@trace_tool("python-exec")
def python_exec(code: str) -> str:
    """Execute Python code in a subprocess and return its output."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True, text=True, timeout=30,
            )
            output = result.stdout
            if result.stderr:
                output += f"\nStderr: {result.stderr}"
            if result.returncode != 0:
                output += f"\nReturn code: {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out after 30 seconds"
    except Exception as e:
        return f"Error: {e}"
    finally:
        try:
            os.unlink(f.name)
        except OSError:
            pass


# ═══════════════════════════════════════════════════════════════════
#  📋 Tool Schemas (OpenAI function-calling format)
# ═══════════════════════════════════════════════════════════════════

TOOLS = {
    "shell_exec": {
        "function": shell_exec,
        "schema": {
            "type": "function",
            "function": {
                "name": "shell_exec",
                "description": "Execute a shell command and return its output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute.",
                        }
                    },
                    "required": ["command"],
                },
            },
        },
    },
    "file_read": {
        "function": file_read,
        "schema": {
            "type": "function",
            "function": {
                "name": "file_read",
                "description": "Read the contents of a file at the given path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute or relative file path.",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        },
    },
    "file_write": {
        "function": file_write,
        "schema": {
            "type": "function",
            "function": {
                "name": "file_write",
                "description": "Write content to a file (creates parent directories if needed).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute or relative file path.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write.",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            },
        },
    },
    "python_exec": {
        "function": python_exec,
        "schema": {
            "type": "function",
            "function": {
                "name": "python_exec",
                "description": "Execute Python code in a subprocess and return its output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python source code to execute.",
                        }
                    },
                    "required": ["code"],
                },
            },
        },
    },
}

SYSTEM_PROMPT = """You are a helpful AI assistant with access to the following tools:
1. shell_exec — run shell commands
2. file_read — read file contents
3. file_write — write content to a file
4. python_exec — execute Python code
Think step by step. Use tools when you need to interact with the file system, \
run commands, or execute code. When the task is complete, respond directly \
without calling any tool."""


# ═══════════════════════════════════════════════════════════════════
#  🤖 Agent Loop — Fully traced with traceweave
# ═══════════════════════════════════════════════════════════════════

def agent_loop(user_message: str, messages: list, client: OpenAI) -> str:
    """
    Agent loop with full traceweave instrumentation.

    Trace structure:
      agent-loop (AGENT)
        ├── llm-call-turn-1 (LLM)  ← DeepSeek API call
        ├── shell-exec (TOOL)       ← if agent calls tools
        ├── llm-call-turn-2 (LLM)  ← follow-up reasoning
        └── ...
    """
    messages.append({"role": "user", "content": user_message})
    tool_schemas = [t["schema"] for t in TOOLS.values()]

    with tracer.start_span("agent-loop", SpanKind.AGENT) as agent_span:
        agent_span.set_input({"user_message": user_message})

        for turn in range(1, MAX_TURN + 1):
            # ── LLM Call (traced) ──────────────────────────────
            with tracer.start_span(f"llm-call-turn-{turn}", SpanKind.LLM) as llm_span:
                llm_span._data.model_name = MODEL
                llm_span.set_input({
                    "messages_count": len(messages),
                    "last_message_role": messages[-1]["role"] if messages else None,
                })

                try:
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=messages,
                        tools=tool_schemas,
                    )
                except Exception as e:
                    llm_span.set_error(e)
                    agent_span.set_error(e)
                    return f"[error] LLM call failed: {e}"

                choice = response.choices[0]
                assistant_message = choice.message

                # Record token usage
                if response.usage:
                    llm_span.set_token_usage(
                        prompt_tokens=response.usage.prompt_tokens or 0,
                        completion_tokens=response.usage.completion_tokens or 0,
                        model=MODEL,
                        prompt_cost_per_1k=PROMPT_COST_PER_1K,
                        completion_cost_per_1k=COMPLETION_COST_PER_1K,
                    )

                # Record output
                tool_calls_info = None
                if assistant_message.tool_calls:
                    tool_calls_info = [
                        {"name": tc.function.name, "args": tc.function.arguments[:200]}
                        for tc in assistant_message.tool_calls
                    ]
                llm_span.set_output({
                    "content": (assistant_message.content or "")[:300],
                    "tool_calls": tool_calls_info,
                    "finish_reason": choice.finish_reason,
                })

            # Append assistant message to history
            messages.append(assistant_message.model_dump())

            # ── No tool calls → return final answer ────────────
            if not assistant_message.tool_calls:
                reply = assistant_message.content or ""
                agent_span.set_output({"reply": reply[:500], "turns": turn})
                return reply

            # ── Execute tool calls (each auto-traced by @trace_tool) ──
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)

                console.print(
                    f"    [dim]Turn {turn}:[/dim] [yellow]🔧 {tool_name}[/yellow]"
                    f" [dim]{json.dumps(tool_input, ensure_ascii=False)[:80]}[/dim]"
                )

                tool = TOOLS.get(tool_name)
                if tool is None:
                    tool_output = f"Error: unknown tool '{tool_name}'"
                else:
                    tool_output = tool["function"](**tool_input)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output if isinstance(tool_output, str) else str(tool_output),
                })

        agent_span.set_output({"reply": "[max turns reached]", "turns": MAX_TURN})
        return "[agent] reached max turns"


# ═══════════════════════════════════════════════════════════════════
#  🖨️  Pretty print helpers
# ═══════════════════════════════════════════════════════════════════

def print_header():
    header = Text()
    header.append("🔍 traceweave", style="bold cyan")
    header.append(" × ", style="bold white")
    header.append("DeepSeek Agent", style="bold green")
    header.append(" — Real-World Demo\n\n", style="bold white")
    header.append(
        "A real AI agent with full observability.\n"
        "Every LLM call, tool execution, and reasoning step is traced.\n\n",
        style="dim",
    )
    header.append("  🧠 ", style="magenta")
    header.append("LLM calls → DeepSeek API (real, not simulated)\n", style="white")
    header.append("  🔧 ", style="yellow")
    header.append("4 tools: shell, file_read, file_write, python_exec\n", style="white")
    header.append("  📊 ", style="cyan")
    header.append("Token usage & cost tracking from API response\n", style="white")
    header.append("  🌳 ", style="green")
    header.append("Hierarchical trace tree visualization\n", style="white")

    console.print(Panel(header, border_style="cyan", box=box.DOUBLE))
    console.print()


def print_summary(trace_data):
    """Print a summary panel after trace visualization."""
    from agent_trace.core.models import SpanKind

    def count_by_kind(span, kind):
        count = 1 if span.kind == kind else 0
        for child in span.children:
            count += count_by_kind(child, kind)
        return count

    llm_count = count_by_kind(trace_data.root_span, SpanKind.LLM)
    tool_count = count_by_kind(trace_data.root_span, SpanKind.TOOL)
    agent_count = count_by_kind(trace_data.root_span, SpanKind.AGENT)

    summary = Panel(
        f"[bold]Task completed in {(trace_data.total_duration_ms or 0)/1000:.1f}s[/bold]\n\n"
        f"  🤖 Agent spans:  {agent_count}\n"
        f"  🧠 LLM calls:    {llm_count} (model: {MODEL})\n"
        f"  🔧 Tool calls:   {tool_count}\n"
        f"  📊 Total tokens: {trace_data.total_tokens:,}\n"
        f"  💰 Est. cost:    ${trace_data.total_cost:.6f}\n",
        title="[bold cyan]📊 Trace Summary[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
    )
    console.print(summary)


# ═══════════════════════════════════════════════════════════════════
#  🚀 Main — Demo + Interactive mode
# ═══════════════════════════════════════════════════════════════════

DEMO_TASK = (
    "请用 Python 写一个程序，计算斐波那契数列的前 15 项并打印出来，"
    "然后运行这个程序，把结果告诉我。"
)


# ═══════════════════════════════════════════════════════════════════
#  📊 Dashboard helpers — run TUI / Web dashboard in-process
# ═══════════════════════════════════════════════════════════════════

_dashboard_thread = None
_tui_dashboard = None


def start_web_dashboard(port: int = 8420):
    """Start the web dashboard in a background thread (same-process, shares tracer)."""
    import threading
    from agent_trace.dashboard.server import run_server

    global _dashboard_thread
    _dashboard_thread = threading.Thread(
        target=run_server,
        kwargs={"host": "127.0.0.1", "port": port, "tracer": tracer},
        daemon=True,
    )
    _dashboard_thread.start()
    console.print(
        f"  [bold green]🌐 Web dashboard started:[/bold green] "
        f"[link=http://127.0.0.1:{port}]http://127.0.0.1:{port}[/link]\n"
        f"  [dim]Open this URL in your browser to see traces update in real-time.[/dim]\n"
    )


def start_tui_dashboard():
    """Start the Rich TUI live dashboard (same-process, shares tracer).

    The TUI updates in real-time as spans are created and completed.
    """
    from agent_trace.dashboard.tui import TraceDashboard

    global _tui_dashboard
    _tui_dashboard = TraceDashboard(tracer=tracer)
    _tui_dashboard.start()
    console.print("  [bold green]📺 TUI live dashboard started[/bold green] (updates in real-time)\n")


def stop_tui_dashboard():
    global _tui_dashboard
    if _tui_dashboard:
        _tui_dashboard.stop()
        _tui_dashboard = None


def run_single_task(task: str, messages: list, client: OpenAI, task_label: str = "task",
                    live_mode: bool = False):
    """Run a single agent task with full tracing and visualization."""
    console.print(f"\n  [bold cyan]📝 Task:[/bold cyan] {task}\n")

    with tracer.start_trace(f"deepseek-agent-{task_label}", metadata={"task": task}) as root:
        root.set_attribute("model", MODEL)
        root.set_attribute("task", task[:200])
        reply = agent_loop(task, messages, client)

    console.print(f"\n  [bold green]💬 Agent:[/bold green] {reply}\n")

    # In live_mode (TUI/dashboard), the dashboards update automatically.
    # In normal mode, print a static trace tree.
    if not live_mode:
        traces = tracer.get_all_traces()
        if traces:
            print_trace(traces[-1])
            print_summary(traces[-1])

    # Always export
    traces = tracer.get_all_traces()
    if traces:
        output_path = export_json(traces[-1], f"deepseek_agent_trace_{task_label}.json")
        console.print(f"  [dim]Trace exported to: {output_path}[/dim]\n")


def parse_args():
    """Parse command-line arguments."""
    import argparse
    parser = argparse.ArgumentParser(
        description="traceweave × DeepSeek Agent Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Visualization modes:
  (default)     Print static trace tree after each task
  --tui         Launch Rich TUI live dashboard (real-time updates)
  --dashboard   Launch web dashboard at http://127.0.0.1:8420

Examples:
  python examples/deepseek_agent_demo.py
  python examples/deepseek_agent_demo.py --tui
  python examples/deepseek_agent_demo.py --dashboard
  python examples/deepseek_agent_demo.py --dashboard --port 9000
  python examples/deepseek_agent_demo.py --skip-demo
        """,
    )
    parser.add_argument("--tui", action="store_true",
                        help="Enable Rich TUI live dashboard (real-time trace updates)")
    parser.add_argument("--dashboard", action="store_true",
                        help="Enable web dashboard (opens at http://127.0.0.1:PORT)")
    parser.add_argument("--port", type=int, default=8420,
                        help="Port for web dashboard (default: 8420)")
    parser.add_argument("--skip-demo", action="store_true",
                        help="Skip the preset demo task, go straight to interactive mode")
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate API key
    if API_KEY == "your-api-key-here":
        console.print(
            "[red bold]Error:[/red bold] Please set your DeepSeek API key.\n"
            "  Option 1: Edit API_KEY at the top of this file\n"
            "  Option 2: Set environment variable DEEPSEEK_API_KEY\n"
        )
        sys.exit(1)

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    messages: list = [{"role": "system", "content": SYSTEM_PROMPT}]

    print_header()

    live_mode = args.tui or args.dashboard

    # ── Start dashboards if requested ──────────────────────────
    if args.dashboard:
        start_web_dashboard(port=args.port)

    if args.tui:
        start_tui_dashboard()

    # ── Phase 1: Preset demo task ──────────────────────────────
    if not args.skip_demo:
        console.print(
            Panel(
                "[bold]Phase 1:[/bold] Running preset demo task...\n"
                "[dim]This demonstrates traceweave's full observability on a real Agent.[/dim]",
                border_style="green",
                box=box.ROUNDED,
            )
        )
        run_single_task(DEMO_TASK, messages, client, task_label="demo", live_mode=live_mode)

    # ── Phase 2: Interactive mode ──────────────────────────────
    # Stop TUI before interactive input (TUI Live conflicts with input())
    if args.tui:
        stop_tui_dashboard()
        console.print("  [dim](TUI paused for interactive input)[/dim]\n")

    console.print(
        Panel(
            "[bold]Phase 2:[/bold] Interactive mode\n"
            "[dim]Type your tasks below. Each response will be traced and visualized.\n"
            "Type 'exit' to quit, 'clear' to reset conversation.[/dim]",
            border_style="yellow",
            box=box.ROUNDED,
        )
    )

    task_idx = 0
    while True:
        try:
            user_input = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Bye![/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            console.print("[dim]Bye![/dim]")
            break
        if user_input.lower() == "clear":
            messages.clear()
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
            tracer.clear()
            console.print("[dim](context & traces cleared)[/dim]")
            continue

        task_idx += 1

        # Restart TUI for each task if in TUI mode
        if args.tui:
            start_tui_dashboard()

        run_single_task(user_input, messages, client, task_label=f"interactive-{task_idx}",
                        live_mode=live_mode)

        if args.tui:
            import time
            time.sleep(1)  # Let TUI render final state
            stop_tui_dashboard()

    # Final summary
    all_traces = tracer.get_all_traces()
    if len(all_traces) > 1:
        console.print(f"\n[dim]Session total: {len(all_traces)} traces recorded.[/dim]")

    if args.dashboard:
        console.print(
            f"\n  [bold]🌐 Web dashboard still running at "
            f"http://127.0.0.1:{args.port}[/bold]\n"
            f"  [dim]Press Ctrl+C to stop.[/dim]"
        )
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[dim]Dashboard stopped. Bye![/dim]")


if __name__ == "__main__":
    main()
