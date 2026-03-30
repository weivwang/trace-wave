<div align="center">

# 🔍 traceweave

### AI エージェントのための分散トレーシング＆オブザーバビリティ

**AI エージェントの動作を正確に把握。マルチエージェントシステムをプロのようにデバッグ。**

[![PyPI version](https://img.shields.io/pypi/v/traceweave.svg)](https://pypi.org/project/traceweave/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/traceweave.svg)](https://pypi.org/project/traceweave/)

[English](README.md) | [简体中文](README_CN.md) | **日本語** | [한국어](README_KO.md) | [Español](README_ES.md)

[クイックスタート](#-クイックスタート) · [機能](#-機能) · [インテグレーション](#-インテグレーション) · [ダッシュボード](#-ダッシュボード) · [サンプル](#-サンプル)

</div>

---

> **AI エージェント版の Datadog。** エージェントの判断、ツール呼び出し、LLM とのやり取りを、美しいビジュアライゼーションとゼロコンフィグのインストルメンテーションで追跡します。

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
    ⏱  所要時間: 12.3s │ 🔢 スパン数: 11 │ 📊 トークン: 8.2k │ 💰 コスト: $0.15
```

## なぜ traceweave？

AI エージェント開発で、こんな経験はありませんか？

- 🤯 **「なぜエージェントがそう判断したの？」** — 推論チェーンが見えない
- 💸 **「トークンはどこに消えた？」** — ネストされた呼び出しのコスト追跡ができない
- 🐛 **「どのステップで失敗した？」** — マルチエージェントパイプラインのデバッグは悪夢
- 📊 **「各ステップの所要時間は？」** — エージェントのパフォーマンスプロファイリングがない

**traceweave はたった2行のコードで、これらすべてを解決します。**

## 🚀 クイックスタート

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

# すべてをトレース
with tracer.start_trace("math-task"):
    answer = math_agent("What is 2 + 3?")

# 可視化
print_trace(tracer.get_all_traces()[-1])
```

## ✨ 機能

### 🎯 ゼロコンフィグ自動インストルメンテーション

1行で OpenAI、Anthropic、LangChain を自動トレース：

```python
from agent_trace.integrations import instrument_all
instrument_all()  # これだけ！すべてのLLM呼び出しが自動的にトレースされます。
```

### 🤖 エレガントなデコレータ

```python
@trace_agent("researcher")    # エージェント関数をトレース
@trace_tool("web-search")     # ツール呼び出しをトレース
@trace_llm(model="gpt-4")     # LLM呼び出しをトークン追跡付きでトレース
```

### 📊 トークン & コスト追跡

主要モデルのトークン使用量とコストを自動計算：

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

### 🖥️ 美しいターミナルダッシュボード

```bash
traceweave tui  # リアルタイム更新のターミナルダッシュボード
```

### 🌐 Web ダッシュボード

```bash
traceweave dashboard  # http://localhost:8420 で起動
```

ダークテーマのリアルタイム Web ダッシュボード：
- インタラクティブなトレースツリー可視化
- トークン使用量分析
- エージェント/ツール別コスト内訳
- タイムラインウォーターフォールビュー

### 📤 多形式エクスポート

```python
from agent_trace.exporters import export_json, export_chrome

# JSON として保存
export_json(trace, "my-trace.json")

# Chrome DevTools 形式でエクスポート（chrome://tracing で開けます）
export_chrome(trace, "my-trace.chrome.json")
```

## 🔌 インテグレーション

### OpenAI

```python
from agent_trace.integrations.openai_integration import instrument_openai
instrument_openai()

# すべての OpenAI 呼び出しが自動的にトレースされます！
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "こんにちは！"}]
)
```

### Anthropic

```python
from agent_trace.integrations.anthropic_integration import instrument_anthropic
instrument_anthropic()

# すべての Anthropic 呼び出しが自動的にトレースされます！
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "こんにちは！"}]
)
```

### LangChain

```python
from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

handler = AgentTraceCallbackHandler()
chain = prompt | llm | output_parser
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

## 📁 サンプル

| サンプル | 説明 |
|---------|------|
| [シンプルデモ](examples/simple_demo.py) | 最小限のサンプル — 10行でトレース |
| [マルチエージェントリサーチ](examples/multi_agent_demo.py) | 4エージェントチーム、ツール呼び出し、LLM、コスト追跡付き |

ビルトインデモを実行：

```bash
traceweave demo
```

## 🏗️ アーキテクチャ

```
traceweave/
├── agent_trace/
│   ├── core/           # コアトレーシングエンジン
│   │   ├── models.py   # Pydantic データモデル（Span, Trace, TokenUsage）
│   │   ├── tracer.py   # メイントレーサー（コンテキスト管理付き）
│   │   ├── span.py     # Span コンテキストマネージャー
│   │   ├── context.py  # スレッドセーフなコンテキスト伝播
│   │   └── decorators.py # @trace_agent, @trace_tool, @trace_llm
│   ├── integrations/   # フレームワーク自動インストルメンテーション
│   │   ├── openai_integration.py
│   │   ├── anthropic_integration.py
│   │   └── langchain_integration.py
│   ├── dashboard/      # 可視化
│   │   ├── tui.py      # Rich ターミナルダッシュボード
│   │   └── server.py   # Web ダッシュボード（単一HTML、ビルド不要）
│   ├── exporters/      # エクスポート形式
│   │   ├── json_exporter.py
│   │   └── chrome_exporter.py
│   └── cli.py          # CLI コマンド
└── examples/           # デモスクリプト
```

## 🔑 主要コンセプト

| コンセプト | 説明 |
|-----------|------|
| **Trace（トレース）** | 完全な操作単位（例：「リサーチタスク」）。Span のツリーを含む。 |
| **Span（スパン）** | 個々の作業単位（エージェント呼び出し、ツール使用、LLMリクエスト）。 |
| **SpanKind（種類）** | Span の種類：`AGENT`, `TOOL`, `LLM`, `CHAIN`, `RETRIEVER` |
| **TokenUsage（使用量）** | LLM呼び出しごとのトークン数 + コスト見積もり |

## 📦 インストール

```bash
# コアのみ
pip install traceweave

# 特定のインテグレーション付き
pip install traceweave[openai]
pip install traceweave[anthropic]
pip install traceweave[langchain]

# すべて
pip install traceweave[all]
```

**動作環境：** Python 3.9+

## 🤝 コントリビュート

コントリビューション大歓迎です！お気軽に Pull Request を送ってください。

1. リポジトリを Fork
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing`)
5. Pull Request を作成

## 📄 ライセンス

MIT ライセンス — 詳細は [LICENSE](LICENSE) をご覧ください。

---

<div align="center">

**AI エージェントコミュニティのために ❤️ を込めて開発**

traceweave が役に立ったら、ぜひ ⭐ をお願いします！

</div>
