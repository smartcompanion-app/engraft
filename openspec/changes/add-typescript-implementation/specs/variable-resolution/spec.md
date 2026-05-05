## MODIFIED Requirements

### Requirement: Variables defined with description and optional default
Each variable in the template YAML SHALL have a `description`. The `default` field SHALL be optional. When `default` is present, it represents the current state of the repository; when it is absent, the variable is considered "optional".

#### Scenario: Variable with default
- **WHEN** a template defines a variable with `default: "MyApp"`
- **THEN** the variable resolves to `"MyApp"` if no override is provided in the values file

#### Scenario: Variable without default
- **WHEN** a template defines a variable without a `default` field and the values file does not provide a value for it
- **THEN** the variable resolves to the sentinel "unset" value (None in Python, null in TypeScript)

#### Scenario: Empty-string default distinguished from absent default
- **WHEN** a template defines a variable with `default: ""` (explicit empty string)
- **THEN** the variable resolves to the empty string, not to the unset sentinel

## ADDED Requirements

### Requirement: Unset optional variable causes replace entry to be a noop
When an action's `replace` entry references a variable that resolved to the unset sentinel (no default in the template AND no value in the values file), the engine SHALL skip that entry without erroring and without modifying the target file. For `file_replace`, which references a single variable directly via the `variable` field, an unset variable SHALL result in the entire action being a noop.

#### Scenario: Unset optional variable skips a replace entry
- **WHEN** a template declares a variable with no default
- **AND** the values file does not provide it
- **AND** a `json_replace`/`html_replace`/`regex_replace` action includes a `replace` entry referencing it
- **THEN** the engine leaves the targeted selector in the file untouched
- **AND** no error is raised for that entry

#### Scenario: Other entries in the same action still apply
- **WHEN** an action has two `replace` entries and only the first references an unset variable
- **THEN** the first entry is skipped and the second is applied normally

#### Scenario: file_replace with unset variable is a noop
- **WHEN** a `file_replace` action references an unset optional variable
- **THEN** the action is skipped and the target file is not modified

#### Scenario: Explicit empty string still overwrites
- **WHEN** a variable is declared with `default: ""` or set to `""` in values
- **THEN** the replace entry applies with an empty-string substitution (not skipped)
