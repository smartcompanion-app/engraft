## ADDED Requirements

### Requirement: Version is derived from git tags
The package version SHALL be dynamically derived from git tags using `hatch-vcs` instead of being hardcoded in `pyproject.toml`.

#### Scenario: Tagged commit (release build)
- **WHEN** the current commit has a tag matching `v*` (e.g., `v0.2.0`)
- **THEN** the package version SHALL be the tag version without the `v` prefix (e.g., `0.2.0`)

#### Scenario: Untagged commit (development build)
- **WHEN** the current commit does not have a version tag
- **THEN** the package version SHALL be a dev version derived from the nearest tag (e.g., `0.2.0.dev3+gabcdef`)

### Requirement: pyproject.toml uses dynamic version field
The `pyproject.toml` SHALL declare `dynamic = ["version"]` and remove the hardcoded `version` field. The `[tool.hatch.version]` section SHALL specify `source = "vcs"`.

#### Scenario: pyproject.toml configuration
- **WHEN** inspecting `pyproject.toml`
- **THEN** the `[project]` section SHALL contain `dynamic = ["version"]` and SHALL NOT contain a `version` key
- **THEN** the `[tool.hatch.version]` section SHALL contain `source = "vcs"`

### Requirement: hatch-vcs is a build dependency
The `hatch-vcs` package SHALL be listed in the `[build-system] requires` array.

#### Scenario: Build system includes hatch-vcs
- **WHEN** inspecting `pyproject.toml` `[build-system]` section
- **THEN** the `requires` array SHALL include `hatch-vcs`
