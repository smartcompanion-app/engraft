# Optional Variables with Noop Semantics

## Problem

Today every variable requires a `default`. If no default is given, it silently resolves to an empty string, which corrupts target files. There is no way to define an optional customization point — one that only applies when the consumer explicitly provides a value.

## Proposed Change

1. **Make `default` optional** — a variable without a default is "unset" unless the values file provides it.
2. **Switch variables to array format** — consistent with `customizations`, using `- variable: name` instead of dict keys.
3. **Flatten actions to single-variable** — each action operates on exactly one variable with one selector. Multi-entry `replace` lists in YAML are expanded at parse time.
4. **Fully resolve actions at construction** — actions receive their resolved value, target path (via `work_dir`/`staging_dir`), and source dir (`values_dir`) at construction time. `apply()` becomes a zero-argument method.
5. **Skip unset variables** — actions referencing unset variables are simply not created. No noop logic in actions themselves.

## Template YAML Format Change

```yaml
# Before
variables:
  app_name:
    description: "Application name"
    default: "MyApp"
  theme_color:
    description: "Primary color"

# After
variables:
  - variable: app_name
    description: "Application name"
    default: "MyApp"
  - variable: theme_color
    description: "Primary color"
```

## Engine Flow

```
1. Parse template YAML → variables list + raw customization entries
2. Parse values YAML → flat dict
3. Resolve variables: merge defaults + values → dict (only set keys)
4. Create staging dir
5. Copy target files into staging
6. Expand customization entries into single-variable actions,
   skipping any entry whose variable is absent from resolved dict.
   Inject resolved value + staging_dir + values_dir at construction.
7. Execute: for action in actions: action.apply()
8. Copy back, clean up staging
```

## Impact

- **models.py**: `Variable.default` becomes `str | None`, parse variables from array format
- **engine.py**: new resolution + expansion + filtering logic, action construction with all deps
- **actions/base.py**: `apply()` signature becomes `apply(self) -> None`
- **All action classes**: hold resolved value + paths as fields, drop internal loops
- **Specs**: update `variable-resolution`, `engine`, `unified-action-format`
- **Tests**: update to match new YAML format and action construction
