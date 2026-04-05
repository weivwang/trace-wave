<div align="center">
  <picture>
    <img src="docs/assets/banner.svg" width="100%">
  </picture>

  <h3>すべての判断を追跡。あらゆるエージェントをデバッグ。全コストを管理。</h3>

  [English](README.md) / [简体中文](README_CN.md) / **日本語** / [한국어](README_KO.md) / [Español](README_ES.md)

  [ベストプラクティス][docs-link] · [バグ報告][issues-link] · [機能リクエスト][issues-link]

  [![][pypi-shield]][pypi-link]
  [![][python-shield]][python-link]
  [![][license-shield]][license-link]
  [![][downloads-shield]][pypi-link]
  [![][test-shield]][test-link]

</div>

---

## 目次

- [👋🏻 traceweave とは？](#-traceweave-とは)
- [🚀 主な機能](#-主な機能)
- [🆚 なぜ traceweave？](#-なぜ-traceweave)
- [🏁 クイックスタート](#-クイックスタート)
- [🔌 インテグレーション](#-インテグレーション)
- [📊 ダッシュボード](#-ダッシュボード)
- [📁 サンプル](#-サンプル)
- [🏗️ アーキテクチャ](#️-アーキテクチャ)
- [🤝 コントリビュート](#-コントリビュート)
- [⭐ Star 履歴](#-star-履歴)
- [📄 ライセンス](#-ライセンス)

---

# 👋🏻 traceweave とは？

**traceweave** は **AI エージェント版の Datadog** — マルチエージェント AI システム専用のオープンソース分散トレーシング＆オブザーバビリティプラットフォームです。

**たった2行のコード** で、エージェントの動作を完全に可視化：すべての LLM 呼び出し、ツール実行、判断 — トークン数、コスト追跡、美しいビジュアライゼーション付き。

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

> 💡 このトレースは [Showcase Demo](examples/showcase_demo.py) で生成 — 4つのエージェント、10回のツール呼び出し、5回のLLM呼び出し、エラーハンドリング＆リトライを含む完全なAIカスタマーサポートパイプライン。**APIキー不要。**

---

# 🚀 主な機能

1. 🎯 **ゼロコンフィグ自動インストルメンテーション** — `instrument_all()` 一行で OpenAI、Anthropic、LangChain を自動トレース。コード変更不要。

2. 🤖 **エレガントなデコレータ API** — `@trace_agent`、`@trace_tool`、`@trace_llm` — 1行であらゆる関数をトレース。sync & async 対応。

3. 💰 **トークン＆コスト追跡** — 主要モデルのトークン数とコストを自動計算。予算の使い道を正確に把握。

4. 🖥️ **美しいビジュアライゼーション** — Rich ターミナルダッシュボード（TUI）+ ダークテーマ Web ダッシュボード。スクリーンショット映えする出力。

5. ❌ **エラートレーシング＆デバッグ** — 完全なスタックトレース付きで例外をキャプチャ。どのエージェント/ツールが失敗したか一目瞭然。

6. 📤 **多形式エクスポート** — JSON、Chrome DevTools（`chrome://tracing`）など。既存の可観測性スタックと統合。

7. 🔗 **無制限ネスティング** — `contextvars` による自動親子追跡。手動コンテキスト渡し不要。

8. ⚡ **軽量＆高速** — 純 Python、約3K行、重い依存なし。スパンあたりのオーバーヘッド <1ms。

---

# 🆚 なぜ traceweave？

### 対象ユーザー

| ターゲット | 役割 | 課題 |
|:----------|:-----|:-----|
| **AI エージェント開発者** | LangChain、CrewAI、AutoGen、カスタムエージェント | エージェントの動作が見えない；デバッグは推測 |
| **LLM アプリケーションチーム** | 複数 LLM 呼び出しを含む本番 AI アプリ | トークンコストが制御不能に |
| **AI プラットフォームエンジニア** | 大規模マルチエージェント基盤の運用 | AI 向け可観測性標準がない — 既存 APM はエージェントを理解しない |

### 競合比較

| 機能 | traceweave | LangSmith | Weights & Biases | OpenTelemetry |
|:-----|:----------:|:---------:|:-----------------:|:-------------:|
| オープンソース | ✅ MIT | ❌ プロプライエタリ | ❌ プロプライエタリ | ✅ Apache-2.0 |
| エージェントネイティブスパン | ✅ `AGENT`, `TOOL`, `LLM` | ✅ | ⚠️ 汎用 | ❌ 汎用 |
| ゼロコンフィグ | ✅ `instrument_all()` | ⚠️ SDK変更必要 | ❌ 手動 | ❌ 手動 |
| トークン＆コスト追跡 | ✅ 内蔵 | ✅ | ⚠️ 部分的 | ❌ なし |
| 美しい TUI | ✅ Rich ターミナル UI | ❌ Web のみ | ❌ Web のみ | ❌ UI なし |
| セルフホスト/オフライン | ✅ 100% ローカル | ❌ クラウド必須 | ❌ クラウド必須 | ✅ セルフホスト |
| 軽量 | ✅ ~3K行、純 Python | ❌ 重い SDK | ❌ 重い SDK | ⚠️ 複雑な設定 |
| デコレータ API | ✅ `@trace_agent` | ❌ | ❌ | ❌ |

> **🎯 traceweave の強み：** LangSmith レベルのエージェント可観測性が欲しいが、オープンソースでセルフホストでベンダーロックインなし。

---

# 🏁 クイックスタート

### 1. インストール

```bash
pip install traceweave
```

### 2. コードをインストルメント

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

# すべてをトレース
with tracer.start_trace("my-task"):
    answer = research("AI agents")

# 可視化 — 美しいターミナル出力！
print_trace(tracer.get_all_traces()[-1])
```

### 3. または既存コードをゼロ変更で自動インストルメント

```python
from agent_trace.integrations import instrument_all
instrument_all()  # ← これだけ！すべての OpenAI/Anthropic 呼び出しを自動トレース。

# 既存コードはそのまま動作
client = openai.OpenAI()
response = client.chat.completions.create(model="gpt-4", messages=[...])
# ^ この呼び出しはトークン数＆コスト付きで自動トレース！
```

### 4. ダッシュボードを探索

```bash
traceweave tui        # ターミナルダッシュボード（リアルタイム更新）
traceweave dashboard  # Web ダッシュボード http://localhost:8420
traceweave demo       # ビルトインデモ実行
```

---

# 🔌 インテグレーション

1行で主要 AI フレームワークを自動インストルメント：

| フレームワーク | 統合方法 | インストール |
|:-------------|:---------|:-----------|
| **OpenAI** | `instrument_openai()` | `pip install traceweave[openai]` |
| **Anthropic** | `instrument_anthropic()` | `pip install traceweave[anthropic]` |
| **LangChain** | `AgentTraceCallbackHandler` | `pip install traceweave[langchain]` |
| **すべて** | `instrument_all()` | `pip install traceweave[all]` |

<details>
<summary><b>OpenAI の例</b></summary>

```python
from agent_trace.integrations.openai_integration import instrument_openai
instrument_openai()

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "こんにちは！"}]
)
# 自動トレース：モデル、トークン、コスト、レイテンシ、入出力
```

</details>

<details>
<summary><b>Anthropic の例</b></summary>

```python
from agent_trace.integrations.anthropic_integration import instrument_anthropic
instrument_anthropic()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "こんにちは！"}]
)
```

</details>

<details>
<summary><b>LangChain の例</b></summary>

```python
from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

handler = AgentTraceCallbackHandler()
chain = prompt | llm | output_parser
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

</details>

---

# 📊 ダッシュボード

### ターミナルダッシュボード（TUI）

```bash
traceweave tui
```

Rich ベースのリアルタイムターミナルダッシュボード：
- 🌲 色分けされたインタラクティブトレースツリー
- 📊 トークン使用量ウォーターフォールバー
- 💰 スパンごとのコスト内訳
- ❌ スタックトレース付きエラーハイライト

### Web ダッシュボード

```bash
traceweave dashboard  # → http://localhost:8420
```

セルフホスト型ダークテーマ Web UI：
- インタラクティブなトレースツリー可視化
- トークン使用量分析
- エージェント/ツール別コスト内訳
- タイムラインウォーターフォールビュー
- 外部依存なし — 単一の埋め込み HTML

### Chrome DevTools へエクスポート

```python
from agent_trace.exporters import export_chrome
export_chrome(trace, "my-trace.chrome.json")
# chrome://tracing を開く → 読み込み → インタラクティブフレームグラフ！
```

---

# 📁 サンプル

| サンプル | 説明 | 複雑度 |
|:--------|:-----|:-------|
| **[シンプルデモ](examples/simple_demo.py)** | 10行の最小トレース | ⭐ |
| **[マルチエージェントリサーチ](examples/multi_agent_demo.py)** | 4エージェントチーム + ツール + LLM呼び出し | ⭐⭐ |
| **[Showcase: AIサポートパイプライン](examples/showcase_demo.py)** | 本番シミュレーション：4エージェント、RAG、エラー処理、3モデル | ⭐⭐⭐ |
| **[DeepSeek Agent（実API）](examples/deepseek_agent_demo.py)** | 実際の DeepSeek 駆動エージェント、ライブトレーシング、TUI & Web ダッシュボード | ⭐⭐⭐ |

```bash
# Showcase デモを実行（APIキー不要！）
python examples/showcase_demo.py

# 実際の DeepSeek Agent デモを実行（APIキー必要）
python examples/deepseek_agent_demo.py --dashboard
```

---

# 🔑 主要コンセプト

| コンセプト | 説明 |
|:----------|:-----|
| **Trace** | 完全なエンドツーエンド操作。スパンのツリーを含む。 |
| **Span** | 個々の作業単位 — エージェント呼び出し、ツール実行、LLMリクエスト。 |
| **SpanKind** | スパン分類：`AGENT` 🤖、`TOOL` 🔧、`LLM` 🧠、`CHAIN` 🔗、`RETRIEVER` 📚 |
| **TokenUsage** | スパンごとのトークン数 + モデル価格に基づくコスト推定。 |
| **Decorator API** | `@trace_agent`、`@trace_tool`、`@trace_llm` — 1行デコレータ。 |

---

# 🏗️ アーキテクチャ

```
traceweave/
├── agent_trace/
│   ├── core/               # コアトレーシングエンジン
│   │   ├── models.py       # Pydantic v2 データモデル（Span, Trace, TokenUsage）
│   │   ├── tracer.py       # AgentTracer — コンテキスト管理＆イベントシステム
│   │   ├── span.py         # Span コンテキストマネージャー + Fluent API
│   │   ├── context.py      # スレッドセーフなコンテキスト伝播（contextvars）
│   │   └── decorators.py   # @trace_agent, @trace_tool, @trace_llm
│   ├── integrations/       # ゼロコンフィグ自動インストルメンテーション
│   │   ├── openai_integration.py
│   │   ├── anthropic_integration.py
│   │   └── langchain_integration.py
│   ├── dashboard/           # 可視化レイヤー
│   │   ├── tui.py           # Rich ターミナルダッシュボード（TUI）
│   │   └── server.py        # Web ダッシュボード（自己完結型 HTML）
│   ├── exporters/           # JSON、Chrome Trace 等へエクスポート
│   └── cli.py               # CLI: traceweave tui|dashboard|demo|export
├── examples/                # デモスクリプト（APIキー不要）
└── tests/                   # 39テスト、100%パス
```

| 技術 | 用途 |
|:-----|:-----|
| **Pydantic v2** | データモデル + バリデーション + シリアライゼーション |
| **Rich** | 美しいターミナルレンダリング（TUI） |
| **Click** | CLI フレームワーク |
| **contextvars** | スレッド＆非同期セーフなトレース伝播 |
| **orjson** | 高速 JSON シリアライゼーション（エクスポート） |

---

# 🤝 コントリビュート

コントリビューション大歓迎です！バグ報告、機能リクエスト、プルリクエスト — すべて歓迎します。

1. リポジトリを Fork
2. フィーチャーブランチを作成（`git checkout -b feature/amazing`）
3. テスト実行：`pytest tests/ -v`
4. 変更をコミット（`git commit -m 'Add amazing feature'`）
5. ブランチにプッシュ（`git push origin feature/amazing`）
6. Pull Request を作成

---

# ⭐ Star 履歴

traceweave が役立ったら、ぜひ Star をお願いします！プロジェクトの発見に繋がります。

[![Star History Chart](https://api.star-history.com/svg?repos=weivwang/trace-wave&type=Date)](https://star-history.com/#weivwang/trace-wave&Date)

---

# 📄 ライセンス

MIT ライセンス — 詳細は [LICENSE](LICENSE) をご覧ください。

---

<div align="center">

**AI エージェントコミュニティのために ❤️ を込めて開発**

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
