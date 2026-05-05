## ADDED Requirements

### Requirement: Implementation-parametrized test harness
The e2e harness SHALL run every test scenario once per implementation. It SHALL expose a pytest fixture that resolves to a subprocess-invocable CLI for the selected implementation. The fixture SHALL be parametrized over `["python", "typescript"]`.

#### Scenario: Tests run against both implementations
- **WHEN** a contributor runs `pytest e2e/` and one test scenario is defined
- **THEN** the test executes twice — once with the Python CLI and once with the TypeScript CLI
- **AND** pytest's output identifies which implementation each run targeted

### Requirement: CLI discovery and bootstrap failure
The harness SHALL verify at test-collection time that the selected implementation's CLI is invocable. If the Python implementation is not installed or the TypeScript build artifact is missing, the harness SHALL fail loudly with a clear error message naming the missing prerequisite and the command to run.

#### Scenario: TypeScript build missing
- **WHEN** a contributor runs `pytest e2e/` without having run `npm run build` in `typescript/`
- **THEN** pytest fails with an error message naming the missing `typescript/dist/cli.js` and pointing at the build command

#### Scenario: Python package not installed
- **WHEN** a contributor runs `pytest e2e/` without having run `pip install -e python/`
- **THEN** pytest fails with an error message naming the missing `engraft` command and pointing at the install command

### Requirement: Fixture scenario directory format
E2E test scenarios SHALL live under `e2e/fixtures/<scenario-name>/` with the following structure:
- `template.yaml` — the engraft template
- `values.yaml` — the values file
- `input/` — the initial project directory state that engraft is run against
- `expected/` — the expected post-apply project directory state

#### Scenario: Scenario loaded
- **WHEN** the harness runs a scenario named `minimal-json`
- **THEN** it reads `e2e/fixtures/minimal-json/template.yaml` and `values.yaml` as the CLI inputs
- **AND** it copies `input/` into a temporary working directory before invoking the CLI
- **AND** it compares the post-apply working directory against `expected/` using semantic comparators

### Requirement: Semantic comparators by file extension
The harness SHALL compare each file in `expected/` against its counterpart in the post-apply working directory using a comparator selected by file extension:
- `.json`: parse both via `json.loads` and assert deep structural equality
- `.yaml` / `.yml`: parse both via `yaml.safe_load` and assert deep structural equality
- `.html`: parse both via `lxml.html.fromstring`, then compare structurally — same tag names, attribute sets (order-independent), text content (whitespace-collapsed between tags), and document order; DOCTYPE presence preserved
- any other extension: compare as text, normalizing line endings to `\n`

#### Scenario: JSON files compared structurally
- **WHEN** the Python implementation produces `{"a": 1, "b": 2}` and the TypeScript implementation produces `{"b": 2, "a": 1}` as JSON output
- **THEN** the JSON comparator reports equality (key order is not meaningful in a JSON object)

#### Scenario: HTML files compared structurally
- **WHEN** the Python implementation produces `<p class="x" id="y">hi</p>` and the TypeScript implementation produces `<p id="y" class="x">hi</p>`
- **THEN** the HTML comparator reports equality (attribute order not meaningful)

#### Scenario: Text files compared byte-exact
- **WHEN** engraft produces a `.conf` file (no format-specific comparator)
- **THEN** the harness compares as text after normalizing line endings to `\n`

### Requirement: Isolated per-test working directory
Each scenario SHALL run against a fresh copy of `input/` in a pytest-provided temporary directory. The harness SHALL NOT mutate the fixtures under `e2e/fixtures/`.

#### Scenario: Fixture files unchanged after run
- **WHEN** the e2e suite completes (pass or fail)
- **THEN** no files under `e2e/fixtures/` are modified

### Requirement: Behavioral contract ownership
The e2e scenarios SHALL be the authoritative behavioral contract for user-visible engraft behavior. Implementation-specific unit tests SHALL cover internal concerns (registry mechanics, parser edge cases, impl-specific helpers) but SHALL NOT be the sole source of truth for any user-visible feature.

#### Scenario: New feature requires an e2e scenario
- **WHEN** a contributor adds a user-visible feature in either implementation
- **THEN** they add or extend an e2e scenario covering the feature's observable behavior
- **AND** unit tests in the implementation cover internal details as needed
