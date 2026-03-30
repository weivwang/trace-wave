"""Built-in demo runner for the ``traceweave demo`` CLI command.

This module bridges the CLI entry point to the multi-agent demo script
in the top-level ``examples/`` directory, so users can run::

    traceweave demo
"""
import sys
import os


def run_demo():
    """Run the multi-agent research team demo."""
    # Ensure the project root is importable so we can reach examples/
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    sys.path.insert(0, project_root)

    from examples.multi_agent_demo import main

    main()


if __name__ == "__main__":
    run_demo()
