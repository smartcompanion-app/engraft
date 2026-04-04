## Why

The project has no CI pipeline. Linting and testing run only locally, which means issues can slip into `main` via pull requests. A GitHub Actions pipeline ensures code quality gates are enforced automatically before merging.

## What Changes

- Add a GitHub Actions workflow triggered on PRs to `main`
- Run ruff linting and format checking as a gating step
- Run pytest across multiple Python versions (3.10, 3.12, 3.13)
- Add `pytest` to dev dependencies in `pyproject.toml`

## Capabilities

### New Capabilities
- `pr-ci-pipeline`: GitHub Actions workflow for PR validation — linting, format checking, and multi-version testing

### Modified Capabilities

_None_

## Impact

- **New file**: `.github/workflows/pr.yml`
- **Modified file**: `pyproject.toml` (add pytest to dev dependencies)
- **Dependencies**: No new runtime dependencies; pytest added as dev dependency
