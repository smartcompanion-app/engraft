## ADDED Requirements

### Requirement: Template YAML parsing
The engine SHALL parse a template YAML file containing a `variables` map and a `customizations` list. Each customization entry SHALL specify an `action` field that maps to a registered action type.

#### Scenario: Valid template parsed
- **WHEN** the engine reads a template YAML with variables and customizations
- **THEN** it produces a Template model with resolved Variable objects and instantiated Action objects

#### Scenario: Empty variables section
- **WHEN** the template YAML has no `variables` key or an empty variables map
- **THEN** the engine proceeds with an empty variables dict

#### Scenario: Empty customizations section
- **WHEN** the template YAML has no `customizations` key or an empty list
- **THEN** the engine proceeds with no actions to execute

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
