<div align="center">

# 🔍 traceweave

### AI 에이전트를 위한 분산 트레이싱 & 옵저버빌리티

**AI 에이전트가 무엇을 하는지 정확히 파악하세요. 멀티 에이전트 시스템을 프로처럼 디버깅하세요.**

[![PyPI version](https://img.shields.io/pypi/v/traceweave.svg)](https://pypi.org/project/traceweave/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/traceweave.svg)](https://pypi.org/project/traceweave/)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | **한국어** | [Español](README_ES.md)

[빠른 시작](#-빠른-시작) · [기능](#-기능) · [통합](#-통합) · [대시보드](#-대시보드) · [예제](#-예제)

</div>

---

> **AI 에이전트를 위한 Datadog.** 에이전트의 모든 판단, 도구 호출, LLM 상호작용을 아름다운 시각화와 제로 설정 인스트루먼테이션으로 추적합니다.

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
    ⏱  소요시간: 12.3s │ 🔢 스팬: 11 │ 📊 토큰: 8.2k │ 💰 비용: $0.15
```

## 왜 traceweave인가?

AI 에이전트를 개발하면서 이런 경험이 있으신가요?

- 🤯 **"에이전트가 왜 그렇게 했지?"** — 에이전트 추론 체인을 볼 수 없음
- 💸 **"토큰이 다 어디로 갔지?"** — 중첩 호출에서 비용 추적 불가
- 🐛 **"어떤 단계에서 실패한 거지?"** — 멀티 에이전트 파이프라인 디버깅은 악몽
- 📊 **"각 단계에 시간이 얼마나 걸리지?"** — 에이전트 성능 프로파일링 부재

**traceweave는 단 2줄의 코드로 이 모든 문제를 해결합니다.**

## 🚀 빠른 시작

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

# 모든 것을 추적
with tracer.start_trace("math-task"):
    answer = math_agent("What is 2 + 3?")

# 시각화
print_trace(tracer.get_all_traces()[-1])
```

## ✨ 기능

### 🎯 제로 설정 자동 인스트루먼테이션

한 줄로 OpenAI, Anthropic, LangChain 자동 추적:

```python
from agent_trace.integrations import instrument_all
instrument_all()  # 끝! 모든 LLM 호출이 자동으로 추적됩니다.
```

### 🤖 우아한 데코레이터

```python
@trace_agent("researcher")    # 에이전트 함수 추적
@trace_tool("web-search")     # 도구 호출 추적
@trace_llm(model="gpt-4")     # 토큰 추적이 포함된 LLM 호출 추적
```

### 📊 토큰 & 비용 추적

주요 모델의 토큰 사용량과 비용을 자동 계산:

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

### 🖥️ 아름다운 터미널 대시보드

```bash
traceweave tui  # 실시간 업데이트 터미널 대시보드
```

### 🌐 웹 대시보드

```bash
traceweave dashboard  # http://localhost:8420 에서 열기
```

다크 테마 실시간 웹 대시보드:
- 인터랙티브 트레이스 트리 시각화
- 토큰 사용량 분석
- 에이전트/도구별 비용 분석
- 타임라인 워터폴 뷰

### 📤 다양한 형식으로 내보내기

```python
from agent_trace.exporters import export_json, export_chrome

# JSON으로 저장
export_json(trace, "my-trace.json")

# Chrome DevTools 형식으로 내보내기 (chrome://tracing에서 열기)
export_chrome(trace, "my-trace.chrome.json")
```

## 🔌 통합

### OpenAI

```python
from agent_trace.integrations.openai_integration import instrument_openai
instrument_openai()

# 모든 OpenAI 호출이 자동으로 추적됩니다!
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "안녕하세요!"}]
)
```

### Anthropic

```python
from agent_trace.integrations.anthropic_integration import instrument_anthropic
instrument_anthropic()

# 모든 Anthropic 호출이 자동으로 추적됩니다!
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "안녕하세요!"}]
)
```

### LangChain

```python
from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

handler = AgentTraceCallbackHandler()
chain = prompt | llm | output_parser
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

## 📁 예제

| 예제 | 설명 |
|------|------|
| [간단한 데모](examples/simple_demo.py) | 최소 예제 — 10줄로 추적 |
| [멀티 에이전트 리서치](examples/multi_agent_demo.py) | 4 에이전트 팀, 도구 호출, LLM, 비용 추적 포함 |

내장 데모 실행:

```bash
traceweave demo
```

## 🏗️ 아키텍처

```
traceweave/
├── agent_trace/
│   ├── core/           # 핵심 트레이싱 엔진
│   │   ├── models.py   # Pydantic 데이터 모델 (Span, Trace, TokenUsage)
│   │   ├── tracer.py   # 메인 트레이서 (컨텍스트 관리 포함)
│   │   ├── span.py     # Span 컨텍스트 매니저
│   │   ├── context.py  # 스레드 안전 컨텍스트 전파
│   │   └── decorators.py # @trace_agent, @trace_tool, @trace_llm
│   ├── integrations/   # 프레임워크 자동 인스트루먼테이션
│   │   ├── openai_integration.py
│   │   ├── anthropic_integration.py
│   │   └── langchain_integration.py
│   ├── dashboard/      # 시각화
│   │   ├── tui.py      # Rich 터미널 대시보드
│   │   └── server.py   # 웹 대시보드 (단일 HTML, 빌드 불필요)
│   ├── exporters/      # 내보내기 형식
│   │   ├── json_exporter.py
│   │   └── chrome_exporter.py
│   └── cli.py          # CLI 명령어
└── examples/           # 데모 스크립트
```

## 🔑 핵심 개념

| 개념 | 설명 |
|------|------|
| **Trace (트레이스)** | 완전한 작업 단위 (예: "리서치 태스크"). Span 트리를 포함. |
| **Span (스팬)** | 개별 작업 단위 (에이전트 호출, 도구 사용, LLM 요청). |
| **SpanKind (종류)** | Span 유형: `AGENT`, `TOOL`, `LLM`, `CHAIN`, `RETRIEVER` |
| **TokenUsage (사용량)** | LLM 호출별 토큰 수 + 비용 추정 |

## 📦 설치

```bash
# 코어만
pip install traceweave

# 특정 통합 포함
pip install traceweave[openai]
pip install traceweave[anthropic]
pip install traceweave[langchain]

# 전부
pip install traceweave[all]
```

**요구사항:** Python 3.9+

## 🤝 기여하기

기여를 환영합니다! Pull Request를 자유롭게 제출해 주세요.

1. 저장소 Fork
2. 기능 브랜치 생성 (`git checkout -b feature/amazing`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing`)
5. Pull Request 생성

## 📄 라이선스

MIT 라이선스 — 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

---

<div align="center">

**AI 에이전트 커뮤니티를 위해 ❤️ 를 담아 개발**

traceweave가 유용하다면 ⭐ 를 눌러주세요!

</div>
