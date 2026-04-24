## ADDED Requirements

### Requirement: Variables defined with description and default
Each variable in the template YAML SHALL have a `description` and a `default` value. The default represents the current state of the repository.

#### Scenario: Variable with default
- **WHEN** a template defines a variable with `default: "MyApp"`
- **THEN** the variable resolves to `"MyApp"` if no override is provided in the values file

### Requirement: Values override defaults
Variables provided in the values file SHALL override the defaults from the template. Variables not present in the values file SHALL use their default.

#### Scenario: Value overrides default
- **WHEN** a template defines variable `app_name` with default `"MyApp"` and the values file sets `app_name: "CustomApp"`
- **THEN** the resolved value of `app_name` is `"CustomApp"`

#### Scenario: Value not provided uses default
- **WHEN** a template defines variable `app_name` with default `"MyApp"` and the values file does not include `app_name`
- **THEN** the resolved value of `app_name` is `"MyApp"`

### Requirement: All action values reference variable names
Customization actions SHALL reference variable names, not inline literal values. The resolved variable value is used at apply time.

#### Scenario: Action references variable
- **WHEN** an action specifies `replace: primary_color`
- **THEN** the action uses the resolved value of the `primary_color` variable
