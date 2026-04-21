## MODIFIED Requirements

### Requirement: json_replace action with selector-variable list
The `json_replace` action YAML entry SHALL accept a `replace` list of `{selector, variable}` entries for convenience. At parse time, each entry SHALL be expanded into a separate `JsonReplace` action object holding a single `selector`, the resolved `value`, and the absolute `target` path. The `apply()` method SHALL take no arguments.

#### Scenario: Simple path replacement
- **WHEN** the action is constructed with selector `$.name` and resolved value `"MyApp"`
- **THEN** the top-level `name` field in the target JSON file SHALL be set to `"MyApp"`

#### Scenario: Nested path with array index
- **WHEN** the action is constructed with selector `$.icons[0].sizes` and resolved value `"512x512"`
- **THEN** the `sizes` field of the first element in the `icons` array SHALL be set to `"512x512"`

#### Scenario: Multiple replacements in one YAML entry
- **WHEN** the YAML entry has two replace entries for `$.name` and `$.version`
- **THEN** two separate `JsonReplace` action objects SHALL be created

### Requirement: regex_replace action with selector-variable list
The `regex_replace` action YAML entry SHALL accept a `replace` list of `{selector, variable}` entries. At parse time, each entry SHALL be expanded into a separate `RegexReplace` action object holding a single `selector`, the resolved `value`, and the absolute `target` path. The `apply()` method SHALL take no arguments.

#### Scenario: Single regex replacement
- **WHEN** the action is constructed with selector `'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"'` and resolved value `"#ff0000"`
- **THEN** only the value within the quotes SHALL be replaced, preserving the prefix

#### Scenario: Missing named capture group
- **WHEN** the action is constructed with a selector that does not contain `(?P<value>...)`
- **THEN** the action SHALL raise an error indicating the named capture group is required

#### Scenario: Pattern matches nothing
- **WHEN** the action is constructed with a selector pattern that does not match any content in the file
- **THEN** the action SHALL raise an error indicating no match was found

#### Scenario: Multiple regex replacements on same file
- **WHEN** the YAML entry has two replace entries targeting different patterns in the same file
- **THEN** two separate `RegexReplace` action objects SHALL be created

### Requirement: file_replace action with flat format
The `file_replace` action SHALL accept `file` (target path) and `variable` (variable name resolving to source file path) as flat YAML fields. At construction, the resolved source path (`values_dir / value`) and absolute target path SHALL be stored on the action. The `apply()` method SHALL take no arguments.

#### Scenario: Replace a file
- **WHEN** the action is constructed with target `assets/logo.png` and resolved source path pointing to an existing file
- **THEN** the source file SHALL be copied to the target path

#### Scenario: Source file does not exist
- **WHEN** the resolved source path does not exist
- **THEN** the action SHALL raise an error indicating the source file was not found

### Requirement: html_replace action with selector-variable list
The `html_replace` action YAML entry SHALL accept a `replace` list of `{selector, variable}` entries. At parse time, each entry SHALL be expanded into a separate `HtmlReplace` action object holding a single `selector`, the resolved `value`, and the absolute `target` path. The `apply()` method SHALL take no arguments.

#### Scenario: XPath element replacement
- **WHEN** the action is constructed with an XPath selector targeting an element and resolved value `"My Title"`
- **THEN** the element's text content SHALL be set to `"My Title"`

#### Scenario: XPath attribute replacement
- **WHEN** the action is constructed with an XPath selector targeting an attribute and resolved value `"dark"`
- **THEN** the attribute SHALL be set to `"dark"`

#### Scenario: Multiple HTML replacements on same file
- **WHEN** the YAML entry has two replace entries targeting different XPath selectors
- **THEN** two separate `HtmlReplace` action objects SHALL be created
