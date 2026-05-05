## ADDED Requirements

### Requirement: Sibling implementation subdirectories
The repository SHALL host the Python and TypeScript implementations in sibling top-level subdirectories named `python/` and `typescript/`. Each subdirectory SHALL be self-contained with respect to its language-specific tooling (build config, tests, lockfile, package manifest).

#### Scenario: Python implementation location
- **WHEN** a contributor inspects the repository
- **THEN** the Python source lives under `python/src/engraft/` and Python tests under `python/tests/`
- **AND** `python/pyproject.toml` is the Python package manifest

#### Scenario: TypeScript implementation location
- **WHEN** a contributor inspects the repository
- **THEN** the TypeScript source lives under `typescript/src/` and TypeScript tests under `typescript/tests/`
- **AND** `typescript/package.json` is the TypeScript package manifest

#### Scenario: Implementation independence
- **WHEN** a contributor builds or tests one implementation
- **THEN** no files from the other implementation's subdirectory are required

### Requirement: Python package verbatim subtree
The contents of `python/src/engraft/` and `python/tests/` SHALL be identical in module structure, package name, and import paths to the pre-reorganization layout. Internal code SHALL NOT be restructured as part of the repository reorganization.

#### Scenario: Import paths unchanged
- **WHEN** a contributor imports from the Python package
- **THEN** the import path remains `engraft.*` (e.g., `from engraft.engine import apply`)
- **AND** every module under `python/src/engraft/` corresponds one-to-one with the pre-reorganization layout

### Requirement: End-to-end harness at repository root
The shared end-to-end test harness SHALL live at `e2e/` at the repository root. It SHALL NOT live inside either implementation's subdirectory.

#### Scenario: Harness location
- **WHEN** a contributor runs `pytest e2e/` from the repository root
- **THEN** the harness executes against both implementations

### Requirement: Shared root files
The repository root SHALL contain the following shared files: `README.md` (repo-level overview), `LICENSE`, `CLAUDE.md`, and `openspec/`. These files SHALL NOT be duplicated inside `python/` or `typescript/` (except for per-implementation READMEs tailored to their package registry).

#### Scenario: Root files present
- **WHEN** a contributor inspects the repository root
- **THEN** the root contains `README.md`, `LICENSE`, `CLAUDE.md`, `openspec/`, `python/`, `typescript/`, `e2e/`

### Requirement: Git history preservation for the Python subtree
The reorganization that moves the Python subtree into `python/` SHALL preserve git history for all moved files via `git mv`. Blame and log SHALL remain traceable across the move.

#### Scenario: Blame survives the move
- **WHEN** a contributor runs `git log --follow python/src/engraft/engine.py`
- **THEN** the log shows the full history of the file from before the reorganization
