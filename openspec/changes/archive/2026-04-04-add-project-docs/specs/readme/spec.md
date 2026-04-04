## ADDED Requirements

### Requirement: Project description section
The README SHALL begin with a one-line description matching the pyproject.toml description, followed by a concise explanation of the problem engraft solves (comparison with templating tools, forking, and manual editing).

#### Scenario: Reader understands the purpose
- **WHEN** a user opens README.md
- **THEN** the first section explains what engraft does and why it exists without requiring them to read source code

### Requirement: Installation instructions
The README SHALL include installation instructions using `pip install engraft`.

#### Scenario: User installs the tool
- **WHEN** a user follows the installation section
- **THEN** they can run `engraft --version` successfully

### Requirement: Quick-start usage example
The README SHALL include a complete quick-start example showing a minimal template file, a minimal values file, and the `engraft apply` command.

#### Scenario: User runs the quick-start example
- **WHEN** a user creates the example template and values files from the README and runs the shown command
- **THEN** the target file is modified as described in the example

### Requirement: Action reference for all four action types
The README SHALL document each action type (`json_replace`, `html_replace`, `regex_replace`, `file_replace`) with a brief description and a YAML snippet showing usage in a template file.

#### Scenario: User looks up json_replace action
- **WHEN** a user reads the json_replace section
- **THEN** they see a description, the required fields (`file`, `replace` with `selector` and `variable`), and a YAML example using `$.path.notation`

#### Scenario: User looks up regex_replace action
- **WHEN** a user reads the regex_replace section
- **THEN** they see that the selector must contain a `(?P<value>...)` named capture group, with a YAML example

#### Scenario: User looks up html_replace action
- **WHEN** a user reads the html_replace section
- **THEN** they see that it uses XPath selectors and can target both elements and attributes, with a YAML example

#### Scenario: User looks up file_replace action
- **WHEN** a user reads the file_replace section
- **THEN** they see it replaces an entire file using a source path from a variable, with a YAML example

### Requirement: Development section
The README SHALL include a development section covering how to install dev dependencies, run tests, and run the linter.

#### Scenario: Contributor sets up development environment
- **WHEN** a contributor follows the development section
- **THEN** they can run `pytest` and `ruff check` successfully
