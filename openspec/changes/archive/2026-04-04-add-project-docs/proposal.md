## Why

The project has no README.md or CLAUDE.md. Without a README, new users and contributors have no quick way to understand what engraft does, how to install it, or how to use its action types. Without a CLAUDE.md, Claude Code sessions lack project-specific context — leading to repeated exploration of the same architecture and conventions each session.

## What Changes

- Add `README.md` at the project root covering:
  - Project description and the problem engraft solves (vs templating tools, forking, manual edits)
  - Installation instructions
  - Quick-start usage example with template + values files
  - Action reference for all four action types (`json_replace`, `html_replace`, `regex_replace`, `file_replace`)
  - Development setup (install, test, lint)
- Add `CLAUDE.md` at the project root covering:
  - Project overview and architecture (engine, models, action registry)
  - Tech stack and conventions
  - Key commands for development
  - Code structure guidance

## Capabilities

### New Capabilities
- `readme`: Project README with user-facing documentation covering installation, usage, and action reference
- `claude-config`: CLAUDE.md file providing project context for Claude Code sessions

### Modified Capabilities

_None — this is a documentation-only change with no impact on existing specs._

## Impact

- Two new files at project root: `README.md`, `CLAUDE.md`
- No code changes, no dependency changes, no API changes
