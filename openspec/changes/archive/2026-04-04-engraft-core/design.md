# Design: engraft-core

## Overview

engraft is a Python CLI tool with a single `apply` command. It reads a template file and a values file, resolves variables, and executes customization actions against files in the working directory.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
│  engraft apply --template <path> --values <path>            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Engine                             │
│                                                             │
│  1. Parse template file (YAML)                              │
│  2. Parse values file (YAML)                                │
│  3. Resolve variables (values override defaults)            │
│  4. Execute customizations in order                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ replace  │ │ json_set │ │ replace  │
        │ _value   │ │          │ │ _file    │
        └──────────┘ └──────────┘ └──────────┘
```

## Key design decisions

### Variable resolution

- Variables are defined in the template file with a `description` and `default`
- The values file provides overrides; any variable not in the values file uses its default
- The default represents the current state of the repo — applying with no overrides is a no-op
- All customization action values must reference a variable name; inline literals are not supported

### Action class hierarchy

All actions implement a common `Action` abstract base class with a unified `apply` method signature. This makes the engine a simple loop and ensures every action receives the same context.

```python
from abc import ABC, abstractmethod
from pathlib import Path

class Action(ABC):
    """Base class for all customization actions."""

    @abstractmethod
    def apply(self, variables: dict[str, str], work_dir: Path, values_dir: Path) -> None:
        """Apply this action.

        Args:
            variables: Resolved variable map (name → value).
            work_dir: Repository root directory (for resolving target file paths).
            values_dir: Directory containing the values file (for resolving source file paths).
        """
        ...
```

Each concrete action is a dataclass that holds its configuration from the template YAML and implements `apply`:

```
┌──────────────────────────────────────────────────────┐
│                  Action (ABC)                        │
│  + apply(variables, work_dir, values_dir) -> None    │
├──────────────────────────────────────────────────────┤
         ▲              ▲              ▲
         │              │              │
┌────────────────┐ ┌──────────┐ ┌────────────────┐
│ ReplaceValue   │ │ JsonSet  │ │ ReplaceFile    │
│                │ │          │ │                │
│ file: str      │ │ file: str│ │ source: str    │
│ pattern: str   │ │ set: dict│ │ target: str    │
│ replace: str   │ │          │ │                │
└────────────────┘ └──────────┘ └────────────────┘
```

The engine dispatches by iterating the customizations list:

```python
for action in template.customizations:
    action.apply(variables, work_dir, values_dir)
```

### Action: `ReplaceValue`

- Uses Python `re` module for regex matching
- The pattern **must** contain a named capture group `(?P<value>...)`
- Only the `<value>` group is replaced; all surrounding matched text is preserved
- Re-application is the template author's responsibility — patterns should match any valid value, not just the default

```yaml
- action: replace_value
  file: src/theme/colors.ts
  pattern: '(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"'
  replace: primary_color
```

### Action: `JsonSet`

- Sets values at dot-notation paths in JSON files
- Supports array indexing with bracket notation: `a.b[2].c`
- No glob/wildcard patterns — each path targets exactly one value
- Creates intermediate keys if missing (patch semantics)
- Preserves JSON formatting by using `json.dumps` with indent

```yaml
- action: json_set
  file: app.json
  set:
    expo.name: app_name
    expo.extra.items[0].label: item_label
```

### Action: `ReplaceFile`

- Copies a file from a source path to a target path in the repo
- Source path is resolved relative to the values file location
- Target path is resolved relative to the repo root (working directory)
- The source path comes from a variable, so consumers specify it in their values file

```yaml
- action: replace_file
  source: logo          # variable name → resolved to a file path
  target: assets/images/logo.png
```

### Path resolution

```
Template file paths (file, target)  → relative to working directory (repo root)
Values file paths (file references) → relative to the values file location
```

### Execution order

Customizations are applied in the order they appear in the template file. This is deterministic and allows authors to reason about ordering when it matters.

## Project structure

```
engraft/
├── pyproject.toml
├── src/
│   └── engraft/
│       ├── __init__.py
│       ├── cli.py            # Click-based CLI entry point
│       ├── engine.py         # Core apply logic, variable resolution
│       ├── actions/
│       │   ├── __init__.py   # Exports Action ABC and action registry
│       │   ├── base.py       # Action abstract base class
│       │   ├── replace_value.py  # ReplaceValue action class
│       │   ├── json_set.py       # JsonSet action class
│       │   └── replace_file.py   # ReplaceFile action class
│       └── models.py         # Data classes for Variable, Template; YAML parsing
└── tests/
    ├── conftest.py
    ├── test_cli.py
    ├── test_engine.py
    └── test_actions/
        ├── test_replace_value.py
        ├── test_json_set.py
        └── test_replace_file.py
```

## Dependencies

- **click** — CLI framework
- **pyyaml** — YAML parsing for template and values files
- **Python 3.10+** — for modern type hints and match statements

No other runtime dependencies. Keep it minimal.
