"""
Core module for DHM.

Contains data models, health calculator, dependency resolver, and exceptions.
"""

from dhm.core.calculator import HealthCalculator
from dhm.core.exceptions import (
    CacheError,
    DHMError,
    PackageNotFoundError,
    RateLimitError,
    RepositoryNotFoundError,
)
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
from dhm.core.resolver import DependencyResolver

__all__ = [
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
