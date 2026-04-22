## MODIFIED Requirements

### Requirement: regex_replace action with selector-variable list
The `regex_replace` action SHALL accept a `replace` list of `{selector, variable}` entries. The `selector` field SHALL contain a regex pattern with a named capture group named `value`, written in either of two syntaxes:
- Python-style: `(?P<value>...)`
- ECMAScript-style: `(?<value>...)`

Both syntaxes SHALL be accepted by both the Python and TypeScript implementations. Each implementation SHALL normalize the incoming syntax to its native form before compiling the regex. Only the named group content SHALL be replaced.

#### Scenario: Single regex replacement with Python syntax
- **WHEN** the action is configured with selector `'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"'` and a variable resolving to `"#ff0000"`
- **THEN** only the value within the quotes SHALL be replaced, preserving the `PRIMARY_COLOR = "` prefix

#### Scenario: Single regex replacement with ECMAScript syntax
- **WHEN** the action is configured with selector `'(PRIMARY_COLOR\s*=\s*)"(?<value>[^"]*)"'` and a variable resolving to `"#ff0000"`
- **THEN** only the value within the quotes SHALL be replaced, preserving the `PRIMARY_COLOR = "` prefix
- **AND** the same selector works unchanged in both the Python and TypeScript implementations

#### Scenario: Missing named capture group
- **WHEN** the action is configured with a selector that contains neither `(?P<value>...)` nor `(?<value>...)`
- **THEN** the action SHALL raise an error indicating the `value` named capture group is required

#### Scenario: Pattern matches nothing
- **WHEN** the action is configured with a selector pattern that does not match any content in the file
- **THEN** the action SHALL raise an error indicating no match was found

#### Scenario: Multiple regex replacements on same file
- **WHEN** the action is configured with two replace entries targeting different patterns in the same file
- **THEN** both replacements SHALL be applied to the file content
