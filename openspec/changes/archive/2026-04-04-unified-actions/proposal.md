## Why

The four engraft actions (`json_set`, `replace_value`, `replace_file`) each use a different YAML configuration shape — different field names, different structures for specifying what to replace. This makes the template format harder to learn and inconsistent to read. Additionally, there is no action for modifying HTML files, which is a common need (e.g., setting `<title>`, `<meta>` tags).

## What Changes

- **BREAKING**: Rename and restructure all existing actions to a unified YAML format:
  - `json_set` → `json_replace` — `set` dict becomes `replace` list with `{selector, variable}` entries; selectors use `$.` prefix (JSONPath-like)
  - `replace_value` → `regex_replace` — `pattern`/`replace` fields become `replace` list with `{selector, variable}` entries; selector is the regex pattern (keeps `(?P<value>...)` named group semantics)
  - `replace_file` → `file_replace` — `source`/`target` fields become flat `file` (target path) + `variable` (source path variable)
- **New**: `html_replace` action for modifying HTML element text content and attributes using XPath selectors, powered by `lxml`
- Three of four actions share a `replace: [{selector, variable}]` list structure; `file_replace` uses a simpler flat format since it doesn't need multiple selectors per action

## Capabilities

### New Capabilities
- `html-replace`: HTML document modification via XPath selectors — supports setting element text content and attribute values, single-match enforcement
- `unified-action-format`: Consistent YAML structure across all actions using `replace` list with `{selector, variable}` entries (except `file_replace`)

### Modified Capabilities

_(No existing specs to modify)_

## Impact

- **Action files**: All three existing action files renamed and refactored (`json_set.py` → `json_replace.py`, `replace_value.py` → `regex_replace.py`, `replace_file.py` → `file_replace.py`)
- **New file**: `html_replace.py`
- **Registry**: `src/engraft/actions/__init__.py` updated with new imports and registration names
- **Template parsing**: `src/engraft/models.py` updated to handle new YAML action format
- **Dependencies**: `lxml` added to `pyproject.toml`
- **Tests**: All existing action tests rewritten; new tests for `html_replace`
- **Breaking change**: Existing template YAML files using old action names/formats will need to be updated
