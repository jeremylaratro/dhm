"""
Report generation module.

Provides report generators and formatters for outputting health reports
in various formats including JSON, Markdown, and rich tables.
"""

from dhm.reports.formatters import (
    Formatter,
    JSONFormatter,
    MarkdownFormatter,
    TableFormatter,
)
from dhm.reports.generator import ReportGenerator

__all__ = [
    "ReportGenerator",
    "Formatter",
    "JSONFormatter",
    "MarkdownFormatter",
    "TableFormatter",
]
