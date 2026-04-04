## Context

The engraft project is a Python CLI tool built with Hatch and configured via `pyproject.toml`. It currently has no linting or static analysis tooling. The codebase targets Python 3.10+.

## Goals / Non-Goals

**Goals:**
- Configure Ruff as a linter with a moderate rule set
- Add Ruff as an optional dev dependency
- Fix any existing lint violations in the codebase

**Non-Goals:**
- Code formatting (no `ruff format`)
- Pre-commit hooks
- CI integration (deferred to a future change)
- Aggressive or exhaustive rule sets

## Decisions

### Use Ruff over flake8/pylint
Ruff replaces multiple tools (flake8, isort, pyflakes, pycodestyle, bugbear) in a single fast binary. No plugin management needed. Configures in `pyproject.toml` alongside existing project config.

### Moderate rule set: E, F, I, UP, B
- `E` (pycodestyle) + `F` (pyflakes): baseline correctness checks
- `I` (isort): consistent import ordering
- `UP` (pyupgrade): modernize syntax for Python 3.10+
- `B` (flake8-bugbear): catch common pitfalls

This balances signal-to-noise — catches real issues without being noisy about stylistic opinions.

### Dev dependency via optional-dependencies
Using `[project.optional-dependencies] dev = ["ruff>=0.4"]` keeps the linter out of production installs. Installed via `pip install -e ".[dev]"`.

### Configuration in pyproject.toml
No separate config files. `[tool.ruff]` and `[tool.ruff.lint]` sections keep everything in one place.

## Risks / Trade-offs

- [Existing code violations] → Fix all violations as part of this change. The codebase is small (~18 files), so this is low effort.
- [Ruff version churn] → Pinning `>=0.4` gives flexibility while ensuring a stable feature set.
