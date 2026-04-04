## 1. Configuration

- [x] 1.1 Add `[project.optional-dependencies]` section with `dev = ["ruff>=0.4"]` to `pyproject.toml`
- [x] 1.2 Add `[tool.ruff]` section with `target-version = "py310"` and `line-length = 88` to `pyproject.toml`
- [x] 1.3 Add `[tool.ruff.lint]` section with `select = ["E", "F", "I", "UP", "B"]` to `pyproject.toml`

## 2. Fix Existing Violations

- [x] 2.1 Install dev dependencies and run `ruff check .` to identify violations
- [x] 2.2 Fix all lint violations in `src/` and `tests/`

## 3. Verification

- [x] 3.1 Run `ruff check .` and confirm zero violations
