## Context

engraft has three actions (`json_set`, `replace_value`, `replace_file`) each with a different YAML configuration shape. The template parser in `models.py` passes raw YAML fields directly to action constructors via `create_action(action_name, **item)`. Actions are dataclasses registered in `__init__.py`.

We are unifying the YAML format and adding `html_replace`. All design decisions were made during exploration.

## Goals / Non-Goals

**Goals:**
- Unified `replace: [{selector, variable}]` structure for `json_replace`, `html_replace`, and `regex_replace`
- New `html_replace` action with XPath selectors via `lxml`
- Clean rename of all actions to `*_replace` naming convention
- Multiple replacements per action block (already natural with list format)

**Non-Goals:**
- Full JSONPath implementation (wildcards, filters, recursive descent) — keep simple path parsing
- Support for multi-match XPath results — single match enforced
- Backwards compatibility with old action names/formats — this is a breaking change

## Decisions

### 1. YAML format: list of `{selector, variable}` vs current mixed formats

Three actions use `replace: [{selector, variable}]`. `file_replace` stays flat with `file` + `variable` since it doesn't select within a file.

**Why not force `file_replace` into the same shape?** The `selector` would mean "target path" — semantically misleading. A flat format is more honest about what the action does.

### 2. `json_replace` selector: `$.` prefix with existing parser

Selectors use `$.name`, `$.expo.items[0].label`. Implementation strips the `$.` prefix and feeds into the existing `_parse_path` function.

**Alternative considered:** Full JSONPath library (`python-jsonpath`). Rejected — adds a dependency for power we don't need. Simple dot-path with array indexing covers all use cases.

### 3. `html_replace`: `lxml` for HTML parsing + XPath

Use `lxml.html.parse()` / `lxml.html.fromstring()` to parse HTML, `xpath()` to select nodes, and `lxml.html.tostring()` with `method="html"` to serialize.

**XPath result handling:**
- Attribute XPath (e.g., `//meta[@name="Description"]/@content`) returns `lxml.etree._ElementStringResult` — detect via `isinstance` or `getparent()`/`attrname` and set attribute on parent element
- Element XPath (e.g., `//title`) returns `Element` — set `.text` property

**Single-match enforcement:** If `len(results) == 0`, raise error: "XPath selector matched no elements". If `len(results) > 1`, raise error: "XPath selector matched {n} elements, expected exactly 1".

**Serialization:** Use `lxml.html.tostring(doc, encoding="unicode", method="html")` to preserve HTML conventions (no self-closing void elements). Preserve the original `<!DOCTYPE>` declaration by reading it from the original file and prepending it, since `lxml` may strip or alter it.

**Alternative considered:** `xml.etree.ElementTree` — can't parse real HTML (no self-closing void elements, DOCTYPE). `html.parser` with manual XPath — too much complexity for limited benefit.

### 4. `regex_replace`: keep `(?P<value>...)` semantics

The `selector` field contains the regex pattern including the named capture group. Same replacement logic as current `replace_value` — only the `(?P<value>...)` group content is replaced, surrounding match is preserved. Validate that pattern contains the named group.

### 5. Template parsing adaptation in `models.py`

Current parser does `item.pop("action")` then `create_action(action_name, **item)`. The new `replace` field is a list of dicts, which gets passed directly to the dataclass constructor. No change needed to the parsing dispatch — the dataclass fields just need to accept the new shape.

Action dataclasses change from varied fields to:
- `json_replace`, `html_replace`, `regex_replace`: `file: str`, `replace: list[dict[str, str]]`
- `file_replace`: `file: str`, `variable: str`

### 6. File structure

Rename files to match new action names:
- `json_set.py` → `json_replace.py`
- `replace_value.py` → `regex_replace.py`
- `replace_file.py` → `file_replace.py`
- New: `html_replace.py`

## Risks / Trade-offs

- **[Breaking change]** → All existing template YAML files must be updated. Acceptable since engraft is pre-1.0 and this is the right time for breaking changes.
- **[`lxml` C dependency]** → Adds native dependency. Mitigated: ships prebuilt wheels for all major platforms, widely used, no user-visible install friction.
- **[HTML serialization fidelity]** → `lxml` may alter whitespace or formatting slightly. Mitigated: use `method="html"` and preserve DOCTYPE manually. Minor whitespace differences are acceptable.
