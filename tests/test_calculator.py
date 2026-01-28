"""
Tests for the health calculator.
"""

import pytest
from datetime import datetime, timedelta, timezone

from dhm.core.calculator import HealthCalculator
from dhm.core.models import (
    HealthGrade,
    MaintenanceStatus,
    PyPIMetadata,
    RepositoryMetadata,
    RiskLevel,
    Vulnerability,
)


class TestHealthCalculator:
    """Tests for HealthCalculator class."""

    @pytest.fixture
    def calculator(self):
        """Create a calculator instance."""
        return HealthCalculator()

    def test_default_weights(self, calculator):
        """Test default weight values."""
        assert calculator.weights["security"] == pytest.approx(0.35)
        assert calculator.weights["maintenance"] == pytest.approx(0.30)
        assert calculator.weights["community"] == pytest.approx(0.20)
        assert calculator.weights["popularity"] == pytest.approx(0.15)

    def test_custom_weights(self):
        """Test custom weight configuration."""
        calc = HealthCalculator(weights={"security": 0.5, "maintenance": 0.5})
        # Weights should be normalized
        total = sum(calc.weights.values())
        assert total == pytest.approx(1.0)

    def test_calculate_basic(
        self,
        calculator,
        sample_pypi_metadata,
        sample_repository_metadata,
    ):
        """Test basic health calculation."""
        score = calculator.calculate(
            pypi=sample_pypi_metadata,
            repo=sample_repository_metadata,
            vulnerabilities=[],
        )

        assert score.overall > 0
        assert score.overall <= 100
        assert isinstance(score.grade, HealthGrade)
        assert score.security_score == 100.0  # No vulnerabilities

    def test_calculate_without_metadata(self, calculator):
        """Test calculation with missing metadata."""
        score = calculator.calculate(
            pypi=None,
            repo=None,
            vulnerabilities=[],
        )

        # Should still produce a valid score
        assert score.overall >= 0
        assert score.overall <= 100

    def test_security_score_no_vulns(self, calculator):
        """Test security score with no vulnerabilities."""
        score = calculator._calculate_security_score([])
        assert score == 100.0

    def test_security_score_with_vulns(self, calculator, sample_vulnerability):
        """Test security score with vulnerabilities."""
        # Medium vulnerability should deduct 10 points
        score = calculator._calculate_security_score([sample_vulnerability])
        assert score == 90.0

    def test_security_score_critical_vuln(self, calculator):
        """Test security score with critical vulnerability."""
        critical = Vulnerability(
            id="CVE-2024-CRIT",
            severity=RiskLevel.CRITICAL,
            title="Critical issue",
            description="Very bad",
            affected_versions="*",
        )

        score = calculator._calculate_security_score([critical])
        assert score == 60.0  # 100 - 40

    def test_security_score_multiple_vulns(self, calculator):
        """Test security score with multiple vulnerabilities."""
        vulns = [
            Vulnerability(
                id="CVE-1",
                severity=RiskLevel.CRITICAL,
                title="Critical",
                description="",
                affected_versions="*",
            ),
            Vulnerability(
                id="CVE-2",
                severity=RiskLevel.HIGH,
                title="High",
                description="",
                affected_versions="*",
            ),
        ]

        score = calculator._calculate_security_score(vulns)
        assert score == 35.0  # 100 - 40 - 25

    def test_maintenance_score_recent_release(self, calculator):
        """Test maintenance score with recent release."""
        pypi = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            release_date=datetime.now(timezone.utc) - timedelta(days=15),
            total_releases=10,
        )

        score = calculator._calculate_maintenance_score(pypi, None)
        # Base 50 + 20 (recent) + 5 (releases > 5)
        assert score >= 70

    def test_maintenance_score_old_release(self, calculator):
        """Test maintenance score with old release."""
        pypi = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            release_date=datetime.now(timezone.utc) - timedelta(days=800),
            total_releases=3,
        )

        score = calculator._calculate_maintenance_score(pypi, None)
        # Base 50 - 10 (old release)
        assert score <= 50

    def test_maintenance_score_archived_repo(self, calculator):
        """Test maintenance score with archived repository."""
        repo = RepositoryMetadata(
            url="https://github.com/test/test",
            is_archived=True,
        )

        score = calculator._calculate_maintenance_score(None, repo)
        # Base 50 - 30 (archived)
        assert score <= 30

    def test_community_score_large_community(self, calculator):
        """Test community score with large community."""
        repo = RepositoryMetadata(
            url="https://github.com/test/test",
            contributors_count=150,
            stars=15000,
            forks=500,
            pr_merge_rate_90d=0.8,
        )

        score = calculator._calculate_community_score(repo)
        assert score >= 90  # Should be high

    def test_community_score_small_project(self, calculator):
        """Test community score with small but healthy project.

        With base-50 and logarithmic scoring:
        - 2 contributors: log_normalize(2, 1, 200, 20) ≈ 2.6
        - 5 stars: log_normalize(5, 10, 50000, 20) = 0 (below min)
        - 1 fork: log_normalize(1, 1, 500, 10) = 0 (at min)
        - PR merge rate 0: 0

        Small projects start near neutral, which is appropriate.
        """
        repo = RepositoryMetadata(
            url="https://github.com/test/test",
            contributors_count=2,
            stars=5,
            forks=1,
        )

        score = calculator._calculate_community_score(repo)
        # With log scaling, small values give smaller bonuses
        # Score should be around 50-55 (neutral to slightly above)
        assert 50 <= score <= 58

    def test_community_score_no_repo(self, calculator):
        """Test community score without repository data."""
        score = calculator._calculate_community_score(None)
        assert score == 50.0  # Neutral

    def test_popularity_score_high_downloads(self, calculator):
        """Test popularity score with high downloads.

        With base-50 scoring plus download bonuses, high-download
        packages should score well above neutral.
        """
        pypi = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            downloads_last_month=5_000_000,
        )

        score = calculator._calculate_popularity_score(pypi, None)
        # Base 50 + 30 (1M-10M downloads) = 80
        assert score >= 75

    def test_score_to_grade(self, calculator):
        """Test score to grade conversion.

        Updated thresholds for base-50 scoring:
        - A: >= 85
        - B: >= 75
        - C: >= 65
        - D: >= 55
        - F: < 55
        """
        assert calculator._score_to_grade(95) == HealthGrade.A
        assert calculator._score_to_grade(85) == HealthGrade.A  # A starts at 85
        assert calculator._score_to_grade(80) == HealthGrade.B
        assert calculator._score_to_grade(70) == HealthGrade.C
        assert calculator._score_to_grade(60) == HealthGrade.D
        assert calculator._score_to_grade(50) == HealthGrade.F

    def test_determine_maintenance_status_active(self, calculator):
        """Test determining active maintenance status."""
        pypi = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            release_date=datetime.now(timezone.utc) - timedelta(days=30),
        )

        status = calculator._determine_maintenance_status(pypi, None)
        assert status == MaintenanceStatus.ACTIVE

    def test_determine_maintenance_status_abandoned(self, calculator):
        """Test determining abandoned maintenance status."""
        pypi = PyPIMetadata(
            name="test",
            version="1.0.0",
            summary="Test",
            author="Test",
            release_date=datetime.now(timezone.utc) - timedelta(days=1200),
        )

        status = calculator._determine_maintenance_status(pypi, None)
        assert status == MaintenanceStatus.ABANDONED

    def test_determine_maintenance_status_archived(self, calculator):
        """Test determining archived maintenance status."""
        repo = RepositoryMetadata(
            url="https://github.com/test/test",
            is_archived=True,
        )

        status = calculator._determine_maintenance_status(None, repo)
        assert status == MaintenanceStatus.ARCHIVED

    def test_identify_risks(self, calculator, sample_vulnerability):
        """Test risk identification."""
        critical_vuln = Vulnerability(
            id="CVE-CRIT",
            severity=RiskLevel.CRITICAL,
            title="Critical",
            description="",
            affected_versions="*",
        )

        risks = calculator._identify_risks(
            pypi=None,
            repo=None,
            vulnerabilities=[critical_vuln, sample_vulnerability],
        )

        assert any("critical" in r.lower() for r in risks)

    def test_identify_positives(self, calculator, sample_pypi_metadata):
        """Test positive factor identification."""
        positives = calculator._identify_positives(
            sample_pypi_metadata,
            None,
        )

        # sample_pypi_metadata has 50M downloads
        assert any("popular" in p.lower() for p in positives)
