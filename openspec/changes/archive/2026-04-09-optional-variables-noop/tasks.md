## 1. Models and Variable Parsing

- [x] 1.1 Update `Variable` dataclass: change `default: str` to `default: str | None`
- [x] 1.2 Rewrite `parse_template` to parse variables from array format (`- variable: name`) with optional `default`
- [x] 1.3 Add duplicate variable name detection in `parse_template`
- [x] 1.4 Update/add tests for new variable parsing (array format, optional default, duplicates)

## 2. Action Base Class and Subclasses

- [x] 2.1 Change `Action.apply()` signature to `apply(self) -> None` (no parameters)
- [x] 2.2 Refactor `JsonReplace`: single `selector: str`, `value: str`, `target: Path` fields; remove `replace` list and internal loop
- [x] 2.3 Refactor `RegexReplace`: single `selector: str`, `value: str`, `target: Path` fields; remove `replace` list and internal loop
- [x] 2.4 Refactor `HtmlReplace`: single `selector: str`, `value: str`, `target: Path` fields; remove `replace` list and internal loop
- [x] 2.5 Refactor `FileReplace`: `source_path: Path`, `target: Path` fields; resolve source at construction
- [x] 2.6 Remove `target_files()` from `Action` ABC (no longer needed on instances)
- [x] 2.7 Update/add tests for all refactored action classes

## 3. Engine Refactor

- [x] 3.1 Implement variable resolution: merge defaults + values, omit unset variables from dict
- [x] 3.2 Extract target files from raw YAML customization entries (before action construction)
- [x] 3.3 Implement action expansion: iterate customization entries, expand `replace` lists, skip entries with unset variables, construct actions with resolved value + paths
- [x] 3.4 Simplify execution loop to `action.apply()` with no arguments
- [x] 3.5 Update/add engine tests: unset variable skipping, mixed set/unset, full apply flow

## 4. Action Registry Update

- [x] 4.1 Update `create_action` / registry to support new constructor signatures (value, target, values_dir)
- [x] 4.2 Update action imports and registration in `actions/__init__.py`

## 5. Integration and CLI

- [x] 5.1 Run full test suite and fix any regressions
- [x] 5.2 Run ruff lint and format checks, fix issues
