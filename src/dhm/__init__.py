"""
Dependency Health Monitor (DHM)

A comprehensive health assessment tool for Python project dependencies.
Aggregates data from PyPI, GitHub, and security databases to calculate
composite health scores, identify vulnerabilities, and recommend alternatives.
"""

__version__ = "0.1.0"

from dhm.core.models import (
    AlternativePackage,
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
from dhm.core.calculator import HealthCalculator
from dhm.core.resolver import DependencyResolver
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
    # Models
    "AlternativePackage",
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
