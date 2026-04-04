## Context

The engraft project currently has ruff configured for linting and pytest for testing, but no CI pipeline. All quality checks depend on developers running them locally. The project targets Python >=3.10 and uses hatchling as build backend.

## Goals / Non-Goals

**Goals:**
- Automatically validate PRs to `main` with linting and tests
- Catch formatting and lint issues before code review
- Verify compatibility across supported Python versions (3.10, 3.12, 3.13)

**Non-Goals:**
- Publishing/release automation
- Coverage reporting or badges
- Deployment pipelines
- Running CI on pushes to non-main branches

## Decisions

### Serial job execution: lint gates tests
Lint and test are separate jobs, but tests depend on lint (`needs: lint`). If linting fails, test jobs are skipped — no point running tests on code that doesn't pass quality checks.

**Alternative considered**: Parallel execution. Rejected because failing fast on lint saves CI minutes and gives clearer feedback.

### Python version matrix: 3.10, 3.12, 3.13
Covers the minimum supported version (3.10), current stable (3.13), and one intermediate (3.12). This catches compatibility issues at both ends without excessive matrix size.

**Alternative considered**: Testing all versions 3.10-3.13. Rejected as 3.11 adds little signal given 3.10 and 3.12 are covered.

### Lint job uses single Python version (3.13)
Ruff output is Python-version-independent (it's a static analyzer configured with `target-version`). Running it once on the latest Python is sufficient.

### pip caching via setup-python
Use the built-in `cache: 'pip'` option in `actions/setup-python` to avoid reinstalling dependencies on every run.

## Risks / Trade-offs

- **[Risk] GitHub Actions runner changes** → Pin action versions to major tags (e.g., `actions/checkout@v4`) for stability while still receiving patches.
- **[Risk] Flaky tests block PRs** → Not mitigated in this change; tests should be deterministic. Address if it becomes an issue.
- **[Trade-off] No 3.11 coverage** → Acceptable given 3.10 and 3.12 bracket it. Can add later if needed.
