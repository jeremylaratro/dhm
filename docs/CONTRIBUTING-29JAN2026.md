# Contributing to Dependency Health Monitor

Thank you for your interest in contributing to DHM! This guide will help you get started with development, testing, and submitting contributions.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Quality Standards](#code-quality-standards)
- [Testing](#testing)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)
- [Getting Help](#getting-help)

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A GitHub account (for contributing)

### 1. Clone the Repository

```bash
git clone https://github.com/jeremylaratro/dhm.git
cd dhm
```

### 2. Create a Virtual Environment

Using `venv` (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Or using `uv` (faster):

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Using pip
pip install -e ".[dev]"

# Or using uv (faster)
uv pip install -e ".[dev]"
```

This installs:
- **Runtime dependencies**: `click`, `rich`, `aiohttp`, `tomli`
- **Development tools**: `pytest`, `pytest-asyncio`, `pytest-cov`, `aioresponses`, `mypy`, `ruff`

### 4. Verify Installation

```bash
# Run tests to ensure everything is working
pytest

# Check that the CLI is installed
dhm --version

# Try a health check
dhm check requests
```

### 5. Optional: GitHub Token for Testing

DHM uses GitHub's API to collect repository metrics. Without authentication, you're limited to 60 requests/hour. To increase this to 5,000/hour:

```bash
# Create a GitHub Personal Access Token (no scopes needed)
# https://github.com/settings/tokens

export GITHUB_TOKEN="your_token_here"

# Or add to .env file (gitignored)
echo "GITHUB_TOKEN=your_token_here" > .env
```

---

## Project Structure

Understanding the codebase layout helps you know where to make changes:

```
dependency_health_monitor/
├── src/dhm/                    # Main package source
│   ├── __init__.py            # Public API exports
│   ├── api.py                 # High-level async/sync API functions
│   ├── analyzers/             # Alternative package analysis
│   │   └── alternatives.py
│   ├── cache/                 # SQLite caching layer
│   │   └── sqlite.py
│   ├── cli/                   # Command-line interface
│   │   ├── main.py           # CLI commands (scan, check, etc.)
│   │   └── output.py         # Rich terminal formatting
│   ├── collectors/            # Data collection from external APIs
│   │   ├── base.py           # Base collector interface
│   │   ├── github.py         # GitHub API integration
│   │   ├── pypi.py           # PyPI/pypistats.org integration
│   │   └── vulnerability.py  # OSV vulnerability database
│   ├── core/                  # Core business logic
│   │   ├── calculator.py     # Health score calculation engine
│   │   ├── exceptions.py     # Custom exception classes
│   │   ├── models.py         # Data models (Pydantic/dataclasses)
│   │   └── resolver.py       # Dependency resolution (requirements.txt, pyproject.toml)
│   └── reports/               # Report generation and formatting
│       ├── generator.py      # DependencyReport creation
│       └── formatters.py     # Output formats (table, JSON, markdown)
│
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest fixtures and test data
│   ├── test_calculator.py    # Health calculation tests
│   ├── test_models.py        # Data model validation tests
│   └── test_resolver.py      # Dependency resolution tests
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE-26JAN2026.md
│   ├── ROADMAP-26JAN2026.md
│   ├── SCORING_ALGORITHM_ANALYSIS-27JAN2026.md
│   └── SCORING_CRITERIA-27JAN2026.md
│
├── pyproject.toml            # Build configuration, dependencies, tool settings
├── CHANGELOG.md              # Version history (Keep a Changelog format)
├── README.md                 # User-facing documentation
└── LICENSE                   # MIT License
```

### Module Responsibilities

#### Where to Add Features

| Feature Type | Location | Example |
|--------------|----------|---------|
| New data source (e.g., GitLab API) | `src/dhm/collectors/` | Add `gitlab.py` with `BaseCollector` interface |
| Health score tweaks | `src/dhm/core/calculator.py` | Modify `HealthCalculator` weights or algorithms |
| New CLI command | `src/dhm/cli/main.py` | Add new Click command function |
| Alternative package logic | `src/dhm/analyzers/alternatives.py` | Update `AlternativeAnalyzer` |
| Output format (e.g., XML) | `src/dhm/reports/formatters.py` | Add new `format_xml()` function |
| Cache backends (e.g., Redis) | `src/dhm/cache/` | Implement `BaseCache` interface |

---

## Code Quality Standards

DHM uses automated tools to maintain code quality. All checks must pass before merging.

### Linting with Ruff

We use [Ruff](https://docs.astral.sh/ruff/) for fast Python linting and formatting:

```bash
# Check for linting errors
ruff check .

# Auto-fix issues where possible
ruff check --fix .

# Format code
ruff format .
```

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```

Selected rules:
- **E**: PEP 8 errors
- **F**: Pyflakes (unused imports, undefined names)
- **I**: Import sorting (isort)
- **N**: PEP 8 naming conventions
- **W**: PEP 8 warnings
- **UP**: pyupgrade (modern Python syntax)

### Type Checking with mypy

We encourage type hints for new code:

```bash
mypy src/dhm
```

**Configuration** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true  # For third-party libraries without stubs
```

**Type Hints Best Practices:**
- Use type hints for function signatures
- Use `typing` module for complex types (`Optional`, `Union`, `Dict`, etc.)
- Async functions return `Coroutine` or use `async def`

Example:
```python
from typing import Optional
from dhm.core.models import DependencyReport

async def check(package: str, version: Optional[str] = None) -> DependencyReport:
    """Check health of a single package."""
    ...
```

### Code Style Guidelines

1. **Line Length**: Max 100 characters
2. **Imports**: Sorted automatically by Ruff (stdlib → third-party → local)
3. **Naming**:
   - Functions/variables: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Private members: `_leading_underscore`
4. **Docstrings**: Use Google-style docstrings for public functions/classes
5. **Async/Await**: Prefer `async`/`await` over callbacks for async code

---

## Testing

DHM uses `pytest` with async support and coverage tracking.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=dhm --cov-report=term-missing

# Run specific test file
pytest tests/test_calculator.py

# Run specific test function
pytest tests/test_calculator.py::TestHealthCalculator::test_default_weights

# Run tests matching a pattern
pytest -k "security"

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Configuration

**`pyproject.toml`**:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"           # Automatically detect and run async tests
testpaths = ["tests"]           # Look for tests in tests/ directory
addopts = "-v --cov=dhm --cov-report=term-missing"
```

### Test Organization

- **`tests/conftest.py`**: Shared fixtures (sample data, mock API responses, temp files)
- **`tests/test_*.py`**: Test modules mirroring source structure
- **Test Classes**: Group related tests using `TestClassName` convention
- **Test Functions**: Descriptive names like `test_calculate_with_vulnerabilities`

### Writing Tests

#### 1. Use Fixtures for Test Data

```python
def test_health_score_with_vulnerabilities(calculator, sample_vulnerability):
    """Test that vulnerabilities reduce security score."""
    score = calculator._calculate_security_score([sample_vulnerability])
    assert score < 100.0
```

#### 2. Test Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_check_package_async():
    """Test async package health check."""
    from dhm import check
    report = await check("requests")
    assert report.package.name == "requests"
```

#### 3. Mock External APIs

```python
from aioresponses import aioresponses

@pytest.mark.asyncio
async def test_pypi_collector_with_mock():
    """Test PyPI collector with mocked HTTP responses."""
    with aioresponses() as mock:
        mock.get(
            "https://pypi.org/pypi/requests/json",
            payload={"info": {"name": "requests", "version": "2.28.0"}},
        )

        from dhm.collectors.pypi import PyPICollector
        collector = PyPICollector()
        metadata = await collector.get_metadata("requests")
        assert metadata.name == "requests"
```

#### 4. Test Edge Cases

```python
def test_calculate_with_no_metadata(calculator):
    """Calculator should handle missing metadata gracefully."""
    score = calculator.calculate(pypi=None, repo=None, vulnerabilities=[])
    assert 0 <= score.overall <= 100
    assert score.grade is not None
```

### Coverage Expectations

- Aim for **80%+ coverage** on new code
- Focus on critical paths: health calculation, vulnerability detection, CLI commands
- Don't obsess over 100% coverage; some error paths are hard to test

---

## Making Changes

### Branch Naming

Use descriptive branch names with prefixes:

- `feat/add-gitlab-support` - New features
- `fix/cache-invalidation-bug` - Bug fixes
- `refactor/simplify-calculator` - Code refactoring
- `docs/update-contributing-guide` - Documentation
- `test/add-vulnerability-tests` - Test improvements
- `chore/upgrade-dependencies` - Maintenance tasks

### Commit Message Format

DHM follows [Conventional Commits](https://www.conventionalcommits.org/) for clear, parseable commit history.

**Format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature (triggers MINOR version bump)
- `fix`: Bug fix (triggers PATCH version bump)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code restructuring without behavior change
- `test`: Adding/updating tests
- `chore`: Build process, dependencies, CI/CD
- `ci`: Continuous integration changes
- `perf`: Performance improvements

**Examples:**

```bash
# Good commit messages
git commit -m "feat: Add GitLab repository collector"
git commit -m "fix: Handle rate limit errors in GitHub API"
git commit -m "docs: Add examples for synchronous API usage"
git commit -m "test: Add edge cases for vulnerability version parsing"
git commit -m "chore: Upgrade aiohttp to 3.9.0"

# Bad commit messages (avoid these)
git commit -m "updates"
git commit -m "fixed stuff"
git commit -m "WIP"
```

**Breaking Changes:**

```bash
git commit -m "feat!: Change health score weights

BREAKING CHANGE: Security weight increased from 30% to 35%.
This will change health scores for all packages."
```

### Update CHANGELOG.md

**MANDATORY**: Every code change must update the `CHANGELOG.md` file.

Add your change under the `## [Unreleased]` section:

```markdown
## [Unreleased]

### Added
- GitLab repository collector for projects hosted on GitLab.com
- `--gitlab-token` CLI option for authenticated API access

### Changed
- Increased GitHub API timeout from 10s to 30s for large repositories

### Fixed
- Cache invalidation bug when package version changes
- Division by zero error in popularity score calculation

### Removed
```

**Categories:**
- **Added**: New features, capabilities, or files
- **Changed**: Modifications to existing functionality
- **Fixed**: Bug fixes
- **Removed**: Deleted features or files
- **Deprecated**: Features marked for future removal
- **Security**: Security-related changes

---

## Pull Request Process

### 1. Prepare Your Changes

Before opening a PR:

```bash
# Ensure tests pass
pytest

# Run linting
ruff check .
ruff format .

# Check types (optional but recommended)
mypy src/dhm

# Update CHANGELOG.md
# Edit CHANGELOG.md and add your changes under [Unreleased]
```

### 2. Push Your Branch

```bash
git push origin feat/your-feature-name
```

### 3. Open a Pull Request

Go to the [GitHub repository](https://github.com/jeremylaratro/dhm) and click "New Pull Request".

**PR Title**: Use the same format as commit messages:
```
feat: Add GitLab repository collector
fix: Handle rate limit errors in GitHub API
docs: Update contributing guide with testing examples
```

**PR Description Template**:

```markdown
## Summary

Brief description of what this PR does and why.

## Changes

- Added `GitLabCollector` class to `src/dhm/collectors/gitlab.py`
- Updated `RepositoryCollector` to support both GitHub and GitLab
- Added tests in `tests/test_gitlab_collector.py`

## Testing

- [ ] All existing tests pass
- [ ] Added new tests for GitLab collector
- [ ] Manually tested with `dhm check <gitlab-package>`

## Checklist

- [ ] Code follows Ruff style guidelines
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or documented in CHANGELOG)

## Related Issues

Closes #42
```

### 4. Review Process

- **Automated Checks**: CI will run tests and linting automatically
- **Code Review**: A maintainer will review your code
- **Feedback**: Address any requested changes
- **Approval**: Once approved, a maintainer will merge your PR

### 5. After Merge

Your changes will appear in the next release! Thank you for contributing!

---

## Release Process

**For Maintainers Only**

DHM uses [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking changes (incompatible API changes)
- **MINOR** (0.X.0): New features (backward compatible)
- **PATCH** (0.0.X): Bug fixes (backward compatible)

### Version Numbering Examples

| Change | Old Version | New Version |
|--------|-------------|-------------|
| Bug fix | 0.1.0 | 0.1.1 |
| New feature (no breaking changes) | 0.1.1 | 0.2.0 |
| Breaking API change | 0.2.0 | 1.0.0 |

### Release Steps

#### 1. Determine Version Number

Based on changes in `CHANGELOG.md` under `[Unreleased]`:

- **BREAKING CHANGE** or `feat!:` commits → MAJOR bump
- `feat:` commits → MINOR bump
- `fix:`, `docs:`, `chore:` commits → PATCH bump

#### 2. Update Version Files

```bash
# Example: Releasing 0.2.0

# Update pyproject.toml
sed -i 's/version = "0.1.0"/version = "0.2.0"/' pyproject.toml

# Update src/dhm/__init__.py
sed -i 's/__version__ = "0.1.0"/__version__ = "0.2.0"/' src/dhm/__init__.py

# Verify changes
grep version pyproject.toml
grep __version__ src/dhm/__init__.py
```

#### 3. Update CHANGELOG.md

Move `[Unreleased]` entries to new version section with release date:

```markdown
## [Unreleased]

### Added

### Changed

### Fixed

### Removed

---

## [0.2.0] - 2026-01-29

### Added
- GitLab repository collector for projects hosted on GitLab.com
- `--gitlab-token` CLI option for authenticated API access

### Changed
- Increased GitHub API timeout from 10s to 30s

### Fixed
- Cache invalidation bug when package version changes
```

#### 4. Commit Release Changes

```bash
git add pyproject.toml src/dhm/__init__.py CHANGELOG.md
git commit -m "chore: Release v0.2.0"
```

#### 5. Create Git Tag

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
```

#### 6. Push Changes and Tag

```bash
git push origin main
git push origin v0.2.0
```

#### 7. Create GitHub Release

1. Go to https://github.com/jeremylaratro/dhm/releases/new
2. Select tag: `v0.2.0`
3. Release title: `v0.2.0`
4. Description: Copy relevant section from CHANGELOG.md
5. Click "Publish release"

#### 8. Automated PyPI Publishing

The GitHub Actions workflow (`.github/workflows/publish.yml`) will automatically:

1. Detect the new release
2. Build the distribution (`python -m build`)
3. Publish to PyPI using [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

**No manual `twine upload` needed!**

#### 9. Verify Publication

```bash
# Wait 2-5 minutes for PyPI to index

# Check PyPI page
open https://pypi.org/project/dependency-health-monitor/

# Test installation in clean environment
python -m venv test-env
source test-env/bin/activate
pip install dependency-health-monitor==0.2.0
dhm --version  # Should show 0.2.0
```

### Manual PyPI Publishing (Fallback)

If automated publishing fails:

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Check build artifacts
ls -lh dist/
# dependency_health_monitor-0.2.0-py3-none-any.whl
# dependency_health_monitor-0.2.0.tar.gz

# Upload to PyPI
twine upload dist/dependency-health-monitor-0.2.0*

# Enter PyPI credentials when prompted
```

---

## Getting Help

### Resources

- **Documentation**: Check `docs/` directory
  - `ARCHITECTURE-26JAN2026.md`: System design and component interactions
  - `SCORING_CRITERIA-27JAN2026.md`: Health scoring algorithm details
  - `ROADMAP-26JAN2026.md`: Future plans and priorities

- **Code Examples**: See `README.md` for API usage examples

- **Issues**: Browse [existing issues](https://github.com/jeremylaratro/dhm/issues) or create a new one

### Questions and Discussions

- **Bug Reports**: [Open an issue](https://github.com/jeremylaratro/dhm/issues/new) with:
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (Python version, OS)
  - Relevant logs or error messages

- **Feature Requests**: [Open an issue](https://github.com/jeremylaratro/dhm/issues/new) with:
  - Use case description
  - Proposed solution (if you have one)
  - Alternative approaches considered

- **General Questions**: Open a discussion or ask in an issue

### Local Development Tips

#### Reset Development Environment

```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info

# Clean cache
rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/

# Remove coverage data
rm -f .coverage

# Reinstall in development mode
pip install -e ".[dev]"
```

#### Debug CLI Commands

```bash
# Run CLI in development mode with verbose logging
python -m dhm --help
python -m dhm check requests

# Or directly invoke the entry point
python src/dhm/__main__.py check requests
```

#### Inspect Cache Database

```bash
# SQLite cache is stored at ~/.cache/dhm/cache.db (Linux/macOS)
# or %LOCALAPPDATA%\dhm\cache.db (Windows)

sqlite3 ~/.cache/dhm/cache.db

# View cached entries
sqlite> SELECT key, expires_at FROM cache_entries LIMIT 10;

# Clear cache manually
sqlite> DELETE FROM cache_entries;
```

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the project and community
- Assume good intentions

---

## License

By contributing to DHM, you agree that your contributions will be licensed under the MIT License.
