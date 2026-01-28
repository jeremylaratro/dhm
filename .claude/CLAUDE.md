# DHM Development Guidelines

## Version Control Requirements

**MANDATORY for all code changes:**

1. **Commit frequently** - After each logical unit of work
2. **Update CHANGELOG.md** - Add entry under `## [Unreleased]` section
3. **Follow Conventional Commits** - Use prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `ci:`, `refactor:`, `test:`

## Release Process

When releasing a new version:

1. Update version in:
   - `pyproject.toml` (`version = "X.Y.Z"`)
   - `src/dhm/__init__.py` (`__version__ = "X.Y.Z"`)

2. Update CHANGELOG.md:
   - Move `[Unreleased]` items to new version section
   - Add release date: `## [X.Y.Z] - YYYY-MM-DD`

3. Commit: `git commit -m "chore: Release vX.Y.Z"`

4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`

5. Push: `git push && git push --tags`

6. Build & Publish:
   ```bash
   python -m build
   twine upload dist/*
   ```

## Semantic Versioning

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## CHANGELOG Entry Format

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Modified behavior description

### Fixed
- Bug fix description

### Removed
- Removed feature description
```
