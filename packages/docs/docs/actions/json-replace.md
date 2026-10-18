# `json_replace`

Sets values in a JSON file, addressed by a dot path.

```yaml
- action: json_replace
  file: app.json
  replace:
    - selector: $.expo.name
      variable: app_name
    - selector: $.expo.extra.items[0].label
      variable: first_item_label
```

| Field                | Meaning                                          |
| -------------------- | ------------------------------------------------ |
| `file`               | The JSON file, relative to the working directory |
| `replace[].selector` | Dot path to the value to set                     |
| `replace[].variable` | The variable supplying the new value             |

## Selectors

A selector is a `$.`-prefixed path of keys, with `[n]` for array indices:

| Selector           | Targets                                 |
| ------------------ | --------------------------------------- |
| `$.name`           | The top-level `name` key                |
| `$.expo.name`      | `name` inside the `expo` object         |
| `$.icons[0].sizes` | `sizes` on the first element of `icons` |
| `$.a.b[2].c.d`     | Nesting and indices mix freely          |

The `$.` prefix is stripped if present and optional — `name` and `$.name` are
the same selector. Use it anyway; it reads as a path rather than a key.

This is a deliberately small subset of JSONPath. There are no wildcards, no
filters and no recursive descent: a selector addresses exactly one location.

## Example

```json
{
  "name": "default-app",
  "version": "1.0.0",
  "icons": [{ "src": "icon.png", "sizes": "192x192" }]
}
```

```yaml
- action: json_replace
  file: manifest.json
  replace:
    - selector: $.name
      variable: app_name
    - selector: $.icons[0].sizes
      variable: icon_size
```

```yaml
app_name: acme-portal
icon_size: 512x512
```

```json
{
  "name": "acme-portal",
  "version": "1.0.0",
  "icons": [{ "src": "icon.png", "sizes": "512x512" }]
}
```

## Values are written as strings

engraft replaces text, so every value lands as a JSON string:

```yaml
version: 2
```

```json
{ "version": "2" }
```

If a target has to stay a number or a boolean, use
[`regex_replace`](regex-replace.md), which writes into the file without
retyping the document.

## Formatting

The file is parsed and re-serialised, so the output is normalised: two-space
indentation, a trailing newline, and whatever key order the original had
(insertion order is preserved by the parse). Comments are not preserved,
because JSON has none — if the file is really JSONC, use
[`regex_replace`](regex-replace.md).

Re-serialising is also why a `json_replace` on a file no one customized still
shows up in a diff if that file was formatted differently. Run engraft once and
commit the normalisation on its own.

## Errors

| Situation                                                     | Result                                                        |
| ------------------------------------------------------------- | ------------------------------------------------------------- |
| The file does not exist                                       | Error; the apply aborts                                       |
| The file is not valid JSON                                    | Error; the apply aborts                                       |
| An index part-way along the path is past the end of its array | Error naming the index                                        |
| The path descends through a non-object                        | Error naming the key                                          |
| A missing intermediate key                                    | Created — an object, or an array if the next step is an index |
| The **final** index is past the end of its array              | The array is extended with `null`s up to that index           |
| The variable resolved to nothing                              | The entry is skipped; the file is untouched                   |

Two of those are worth reading twice. Missing intermediate keys are created, so
a selector can add a key the file does not have yet — and a typo in a path
grows a new key instead of failing. A trailing index past the end extends the
array rather than erroring, so `$.items[3]` on a one-element array leaves two
`null` holes behind. Neither shows up as an error, so check the diff after
adding a customization.
