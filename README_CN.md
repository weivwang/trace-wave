<div align="center">

# 🔍 traceweave

### AI Agent 分布式追踪与可观测性平台

**精确掌握你的 AI Agent 在做什么。像专家一样调试多Agent系统。**

[![PyPI version](https://img.shields.io/pypi/v/traceweave.svg)](https://pypi.org/project/traceweave/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/traceweave.svg)](https://pypi.org/project/traceweave/)

[English](README.md) | **简体中文** | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md)

[快速开始](#-快速开始) · [核心特性](#-核心特性) · [框架集成](#-框架集成) · [可视化面板](#-可视化面板) · [示例](#-示例)

</div>

---

> **AI Agent 领域的 Datadog。** 追踪每一次 Agent 决策、工具调用和 LLM 交互，配合精美可视化和零配置自动插桩。

```
📍 Trace: multi-agent-research  id=a3f2c1d8...
├── ✅ 🔗 multi-agent-research           ██████████████████████░░ 12.3s   tokens: 8.2k   cost: $0.15
│   ├── ✅ 🤖 planner                    ████████░░░░░░░░░░░░░░  3.2s    tokens: 2.1k   cost: $0.04
│   │   └── ✅ 🧠 plan-generation        ██████░░░░░░░░░░░░░░░░  2.1s    tokens: 1.8k   cost: $0.03
│   ├── ✅ 🤖 researcher                 ████████████░░░░░░░░░░  5.1s    tokens: 3.4k   cost: $0.06
│   │   ├── ✅ 🔧 web-search             ██░░░░░░░░░░░░░░░░░░░░  0.6s    tokens: -      cost: -
│   │   ├── ✅ 🔧 arxiv-search           █░░░░░░░░░░░░░░░░░░░░░  0.3s    tokens: -      cost: -
│   │   └── ✅ 🧠 analyze-results        ████████░░░░░░░░░░░░░░  3.1s    tokens: 2.8k   cost: $0.05
│   ├── ✅ 🤖 writer                     ██████████░░░░░░░░░░░░  4.8s    tokens: 1.9k   cost: $0.04
│   │   └── ✅ 🧠 write-report           ██████████░░░░░░░░░░░░  4.2s    tokens: 1.9k   cost: $0.04
│   └── ✅ 🤖 reviewer                   ██████░░░░░░░░░░░░░░░░  2.4s    tokens: 0.8k   cost: $0.01
│       └── ✅ 🧠 review-report          ██████░░░░░░░░░░░░░░░░  2.1s    tokens: 0.8k   cost: $0.01
╰── Summary ─────────────────────────────────────────────────────
    ⏱  耗时: 12.3s │ 🔢 Span数: 11 │ 📊 Token: 8.2k │ 💰 费用: $0.15
```

## 为什么选择 traceweave？

如果你正在开发 AI Agent 应用，你一定遇到过这些问题：

- 🤯 **"我的 Agent 为什么这么做？"** — 无法看到 Agent 的推理链路
- 💸 **"我的 Token 都花在哪了？"** — 嵌套调用中无法追踪费用
- 🐛 **"到底是哪一步出错了？"** — 多 Agent 流水线调试是噩梦
- 📊 **"每一步耗时多少？"** — 缺乏 Agent 性能分析工具

**traceweave 只需 2 行代码即可解决以上所有问题。**

## 🚀 快速开始

```bash
pip install traceweave
```

```python
from agent_trace import tracer, trace_agent, trace_tool
from agent_trace.dashboard.tui import print_trace

@trace_tool("calculator")
def add(a: int, b: int) -> int:
    return a + b

@trace_agent("math-agent")
def math_agent(question: str) -> int:
    return add(2, 3)

# 追踪一切
with tracer.start_trace("math-task"):
    answer = math_agent("What is 2 + 3?")

# 可视化展示
print_trace(tracer.get_all_traces()[-1])
```

## ✨ 核心特性

### 🎯 零配置自动插桩

一行代码自动追踪 OpenAI、Anthropic 和 LangChain：

```python
from agent_trace.integrations import instrument_all
instrument_all()  # 搞定！所有 LLM 调用自动追踪。
```

### 🤖 优雅的装饰器

```python
@trace_agent("researcher")    # 追踪 Agent 函数
@trace_tool("web-search")     # 追踪工具调用
@trace_llm(model="gpt-4")     # 追踪 LLM 调用，自动记录 Token
```

### 📊 Token 用量 & 费用追踪

自动统计所有主流模型的 Token 消耗和费用：

```python
with tracer.start_span("my-llm-call", SpanKind.LLM) as span:
    response = call_llm(prompt)
    span.set_token_usage(
        prompt_tokens=1500,
        completion_tokens=500,
        model="claude-3-sonnet",
        prompt_cost_per_1k=0.003,
        completion_cost_per_1k=0.015,
    )
```

### 🖥️ 精美终端面板

```bash
traceweave tui  # 实时更新的终端仪表板
```

### 🌐 Web 可视化面板

```bash
traceweave dashboard  # 在 http://localhost:8420 打开
```

深色主题，实时更新的 Web 面板，支持：
- 交互式追踪树可视化
- Token 用量分析
- 按 Agent/工具 维度的费用明细
- 时间线瀑布图

### 📤 多格式导出

```python
from agent_trace.exporters import export_json, export_chrome

# 保存为 JSON
export_json(trace, "my-trace.json")

# 导出为 Chrome DevTools 格式（在 chrome://tracing 中打开）
export_chrome(trace, "my-trace.chrome.json")
```

## 🔌 框架集成

### OpenAI

```python
from agent_trace.integrations.openai_integration import instrument_openai
instrument_openai()

# 所有 OpenAI 调用自动追踪！
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "你好！"}]
)
```

### Anthropic

```python
from agent_trace.integrations.anthropic_integration import instrument_anthropic
instrument_anthropic()

# 所有 Anthropic 调用自动追踪！
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "你好！"}]
)
```

### LangChain

```python
from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

handler = AgentTraceCallbackHandler()
chain = prompt | llm | output_parser
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

## 📁 示例

| 示例 | 说明 |
|------|------|
| [简单示例](examples/simple_demo.py) | 最小化示例 — 10 行代码完成追踪 |
| [多 Agent 研究团队](examples/multi_agent_demo.py) | 4 Agent 协作，包含工具调用、LLM 和费用追踪 |

运行内置演示：

```bash
traceweave demo
```

## 🏗️ 架构

```
traceweave/
├── agent_trace/
│   ├── core/           # 核心追踪引擎
│   │   ├── models.py   # Pydantic 数据模型（Span, Trace, TokenUsage）
│   │   ├── tracer.py   # 主追踪器，带上下文管理
│   │   ├── span.py     # Span 上下文管理器
│   │   ├── context.py  # 线程安全的上下文传播
│   │   └── decorators.py # @trace_agent, @trace_tool, @trace_llm
│   ├── integrations/   # 框架自动插桩
│   │   ├── openai_integration.py
│   │   ├── anthropic_integration.py
│   │   └── langchain_integration.py
│   ├── dashboard/      # 可视化
│   │   ├── tui.py      # Rich 终端仪表板
│   │   └── server.py   # Web 仪表板（单 HTML 文件，无需构建）
│   ├── exporters/      # 导出格式
│   │   ├── json_exporter.py
│   │   └── chrome_exporter.py
│   └── cli.py          # CLI 命令
└── examples/           # 演示脚本
```

## 🔑 核心概念

| 概念 | 说明 |
|------|------|
| **Trace（追踪）** | 一次完整操作（如"研究任务"），包含 Span 树。 |
| **Span（跨度）** | 一个工作单元（Agent 调用、工具使用、LLM 请求）。 |
| **SpanKind（类型）** | Span 类型：`AGENT`, `TOOL`, `LLM`, `CHAIN`, `RETRIEVER` |
| **TokenUsage（用量）** | 每次 LLM 调用的 Token 统计 + 费用估算 |

## 📦 安装

```bash
# 仅核心功能
pip install traceweave

# 指定框架集成
pip install traceweave[openai]
pip install traceweave[anthropic]
pip install traceweave[langchain]

# 全部安装
pip install traceweave[all]
```

**环境要求：** Python 3.9+

## 🤝 参与贡献

欢迎贡献代码！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到远程 (`git push origin feature/amazing`)
5. 创建 Pull Request

## 📄 开源协议

MIT 协议 — 详见 [LICENSE](LICENSE)。

---

<div align="center">

**用 ❤️ 为 AI Agent 社区构建**

如果觉得 traceweave 有用，请给个 ⭐ 支持一下！

</div>
