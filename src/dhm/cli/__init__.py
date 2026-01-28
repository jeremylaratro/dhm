"""
Command-line interface for DHM.

Provides Click-based CLI commands for scanning dependencies,
checking package health, and finding alternatives.
"""

from dhm.cli.main import cli

__all__ = ["cli"]
