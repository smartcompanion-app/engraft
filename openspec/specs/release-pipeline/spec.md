## ADDED Requirements

### Requirement: Release workflow triggers on GitHub Release publish
The release workflow SHALL be triggered when a GitHub Release is published (`on: release: types: [published]`).

#### Scenario: Release is published via GitHub UI
- **WHEN** a user publishes a GitHub Release
- **THEN** the release workflow starts execution

#### Scenario: Draft release is created
- **WHEN** a user creates a draft release without publishing
- **THEN** the release workflow SHALL NOT trigger

### Requirement: Quality gate runs lint and format checks
The release workflow SHALL run `ruff check .` and `ruff format --check .` as a quality gate before building.

#### Scenario: Lint check passes
- **WHEN** all source files pass ruff lint rules
- **THEN** the workflow proceeds to the test stage

#### Scenario: Lint or format check fails
- **WHEN** any source file fails ruff lint or format check
- **THEN** the workflow SHALL fail and NOT proceed to build or publish

### Requirement: Quality gate runs tests across Python matrix
The release workflow SHALL run `pytest` across Python versions 3.10, 3.12, and 3.13.

#### Scenario: All tests pass on all Python versions
- **WHEN** pytest passes on Python 3.10, 3.12, and 3.13
- **THEN** the workflow proceeds to the build stage

#### Scenario: Tests fail on any Python version
- **WHEN** pytest fails on any matrix version
- **THEN** the workflow SHALL fail and NOT proceed to build or publish

### Requirement: Build produces sdist and wheel artifacts
The release workflow SHALL build both an sdist and a wheel using `python -m build`.

#### Scenario: Successful build
- **WHEN** the quality gate passes
- **THEN** the workflow builds sdist and wheel artifacts in `dist/`

### Requirement: Publish to PyPI using Trusted Publisher OIDC
The release workflow SHALL publish to PyPI using `pypa/gh-action-pypi-publish` with OIDC authentication (no API tokens). The job SHALL use the `pypi` GitHub environment.

#### Scenario: Successful publish
- **WHEN** build artifacts exist and OIDC authentication succeeds
- **THEN** the package is published to pypi.org

#### Scenario: OIDC authentication fails
- **WHEN** the Trusted Publisher configuration is missing or misconfigured
- **THEN** the publish step SHALL fail with an authentication error

### Requirement: Releases are signed with Sigstore attestations
The release workflow SHALL enable Sigstore attestations (`attestations: true`) when publishing.

#### Scenario: Package is published with attestation
- **WHEN** a package is successfully published to PyPI
- **THEN** Sigstore attestations SHALL be generated for the published artifacts

### Requirement: Publish depends on all quality gates passing
The publish job SHALL only run after lint, format, test, and build jobs all succeed.

#### Scenario: Quality gate fails
- **WHEN** any quality gate job (lint, test) fails
- **THEN** the build and publish jobs SHALL NOT execute
