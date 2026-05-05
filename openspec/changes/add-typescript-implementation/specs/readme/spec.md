## MODIFIED Requirements

### Requirement: Project description section
The Python implementation's README (`python/README.md`) SHALL begin with a one-line description matching the `pyproject.toml` description, followed by a concise explanation of the problem engraft solves (comparison with templating tools, forking, and manual editing).

#### Scenario: Reader understands the purpose
- **WHEN** a user opens `python/README.md`
- **THEN** the first section explains what engraft does and why it exists without requiring them to read source code

### Requirement: Installation instructions
The Python implementation's README (`python/README.md`) SHALL include installation instructions using `pip install engraft`.

#### Scenario: User installs the tool
- **WHEN** a user follows the installation section
- **THEN** they can run `engraft --version` successfully

### Requirement: Quick-start usage example
The Python implementation's README (`python/README.md`) SHALL include a complete quick-start example showing a minimal template file, a minimal values file, and the `engraft apply` command.

#### Scenario: User runs the quick-start example
- **WHEN** a user creates the example template and values files from the README and runs the shown command
- **THEN** the target file is modified as described in the example

### Requirement: Action reference for all four action types
The Python implementation's README (`python/README.md`) SHALL document each action type (`json_replace`, `html_replace`, `regex_replace`, `file_replace`) with a brief description and a YAML snippet showing usage in a template file.

#### Scenario: User looks up json_replace action
- **WHEN** a user reads the json_replace section
- **THEN** they see a description, the required fields (`file`, `replace` with `selector` and `variable`), and a YAML example using `$.path.notation`

#### Scenario: User looks up regex_replace action
- **WHEN** a user reads the regex_replace section
- **THEN** they see that the selector must contain a `value` named capture group (using either `(?P<value>...)` or `(?<value>...)` syntax), with a YAML example

#### Scenario: User looks up html_replace action
- **WHEN** a user reads the html_replace section
- **THEN** they see that it uses XPath selectors and can target both elements and attributes, with a YAML example

#### Scenario: User looks up file_replace action
- **WHEN** a user reads the file_replace section
- **THEN** they see it replaces an entire file using a source path from a variable, with a YAML example

### Requirement: Development section
The Python implementation's README (`python/README.md`) SHALL include a development section covering how to install dev dependencies, run tests, and run the linter. It SHALL instruct contributors to run these commands from the `python/` subdirectory of the repository.

#### Scenario: Contributor sets up development environment
- **WHEN** a contributor follows the development section
- **THEN** they can run `pytest` and `ruff check` successfully from inside `python/`

## ADDED Requirements

### Requirement: Root README provides dual-implementation overview
The repository root SHALL contain a `README.md` that introduces engraft, identifies the two implementations (Python and TypeScript), summarizes when to use each, and links to `python/README.md` and `typescript/README.md` for installation and usage details.

#### Scenario: Reader learns engraft ships in two implementations
- **WHEN** a user opens the root `README.md`
- **THEN** the reader sees a brief project description and is informed that engraft is available for both Python (via PyPI) and Node/TypeScript (via npm)
- **AND** the reader is pointed at `python/README.md` and `typescript/README.md` for details

#### Scenario: Reader finds the e2e harness
- **WHEN** a user opens the root `README.md`
- **THEN** a section describes the shared end-to-end test suite at `e2e/` and its role as the behavioral contract between the two implementations

### Requirement: TypeScript implementation README
The TypeScript implementation SHALL have a `typescript/README.md` tailored for an npm audience. It SHALL include:
- A one-line description matching the npm package description.
- Installation instructions using `npm install -g engraft` (or `npx engraft`).
- A quick-start usage example using the TypeScript CLI.
- The same action reference as `python/README.md`, noting that both `(?P<value>…)` and `(?<value>…)` regex named-group syntaxes are accepted.
- A development section covering `npm install`, `npm run build`, and `npm test` run from inside `typescript/`.
- A note identifying the minimum Node version (Node ≥20).

#### Scenario: npm reader understands the package
- **WHEN** a user views the engraft page on npm
- **THEN** they see the `typescript/README.md` content
- **AND** the reader can install and run engraft using only npm-native commands

### Requirement: Regex syntax portability documented
The action reference section of both `python/README.md` and `typescript/README.md` SHALL note that the `regex_replace` selector accepts both `(?P<value>…)` and `(?<value>…)` syntaxes interchangeably in either implementation.

#### Scenario: Template author sees the portability note
- **WHEN** a user reads the regex_replace section of either README
- **THEN** they see that both named-group syntaxes are accepted in both implementations
