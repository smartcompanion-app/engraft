## ADDED Requirements

### Requirement: json_replace action with selector-variable list
The `json_replace` action SHALL accept a `replace` list of `{selector, variable}` entries. The `selector` field SHALL use a `$.` prefix followed by dot-notation path with optional array indexing (e.g., `$.expo.name`, `$.items[0].label`).

#### Scenario: Simple path replacement
- **WHEN** the action is configured with selector `$.name` and a variable resolving to `"MyApp"`
- **THEN** the top-level `name` field in the JSON file SHALL be set to `"MyApp"`

#### Scenario: Nested path with array index
- **WHEN** the action is configured with selector `$.icons[0].sizes` and a variable resolving to `"512x512"`
- **THEN** the `sizes` field of the first element in the `icons` array SHALL be set to `"512x512"`

#### Scenario: Multiple replacements in one action
- **WHEN** the action is configured with two replace entries for `$.name` and `$.version`
- **THEN** both fields SHALL be updated in the output JSON file

### Requirement: regex_replace action with selector-variable list
The `regex_replace` action SHALL accept a `replace` list of `{selector, variable}` entries. The `selector` field SHALL contain a regex pattern with a `(?P<value>...)` named capture group. Only the named group content SHALL be replaced.

#### Scenario: Single regex replacement
- **WHEN** the action is configured with selector `'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"'` and a variable resolving to `"#ff0000"`
- **THEN** only the value within the quotes SHALL be replaced, preserving the `PRIMARY_COLOR = "` prefix

#### Scenario: Missing named capture group
- **WHEN** the action is configured with a selector that does not contain `(?P<value>...)`
- **THEN** the action SHALL raise an error indicating the named capture group is required

#### Scenario: Pattern matches nothing
- **WHEN** the action is configured with a selector pattern that does not match any content in the file
- **THEN** the action SHALL raise an error indicating no match was found

#### Scenario: Multiple regex replacements on same file
- **WHEN** the action is configured with two replace entries targeting different patterns in the same file
- **THEN** both replacements SHALL be applied to the file content

### Requirement: file_replace action with flat format
The `file_replace` action SHALL accept `file` (target path in repo) and `variable` (variable name resolving to source file path) as flat fields. It SHALL NOT use a `replace` list.

#### Scenario: Replace a file
- **WHEN** the action is configured with `file: assets/logo.png` and a variable resolving to a source file path
- **THEN** the source file SHALL be copied to `assets/logo.png` in the working directory

#### Scenario: Source file does not exist
- **WHEN** the variable resolves to a path that does not exist
- **THEN** the action SHALL raise an error indicating the source file was not found

### Requirement: Consistent action naming
All actions SHALL use the `*_replace` naming convention: `json_replace`, `html_replace`, `regex_replace`, `file_replace`.

#### Scenario: Actions registered under new names
- **WHEN** a template YAML uses `action: json_replace`
- **THEN** the action registry SHALL resolve to the `JsonReplace` action class

#### Scenario: Old action names rejected
- **WHEN** a template YAML uses `action: json_set` (old name)
- **THEN** the action registry SHALL raise an error indicating the action is unknown
