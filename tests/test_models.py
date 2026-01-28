"""
Tests for core data models.
"""

import pytest
from datetime import datetime, timezone

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


class TestPackageIdentifier:
    """Tests for PackageIdentifier dataclass."""

    def test_basic_creation(self):
        """Test creating a basic package identifier."""
        pkg = PackageIdentifier(name="requests")
        assert pkg.name == "requests"
        assert pkg.version is None
        assert pkg.extras == ()

    def test_with_version(self):
        """Test creating a package identifier with version."""
        pkg = PackageIdentifier(name="requests", version="2.28.0")
        assert pkg.name == "requests"
        assert pkg.version == "2.28.0"

    def test_with_extras(self):
        """Test creating a package identifier with extras."""
        pkg = PackageIdentifier(
            name="requests",
            version="2.28.0",
            extras=("security", "socks"),
        )
        assert pkg.extras == ("security", "socks")

    def test_str_representation(self):
        """Test string representation."""
        # Basic
        assert str(PackageIdentifier(name="requests")) == "requests"

        # With version
        assert str(PackageIdentifier(name="requests", version="2.28.0")) == "requests==2.28.0"

        # With extras
        pkg = PackageIdentifier(name="requests", extras=("security",))
        assert str(pkg) == "requests[security]"

        # With extras and version
        pkg = PackageIdentifier(
            name="requests",
            version="2.28.0",
            extras=("security", "socks"),
        )
        assert str(pkg) == "requests[security,socks]==2.28.0"

    def test_normalized_name(self):
        """Test normalized package name."""
        assert PackageIdentifier(name="My_Package").normalized_name == "my-package"
        assert PackageIdentifier(name="requests").normalized_name == "requests"

    def test_equality(self):
        """Test package identifier equality."""
        pkg1 = PackageIdentifier(name="requests", version="2.28.0")
        pkg2 = PackageIdentifier(name="requests", version="2.28.0")
        pkg3 = PackageIdentifier(name="Requests", version="2.28.0")  # Different case

        assert pkg1 == pkg2
        assert pkg1 == pkg3  # Case-insensitive comparison

    def test_hash(self):
        """Test package identifier hashing."""
        pkg1 = PackageIdentifier(name="requests", version="2.28.0")
        pkg2 = PackageIdentifier(name="requests", version="2.28.0")

        assert hash(pkg1) == hash(pkg2)
        assert {pkg1, pkg2} == {pkg1}  # Same in a set


class TestHealthGrade:
    """Tests for HealthGrade enum."""

    def test_grade_values(self):
        """Test grade string values."""
        assert HealthGrade.A.value == "A"
        assert HealthGrade.F.value == "F"

    def test_grade_str(self):
        """Test grade string representation."""
        assert str(HealthGrade.A) == "A"


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_risk_values(self):
        """Test risk level values."""
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.LOW.value == "low"

    def test_sort_order(self):
        """Test risk level sort order."""
        assert RiskLevel.CRITICAL.sort_order < RiskLevel.HIGH.sort_order
        assert RiskLevel.HIGH.sort_order < RiskLevel.MEDIUM.sort_order
        assert RiskLevel.MEDIUM.sort_order < RiskLevel.LOW.sort_order
        assert RiskLevel.LOW.sort_order < RiskLevel.INFO.sort_order


class TestMaintenanceStatus:
    """Tests for MaintenanceStatus enum."""

    def test_is_concerning(self):
        """Test is_concerning property."""
        assert MaintenanceStatus.ABANDONED.is_concerning
        assert MaintenanceStatus.ARCHIVED.is_concerning
        assert MaintenanceStatus.DEPRECATED.is_concerning

        assert not MaintenanceStatus.ACTIVE.is_concerning
        assert not MaintenanceStatus.STABLE.is_concerning


class TestVulnerability:
    """Tests for Vulnerability dataclass."""

    def test_basic_creation(self, sample_vulnerability):
        """Test creating a vulnerability."""
        assert sample_vulnerability.id == "CVE-2023-32681"
        assert sample_vulnerability.severity == RiskLevel.MEDIUM
        assert sample_vulnerability.fixed_version == "2.31.0"

    def test_has_fix(self, sample_vulnerability):
        """Test has_fix property."""
        assert sample_vulnerability.has_fix

        no_fix_vuln = Vulnerability(
            id="CVE-2024-0001",
            severity=RiskLevel.HIGH,
            title="Test vulnerability",
            description="Test",
            affected_versions=">=1.0.0",
        )
        assert not no_fix_vuln.has_fix

    def test_str_representation(self, sample_vulnerability):
        """Test string representation."""
        result = str(sample_vulnerability)
        assert "CVE-2023-32681" in result
        assert "medium" in result


class TestPyPIMetadata:
    """Tests for PyPIMetadata dataclass."""

    def test_repository_url(self, sample_pypi_metadata):
        """Test repository_url property."""
        assert sample_pypi_metadata.repository_url == "https://github.com/psf/requests"

    def test_repository_url_fallback(self):
        """Test repository_url with alternative keys."""
        metadata = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            project_urls={"Source": "https://github.com/test/test"},
        )
        assert metadata.repository_url == "https://github.com/test/test"

    def test_is_deprecated(self):
        """Test is_deprecated property."""
        active = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            classifiers=["Development Status :: 5 - Production/Stable"],
        )
        assert not active.is_deprecated

        deprecated = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            classifiers=["Development Status :: 7 - Inactive"],
        )
        assert deprecated.is_deprecated


class TestHealthScore:
    """Tests for HealthScore dataclass."""

    def test_is_healthy(self, sample_health_score):
        """Test is_healthy property."""
        assert sample_health_score.is_healthy  # Grade B

        unhealthy = HealthScore(overall=50, grade=HealthGrade.F)
        assert not unhealthy.is_healthy

    def test_is_concerning(self):
        """Test is_concerning property."""
        concerning = HealthScore(overall=55, grade=HealthGrade.F)
        assert concerning.is_concerning

        not_concerning = HealthScore(overall=85, grade=HealthGrade.B)
        assert not not_concerning.is_concerning

    def test_has_vulnerabilities(self, sample_vulnerability):
        """Test has_vulnerabilities property."""
        with_vulns = HealthScore(
            overall=70,
            grade=HealthGrade.C,
            vulnerabilities=[sample_vulnerability],
        )
        assert with_vulns.has_vulnerabilities

        without_vulns = HealthScore(overall=90, grade=HealthGrade.A)
        assert not without_vulns.has_vulnerabilities

    def test_critical_vulnerabilities(self, sample_vulnerability):
        """Test critical_vulnerabilities property."""
        critical_vuln = Vulnerability(
            id="CVE-2024-CRITICAL",
            severity=RiskLevel.CRITICAL,
            title="Critical issue",
            description="Very bad",
            affected_versions="*",
        )

        score = HealthScore(
            overall=40,
            grade=HealthGrade.F,
            vulnerabilities=[sample_vulnerability, critical_vuln],
        )

        assert len(score.critical_vulnerabilities) == 1
        assert score.critical_vulnerabilities[0].id == "CVE-2024-CRITICAL"


class TestDependencyReport:
    """Tests for DependencyReport dataclass."""

    def test_needs_attention(self, sample_dependency_report, sample_vulnerability):
        """Test needs_attention property."""
        # Healthy report doesn't need attention
        assert not sample_dependency_report.needs_attention

        # Report with vulnerabilities needs attention
        report_with_vulns = DependencyReport(
            package=PackageIdentifier(name="test"),
            health=HealthScore(
                overall=70,
                grade=HealthGrade.C,
                vulnerabilities=[sample_vulnerability],
            ),
        )
        assert report_with_vulns.needs_attention

        # Concerning grade needs attention
        report_bad_grade = DependencyReport(
            package=PackageIdentifier(name="test"),
            health=HealthScore(overall=55, grade=HealthGrade.F),
        )
        assert report_bad_grade.needs_attention

    def test_to_dict(self, sample_dependency_report):
        """Test to_dict serialization."""
        result = sample_dependency_report.to_dict()

        assert result["package"]["name"] == "requests"
        assert result["package"]["version"] == "2.28.0"
        assert result["health"]["grade"] == "B"
        assert result["health"]["overall"] == 85.0
        assert result["update_available"] == "2.31.0"
        assert result["is_direct"] is True
