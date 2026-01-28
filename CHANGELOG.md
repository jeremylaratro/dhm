# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

---

## [0.1.0] - 2026-01-27

### Added
- Initial release of Dependency Health Monitor
- Core health scoring with weighted components:
  - Security (35%): Vulnerability detection via OSV database
  - Maintenance (30%): Release frequency, repository activity
  - Community (20%): Contributors, stars, PR merge rates
  - Popularity (15%): Download statistics from pypistats.org
- Base-50 scoring philosophy with logarithmic normalization
- Open vs Fixed vulnerability distinction with version comparison
- License scoring with category detection (permissive, copyleft, weak copyleft)
- Confidence levels (HIGH/MEDIUM/LOW) based on data availability
- SQLite caching layer with configurable TTLs:
  - GitHub data: 24 hours
  - PyPI metadata: 1 hour
  - Download stats: 6 hours
  - Vulnerabilities: 6 hours
- CLI commands:
  - `dhm scan` - Scan project dependencies
  - `dhm check <package>` - Check single package health
  - `dhm alternatives <package>` - Find healthier alternatives
  - `dhm cache` - Manage local cache
- Multiple output formats: table, JSON, markdown
- CI/CD integration with `--fail-on` threshold
- Programmatic Python API for library usage

### Grade Thresholds
- A: >= 85 (Excellent)
- B: >= 75 (Good)
- C: >= 65 (Acceptable)
- D: >= 55 (Concerning)
- F: < 55 (Critical)
