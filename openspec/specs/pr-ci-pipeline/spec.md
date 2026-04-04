### Requirement: PR workflow trigger
The workflow SHALL trigger on pull requests targeting the `main` branch.

#### Scenario: PR opened to main
- **WHEN** a pull request is opened against `main`
- **THEN** the CI pipeline runs lint and test jobs

#### Scenario: PR opened to non-main branch
- **WHEN** a pull request is opened against a branch other than `main`
- **THEN** the CI pipeline SHALL NOT trigger

### Requirement: Lint job runs ruff checks
The lint job SHALL run `ruff check .` and `ruff format --check .` to validate code quality and formatting.

#### Scenario: Lint passes
- **WHEN** code passes both `ruff check` and `ruff format --check`
- **THEN** the lint job succeeds and test jobs are unblocked

#### Scenario: Lint fails on check
- **WHEN** code has ruff lint violations
- **THEN** the lint job fails and test jobs are skipped

#### Scenario: Lint fails on format
- **WHEN** code has formatting issues detected by `ruff format --check`
- **THEN** the lint job fails and test jobs are skipped

### Requirement: Test job runs pytest across Python versions
The test job SHALL run `pytest` in a matrix of Python versions: 3.10, 3.12, and 3.13.

#### Scenario: Tests pass on all versions
- **WHEN** all tests pass on Python 3.10, 3.12, and 3.13
- **THEN** the test job succeeds for all matrix entries

#### Scenario: Tests fail on one version
- **WHEN** tests fail on one Python version but pass on others
- **THEN** the test job fails for that matrix entry

### Requirement: Test job depends on lint
The test job SHALL declare a dependency on the lint job via `needs: lint`.

#### Scenario: Lint fails
- **WHEN** the lint job fails
- **THEN** all test matrix jobs are skipped

#### Scenario: Lint passes
- **WHEN** the lint job succeeds
- **THEN** test matrix jobs proceed to run

### Requirement: Pytest in dev dependencies
The `pyproject.toml` SHALL include `pytest>=7.0` in the `[project.optional-dependencies] dev` list.

#### Scenario: Dev install includes pytest
- **WHEN** a developer runs `pip install -e ".[dev]"`
- **THEN** pytest is installed alongside ruff
