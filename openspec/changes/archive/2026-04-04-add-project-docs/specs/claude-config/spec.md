## ADDED Requirements

### Requirement: Project overview
CLAUDE.md SHALL include a brief project overview describing what engraft does and its core concept (two-file model: template + values).

#### Scenario: Claude Code reads project context
- **WHEN** a Claude Code session starts in this project
- **THEN** CLAUDE.md provides enough context to understand the project's purpose without reading source files

### Requirement: Architecture description
CLAUDE.md SHALL describe the code architecture: CLI (cli.py) → engine (engine.py) → models (models.py) → actions (plugin registry in actions/), including the action registration pattern using the `@register` decorator.

#### Scenario: Claude Code understands code flow
- **WHEN** Claude Code needs to modify or extend the codebase
- **THEN** CLAUDE.md explains how the components connect and where new actions are registered

### Requirement: Development commands
CLAUDE.md SHALL list the key development commands: install, test, lint, and the CLI entry point.

#### Scenario: Claude Code runs project commands
- **WHEN** Claude Code needs to verify changes
- **THEN** CLAUDE.md provides the exact commands to run tests and linting

### Requirement: Coding conventions
CLAUDE.md SHALL document the project's coding conventions: Python 3.10+, type hints, ruff linting rules, and pytest for testing.

#### Scenario: Claude Code writes new code
- **WHEN** Claude Code generates or modifies code
- **THEN** CLAUDE.md provides conventions to follow so the code matches the project style
