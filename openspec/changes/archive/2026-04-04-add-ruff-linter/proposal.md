## Why

The project has no linting setup. Adding Ruff provides automated detection of bugs, style issues, and outdated Python patterns with minimal configuration overhead. Ruff is fast, covers multiple lint categories in a single tool, and configures directly in `pyproject.toml`.

## What Changes

- Add Ruff as a dev dependency in `pyproject.toml`
- Add `[tool.ruff]` and `[tool.ruff.lint]` configuration sections in `pyproject.toml`
- Enable a moderate rule set: `E` (pycodestyle), `F` (pyflakes), `I` (isort), `UP` (pyupgrade), `B` (flake8-bugbear)
- Fix any existing lint violations in the codebase

## Capabilities

### New Capabilities
- `ruff-linting`: Static analysis configuration and integration using Ruff with a moderate rule set

### Modified Capabilities
<!-- None — no existing spec-level behavior changes -->

## Impact

- **Dependencies**: Adds `ruff>=0.4` as an optional dev dependency
- **Config**: Extends `pyproject.toml` with Ruff tool configuration
- **Code**: Existing source files may need minor fixes to pass lint checks (import ordering, unused imports, outdated syntax)
