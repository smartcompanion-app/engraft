## Why

The project has no automated release process. Publishing to PyPI is manual and error-prone, with no guarantee that quality checks pass before a release goes out. A release pipeline triggered by GitHub Releases ensures every published version is linted, tested, and signed.

## What Changes

- Add a GitHub Actions workflow (`release.yml`) triggered on `release: published` events that runs lint/format/test gates, builds the package, and publishes to PyPI via Trusted Publisher OIDC with Sigstore signing.
- Switch from hardcoded version in `pyproject.toml` to `hatch-vcs` so the package version is derived automatically from git tags.
- Add `build` as a build-time or CI dependency for producing sdist and wheel artifacts.

## Capabilities

### New Capabilities
- `release-pipeline`: GitHub Actions workflow for automated quality-gated release and PyPI publishing
- `dynamic-versioning`: Switch to hatch-vcs for git-tag-based version derivation

### Modified Capabilities
- `pr-ci-pipeline`: No requirement change — the release pipeline duplicates the same checks independently

## Impact

- **Files added**: `.github/workflows/release.yml`
- **Files modified**: `pyproject.toml` (versioning config, build dependencies)
- **Dependencies added**: `hatch-vcs` (build-time), `build` (CI-only)
- **External config required**: GitHub environment `pypi` must exist with OIDC trust; Trusted Publisher already configured on pypi.org
