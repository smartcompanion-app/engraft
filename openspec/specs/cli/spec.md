## ADDED Requirements

### Requirement: Apply command
The CLI SHALL provide an `engraft apply` command with required `--template` and `--values` options.

#### Scenario: Successful apply
- **WHEN** the user runs `engraft apply --template template.yml --values values.yml`
- **THEN** customizations are applied and the CLI prints a success message

### Requirement: Error handling for missing files
The CLI SHALL display a clear error message when the template or values file does not exist.

#### Scenario: Template file missing
- **WHEN** the user runs `engraft apply --template nonexistent.yml --values values.yml`
- **THEN** the CLI displays an error indicating the template file was not found

#### Scenario: Values file missing
- **WHEN** the user runs `engraft apply --template template.yml --values nonexistent.yml`
- **THEN** the CLI displays an error indicating the values file was not found

### Requirement: Error handling for invalid YAML
The CLI SHALL display a clear error message when the template or values file contains invalid YAML.

#### Scenario: Malformed YAML
- **WHEN** the user runs `engraft apply` with a malformed YAML file
- **THEN** the CLI displays an error describing the parsing failure

### Requirement: Error handling for action errors
The CLI SHALL display a clear error message when an action fails during execution.

#### Scenario: Action raises error
- **WHEN** an action fails (e.g., target file not found, pattern doesn't match)
- **THEN** the CLI displays the action error message and exits with a non-zero code

### Requirement: Version flag
The CLI SHALL support `--version` to display the current engraft version.

#### Scenario: Version displayed
- **WHEN** the user runs `engraft --version`
- **THEN** the CLI prints the version string
