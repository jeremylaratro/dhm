"""
Dependency Health Monitor (DHM)

A comprehensive health assessment tool for Python project dependencies.
Aggregates data from PyPI, GitHub, and security databases to calculate
composite health scores, identify vulnerabilities, and recommend alternatives.

Quick Start:
    >>> import asyncio
    >>> from dhm import check
    >>> report = asyncio.run(check("requests"))
    >>> print(f"{report.package.name}: {report.health.grade}")
    requests: B

    # Or use synchronous API:
    >>> from dhm import check_sync
    >>> report = check_sync("flask")
    >>> if report.health.has_open_vulnerabilities:
    ...     print("Update needed!")
"""

__version__ = "0.1.0"

# High-level API (recommended for most users)
from dhm.api import (
    check,
    check_sync,
    check_packages,
    scan,
    scan_sync,
)

# Data models
from dhm.core.models import (
    AlternativePackage,
    ConfidenceLevel,
    DependencyReport,
    HealthGrade,
    HealthScore,
    MaintenanceStatus,
    PackageIdentifier,
    PyPIMetadata,
    RepositoryMetadata,
    RiskLevel,
    Vulnerability,
)

# Core components (for advanced usage)
from dhm.core.calculator import HealthCalculator
from dhm.core.resolver import DependencyResolver

# Exceptions
from dhm.core.exceptions import (
    DHMError,
    PackageNotFoundError,
    RepositoryNotFoundError,
    RateLimitError,
    CacheError,
)

__all__ = [
    # Version
    "__version__",
    # High-level API
    "check",
    "check_sync",
    "check_packages",
    "scan",
    "scan_sync",
    # Models
    "AlternativePackage",
    "ConfidenceLevel",
    "DependencyReport",
    "HealthGrade",
    "HealthScore",
    "MaintenanceStatus",
    "PackageIdentifier",
    "PyPIMetadata",
    "RepositoryMetadata",
    "RiskLevel",
    "Vulnerability",
    # Core
    "HealthCalculator",
    "DependencyResolver",
    # Exceptions
    "DHMError",
    "PackageNotFoundError",
    "RepositoryNotFoundError",
    "RateLimitError",
    "CacheError",
]
