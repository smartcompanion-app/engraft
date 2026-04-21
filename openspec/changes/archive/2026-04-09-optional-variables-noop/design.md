## Context

The engine currently treats every variable as required with a mandatory `default`. The `Variable` dataclass holds `default: str`, and `parse_template` falls back to `""` when no default is given. Actions receive a `variables: dict[str, str]` in `apply()` and blindly use whatever value is present — including empty strings from missing defaults.

Actions also hold a `replace: list[dict]` allowing multiple selector/variable pairs per action. This means a single action can reference multiple variables, complicating the question of "what happens when one variable is set and another isn't."

## Goals / Non-Goals

**Goals:**
- Allow variables without a `default` — these are unset unless the values file provides them
- Actions referencing unset variables are never constructed (noop by absence)
- Switch variables YAML from dict to array format for consistency with customizations
- Flatten actions to single-variable, single-selector — fully resolved at construction
- `apply()` becomes a zero-argument method; actions are self-contained deferred operations

**Non-Goals:**
- Multi-variable actions or template interpolation within a single action
- Validation or warning system for unset variables (may come later)
- Changes to the values YAML format
- Changes to CLI interface

## Decisions

### 1. Variables as array in template YAML

Use `- variable: name` entries instead of dict keys. This mirrors the `customizations` format and avoids overloading YAML dict keys as identifiers.

**Alternative**: Keep dict format, just make `default` optional. Rejected because it's inconsistent with how customizations are defined.

### 2. `Variable.default` becomes `str | None`

`None` means "no default provided." During resolution, if neither the values file nor the default supplies a value, the variable is absent from the resolved dict.

**Alternative**: Use a sentinel string like `"__UNSET__"`. Rejected — `None` is idiomatic Python and avoids collision with legitimate values.

### 3. Expand multi-entry actions at parse/construction time

A YAML customization with `replace: [{selector: ..., variable: ...}, ...]` is expanded into N individual action objects, one per entry. Each holds a single `selector` and the resolved `value`.

**Alternative**: Keep the list internally and have actions loop + skip unset entries. Rejected — pushing noop logic into every action duplicates responsibility and complicates the action interface.

### 4. Inject all dependencies at action construction

Actions receive `value`, `target` (absolute path to file in staging dir), and `values_dir` (for `file_replace` source resolution) at construction time. `apply()` takes no arguments.

**Alternative**: Pass `work_dir` and `values_dir` to `apply()`. Rejected — the user's preference is to make actions fully self-contained at construction.

### 5. Skip unset variables during action construction

The engine builds the resolved variables dict (only set keys), then iterates customization entries. For each entry, if the referenced variable is absent from the dict, the action is not created. No filtering loop needed later — the action list only contains executable actions.

**Alternative**: Create all actions, mark some as noop, filter before execution. Rejected — unnecessary complexity; not creating the action is simpler than creating and skipping it.

### 6. `file_replace` source path resolved at construction

`file_replace` uses its variable value as a file path. The absolute source path (`values_dir / value`) is resolved at construction and stored on the action. `apply()` copies from `source_path` to `target` without needing `values_dir`.

### 7. Target file collection remains a class-level concern

`target_files()` is needed before staging dir creation (to know which files to copy). Since actions are constructed after staging, `target_files()` must work from the raw YAML data, not from action instances. This means the engine extracts `file` fields from customization entries directly, before action construction.

**Alternative**: Two-phase construction (create actions for target_files, then inject paths). Rejected — over-engineered for extracting a `file` field from a dict.

## Risks / Trade-offs

**Breaking change to template YAML format** — Existing templates using dict-style variables will break. This is acceptable since the project is pre-1.0 and no external consumers exist yet.

**Single-variable actions increase object count** — A customization with 5 replace entries becomes 5 action objects instead of 1. This is negligible for the expected scale of templates.

**`target_files()` extracted from raw YAML, not from actions** — Slight duplication of knowing which field holds the file path. Mitigated by keeping the extraction simple (just read `file` key from each customization entry).
