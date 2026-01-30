"""
Report generator for orchestrating health report creation.

Provides the main ReportGenerator class that coordinates data collection
and formatting to produce complete dependency health reports.
"""

import asyncio
from pathlib import Path

import aiohttp

from dhm.cache.sqlite import CacheLayer
from dhm.collectors.github import GitHubClient
from dhm.collectors.pypi import PyPIClient
from dhm.collectors.vulnerability import VulnerabilityScanner
from dhm.core.calculator import HealthCalculator
from dhm.core.models import (
    DependencyReport,
    HealthScore,
    PackageIdentifier,
)
from dhm.core.resolver import DependencyResolver
from dhm.reports.formatters import (
    Formatter,
    JSONFormatter,
    MarkdownFormatter,
    TableFormatter,
)


class ReportGenerator:
    """Generate health reports for project dependencies.

    Orchestrates the entire process of resolving dependencies,
    fetching metadata, scanning for vulnerabilities, calculating
    health scores, and formatting output.
    """

    def __init__(
        self,
        github_token: str | None = None,
        cache_ttl: int = 3600,
        use_cache: bool = True,
    ):
        """Initialize the report generator.

        Args:
            github_token: Optional GitHub API token for higher rate limits.
            cache_ttl: Cache time-to-live in seconds.
            use_cache: Whether to use caching.
        """
        self.github_token = github_token
        self.cache_ttl = cache_ttl
        self.use_cache = use_cache

        self.resolver = DependencyResolver()
        self.calculator = HealthCalculator()

        if use_cache:
            self.cache = CacheLayer(default_ttl=cache_ttl)
        else:
            self.cache = None

        # Formatters
        self.formatters: dict[str, Formatter] = {
            "json": JSONFormatter(),
            "markdown": MarkdownFormatter(),
            "table": TableFormatter(),
        }

    async def generate(
        self,
        project_path: Path,
        output_format: str = "table",
        output_path: Path | None = None,
    ) -> tuple[list[DependencyReport], str]:
        """Generate a health report for a project.

        Args:
            project_path: Path to project root or dependency file.
            output_format: Output format ('json', 'markdown', 'table').
            output_path: Optional path to write output file.

        Returns:
            Tuple of (list of DependencyReport, formatted output string).
        """
        # Resolve dependencies
        packages = self.resolver.resolve(project_path)

        if not packages:
            return [], "No dependencies found."

        # Generate reports for all packages
        reports = await self.generate_reports(packages)

        # Format output
        formatted = self.format_reports(reports, output_format)

        # Write to file if requested
        if output_path:
            output_path.write_text(formatted)

        return reports, formatted

    async def generate_reports(
        self,
        packages: list[PackageIdentifier],
    ) -> list[DependencyReport]:
        """Generate health reports for a list of packages.

        Args:
            packages: List of packages to analyze.

        Returns:
            List of DependencyReport objects.
        """
        async with aiohttp.ClientSession() as session:
            pypi_client = PyPIClient(session, cache=self.cache)
            github_client = GitHubClient(session, token=self.github_token, cache=self.cache)
            vuln_scanner = VulnerabilityScanner(session, cache=self.cache)

            # Fetch data for all packages concurrently
            tasks = [
                self._generate_single_report(
                    pkg,
                    pypi_client,
                    github_client,
                    vuln_scanner,
                )
                for pkg in packages
            ]

            reports = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and return valid reports
            valid_reports = []
            for report in reports:
                if isinstance(report, DependencyReport):
                    valid_reports.append(report)
                elif isinstance(report, Exception):
                    # Log or handle the exception
                    pass

            return valid_reports

    async def _generate_single_report(
        self,
        package: PackageIdentifier,
        pypi_client: PyPIClient,
        github_client: GitHubClient,
        vuln_scanner: VulnerabilityScanner,
    ) -> DependencyReport:
        """Generate a health report for a single package.

        Args:
            package: Package to analyze.
            pypi_client: PyPI client instance.
            github_client: GitHub client instance.
            vuln_scanner: Vulnerability scanner instance.

        Returns:
            DependencyReport for the package.
        """
        # Check cache first
        cache_key = CacheLayer.make_key("report", package.name, package.version or "latest")
        if self.cache:
            cached = self.cache.get_value(cache_key)
            if cached:
                # Reconstruct report from cached data
                # For simplicity, we skip this in MVP and always fetch fresh data
                pass

        # Fetch PyPI metadata
        pypi_metadata = None
        try:
            pypi_metadata = await pypi_client.get_package_info(
                package.name,
                package.version,
            )
            # Also fetch download stats from pypistats.org
            if pypi_metadata:
                downloads = await pypi_client.get_download_stats(package.name)
                # Update the metadata object with real download count
                pypi_metadata.downloads_last_month = downloads

                # IMPORTANT: Update package version from PyPI if not specified
                # This enables accurate open vs fixed vulnerability detection
                if not package.version and pypi_metadata.version:
                    package = PackageIdentifier(
                        name=package.name,
                        version=pypi_metadata.version,
                        extras=package.extras,
                    )
        except Exception:
            pass

        # Fetch repository metadata if available
        repo_metadata = None
        if pypi_metadata and pypi_metadata.repository_url:
            repo_url = pypi_metadata.repository_url
            if "github.com" in repo_url:
                try:
                    owner, repo = github_client.extract_repo_from_url(repo_url)
                    repo_metadata = await github_client.get_repository(owner, repo)
                except Exception:
                    pass

        # Scan for vulnerabilities
        vulnerabilities = []
        try:
            vulnerabilities = await vuln_scanner.scan_package(package)
        except Exception:
            pass

        # Calculate health score
        health = self.calculator.calculate(
            pypi_metadata,
            repo_metadata,
            vulnerabilities,
        )

        # Check for available updates
        update_available = None
        if pypi_metadata and package.version:
            if package.version != pypi_metadata.version:
                update_available = pypi_metadata.version

        # Build the report
        report = DependencyReport(
            package=package,
            health=health,
            pypi=pypi_metadata,
            repository=repo_metadata,
            update_available=update_available,
            is_direct=True,
        )

        # Cache the result
        if self.cache:
            try:
                self.cache.set(cache_key, report.to_dict(), self.cache_ttl)
            except Exception:
                pass

        return report

    async def check_package(
        self,
        name: str,
        version: str | None = None,
    ) -> DependencyReport:
        """Check health of a single package.

        Args:
            name: Package name.
            version: Optional specific version.

        Returns:
            DependencyReport for the package.
        """
        package = PackageIdentifier(name=name, version=version)
        reports = await self.generate_reports([package])

        if not reports:
            # Return a minimal report indicating failure
            from dhm.core.models import HealthGrade, MaintenanceStatus

            return DependencyReport(
                package=package,
                health=HealthScore(
                    overall=0,
                    grade=HealthGrade.F,
                    maintenance_status=MaintenanceStatus.ABANDONED,
                    risk_factors=["Package not found or unavailable"],
                ),
            )

        return reports[0]

    def format_reports(
        self,
        reports: list[DependencyReport],
        format_name: str = "table",
    ) -> str:
        """Format reports using the specified formatter.

        Args:
            reports: List of DependencyReport objects.
            format_name: Name of formatter to use.

        Returns:
            Formatted string output.

        Raises:
            ValueError: If format_name is not recognized.
        """
        formatter = self.formatters.get(format_name)
        if not formatter:
            raise ValueError(
                f"Unknown format: {format_name}. "
                f"Available formats: {list(self.formatters.keys())}"
            )

        return formatter.format(reports)

    def add_formatter(self, name: str, formatter: Formatter) -> None:
        """Add a custom formatter.

        Args:
            name: Name for the formatter.
            formatter: Formatter instance.
        """
        self.formatters[name] = formatter
