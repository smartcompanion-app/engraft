## MODIFIED Requirements

### Requirement: Template YAML parsing
The engine SHALL parse a template YAML file containing a `variables` array and a `customizations` list. Each customization entry SHALL specify an `action` field that maps to a registered action type. Multi-entry `replace` lists SHALL be expanded into individual single-variable action objects at parse time.

#### Scenario: Valid template parsed
- **WHEN** the engine reads a template YAML with variables array and customizations
- **THEN** it produces a list of Variable objects and a list of raw customization entries

#### Scenario: Empty variables section
- **WHEN** the template YAML has no `variables` key or an empty array
- **THEN** the engine proceeds with an empty variables list

#### Scenario: Empty customizations section
- **WHEN** the template YAML has no `customizations` key or an empty list
- **THEN** the engine proceeds with no actions to execute

#### Scenario: Multi-entry replace list expanded
- **WHEN** a customization has `replace: [{selector: "$.name", variable: "app_name"}, {selector: "$.theme", variable: "theme"}]`
- **THEN** the engine creates two separate action objects, one per entry

### Requirement: Target file collection
Each customization entry in the raw YAML SHALL contain a `file` field. The engine SHALL extract and deduplicate `file` values from all customization entries to determine which files to copy into the staging directory.

#### Scenario: Single-file actions
- **WHEN** customization entries target `src/config.json` and `assets/index.html`
- **THEN** both files are copied into the staging directory

#### Scenario: Duplicate file targets
- **WHEN** multiple customization entries target the same file `src/config.json`
- **THEN** the file is copied into the staging directory once

## ADDED Requirements

### Requirement: Actions constructed with resolved values
Action objects SHALL receive the resolved variable value, the absolute target file path (within staging dir), and the values directory path at construction time. The `apply()` method SHALL take no arguments.

#### Scenario: Action receives resolved value
- **WHEN** a `json_replace` action is constructed for variable `app_name` with resolved value `"Foo"`
- **THEN** the action object holds `value="Foo"` and `apply()` uses it directly

#### Scenario: Action receives absolute target path
- **WHEN** a `json_replace` action targets `src/config.json` and the staging dir is `/repo/.engraft`
- **THEN** the action object holds `target=Path("/repo/.engraft/src/config.json")`

### Requirement: Unset variables skip action creation
When expanding customization entries into actions, the engine SHALL skip any entry whose referenced variable is absent from the resolved variables dict. No action object is created for unset variables.

#### Scenario: Unset variable skipped
- **WHEN** a customization references variable `theme_color` which has no default and no value provided
- **THEN** no action is created for that entry

#### Scenario: Set variable creates action
- **WHEN** a customization references variable `app_name` which resolves to `"Foo"`
- **THEN** an action is created with the resolved value

#### Scenario: Mixed set and unset in same customization
- **WHEN** a customization has two replace entries, one referencing a set variable and one referencing an unset variable
- **THEN** only the action for the set variable is created; the unset entry is skipped
