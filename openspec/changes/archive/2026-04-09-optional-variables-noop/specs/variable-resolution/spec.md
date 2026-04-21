## MODIFIED Requirements

### Requirement: Variables defined with description and default
Each variable in the template YAML SHALL be defined as an array entry with a `variable` field (name), a `description` field, and an optional `default` field. When `default` is not provided, the variable is unset unless the values file supplies a value.

#### Scenario: Variable with default
- **WHEN** a template defines a variable with `default: "MyApp"`
- **THEN** the variable resolves to `"MyApp"` if no override is provided in the values file

#### Scenario: Variable without default and no value provided
- **WHEN** a template defines a variable without a `default` field and the values file does not include that variable
- **THEN** the variable is absent from the resolved variables dict

#### Scenario: Variable without default but value provided
- **WHEN** a template defines a variable without a `default` field and the values file provides a value for it
- **THEN** the variable resolves to the value from the values file

### Requirement: Values override defaults
Variables provided in the values file SHALL override the defaults from the template. Variables not present in the values file SHALL use their default if one exists. Variables with neither a value nor a default SHALL be absent from the resolved variables dict.

#### Scenario: Value overrides default
- **WHEN** a template defines variable `app_name` with default `"MyApp"` and the values file sets `app_name: "CustomApp"`
- **THEN** the resolved value of `app_name` is `"CustomApp"`

#### Scenario: Value not provided uses default
- **WHEN** a template defines variable `app_name` with default `"MyApp"` and the values file does not include `app_name`
- **THEN** the resolved value of `app_name` is `"MyApp"`

#### Scenario: No default and no value
- **WHEN** a template defines variable `theme_color` without a default and the values file does not include `theme_color`
- **THEN** `theme_color` is absent from the resolved variables dict

## ADDED Requirements

### Requirement: Variables use array format
Variables in the template YAML SHALL be defined as an array of objects, each with a `variable` field as the identifier, a `description` field, and an optional `default` field.

#### Scenario: Array-format variables parsed
- **WHEN** the template defines variables as `[{variable: "app_name", description: "...", default: "MyApp"}, {variable: "theme", description: "..."}]`
- **THEN** the parser produces Variable objects with `name="app_name"`, `default="MyApp"` and `name="theme"`, `default=None`

#### Scenario: Duplicate variable names
- **WHEN** the template defines two variables with the same `variable` field value
- **THEN** the parser SHALL raise an error indicating the duplicate
