## ADDED Requirements

### Requirement: TypeScript implementation exists and is distributable
The repository SHALL include a TypeScript implementation of engraft under `typescript/` that is buildable into a single-file CLI executable and publishable to npm.

#### Scenario: Build produces an executable
- **WHEN** a contributor runs `npm install && npm run build` inside `typescript/`
- **THEN** a CLI entry file is produced at `typescript/dist/cli.js`
- **AND** `node typescript/dist/cli.js --version` prints a version string

#### Scenario: Package binary named engraft
- **WHEN** the TypeScript package is installed globally via npm
- **THEN** an `engraft` command is available on the user's PATH

### Requirement: Node runtime minimum version
The TypeScript implementation SHALL require Node ≥20 (LTS). The `package.json` `engines` field SHALL declare this minimum.

#### Scenario: Engines field present
- **WHEN** a contributor inspects `typescript/package.json`
- **THEN** the `engines.node` field specifies `>=20`

### Requirement: Command-line surface parity
The TypeScript `engraft` CLI SHALL accept the same commands, options, and flags as the Python CLI. This includes the `apply` command with `--template` and `--values` options and the `--version` flag.

#### Scenario: Apply command available
- **WHEN** a user runs `engraft apply --template template.yml --values values.yml` from the TypeScript CLI
- **THEN** the behavior is equivalent to the Python CLI for the same inputs, including file resolution, variable resolution, and staging

#### Scenario: Version flag available
- **WHEN** a user runs `engraft --version` from the TypeScript CLI
- **THEN** the CLI prints a version string

### Requirement: Version string identical across implementations
The TypeScript CLI SHALL print the same version string as the Python CLI when invoked with `--version`. The TypeScript implementation's version SHALL be sourced from `package.json`; the Python implementation's version SHALL be sourced from package metadata.

#### Scenario: Matching version output
- **WHEN** a user runs `engraft --version` against both implementations at the same release
- **THEN** the two outputs are byte-identical

### Requirement: Behavioral conformance to existing engraft specs
The TypeScript implementation SHALL satisfy every scenario defined in the `cli`, `engine`, `variable-resolution`, `unified-action-format`, and `html-replace` capabilities. The e2e harness SHALL be the means of verifying this conformance.

#### Scenario: E2E suite passes for TypeScript
- **WHEN** the e2e harness runs with the TypeScript implementation selected
- **THEN** every scenario passes with semantically equivalent output to the Python implementation

### Requirement: Action registry extensibility
The TypeScript implementation SHALL provide an action registry analogous to the Python `@register("name")` decorator such that a new action type can be added by creating a single file under `typescript/src/actions/` and registering it.

#### Scenario: New action can be added in one file
- **WHEN** a contributor adds a new action class to `typescript/src/actions/`
- **AND** the class is registered via the `register("name")` mechanism
- **AND** the class is imported from `typescript/src/actions/index.ts`
- **THEN** the new action is available for use in template YAML files
