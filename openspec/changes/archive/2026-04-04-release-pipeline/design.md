## Context

The project uses hatchling for building and has an existing PR pipeline (`.github/workflows/pr.yml`) that runs ruff lint, ruff format check, and pytest across Python 3.10/3.12/3.13. There is no release automation — publishing to PyPI is not yet set up. The version is hardcoded as `0.1.0` in `pyproject.toml`.

## Goals / Non-Goals

**Goals:**
- Automate PyPI publishing on every GitHub Release
- Gate releases on the same quality checks as PRs (lint, format, test)
- Use modern PyPI authentication (Trusted Publisher / OIDC) — no stored API tokens
- Sign releases with Sigstore attestations
- Derive package version from git tags via hatch-vcs

**Non-Goals:**
- TestPyPI publishing (not needed, Trusted Publisher is already configured)
- Changelog generation or release notes automation
- Multi-platform wheel builds (pure Python package, universal wheel is sufficient)
- Reusable workflow extraction (duplicating checks is simpler for this project size)

## Decisions

### 1. Trigger: `on: release: types: [published]`
**Rationale**: The user wants to use GitHub's Release UI. This trigger fires when a release is published (which also creates a tag). Preferred over `on: push: tags` because it ties the workflow to an intentional release action, not just any tag push.

### 2. Trusted Publisher with OIDC (no API tokens)
**Rationale**: PyPI's Trusted Publisher feature uses GitHub's OIDC identity provider. The workflow gets a short-lived token automatically — no secrets to rotate or leak. This is PyPI's recommended approach. Requires a GitHub environment named `pypi` with `id-token: write` permission.

### 3. Sigstore signing via `pypa/gh-action-pypi-publish`
**Rationale**: The `pypa/gh-action-pypi-publish` action supports `attestations: true` which generates Sigstore attestations automatically. This provides cryptographic proof that the package was built from this repository. No additional tooling needed.

### 4. hatch-vcs for dynamic versioning
**Rationale**: Eliminates version string duplication between `pyproject.toml` and git tags. The version is the single source of truth from the tag. Requires adding `hatch-vcs` as a build dependency and switching to `dynamic = ["version"]` in `pyproject.toml`. Alternative considered: manual version bumps with a CI validation step — rejected because it adds friction and is error-prone.

### 5. Duplicate quality checks (don't reuse PR workflow)
**Rationale**: The quality gate jobs are small (lint + format + test). Extracting a reusable workflow adds indirection without meaningful DRY benefit at this project size. Duplication keeps the release workflow self-contained and easy to understand.

### 6. Build with `python -m build`
**Rationale**: Standard Python packaging tool that produces both sdist and wheel. Works with hatchling backend. The `build` package is installed in the CI job, not added as a project dependency.

## Risks / Trade-offs

- **[Tag/version mismatch]** → hatch-vcs derives version from tags. If a release is created without a proper `v*` tag prefix, the version may be unexpected. Mitigation: document tag format convention (`vX.Y.Z`).
- **[OIDC trust scope]** → The GitHub environment `pypi` must be correctly configured. If misconfigured, the publish step will fail with an auth error. Mitigation: clear error message from the action; one-time setup already done.
- **[Duplicated CI logic]** → Quality checks exist in both `pr.yml` and `release.yml`. If one is updated, the other may drift. Mitigation: acceptable trade-off for simplicity; both files are small and co-located.
