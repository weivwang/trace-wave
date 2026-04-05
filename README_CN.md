<div align="center">
  <picture>
    <img src="docs/assets/banner.svg" width="100%">
  </picture>

  <h3>追踪每一次决策。调试任意 Agent。掌控全部成本。</h3>

  [English](README.md) / **简体中文** / [日本語](README_JA.md) / [한국어](README_KO.md) / [Español](README_ES.md)

  [最佳实践][docs-link] · [报告 Bug][issues-link] · [功能请求][issues-link]

  [![][pypi-shield]][pypi-link]
  [![][python-shield]][python-link]
  [![][license-shield]][license-link]
  [![][downloads-shield]][pypi-link]
  [![][test-shield]][test-link]

</div>

---

## 目录

- [👋🏻 什么是 traceweave？](#-什么是-traceweave)
- [🚀 核心特性](#-核心特性)
- [🆚 为什么选择 traceweave？](#-为什么选择-traceweave)
- [🏁 快速开始](#-快速开始)
- [🔌 框架集成](#-框架集成)
- [📊 可视化面板](#-可视化面板)
- [📁 示例](#-示例)
- [🏗️ 架构](#️-架构)
- [🤝 参与贡献](#-参与贡献)
- [⭐ Star 趋势](#-star-趋势)
- [📄 开源协议](#-开源协议)

---

# 👋🏻 什么是 traceweave？

**traceweave** 是 **AI Agent 领域的 Datadog** — 一个开源的分布式追踪与可观测性平台，专为多 Agent AI 系统构建。

只需 **2 行代码**，即可清晰看到你的 Agent 在做什么：每次 LLM 调用、每次工具调用、每个决策 — 附带 Token 统计、费用追踪和精美可视化。

```
📍 Trace: customer-support-pipeline  id=a3f2c1d8...
├── ✅ 🔗 customer-support-pipeline     ██████████████████████░░ 5.3s   tokens: 3.1k   cost: $0.05
│   ├── ✅ 🔧 email-reader              █░░░░░░░░░░░░░░░░░░░░░  0.2s   tokens: -      cost: -
│   ├── ✅ 🤖 triage-agent              ████░░░░░░░░░░░░░░░░░░  1.2s   tokens: 704    cost: $0.0004
│   │   ├── ✅ 🧠 classify-email        █░░░░░░░░░░░░░░░░░░░░░  0.2s   tokens: 704    cost: $0.0004
│   │   │        (claude-4-haiku)
│   │   ├── ❌ 🔧 sentiment-api         █░░░░░░░░░░░░░░░░░░░░░  0.4s   ⚠ TIMEOUT
│   │   └── ❌ 🔧 sentiment-api         █░░░░░░░░░░░░░░░░░░░░░  0.4s   ⚠ RETRY FAILED
│   ├── ✅ 🤖 research-agent            ███░░░░░░░░░░░░░░░░░░░  1.0s   tokens: 628    cost: $0.004
│   │   ├── ✅ 🔧 vector-search         █░░░░░░░░░░░░░░░░░░░░░  0.3s   (3 docs, top=0.94)
│   │   ├── ✅ 🔧 sql-query             █░░░░░░░░░░░░░░░░░░░░░  0.2s   (customer: enterprise)
│   │   └── ✅ 🧠 analyze-issue         ██░░░░░░░░░░░░░░░░░░░░  0.6s   tokens: 628    cost: $0.004
│   │            (claude-4-sonnet)
│   ├── ✅ 🤖 resolution-agent          ██░░░░░░░░░░░░░░░░░░░░  0.6s
│   │   ├── ✅ 🔧 rate-limit-override   █░░░░░░░░░░░░░░░░░░░░░  0.4s   (limit: 10K→20K)
│   │   ├── ✅ 🔧 ticket-update         █░░░░░░░░░░░░░░░░░░░░░  0.1s
│   │   └── ✅ 🔧 slack-notify          █░░░░░░░░░░░░░░░░░░░░░  0.1s   (#support-escalations)
│   └── ✅ 🤖 response-agent            ████████░░░░░░░░░░░░░░  2.3s   tokens: 1.7k   cost: $0.047
│       ├── ✅ 🧠 draft-response        ███░░░░░░░░░░░░░░░░░░░  0.9s   tokens: 861    cost: $0.04
│       │        (claude-4-opus)
│       ├── ✅ 🧠 review-response       ███░░░░░░░░░░░░░░░░░░░  1.0s   tokens: 868    cost: $0.007
│       │        (claude-4-sonnet)
│       ├── ✅ 🔧 send-email            █░░░░░░░░░░░░░░░░░░░░░  0.2s
│       └── ✅ 🔧 ticket-update         █░░░░░░░░░░░░░░░░░░░░░  0.2s   (status: resolved)
╰── Summary ───────────────────────────────────────────────────────────────
    ⏱  5.3s │ 🔢 19 spans │ 📊 3,061 tokens │ 💰 $0.047 │ ❌ 2 errors (handled)
```

> 💡 此 trace 由 [Showcase Demo](examples/showcase_demo.py) 生成 — 完整的 AI 客户支持流水线，包含 4 个 Agent、10 次工具调用、5 次 LLM 调用、错误处理与重试。**无需 API Key。**

---

# 🚀 核心特性

1. 🎯 **零配置自动插桩** — 一行 `instrument_all()` 自动追踪 OpenAI、Anthropic、LangChain。无需修改调用代码。

2. 🤖 **优雅的装饰器 API** — `@trace_agent`、`@trace_tool`、`@trace_llm` — 一行代码追踪任意函数。支持同步和异步。

3. 💰 **Token 与费用追踪** — 自动统计所有主流模型的 Token 用量和费用。精确定位你的预算花在哪里。

4. 🖥️ **精美可视化** — 绚丽的终端仪表盘（Rich TUI）+ 深色主题 Web 仪表盘。截图级输出效果。

5. ❌ **错误追踪与调试** — 自动捕获异常并记录完整堆栈。精确定位哪个 Agent/工具出了问题。

6. 📤 **多格式导出** — JSON、Chrome DevTools（`chrome://tracing`）等。与你现有的可观测性工具无缝集成。

7. 🔗 **无限层级嵌套** — 基于 `contextvars` 的自动父子关系追踪，无需手动传递上下文。

8. ⚡ **轻量高性能** — 纯 Python，约 3K 行代码，零重型依赖。每个 Span 额外开销 <1ms。

---

# 🆚 为什么选择 traceweave？

### 适用人群

| 目标用户 | 角色 | 痛点 |
|:---------|:-----|:-----|
| **AI Agent 开发者** | 使用 LangChain、CrewAI、AutoGen 或自定义 Agent | 看不到 Agent 在做什么；调试全靠猜 |
| **LLM 应用团队** | 运行包含多次 LLM 调用的生产应用 | Token 费用失控，无法定位 |
| **AI 平台工程师** | 运维大规模多 Agent 基础设施 | AI 领域缺少可观测性标准 — 现有 APM 工具不理解 Agent |

### 与竞品对比

| 能力 | traceweave | LangSmith | Weights & Biases | OpenTelemetry |
|:-----|:----------:|:---------:|:-----------------:|:-------------:|
| 开源 | ✅ MIT | ❌ 私有 | ❌ 私有 | ✅ Apache-2.0 |
| Agent 原生 Span | ✅ `AGENT`, `TOOL`, `LLM` | ✅ | ⚠️ 通用 | ❌ 通用 |
| 零配置插桩 | ✅ `instrument_all()` | ⚠️ 需修改 SDK | ❌ 手动 | ❌ 手动 |
| Token 与费用追踪 | ✅ 内置 | ✅ | ⚠️ 部分 | ❌ 无 |
| 精美 TUI | ✅ Rich 终端 UI | ❌ 仅 Web | ❌ 仅 Web | ❌ 无 UI |
| 自托管/离线 | ✅ 100% 本地 | ❌ 需要云 | ❌ 需要云 | ✅ 自托管 |
| 轻量级 | ✅ ~3K 行纯 Python | ❌ 重量级 SDK | ❌ 重量级 SDK | ⚠️ 复杂配置 |
| 装饰器 API | ✅ `@trace_agent` | ❌ | ❌ | ❌ |

> **🎯 traceweave 的定位：** 你需要 LangSmith 级别的 Agent 可观测性，但要求开源、自托管、无供应商锁定。

---

# 🏁 快速开始

### 1. 安装

```bash
pip install traceweave
```

### 2. 插桩你的代码

```python
from agent_trace import tracer, trace_agent, trace_tool
from agent_trace.dashboard.tui import print_trace

@trace_tool("web-search")
def search(query: str) -> list[str]:
    return ["result 1", "result 2"]

@trace_agent("researcher")
def research(topic: str) -> str:
    results = search(topic)
    return f"Found {len(results)} results about {topic}"

# 追踪一切
with tracer.start_trace("my-task"):
    answer = research("AI agents")

# 可视化 — 精美的终端输出！
print_trace(tracer.get_all_traces()[-1])
```

### 3. 或零改动自动插桩已有代码

```python
from agent_trace.integrations import instrument_all
instrument_all()  # ← 就这一行！所有 OpenAI/Anthropic 调用自动追踪。

# 你的现有代码无需任何改动
client = openai.OpenAI()
response = client.chat.completions.create(model="gpt-4", messages=[...])
# ^ 此调用已自动追踪，包含 Token 统计和费用！
```

### 4. 探索仪表盘

```bash
traceweave tui        # 终端仪表盘（实时更新）
traceweave dashboard  # Web 仪表盘 http://localhost:8420
traceweave demo       # 运行内置演示
```

---

# 🔌 框架集成

一行代码自动插桩主流 AI 框架：

| 框架 | 集成方式 | 安装 |
|:-----|:---------|:-----|
| **OpenAI** | `instrument_openai()` | `pip install traceweave[openai]` |
| **Anthropic** | `instrument_anthropic()` | `pip install traceweave[anthropic]` |
| **LangChain** | `AgentTraceCallbackHandler` | `pip install traceweave[langchain]` |
| **全部** | `instrument_all()` | `pip install traceweave[all]` |

<details>
<summary><b>OpenAI 示例</b></summary>

```python
from agent_trace.integrations.openai_integration import instrument_openai
instrument_openai()

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "你好！"}]
)
# 自动追踪：模型、Token、费用、延迟、输入/输出
```

</details>

<details>
<summary><b>Anthropic 示例</b></summary>

```python
from agent_trace.integrations.anthropic_integration import instrument_anthropic
instrument_anthropic()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "你好！"}]
)
```

</details>

<details>
<summary><b>LangChain 示例</b></summary>

```python
from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

handler = AgentTraceCallbackHandler()
chain = prompt | llm | output_parser
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

</details>

---

# 📊 可视化面板

### 终端仪表盘（TUI）

```bash
traceweave tui
```

基于 Rich 的实时终端仪表盘：
- 🌲 交互式 trace 树，按类型着色
- 📊 Token 用量瀑布图
- 💰 每个 Span 的费用明细
- ❌ 错误高亮 + 堆栈信息

### Web 仪表盘

```bash
traceweave dashboard  # → http://localhost:8420
```

自托管深色主题 Web UI：
- 交互式 trace 树可视化
- Token 用量分析
- 按 Agent/工具 维度的费用明细
- 时间线瀑布图
- 无外部依赖 — 单个嵌入式 HTML

### 导出至 Chrome DevTools

```python
from agent_trace.exporters import export_chrome
export_chrome(trace, "my-trace.chrome.json")
# 打开 chrome://tracing → 加载 → 交互式火焰图！
```

---

# 📁 示例

| 示例 | 说明 | 复杂度 |
|:-----|:-----|:-------|
| **[简单示例](examples/simple_demo.py)** | 10 行代码的最小追踪 | ⭐ |
| **[多 Agent 研究团队](examples/multi_agent_demo.py)** | 4 Agent 协作 + 工具 + LLM 调用 | ⭐⭐ |
| **[Showcase：AI 客户支持流水线](examples/showcase_demo.py)** | 生产级模拟：4 Agent、RAG、错误处理、3 模型 | ⭐⭐⭐ |
| **[DeepSeek Agent（真实 API）](examples/deepseek_agent_demo.py)** | 真实 DeepSeek 驱动的 Agent，实时追踪、TUI 和 Web 仪表盘 | ⭐⭐⭐ |

```bash
# 运行 Showcase 演示（无需 API Key！）
python examples/showcase_demo.py

# 运行真实 DeepSeek Agent 演示（需要 API Key）
python examples/deepseek_agent_demo.py --dashboard
```

---

# 🔑 核心概念

| 概念 | 说明 |
|:-----|:-----|
| **Trace（追踪）** | 一次完整的端到端操作，包含一棵 Span 树。 |
| **Span（跨度）** | 一个工作单元 — Agent 调用、工具调用或 LLM 请求。 |
| **SpanKind（类型）** | Span 分类：`AGENT` 🤖、`TOOL` 🔧、`LLM` 🧠、`CHAIN` 🔗、`RETRIEVER` 📚 |
| **TokenUsage（用量）** | 每个 Span 的 Token 统计 + 基于模型定价的费用估算。 |
| **Decorator API** | `@trace_agent`、`@trace_tool`、`@trace_llm` — 一行装饰器完成插桩。 |

---

# 🏗️ 架构

```
traceweave/
├── agent_trace/
│   ├── core/               # 核心追踪引擎
│   │   ├── models.py       # Pydantic v2 数据模型（Span, Trace, TokenUsage）
│   │   ├── tracer.py       # AgentTracer — 上下文管理与事件系统
│   │   ├── span.py         # Span 上下文管理器 + 流式 API
│   │   ├── context.py      # 线程安全的上下文传播（contextvars）
│   │   └── decorators.py   # @trace_agent, @trace_tool, @trace_llm
│   ├── integrations/       # 零配置框架自动插桩
│   │   ├── openai_integration.py
│   │   ├── anthropic_integration.py
│   │   └── langchain_integration.py
│   ├── dashboard/           # 可视化层
│   │   ├── tui.py           # Rich 终端仪表盘（TUI）
│   │   └── server.py        # Web 仪表盘（自包含 HTML）
│   ├── exporters/           # 导出为 JSON、Chrome Trace 等
│   └── cli.py               # CLI: traceweave tui|dashboard|demo|export
├── examples/                # 演示脚本（无需 API Key）
└── tests/                   # 39 个测试，100% 通过
```

| 技术 | 用途 |
|:-----|:-----|
| **Pydantic v2** | 数据模型 + 校验 + 序列化 |
| **Rich** | 精美终端渲染（TUI 仪表盘） |
| **Click** | CLI 框架 |
| **contextvars** | 线程与异步安全的 trace 传播 |
| **orjson** | 高性能 JSON 序列化（导出） |

---

# 🤝 参与贡献

欢迎贡献！无论是 Bug 报告、功能建议还是 Pull Request，我们都非常感谢。

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/amazing`）
3. 运行测试：`pytest tests/ -v`
4. 提交更改（`git commit -m 'Add amazing feature'`）
5. 推送到远程（`git push origin feature/amazing`）
6. 创建 Pull Request

---

# ⭐ Star 趋势

如果觉得 traceweave 有用，请给我们一个 Star！这有助于更多人发现这个项目。

[![Star History Chart](https://api.star-history.com/svg?repos=weivwang/trace-wave&type=Date)](https://star-history.com/#weivwang/trace-wave&Date)

---

# 📄 开源协议

MIT 协议 — 详见 [LICENSE](LICENSE)。

---

<div align="center">

**用 ❤️ 为 AI Agent 社区构建**

[![][pypi-shield]][pypi-link] [![][license-shield]][license-link]

</div>

<!-- LINKS -->
[pypi-shield]: https://img.shields.io/pypi/v/traceweave?color=369eff&labelColor=black&logo=pypi&logoColor=white&style=flat-square
[pypi-link]: https://pypi.org/project/traceweave/
[python-shield]: https://img.shields.io/badge/python-3.9+-369eff?labelColor=black&logo=python&logoColor=white&style=flat-square
[python-link]: https://www.python.org/downloads/
[license-shield]: https://img.shields.io/badge/license-MIT-369eff?labelColor=black&style=flat-square
[license-link]: https://opensource.org/licenses/MIT
[downloads-shield]: https://img.shields.io/pypi/dm/traceweave?color=369eff&labelColor=black&style=flat-square
[test-shield]: https://img.shields.io/badge/tests-39%20passed-369eff?labelColor=black&logo=pytest&logoColor=white&style=flat-square
[test-link]: https://github.com/weivwang/trace-wave/actions
[docs-link]: https://github.com/weivwang/trace-wave#-quick-start
[issues-link]: https://github.com/weivwang/trace-wave/issues
