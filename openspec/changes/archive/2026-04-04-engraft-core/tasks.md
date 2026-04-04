# Tasks: engraft-core

## 1. Project scaffolding
- [x] Create `pyproject.toml` with hatchling build system, project metadata, CLI entry point (`engraft = "engraft.cli:main"`), and dependencies (click, pyyaml)
- [x] Create `src/engraft/__init__.py` with version
- [x] Create directory structure: `src/engraft/actions/`, `tests/`, `tests/test_actions/`
- [x] Verify `pip install -e .` works and `engraft --help` runs

## 2. Action base class and registry
- [x] Create `src/engraft/actions/base.py` with `Action` ABC: abstract `apply(self, variables: dict[str, str], work_dir: Path, values_dir: Path) -> None`
- [x] Create `src/engraft/actions/__init__.py` with a registry that maps action name strings (e.g. `"replace_value"`) to Action subclasses
- [x] Add a factory function `create_action(action_name: str, **config) -> Action` that instantiates the right subclass from template YAML data

## 3. Data models and parsing
- [x] Create `src/engraft/models.py` with dataclasses:
  - `Variable`: name, description, default
  - `Template`: variables dict, customizations list (list of `Action` instances)
- [x] Add parsing logic to load template YAML into `Template` model, using the action factory to instantiate `Action` subclasses from the `customizations` list
- [x] Add parsing logic to load values YAML into a flat dict

## 4. Core engine
- [x] Create `src/engraft/engine.py` with `apply(template_path, values_path)` function
- [x] Implement variable resolution: merge values over defaults
- [x] Implement customization loop: `for action in template.customizations: action.apply(variables, work_dir, values_dir)`
- [x] Handle path resolution: work_dir from cwd, values_dir from values file parent

## 5. Action: `ReplaceValue`
- [x] Create `src/engraft/actions/replace_value.py` with `ReplaceValue(Action)` dataclass
- [x] Fields: `file: str`, `pattern: str`, `replace: str` (variable name)
- [x] Implement `apply()`: regex matching with `(?P<value>...)` named group replacement
- [x] Error if pattern has no `<value>` named group
- [x] Error if pattern doesn't match anything in the file
- [x] Write tests: basic replacement, multiple matches in file, re-application with changed values

## 6. Action: `JsonSet`
- [x] Create `src/engraft/actions/json_set.py` with `JsonSet(Action)` dataclass
- [x] Fields: `file: str`, `set: dict[str, str]` (dot_path → variable name)
- [x] Implement `apply()`: dot-path parsing including `[n]` array index notation
- [x] Implement value setting at parsed path (create intermediate keys if missing)
- [x] Preserve JSON formatting (read with json.load, write with json.dumps indent=2)
- [x] Write tests: simple path, nested path, array index path, missing intermediate key creation

## 7. Action: `ReplaceFile`
- [x] Create `src/engraft/actions/replace_file.py` with `ReplaceFile(Action)` dataclass
- [x] Fields: `source: str` (variable name), `target: str`
- [x] Implement `apply()`: resolve source from `values_dir`, target from `work_dir`, copy file
- [x] Error if source file doesn't exist
- [x] Write tests: basic file replacement, binary file (image) replacement

## 8. CLI
- [x] Create `src/engraft/cli.py` with click
- [x] Implement `engraft apply --template <path> --values <path>` command
- [x] Add clear error messages for: missing files, invalid YAML, action errors
- [x] Write CLI integration tests using click's CliRunner

## 9. End-to-end test
- [x] Create a test fixture with a mock project (JSON file, TS file, image)
- [x] Create a test template and values file exercising all three actions
- [x] Verify full `engraft apply` produces expected output
- [x] Test re-application: apply twice with different values, verify second apply works correctly
