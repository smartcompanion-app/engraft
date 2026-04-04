## ADDED Requirements

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

Each action SHALL expose a `target_files()` method returning the list of project-relative file paths it operates on. The engine SHALL collect and deduplicate these paths to determine which files to copy into the staging directory.

#### Scenario: Single-file actions

- **WHEN** a `json_replace`, `html_replace`, `regex_replace`, or `file_replace` action targets `src/config.json`
- **THEN** `target_files()` returns `["src/config.json"]`

### Requirement: Staging directory preserves structure

The staging directory SHALL preserve the relative directory structure of copied files.

#### Scenario: Nested file paths

- **WHEN** actions target `src/config.json` and `assets/img/logo.png`
- **THEN** `.engraft/src/config.json` and `.engraft/assets/img/logo.png` are created with the same content

## CHANGED Requirements

### Requirement: file_replace target validation

The `file_replace` action SHALL verify that the target file exists before applying. Previously, only the source file was validated.

#### Scenario: Target file does not exist

- **WHEN** `file_replace` targets a file that does not exist in the work directory
- **THEN** a `FileNotFoundError` is raised with a message identifying the missing target path
