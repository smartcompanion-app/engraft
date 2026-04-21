## ADDED Requirements

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

### Requirement: Values YAML parsing
The engine SHALL parse a values YAML file into a flat string-to-string dictionary.

#### Scenario: Valid values parsed
- **WHEN** the engine reads a values YAML with key-value pairs
- **THEN** it produces a flat dict of variable overrides

#### Scenario: Empty values file
- **WHEN** the values YAML is empty or contains no keys
- **THEN** the engine proceeds with an empty overrides dict

### Requirement: Customizations executed in order
The engine SHALL execute customization actions in the order they appear in the template file.

#### Scenario: Sequential execution
- **WHEN** a template defines three customization actions in order A, B, C
- **THEN** the engine executes A, then B, then C

### Requirement: Path resolution
Template file paths (file targets) SHALL resolve relative to the working directory. Values file paths (source references) SHALL resolve relative to the values file location.

#### Scenario: Target file resolved from work dir
- **WHEN** an action targets `src/config.json` and the work dir is `/repo`
- **THEN** the action operates on `/repo/src/config.json`

#### Scenario: Source file resolved from values dir
- **WHEN** a values file at `/home/user/values/engraft.values.yml` references a file `logo.png`
- **THEN** the file resolves to `/home/user/values/logo.png`

### Requirement: Re-application produces correct results
Applying the same template with different values to an already-customized project SHALL produce results matching the new values.

#### Scenario: Apply twice with different values
- **WHEN** `engraft apply` runs with values A, then runs again with values B
- **THEN** the project reflects values B after the second application

### Requirement: Action registry
The engine SHALL maintain a registry mapping action name strings to Action subclasses. Unknown action names SHALL raise an error.

#### Scenario: Known action type
- **WHEN** a customization specifies `action: regex_replace`
- **THEN** the engine instantiates the corresponding `RegexReplace` action class

#### Scenario: Unknown action type
- **WHEN** a customization specifies an unregistered action name
- **THEN** the engine raises an error

### Requirement: Staging directory for atomic apply

The engine SHALL execute all actions against a staging directory (`.engraft/`) and only copy results back to the project when all actions succeed.

#### Scenario: All actions succeed

- **WHEN** `engraft apply` runs with 3 valid customizations
- **THEN** all actions execute against `.engraft/`, modified files are copied back to the project, and `.engraft/` is removed

#### Scenario: An action fails mid-execution

- **WHEN** action 2 of 3 raises an exception
- **THEN** the project files remain in their original state, `.engraft/` is removed, and the exception propagates to the caller

#### Scenario: Staging directory already exists

- **WHEN** `.engraft/` exists before `engraft apply` runs (e.g., from a previous crash)
- **THEN** the existing `.engraft/` directory is removed before creating a new one

#### Scenario: Staging directory cleaned up on failure

- **WHEN** any step in the apply process fails
- **THEN** the `.engraft/` directory is removed regardless of where the failure occurred

### Requirement: Target file collection

Each customization entry in the raw YAML SHALL contain a `file` field. The engine SHALL extract and deduplicate `file` values from all customization entries to determine which files to copy into the staging directory.

#### Scenario: Single-file actions

- **WHEN** customization entries target `src/config.json` and `assets/index.html`
- **THEN** both files are copied into the staging directory

#### Scenario: Duplicate file targets

- **WHEN** multiple customization entries target the same file `src/config.json`
- **THEN** the file is copied into the staging directory once

### Requirement: Staging directory preserves structure

The staging directory SHALL preserve the relative directory structure of copied files.

#### Scenario: Nested file paths

- **WHEN** actions target `src/config.json` and `assets/img/logo.png`
- **THEN** `.engraft/src/config.json` and `.engraft/assets/img/logo.png` are created with the same content

### Requirement: file_replace target validation

The `file_replace` action SHALL verify that the target file exists before applying.

#### Scenario: Target file does not exist

- **WHEN** `file_replace` targets a file that does not exist in the work directory
- **THEN** a `FileNotFoundError` is raised with a message identifying the missing target path

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
