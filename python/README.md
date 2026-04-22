# engraft

Apply customizations to any project without templating placeholders.

## The Problem

Customizing a project (e.g., white-label products) forces a choice between bad options:

- **Templating tools** (Cookiecutter, Copier, Yeoman) require `{{ placeholders }}` in source code — the repo is no longer a working app
- **Forking** leads to diverging codebases that are painful to sync with upstream
- **Manual editing** is error-prone, undocumented, and impossible to reproduce

engraft solves this by keeping the source repo clean and runnable while providing a declarative, reproducible customization layer on top.

## How It Works

engraft uses a two-file model:

- **Template file** — defines what can be customized and how (maintained by the repo author)
- **Values file** — contains the consumer's customization values

The original project stays untouched. Run `engraft apply` and the customizations are applied in place.

## Installation

```
pip install engraft
```

## Quick Start

Given a project with a `config.json`:

```json
{
  "name": "DefaultApp",
  "version": "1.0.0"
}
```

Create a template file `engraft.template.yml`:

```yaml
variables:
  app_name:
    description: Application name
    default: DefaultApp

customizations:
  - action: json_replace
    file: config.json
    replace:
      - selector: $.name
        variable: app_name
```

Create a values file `engraft.values.yml`:

```yaml
app_name: MyApp
```

Apply:

```
engraft apply --template engraft.template.yml --values engraft.values.yml
```

Result — `config.json` now contains:

```json
{
  "name": "MyApp",
  "version": "1.0.0"
}
```

## Action Reference

### `json_replace`

Replace values in JSON files using JSONPath-like selectors.

```yaml
- action: json_replace
  file: app.json
  replace:
    - selector: $.expo.name
      variable: app_name
    - selector: $.expo.extra.items[0].label
      variable: item_label
```

Selectors use dot notation with optional array indices: `$.path.to.key` or `$.array[0].field`.

### `html_replace`

Replace values in HTML files using XPath selectors. Supports both element text and attribute values.

```yaml
- action: html_replace
  file: index.html
  replace:
    - selector: //title
      variable: page_title
    - selector: //meta[@name='description']/@content
      variable: page_description
```

The selector must match exactly one element or attribute. Matching zero or more than one is an error.

### `regex_replace`

Replace values in any text file using regex with a named capture group.

```yaml
- action: regex_replace
  file: src/theme.ts
  replace:
    - selector: '(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"'
      variable: primary_color
```

The selector **must** contain a named capture group called `value`. Both syntaxes are accepted:

- Python style: `(?P<value>...)`
- ECMAScript/JavaScript style: `(?<value>...)`

Using the ECMAScript form keeps templates portable between the Python and TypeScript implementations. Only the captured group is replaced; the surrounding match is preserved.

### `file_replace`

Replace an entire file with a source file referenced by a variable.

```yaml
- action: file_replace
  file: assets/logo.png
  variable: logo
```

The variable value is a path relative to the values file directory. Useful for binary files like images.

## Releasing

Versioning is automatic via [hatch-vcs](https://github.com/ofek/hatch-vcs) — the package version is derived from git tags.

To publish a new release:

1. Create a GitHub Release with a tag matching `vX.Y.Z` (e.g., `v0.2.0`)
2. The release pipeline automatically runs lint, format check, and tests
3. If all checks pass, the package is built and published to PyPI with Sigstore signing

## Values file notes

Values are parsed as YAML 1.2. The bare words `yes`, `no`, `on`, `off` (and their capitalized variants) parse as **strings**, not booleans — only `true` and `false` are coerced to booleans. If you are migrating a values file from older tooling that assumed YAML 1.1 boolean semantics, quote the value explicitly (`flag: "true"`) when a string was intended.

Non-string scalars (numbers, booleans) are coerced to strings before being substituted into target files. A key whose value is `null` is treated as "not provided" — the variable's default (or the noop sentinel for optional variables) is used instead.

## Development

Development commands are run from inside the `python/` directory:

```bash
cd python/

# Install with dev dependencies
pip install -e ".[dev]"

# Run unit tests
pytest

# Run linter
ruff check src/ tests/
```

The repo also has an end-to-end harness under `e2e/` (run from the repo root) that runs the same fixture scenarios against both the Python and TypeScript CLIs and asserts identical output.
