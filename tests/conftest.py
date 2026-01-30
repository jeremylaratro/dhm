"""
Pytest fixtures and configuration for DHM tests.

Provides mock API responses and test data for unit testing.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from dhm.core.models import (
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

# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_package() -> PackageIdentifier:
    """Create a sample package identifier."""
    return PackageIdentifier(name="requests", version="2.28.0")


@pytest.fixture
def sample_package_with_extras() -> PackageIdentifier:
    """Create a sample package identifier with extras."""
    return PackageIdentifier(
        name="requests",
        version="2.28.0",
        extras=("security", "socks"),
    )


@pytest.fixture
def sample_pypi_metadata() -> PyPIMetadata:
    """Create sample PyPI metadata."""
    return PyPIMetadata(
        name="requests",
        version="2.28.0",
        summary="Python HTTP for Humans.",
        author="Kenneth Reitz",
        author_email="me@kennethreitz.org",
        license="Apache-2.0",
        python_requires=">=3.7",
        requires_dist=["urllib3>=1.21.1", "charset_normalizer>=2,<4"],
        project_urls={
            "Homepage": "https://requests.readthedocs.io",
            "Repository": "https://github.com/psf/requests",
        },
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Programming Language :: Python :: 3",
        ],
        downloads_last_month=50_000_000,
        release_date=datetime(2023, 6, 15, tzinfo=timezone.utc),
        first_release_date=datetime(2011, 2, 14, tzinfo=timezone.utc),
        total_releases=150,
        yanked_releases=2,
    )


@pytest.fixture
def sample_repository_metadata() -> RepositoryMetadata:
    """Create sample repository metadata."""
    return RepositoryMetadata(
        url="https://github.com/psf/requests",
        stars=50000,
        forks=9000,
        open_issues=150,
        open_pull_requests=25,
        watchers=1500,
        contributors_count=700,
        last_commit_date=datetime(2024, 1, 10, tzinfo=timezone.utc),
        created_date=datetime(2011, 2, 13, tzinfo=timezone.utc),
        is_archived=False,
        is_fork=False,
        license="Apache-2.0",
        topics=["http", "python", "requests"],
        default_branch="main",
        commit_frequency_30d=0.5,
        issue_close_rate_90d=0.75,
        pr_merge_rate_90d=0.80,
        avg_issue_close_time_days=14.0,
        avg_pr_merge_time_days=7.0,
    )


@pytest.fixture
def sample_vulnerability() -> Vulnerability:
    """Create a sample vulnerability."""
    return Vulnerability(
        id="CVE-2023-32681",
        severity=RiskLevel.MEDIUM,
        title="Unintended leak of Proxy-Authorization header",
        description="Requests may leak Proxy-Authorization headers to destination servers.",
        affected_versions=">=2.3.0,<2.31.0",
        fixed_version="2.31.0",
        published=datetime(2023, 5, 26, tzinfo=timezone.utc),
        references=["https://nvd.nist.gov/vuln/detail/CVE-2023-32681"],
        cvss_score=6.1,
    )


@pytest.fixture
def sample_health_score() -> HealthScore:
    """Create a sample health score."""
    return HealthScore(
        overall=85.0,
        grade=HealthGrade.B,
        security_score=90.0,
        maintenance_score=80.0,
        community_score=95.0,
        popularity_score=90.0,
        code_quality_score=75.0,
        maintenance_status=MaintenanceStatus.ACTIVE,
        vulnerabilities=[],
        risk_factors=[],
        positive_factors=[
            "Highly popular (1M+ monthly downloads)",
            "Large contributor community",
        ],
        calculated_at=datetime.now(timezone.utc),
        data_freshness={},
    )


@pytest.fixture
def sample_dependency_report(
    sample_package: PackageIdentifier,
    sample_health_score: HealthScore,
    sample_pypi_metadata: PyPIMetadata,
    sample_repository_metadata: RepositoryMetadata,
) -> DependencyReport:
    """Create a sample dependency report."""
    return DependencyReport(
        package=sample_package,
        health=sample_health_score,
        pypi=sample_pypi_metadata,
        repository=sample_repository_metadata,
        alternatives=[],
        update_available="2.31.0",
        is_direct=True,
        dependents=[],
    )


# =============================================================================
# Mock API Response Fixtures
# =============================================================================


@pytest.fixture
def mock_pypi_response() -> dict[str, Any]:
    """Create a mock PyPI API response."""
    return {
        "info": {
            "name": "requests",
            "version": "2.28.0",
            "summary": "Python HTTP for Humans.",
            "author": "Kenneth Reitz",
            "author_email": "me@kennethreitz.org",
            "license": "Apache-2.0",
            "requires_python": ">=3.7",
            "requires_dist": ["urllib3>=1.21.1", "charset_normalizer>=2,<4"],
            "project_urls": {
                "Homepage": "https://requests.readthedocs.io",
                "Repository": "https://github.com/psf/requests",
            },
            "classifiers": [
                "Development Status :: 5 - Production/Stable",
                "Programming Language :: Python :: 3",
            ],
        },
        "releases": {
            "2.28.0": [
                {
                    "upload_time": "2023-06-15T12:00:00",
                    "yanked": False,
                }
            ],
            "2.27.0": [
                {
                    "upload_time": "2023-01-10T12:00:00",
                    "yanked": False,
                }
            ],
        },
    }


@pytest.fixture
def mock_github_response() -> dict[str, Any]:
    """Create a mock GitHub API response."""
    return {
        "html_url": "https://github.com/psf/requests",
        "stargazers_count": 50000,
        "forks_count": 9000,
        "open_issues_count": 150,
        "subscribers_count": 1500,
        "archived": False,
        "fork": False,
        "license": {"spdx_id": "Apache-2.0"},
        "topics": ["http", "python", "requests"],
        "default_branch": "main",
        "created_at": "2011-02-13T00:00:00Z",
    }


@pytest.fixture
def mock_osv_response() -> dict[str, Any]:
    """Create a mock OSV API response."""
    return {
        "vulns": [
            {
                "id": "GHSA-j8r2-6x86-q33q",
                "aliases": ["CVE-2023-32681"],
                "summary": "Unintended leak of Proxy-Authorization header",
                "details": "Requests may leak Proxy-Authorization headers.",
                "published": "2023-05-26T00:00:00Z",
                "severity": [{"type": "CVSS_V3", "score": "6.1"}],
                "affected": [
                    {
                        "ranges": [
                            {
                                "events": [
                                    {"introduced": "2.3.0"},
                                    {"fixed": "2.31.0"},
                                ]
                            }
                        ]
                    }
                ],
                "references": [
                    {"url": "https://nvd.nist.gov/vuln/detail/CVE-2023-32681"}
                ],
            }
        ]
    }


# =============================================================================
# File Fixtures
# =============================================================================


@pytest.fixture
def tmp_requirements_txt(tmp_path: Path) -> Path:
    """Create a temporary requirements.txt file."""
    content = """
# Main dependencies
requests==2.28.0
click>=8.0.0
rich[jupyter]>=13.0.0

# Development dependencies
pytest>=7.0.0
pytest-cov

# With environment markers
numpy>=1.20.0; python_version >= "3.8"
"""
    file_path = tmp_path / "requirements.txt"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def tmp_pyproject_toml(tmp_path: Path) -> Path:
    """Create a temporary pyproject.toml file."""
    content = """
[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[tool.poetry.dependencies]
python = "^3.10"
aiohttp = "^3.8.0"
"""
    file_path = tmp_path / "pyproject.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def tmp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory with multiple dependency files."""
    # Create requirements.txt
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("requests>=2.28.0\nclick>=8.0.0\n")

    # Create requirements-dev.txt
    dev_requirements = tmp_path / "requirements-dev.txt"
    dev_requirements.write_text("pytest>=7.0.0\n-r requirements.txt\n")

    # Create pyproject.toml
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "test-project"
version = "1.0.0"
dependencies = ["rich>=13.0.0"]
""")

    return tmp_path


# =============================================================================
# Mock Client Fixtures
# =============================================================================


@pytest.fixture
def mock_pypi_client(mock_pypi_response: dict) -> MagicMock:
    """Create a mock PyPI client."""
    client = MagicMock()
    client.get_package_info = AsyncMock(return_value=mock_pypi_response)
    return client


@pytest.fixture
def mock_github_client(mock_github_response: dict) -> MagicMock:
    """Create a mock GitHub client."""
    client = MagicMock()
    client.get_repository = AsyncMock(return_value=mock_github_response)
    client.extract_repo_from_url = MagicMock(return_value=("psf", "requests"))
    return client


@pytest.fixture
def mock_vulnerability_scanner(mock_osv_response: dict) -> MagicMock:
    """Create a mock vulnerability scanner."""
    scanner = MagicMock()
    scanner.scan_package = AsyncMock(return_value=[])
    return scanner


# =============================================================================
# Cache Fixtures
# =============================================================================


@pytest.fixture
def tmp_cache_db(tmp_path: Path) -> Path:
    """Create a temporary cache database path."""
    return tmp_path / "test_cache.db"
