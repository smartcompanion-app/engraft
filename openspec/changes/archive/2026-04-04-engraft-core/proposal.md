# Proposal: engraft-core

## What

Build the core `engraft` Python CLI tool that applies customizations to any existing project or git repository without requiring the original repo to use templating placeholders.

The tool introduces a clean two-file model:
- **Template file** (`engraft.template.yml`) — defines what can be customized and how, maintained by the repo author
- **Values file** (`engraft.values.yml`) — provided by the consumer, contains only their customization values

## Why

Today, customizing a project (e.g., white-label products) forces a choice between bad options:

- **Templating tools** (Cookiecutter, Copier, Yeoman) require `{{ placeholders }}` in source code — the repo is no longer a working app
- **Forking** leads to diverging codebases that are painful to sync with upstream
- **Manual editing** is error-prone, undocumented, and impossible to reproduce

engraft solves this by keeping the source repo clean and runnable while providing a declarative, reproducible customization layer on top.

## Scope

### In scope
- Single CLI command: `engraft apply --template <file> --values <file>`
- Three customization actions: `replace_value`, `json_set`, `replace_file`
- Variable system with defaults (no validation/typing for now)
- Installable via `pip install engraft`

### Out of scope
- Additional CLI commands (validate, diff, preview, init)
- Variable types or validation
- YAML/XML/TOML structured patching (only JSON via `json_set`)
- Interactive/prompt mode for collecting values
- Undo/rollback functionality

## Success criteria
- A user can clone a repo, run `engraft apply` with a template and values file, and get a correctly customized project
- Re-application works when the template author writes sufficiently broad regex patterns
- The tool is installable from PyPI via `pip install engraft`
