# Actions

An action is one entry under `customizations` in the [template
file](../concepts/template-file.md). It names a file and describes what to
change inside it.

engraft ships four.

| Action                              | Use it for                             | Selector syntax                                |
| ----------------------------------- | -------------------------------------- | ---------------------------------------------- |
| [`json_replace`](json-replace.md)   | JSON files                             | Dot path — `$.expo.extra.items[0].label`       |
| [`html_replace`](html-replace.md)   | HTML files                             | XPath — `//meta[@name='description']/@content` |
| [`regex_replace`](regex-replace.md) | Any text file — source code, INI, TOML | Regex with a `value` capture group             |
| [`file_replace`](file-replace.md)   | Whole files, including binaries        | None — the file is the unit                    |

## Choosing one

Reach for the **format-aware** action when there is one. `json_replace` parses
the document, so `$.name` means the `name` key wherever it sits in the file and
however it is formatted. A regex that happens to match `"name": "..."` today
breaks the first time someone reformats or adds a second `name` key deeper in.

`regex_replace` is the general-purpose escape hatch, and the only option for
source code, config formats engraft does not parse, and anything where the
value is embedded in a larger string.

`file_replace` is for the cases where nothing inside the file is being
edited — an icon, a font, a whole config file swapped for another.

## Common shape

Every action takes a `file`, relative to the current working directory:

```yaml
- action: json_replace
  file: config/app.json
```

The three value-replacing actions take a `replace` list of
`{selector, variable}` pairs, applied in order to the same file:

```yaml
- action: json_replace
  file: package.json
  replace:
    - selector: $.name
      variable: app_name
    - selector: $.description
      variable: app_description
```

`file_replace` is the exception: it takes a flat `variable` instead, because
there is nothing inside the file to select.

```yaml
- action: file_replace
  file: assets/logo.png
  variable: logo
```

## Rules that hold for all of them

- **A `replace` entry whose variable resolves to nothing is skipped**, leaving
  that part of the file untouched. See
  [Variables](../concepts/variables.md#optional-variables).
- **A missing target file is an error**, and the error aborts the whole apply.
- **Actions run in template order**, against a staging copy. If any action
  fails, nothing is written. See [Architecture](../architecture.md).
- **Values are text.** A number in the values file arrives as a string.

## Adding an action

Actions are a plugin registry — see
[Contributing](../../CONTRIBUTING.md#adding-an-action).
