## MODIFIED Requirements

### Requirement: Lint job runs ruff checks
The Python lint job SHALL run `ruff check .` and `ruff format --check .` from inside the `python/` directory to validate code quality and formatting for the Python implementation.

#### Scenario: Lint passes
- **WHEN** Python code passes both `ruff check` and `ruff format --check` in `python/`
- **THEN** the Python lint job succeeds and the Python test job is unblocked

#### Scenario: Lint fails on check
- **WHEN** Python code has ruff lint violations
- **THEN** the Python lint job fails and the Python test job is skipped

#### Scenario: Lint fails on format
- **WHEN** Python code has formatting issues detected by `ruff format --check`
- **THEN** the Python lint job fails and the Python test job is skipped

### Requirement: Test job runs pytest across Python versions
The Python test job SHALL install the Python implementation with `pip install -e .[dev]` from inside the `python/` directory and run `pytest` in a matrix of Python versions: 3.10, 3.12, and 3.13.

#### Scenario: Tests pass on all versions
- **WHEN** all Python tests pass on Python 3.10, 3.12, and 3.13
- **THEN** the Python test job succeeds for all matrix entries

#### Scenario: Tests fail on one version
- **WHEN** Python tests fail on one Python version but pass on others
- **THEN** the Python test job fails for that matrix entry

### Requirement: Test job depends on lint
The Python test job SHALL declare a dependency on the Python lint job via `needs: <python-lint-job-id>`, and the TypeScript test job SHALL declare a dependency on the TypeScript lint job via `needs: <typescript-lint-job-id>`.

#### Scenario: Python lint fails
- **WHEN** the Python lint job fails
- **THEN** all Python test matrix jobs are skipped

#### Scenario: Python lint passes
- **WHEN** the Python lint job succeeds
- **THEN** Python test matrix jobs proceed to run

#### Scenario: TypeScript lint fails
- **WHEN** the TypeScript lint job fails
- **THEN** the TypeScript test job is skipped

#### Scenario: TypeScript lint passes
- **WHEN** the TypeScript lint job succeeds
- **THEN** the TypeScript test job proceeds to run

### Requirement: Pytest in dev dependencies
The `python/pyproject.toml` SHALL include `pytest>=7.0` in the `[project.optional-dependencies] dev` list.

#### Scenario: Dev install includes pytest
- **WHEN** a developer runs `pip install -e .[dev]` from inside `python/`
- **THEN** pytest is installed alongside ruff

## ADDED Requirements

### Requirement: TypeScript lint job runs type check
The TypeScript lint job SHALL run `npm ci` followed by `npm run lint` (which invokes `tsc --noEmit`) from inside the `typescript/` directory to validate type correctness.

#### Scenario: Type check passes
- **WHEN** TypeScript code passes `tsc --noEmit`
- **THEN** the TypeScript lint job succeeds and the TypeScript test job is unblocked

#### Scenario: Type check fails
- **WHEN** TypeScript code has type errors detected by `tsc --noEmit`
- **THEN** the TypeScript lint job fails and the TypeScript test job is skipped

### Requirement: TypeScript test job runs build and vitest
The TypeScript test job SHALL run `npm ci`, `npm run build`, and `npm test` from inside the `typescript/` directory on Node.js 20.

#### Scenario: Build and tests pass
- **WHEN** `npm run build` produces `dist/cli.js` and `npm test` reports all vitest tests passing
- **THEN** the TypeScript test job succeeds

#### Scenario: Build fails
- **WHEN** `npm run build` fails
- **THEN** the TypeScript test job fails without running vitest

#### Scenario: A vitest test fails
- **WHEN** any vitest test fails
- **THEN** the TypeScript test job fails

### Requirement: E2E parity job runs shared harness against both implementations
The e2e parity job SHALL install the Python CLI (`pip install -e ./python`), build the TypeScript CLI (`npm ci` and `npm run build` inside `typescript/`), install the e2e harness dependencies, and run `pytest e2e/` from the repo root so every fixture executes against both implementations in a single job.

#### Scenario: Both implementations agree on every fixture
- **WHEN** every fixture under `e2e/fixtures/` produces the expected output for both the Python and TypeScript CLIs
- **THEN** the e2e parity job succeeds

#### Scenario: Implementations disagree on a fixture
- **WHEN** any fixture produces the expected output for one implementation but not the other
- **THEN** the e2e parity job fails

#### Scenario: Either CLI fails to install or build
- **WHEN** `pip install -e ./python` or `npm run build` in `typescript/` fails
- **THEN** the e2e parity job fails before reaching `pytest`

### Requirement: E2E parity job depends on both language test jobs
The e2e parity job SHALL declare dependencies on both the Python test job and the TypeScript test job via `needs: [<python-test-job-id>, <typescript-test-job-id>]`.

#### Scenario: Python test job fails
- **WHEN** the Python test job fails
- **THEN** the e2e parity job is skipped

#### Scenario: TypeScript test job fails
- **WHEN** the TypeScript test job fails
- **THEN** the e2e parity job is skipped

#### Scenario: Both test jobs succeed
- **WHEN** both the Python and TypeScript test jobs succeed
- **THEN** the e2e parity job runs
