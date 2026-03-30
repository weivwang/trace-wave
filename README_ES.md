<div align="center">

# 🔍 traceweave

### Trazabilidad Distribuida y Observabilidad para Agentes de IA

**Observa exactamente qué hacen tus agentes de IA. Depura sistemas multi-agente como un profesional.**

[![PyPI version](https://img.shields.io/pypi/v/traceweave.svg)](https://pypi.org/project/traceweave/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/traceweave.svg)](https://pypi.org/project/traceweave/)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | **Español**

[Inicio Rápido](#-inicio-rápido) · [Características](#-características) · [Integraciones](#-integraciones) · [Dashboard](#-dashboard) · [Ejemplos](#-ejemplos)

</div>

---

> **Piensa en él como Datadog para Agentes de IA.** Rastrea cada decisión del agente, llamada a herramientas e interacción con LLM con hermosas visualizaciones e instrumentación sin configuración.

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
    ⏱  Duración: 12.3s │ 🔢 Spans: 11 │ 📊 Tokens: 8.2k │ 💰 Costo: $0.15
```

## ¿Por qué traceweave?

¿Estás desarrollando con agentes de IA? Probablemente has experimentado:

- 🤯 **"¿Por qué mi agente hizo eso?"** — Sin visibilidad de las cadenas de razonamiento
- 💸 **"¿A dónde se fueron mis tokens?"** — No se pueden rastrear costos en llamadas anidadas
- 🐛 **"¿Cuál paso falló?"** — Depurar pipelines multi-agente es una pesadilla
- 📊 **"¿Cuánto tarda cada paso?"** — Sin perfilado de rendimiento para agentes

**traceweave resuelve todo esto con solo 2 líneas de código.**

## 🚀 Inicio Rápido

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

# Rastrea todo
with tracer.start_trace("math-task"):
    answer = math_agent("What is 2 + 3?")

# Visualiza
print_trace(tracer.get_all_traces()[-1])
```

## ✨ Características

### 🎯 Instrumentación Automática Sin Configuración

Rastrea automáticamente OpenAI, Anthropic y LangChain con una sola línea:

```python
from agent_trace.integrations import instrument_all
instrument_all()  # ¡Eso es todo! Todas las llamadas LLM se rastrean automáticamente.
```

### 🤖 Decoradores Elegantes

```python
@trace_agent("researcher")    # Rastrea funciones de agente
@trace_tool("web-search")     # Rastrea llamadas a herramientas
@trace_llm(model="gpt-4")     # Rastrea llamadas LLM con seguimiento de tokens
```

### 📊 Seguimiento de Tokens y Costos

Conteo automático de tokens y estimación de costos para todos los modelos principales:

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

### 🖥️ Hermoso Dashboard en Terminal

```bash
traceweave tui  # Dashboard de terminal con actualización en tiempo real
```

### 🌐 Dashboard Web

```bash
traceweave dashboard  # Se abre en http://localhost:8420
```

Dashboard web en tiempo real con tema oscuro:
- Visualización interactiva del árbol de trazas
- Análisis de uso de tokens
- Desglose de costos por agente/herramienta
- Vista de cascada de línea temporal

### 📤 Exportar a Cualquier Formato

```python
from agent_trace.exporters import export_json, export_chrome

# Guardar como JSON
export_json(trace, "my-trace.json")

# Exportar a formato Chrome DevTools (abrir en chrome://tracing)
export_chrome(trace, "my-trace.chrome.json")
```

## 🔌 Integraciones

### OpenAI

```python
from agent_trace.integrations.openai_integration import instrument_openai
instrument_openai()

# ¡Todas las llamadas a OpenAI se rastrean automáticamente!
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "¡Hola!"}]
)
```

### Anthropic

```python
from agent_trace.integrations.anthropic_integration import instrument_anthropic
instrument_anthropic()

# ¡Todas las llamadas a Anthropic se rastrean automáticamente!
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "¡Hola!"}]
)
```

### LangChain

```python
from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

handler = AgentTraceCallbackHandler()
chain = prompt | llm | output_parser
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

## 📁 Ejemplos

| Ejemplo | Descripción |
|---------|-------------|
| [Demo Simple](examples/simple_demo.py) | Ejemplo mínimo — rastreo en 10 líneas |
| [Investigación Multi-Agente](examples/multi_agent_demo.py) | Equipo de 4 agentes con herramientas, LLM y seguimiento de costos |

Ejecutar la demo integrada:

```bash
traceweave demo
```

## 🏗️ Arquitectura

```
traceweave/
├── agent_trace/
│   ├── core/           # Motor de rastreo principal
│   │   ├── models.py   # Modelos de datos Pydantic (Span, Trace, TokenUsage)
│   │   ├── tracer.py   # Rastreador principal con gestión de contexto
│   │   ├── span.py     # Gestor de contexto Span
│   │   ├── context.py  # Propagación de contexto segura para hilos
│   │   └── decorators.py # @trace_agent, @trace_tool, @trace_llm
│   ├── integrations/   # Instrumentación automática de frameworks
│   │   ├── openai_integration.py
│   │   ├── anthropic_integration.py
│   │   └── langchain_integration.py
│   ├── dashboard/      # Visualización
│   │   ├── tui.py      # Dashboard de terminal Rich
│   │   └── server.py   # Dashboard web (HTML único, sin compilación)
│   ├── exporters/      # Formatos de exportación
│   │   ├── json_exporter.py
│   │   └── chrome_exporter.py
│   └── cli.py          # Comandos CLI
└── examples/           # Scripts de demostración
```

## 🔑 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **Trace** | Una operación completa (ej: "tarea de investigación"). Contiene un árbol de spans. |
| **Span** | Una unidad individual de trabajo (llamada de agente, uso de herramienta, petición LLM). |
| **SpanKind** | Tipo de span: `AGENT`, `TOOL`, `LLM`, `CHAIN`, `RETRIEVER` |
| **TokenUsage** | Conteo de tokens + estimación de costos por llamada LLM |

## 📦 Instalación

```bash
# Solo el core
pip install traceweave

# Con integraciones específicas
pip install traceweave[openai]
pip install traceweave[anthropic]
pip install traceweave[langchain]

# Todo incluido
pip install traceweave[all]
```

**Requisitos:** Python 3.9+

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! No dudes en enviar un Pull Request.

1. Haz Fork del repositorio
2. Crea tu rama de funcionalidad (`git checkout -b feature/amazing`)
3. Haz commit de tus cambios (`git commit -m 'Add amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing`)
5. Abre un Pull Request

## 📄 Licencia

Licencia MIT — ver [LICENSE](LICENSE) para más detalles.

---

<div align="center">

**Hecho con ❤️ para la comunidad de agentes de IA**

Si traceweave te resulta útil, ¡dale una ⭐ al repo!

</div>
