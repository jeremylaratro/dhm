"""
Data collectors for fetching package metadata from external sources.

This module provides async clients for PyPI, GitHub, and vulnerability databases.
"""

from dhm.collectors.base import Collector
from dhm.collectors.pypi import PyPIClient
from dhm.collectors.github import GitHubClient
from dhm.collectors.vulnerability import VulnerabilityScanner, OSVClient

__all__ = [
    "Collector",
    "PyPIClient",
    "GitHubClient",
    "VulnerabilityScanner",
    "OSVClient",
]
