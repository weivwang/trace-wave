<div align="center">
  <picture>
    <img src="docs/assets/banner.svg" width="100%">
  </picture>

  <h3>Rastrea Cada Decisión. Depura Cualquier Agente. Controla Todos los Costos.</h3>

  [English](README.md) / [简体中文](README_CN.md) / [日本語](README_JA.md) / [한국어](README_KO.md) / **Español**

  [Mejores Prácticas][docs-link] · [Reportar Bug][issues-link] · [Solicitar Función][issues-link]

  [![][pypi-shield]][pypi-link]
  [![][python-shield]][python-link]
  [![][license-shield]][license-link]
  [![][downloads-shield]][pypi-link]
  [![][test-shield]][test-link]

</div>

---

## Tabla de Contenidos

- [👋🏻 ¿Qué es traceweave?](#-qué-es-traceweave)
- [🚀 Características Principales](#-características-principales)
- [🆚 ¿Por qué traceweave?](#-por-qué-traceweave)
- [🏁 Inicio Rápido](#-inicio-rápido)
- [🔌 Integraciones](#-integraciones)
- [📊 Dashboards](#-dashboards)
- [📁 Ejemplos](#-ejemplos)
- [🏗️ Arquitectura](#️-arquitectura)
- [🤝 Contribuir](#-contribuir)
- [⭐ Historial de Stars](#-historial-de-stars)
- [📄 Licencia](#-licencia)

---

# 👋🏻 ¿Qué es traceweave?

**traceweave** es el **Datadog para Agentes de IA** — una plataforma de trazabilidad distribuida y observabilidad de código abierto, diseñada específicamente para sistemas de IA multi-agente.

Agrega **2 líneas de código** para ver exactamente qué hacen tus agentes: cada llamada LLM, cada invocación de herramientas, cada decisión — con conteo de tokens, seguimiento de costos y hermosas visualizaciones.

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

> 💡 Este trace fue generado por [Showcase Demo](examples/showcase_demo.py) — un pipeline completo de soporte al cliente con IA: 4 agentes, 10 llamadas a herramientas, 5 llamadas LLM, manejo de errores y reintentos. **Sin API keys necesarias.**

---

# 🚀 Características Principales

1. 🎯 **Instrumentación Automática Sin Configuración** — `instrument_all()` auto-rastrea OpenAI, Anthropic, LangChain. Sin cambios en el código.

2. 🤖 **API de Decoradores Elegante** — `@trace_agent`, `@trace_tool`, `@trace_llm` — rastrea cualquier función con una línea. Soporta sync & async.

3. 💰 **Seguimiento de Tokens y Costos** — Conteo automático de tokens y estimación de costos para todos los modelos principales.

4. 🖥️ **Visualizaciones Hermosas** — Dashboard terminal Rich (TUI) + dashboard web con tema oscuro. Salida digna de captura de pantalla.

5. ❌ **Trazado de Errores y Depuración** — Captura de excepciones con stack traces completos. Ve exactamente qué agente/herramienta falló.

6. 📤 **Exportar a Cualquier Formato** — JSON, Chrome DevTools (`chrome://tracing`) y más. Integra con tu stack de observabilidad existente.

7. 🔗 **Anidamiento Profundo** — Seguimiento automático padre-hijo vía `contextvars`. Sin paso manual de contexto.

8. ⚡ **Ligero y Rápido** — Python puro, ~3K líneas, sin dependencias pesadas. <1ms de overhead por span.

---

# 🆚 ¿Por qué traceweave?

### ¿Para quién es?

| Usuarios Objetivo | Roles | Problemas |
|:-----------------|:------|:----------|
| **Desarrolladores de Agentes IA** | Construyendo con LangChain, CrewAI, AutoGen, agentes custom | No pueden ver qué hacen los agentes; depuración por adivinanza |
| **Equipos de Aplicaciones LLM** | Apps IA en producción con múltiples llamadas LLM | Costos de tokens fuera de control |
| **Ingenieros de Plataforma IA** | Operando infraestructura multi-agente a escala | Sin estándar de observabilidad para IA — APM existente no entiende agentes |

### Comparación con alternativas

| Capacidad | traceweave | LangSmith | Weights & Biases | OpenTelemetry |
|:----------|:----------:|:---------:|:-----------------:|:-------------:|
| Código abierto | ✅ MIT | ❌ Propietario | ❌ Propietario | ✅ Apache-2.0 |
| Spans nativos de agente | ✅ `AGENT`, `TOOL`, `LLM` | ✅ | ⚠️ Genérico | ❌ Genérico |
| Zero-config | ✅ `instrument_all()` | ⚠️ Cambios SDK | ❌ Manual | ❌ Manual |
| Token & costo | ✅ Integrado | ✅ | ⚠️ Parcial | ❌ No |
| TUI hermosa | ✅ Rich terminal UI | ❌ Solo web | ❌ Solo web | ❌ Sin UI |
| Self-hosted/offline | ✅ 100% local | ❌ Nube requerida | ❌ Nube requerida | ✅ Self-hosted |
| Ligero | ✅ ~3K líneas, Python puro | ❌ SDK pesado | ❌ SDK pesado | ⚠️ Config compleja |
| API de decoradores | ✅ `@trace_agent` | ❌ | ❌ | ❌ |

> **🎯 El punto fuerte de traceweave:** Quieres observabilidad de agentes nivel LangSmith, pero open-source, self-hosted y sin vendor lock-in.

---

# 🏁 Inicio Rápido

### 1. Instalar

```bash
pip install traceweave
```

### 2. Instrumenta tu código

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

# Rastrea todo
with tracer.start_trace("my-task"):
    answer = research("AI agents")

# Visualiza — ¡hermosa salida en terminal!
print_trace(tracer.get_all_traces()[-1])
```

### 3. O auto-instrumenta código existente (¡sin cambios!)

```python
from agent_trace.integrations import instrument_all
instrument_all()  # ← ¡Eso es todo! Todas las llamadas OpenAI/Anthropic se rastrean.

# Tu código existente funciona sin cambios
client = openai.OpenAI()
response = client.chat.completions.create(model="gpt-4", messages=[...])
# ^ ¡Esta llamada se rastrea automáticamente con tokens y costo!
```

### 4. Explora dashboards

```bash
traceweave tui        # Dashboard terminal (actualización en vivo)
traceweave dashboard  # Dashboard web en http://localhost:8420
traceweave demo       # Ejecutar demo integrada
```

---

# 🔌 Integraciones

Auto-instrumenta frameworks de IA populares con una sola línea:

| Framework | Integración | Instalación |
|:----------|:-----------|:-----------|
| **OpenAI** | `instrument_openai()` | `pip install traceweave[openai]` |
| **Anthropic** | `instrument_anthropic()` | `pip install traceweave[anthropic]` |
| **LangChain** | `AgentTraceCallbackHandler` | `pip install traceweave[langchain]` |
| **Todos** | `instrument_all()` | `pip install traceweave[all]` |

<details>
<summary><b>Ejemplo OpenAI</b></summary>

```python
from agent_trace.integrations.openai_integration import instrument_openai
instrument_openai()

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "¡Hola!"}]
)
# Rastreado automáticamente: modelo, tokens, costo, latencia, entrada/salida
```

</details>

<details>
<summary><b>Ejemplo Anthropic</b></summary>

```python
from agent_trace.integrations.anthropic_integration import instrument_anthropic
instrument_anthropic()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "¡Hola!"}]
)
```

</details>

<details>
<summary><b>Ejemplo LangChain</b></summary>

```python
from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler

handler = AgentTraceCallbackHandler()
chain = prompt | llm | output_parser
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

</details>

---

# 📊 Dashboards

### Dashboard Terminal (TUI)

```bash
traceweave tui
```

Dashboard terminal en tiempo real con Rich:
- 🌲 Árbol de traces interactivo con código de colores
- 📊 Barras de cascada de uso de tokens
- 💰 Desglose de costos por span
- ❌ Resaltado de errores con stack traces

### Dashboard Web

```bash
traceweave dashboard  # → http://localhost:8420
```

UI web self-hosted con tema oscuro:
- Visualización interactiva del árbol de traces
- Análisis de uso de tokens
- Desglose de costos por agente/herramienta
- Vista de cascada temporal
- Sin dependencias externas — HTML embebido único

### Exportar a Chrome DevTools

```python
from agent_trace.exporters import export_chrome
export_chrome(trace, "my-trace.chrome.json")
# Abre chrome://tracing → Cargar → ¡Gráfico de llama interactivo!
```

---

# 📁 Ejemplos

| Ejemplo | Descripción | Complejidad |
|:--------|:-----------|:-----------|
| **[Demo Simple](examples/simple_demo.py)** | Rastreo mínimo en 10 líneas | ⭐ |
| **[Investigación Multi-Agente](examples/multi_agent_demo.py)** | Equipo de 4 agentes + herramientas + llamadas LLM | ⭐⭐ |
| **[Showcase: Pipeline de Soporte IA](examples/showcase_demo.py)** | Simulación producción: 4 agentes, RAG, manejo de errores, 3 modelos | ⭐⭐⭐ |
| **[DeepSeek Agent (API Real)](examples/deepseek_agent_demo.py)** | Agente real con DeepSeek, trazado en vivo, TUI & dashboard web | ⭐⭐⭐ |

```bash
# Ejecutar Showcase demo (¡sin API keys!)
python examples/showcase_demo.py

# Ejecutar demo real de DeepSeek Agent (requiere API key)
python examples/deepseek_agent_demo.py --dashboard
```

---

# 🔑 Conceptos Clave

| Concepto | Descripción |
|:---------|:-----------|
| **Trace** | Una operación completa de extremo a extremo. Contiene un árbol de spans. |
| **Span** | Una unidad de trabajo — llamada de agente, invocación de herramienta, o petición LLM. |
| **SpanKind** | Categoriza spans: `AGENT` 🤖, `TOOL` 🔧, `LLM` 🧠, `CHAIN` 🔗, `RETRIEVER` 📚 |
| **TokenUsage** | Conteo de tokens por span + estimación de costos con precios por modelo. |
| **Decorator API** | `@trace_agent`, `@trace_tool`, `@trace_llm` — instrumentación de una línea. |

---

# 🏗️ Arquitectura

```
traceweave/
├── agent_trace/
│   ├── core/               # Motor de rastreo principal
│   │   ├── models.py       # Modelos de datos Pydantic v2 (Span, Trace, TokenUsage)
│   │   ├── tracer.py       # AgentTracer — gestión de contexto & sistema de eventos
│   │   ├── span.py         # Gestor de contexto Span con API fluida
│   │   ├── context.py      # Propagación de contexto segura para hilos (contextvars)
│   │   └── decorators.py   # @trace_agent, @trace_tool, @trace_llm
│   ├── integrations/       # Auto-instrumentación zero-config de frameworks
│   │   ├── openai_integration.py
│   │   ├── anthropic_integration.py
│   │   └── langchain_integration.py
│   ├── dashboard/           # Capa de visualización
│   │   ├── tui.py           # Dashboard terminal Rich (TUI)
│   │   └── server.py        # Dashboard web (HTML autocontenido)
│   ├── exporters/           # Exportar a JSON, Chrome Trace, etc.
│   └── cli.py               # CLI: traceweave tui|dashboard|demo|export
├── examples/                # Scripts de demo (sin API keys necesarias)
└── tests/                   # 39 tests, 100% pasando
```

| Tecnología | Propósito |
|:-----------|:---------|
| **Pydantic v2** | Modelos de datos + validación + serialización |
| **Rich** | Renderizado de terminal hermoso (TUI) |
| **Click** | Framework CLI |
| **contextvars** | Propagación de trace segura para hilos & async |
| **orjson** | Serialización JSON rápida (exports) |

---

# 🤝 Contribuir

¡Las contribuciones son bienvenidas! Ya sea un reporte de bug, solicitud de función o pull request — lo agradecemos todo.

1. Haz Fork del repositorio
2. Crea tu rama de función (`git checkout -b feature/amazing`)
3. Ejecuta tests: `pytest tests/ -v`
4. Haz commit de tus cambios (`git commit -m 'Add amazing feature'`)
5. Haz push a la rama (`git push origin feature/amazing`)
6. Abre un Pull Request

---

# ⭐ Historial de Stars

Si encuentras útil traceweave, ¡por favor danos una star! Ayuda a que otros descubran el proyecto.

[![Star History Chart](https://api.star-history.com/svg?repos=weivwang/trace-wave&type=Date)](https://star-history.com/#weivwang/trace-wave&Date)

---

# 📄 Licencia

Licencia MIT — ver [LICENSE](LICENSE) para detalles.

---

<div align="center">

**Hecho con ❤️ para la comunidad de agentes de IA**

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
