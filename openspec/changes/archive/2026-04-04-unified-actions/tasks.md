## 1. Dependencies and Setup

- [x] 1.1 Add `lxml` to `pyproject.toml` dependencies

## 2. Refactor Existing Actions

- [x] 2.1 Rename `json_set.py` to `json_replace.py` — update class to `JsonReplace`, register as `json_replace`, change `set: dict` field to `replace: list[dict[str, str]]`, strip `$.` prefix from selectors before parsing
- [x] 2.2 Rename `replace_value.py` to `regex_replace.py` — update class to `RegexReplace`, register as `regex_replace`, change fields to `replace: list[dict[str, str]]`, iterate over replace entries applying existing named-group substitution logic
- [x] 2.3 Rename `replace_file.py` to `file_replace.py` — update class to `FileReplace`, register as `file_replace`, change fields to `file: str` (target) + `variable: str` (source variable name)

## 3. Update Registry

- [x] 3.1 Update `src/engraft/actions/__init__.py` — change imports to new module names (`json_replace`, `regex_replace`, `file_replace`, `html_replace`)

## 4. Implement html_replace

- [x] 4.1 Create `src/engraft/actions/html_replace.py` — `HtmlReplace` dataclass with `file: str` and `replace: list[dict[str, str]]`, parse HTML with `lxml.html`, apply XPath selectors, enforce single-match, handle element text vs attribute, serialize with `method="html"` and preserve DOCTYPE

## 5. Update Tests

- [x] 5.1 Rename and update `test_json_set.py` to `test_json_replace.py` — test `$.` prefix selectors, multiple replacements per action, nested paths, array indices
- [x] 5.2 Rename and update `test_replace_value.py` to `test_regex_replace.py` — test replace list format, multiple replacements, named group validation, no-match error
- [x] 5.3 Rename and update `test_replace_file.py` to `test_file_replace.py` — test new flat `file`/`variable` format, missing source error
- [x] 5.4 Create `test_html_replace.py` — test element text replacement, attribute replacement, single-match enforcement (0 matches error, >1 matches error), DOCTYPE preservation, multiple replacements per action

## 6. Integration

- [x] 6.1 Update `test_cli.py` and `test_e2e.py` to use new action names and YAML format
- [x] 6.2 Run full test suite and fix any remaining issues
