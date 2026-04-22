## ADDED Requirements

### Requirement: YAML 1.2 parsing semantics
The engine SHALL parse template and values YAML files using YAML 1.2 semantics. The strings `yes`, `no`, `on`, `off`, `Yes`, `No`, `On`, `Off`, `YES`, `NO`, `ON`, `OFF` SHALL be parsed as strings, not booleans. Only `true` and `false` (and their capitalized variants as defined by YAML 1.2) SHALL be parsed as booleans.

This requirement applies equally to both the Python and TypeScript implementations and ensures template and values files behave identically across implementations regardless of the underlying YAML library's defaults.

#### Scenario: yes parses as string
- **WHEN** a values file contains `flag: yes`
- **THEN** the variable `flag` resolves to the string `"yes"`, not the boolean `True`

#### Scenario: no parses as string
- **WHEN** a values file contains `flag: no`
- **THEN** the variable `flag` resolves to the string `"no"`, not the boolean `False`

#### Scenario: true parses as boolean
- **WHEN** a values file contains `flag: true`
- **THEN** the variable `flag` resolves to the boolean `True`

#### Scenario: Python implementation uses a configured loader
- **WHEN** the Python implementation parses YAML
- **THEN** it uses a PyYAML loader configured to suppress the YAML 1.1 implicit resolvers for `yes`/`no`/`on`/`off`

#### Scenario: TypeScript implementation uses js-yaml default behavior
- **WHEN** the TypeScript implementation parses YAML
- **THEN** it uses js-yaml's default YAML 1.2 parsing, which already parses `yes`/`no`/`on`/`off` as strings
