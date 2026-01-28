"""
CLI entry point for running dhm as a module.

Usage: python -m dhm [OPTIONS] COMMAND [ARGS]...
"""

from dhm.cli.main import cli

if __name__ == "__main__":
    cli()
