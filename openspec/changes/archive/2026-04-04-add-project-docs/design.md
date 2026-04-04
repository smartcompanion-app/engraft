## Context

engraft is a working CLI tool (v0.1.0) with a complete codebase but no documentation files. The project uses a two-file model (template + values) with four action types, a plugin registry for actions, and a Click-based CLI. All of this needs to be communicated clearly in documentation.

## Goals / Non-Goals

**Goals:**
- README.md accurately reflects the current state of the tool — no aspirational features
- README.md serves both end users (how to use) and contributors (how to develop)
- CLAUDE.md provides enough context that a Claude Code session can orient without re-exploring the codebase
- Both files stay concise and scannable

**Non-Goals:**
- Full API documentation or man pages
- Hosting docs on a website (e.g., Read the Docs)
- Changelog or release notes
- Contributing guide (CONTRIBUTING.md)

## Decisions

### README structure: single file with usage-first layout
The README leads with what the tool does and how to use it, followed by a reference section for all action types, then development instructions at the bottom. This ordering serves the most common reader path: "what is this?" → "how do I use it?" → "how do I contribute?"

**Alternative considered:** Separate docs/ directory with per-action pages. Rejected — the project is small enough that one file covers everything without being overwhelming.

### CLAUDE.md scope: architecture + commands + conventions
CLAUDE.md focuses on what Claude Code needs to be productive: project structure, the action registry pattern, how to run tests/linting, and coding conventions. It does not duplicate README content like installation or usage examples.

**Alternative considered:** Putting everything in CLAUDE.md and skipping README. Rejected — README serves human readers on GitHub; CLAUDE.md serves Claude Code sessions. Different audiences, different content.

### Action documentation: example-driven with YAML snippets
Each action type in the README gets a brief description plus a concrete YAML snippet showing how it looks in a template file. This is more useful than abstract parameter tables for a YAML-based tool.

## Risks / Trade-offs

- **Staleness risk** → Documentation can drift from code. Mitigated by keeping both files concise and focused on stable interfaces rather than implementation details.
- **CLAUDE.md over-specification** → Too much detail in CLAUDE.md can constrain Claude Code unnecessarily. Mitigated by focusing on architecture and conventions rather than prescriptive rules.
