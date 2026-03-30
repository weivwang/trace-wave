"""Framework integrations for traceweave.

Quick start:
    # OpenAI
    from agent_trace.integrations.openai_integration import instrument_openai
    instrument_openai()

    # Anthropic
    from agent_trace.integrations.anthropic_integration import instrument_anthropic
    instrument_anthropic()

    # LangChain
    from agent_trace.integrations.langchain_integration import AgentTraceCallbackHandler
    handler = AgentTraceCallbackHandler()
"""


def instrument_all():
    """Instrument all available frameworks.

    Attempts to patch every supported SDK that is currently installed.
    SDKs that are not installed are silently skipped.

    Returns:
        list[str]: Names of frameworks that were successfully instrumented.
    """
    instrumented = []

    try:
        from agent_trace.integrations.openai_integration import instrument_openai
        instrument_openai()
        instrumented.append("openai")
    except ImportError:
        pass

    try:
        from agent_trace.integrations.anthropic_integration import instrument_anthropic
        instrument_anthropic()
        instrumented.append("anthropic")
    except ImportError:
        pass

    return instrumented
