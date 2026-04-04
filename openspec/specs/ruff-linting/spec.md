## ADDED Requirements

### Requirement: Ruff dev dependency
The project SHALL declare `ruff>=0.4` as an optional dev dependency in `pyproject.toml` under `[project.optional-dependencies]`.

#### Scenario: Installing dev dependencies
- **WHEN** a developer runs `pip install -e ".[dev]"`
- **THEN** Ruff is installed and the `ruff` command is available

### Requirement: Ruff lint configuration
The project SHALL configure Ruff linting in `pyproject.toml` with target version `py310`, line length `88`, and rule set `["E", "F", "I", "UP", "B"]`.

#### Scenario: Running ruff check
- **WHEN** a developer runs `ruff check .` from the project root
- **THEN** Ruff analyzes all Python files using the configured rule set

#### Scenario: Target version matches project
- **WHEN** Ruff evaluates `UP` (pyupgrade) rules
- **THEN** it SHALL suggest syntax available in Python 3.10+

### Requirement: Clean lint baseline
All existing Python files in `src/` and `tests/` SHALL pass `ruff check` with zero violations after this change is applied.

#### Scenario: No existing violations
- **WHEN** a developer runs `ruff check .` after applying this change
- **THEN** zero lint errors or warnings are reported
