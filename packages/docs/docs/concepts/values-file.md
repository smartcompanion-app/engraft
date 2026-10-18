# Values file

The values file carries one consumer's choices. It belongs to that consumer,
not to the project, and it is normally kept outside the project repository —
one per brand, customer or deployment.

There is no required filename; `engraft.values.yml` is the convention.

## Shape

A flat mapping from variable name to value. That is the whole format.

```yaml
app_name: acme-portal
page_title: Acme Portal
primary_color: "#0055ff"
logo: ./brand/acme-logo.svg
```

Nesting is not supported — the keys correspond one-to-one with the names under
`variables` in the [template file](template-file.md).

## Values are strings

Every value is used as text, so non-string scalars are coerced:

```yaml
version: 2 # the string "2"
enabled: true # the string "true"
ratio: 1.5 # the string "1.5"
```

That is almost always what you want, since the destination is a JSON string, an
HTML attribute or a slice of source code. It does mean `json_replace` writes
`"2"`, not `2` — engraft replaces text, it does not retype JSON.

## Unknown and omitted keys

- A key that no template variable declares is **ignored**. Values files
  outlive template changes, so a stale key is not treated as an error.
- A variable the values file does not mention falls back to its `default`.
- A key set explicitly to `null` counts as **not provided** — same as leaving
  it out, so the default applies:

  ```yaml
  app_name: null # identical to omitting the line
  ```

- An empty string is a real value, not an absence. `app_name: ""` writes an
  empty string.

See [Variables](variables.md) for how this interacts with variables that have
no default.

## Source paths

A value consumed by [`file_replace`](../actions/file-replace.md) is a path, and
it resolves **relative to the directory holding the values file** — not the
working directory.

```
brands/
  acme/
    engraft.values.yml    logo: ./logo.svg
    logo.svg              ← this one
```

That keeps a consumer's values and their assets together, so the whole folder
can be moved or committed somewhere else as a unit.

## YAML 1.2

Values files are parsed as **YAML 1.2**, which matters for a specific class of
surprise. In YAML 1.1, the bare words `yes`, `no`, `on` and `off` parse as
booleans; under 1.2 they are plain strings.

```yaml
feature_flag: no # the string "no", not false
country: NO # the string "NO", not false
```

Only `true` and `false` are booleans — and since every value is coerced to a
string anyway, they arrive as `"true"` and `"false"`.

A values file must hold a single YAML document. An empty file is valid and
means "no overrides"; every variable falls back to its default.
