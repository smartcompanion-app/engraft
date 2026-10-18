# CLI reference

```
engraft [options] [command]
```

## `engraft apply`

Applies a template with a set of values to the current directory.

```shell
engraft apply --template <path> --values <path>
```

| Option              | Required | Meaning                                                |
| ------------------- | -------- | ------------------------------------------------------ |
| `--template <path>` | Yes      | Path to the [template file](concepts/template-file.md) |
| `--values <path>`   | Yes      | Path to the [values file](concepts/values-file.md)     |

Both paths may be absolute or relative to where you run the command.

**The target is the current working directory.** `file:` paths in the template
resolve against it, so `cd` into the project first:

```shell
cd my-project
engraft apply \
  --template engraft.template.yml \
  --values ../brands/acme/engraft.values.yml
```

On success:

```
Done. Customizations applied successfully.
```

On failure, a message on stderr and exit code 1:

```
Error: XPath selector "//title" matched no elements in index.html
```

A failed apply leaves the project exactly as it was — see
[Architecture](architecture.md).

## `engraft --version`

Prints the installed version and exits.

```shell
$ engraft --version
0.2.2
```

## `engraft --help`

Prints usage. `engraft apply --help` prints the options for `apply`.

## Exit codes

| Code | Meaning                                                                                                                            |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `0`  | Every customization applied                                                                                                        |
| `1`  | Something failed — a missing file, malformed YAML, an unknown action, or an action that could not do its job. Nothing was written. |

Which makes it usable in a pipeline as-is:

```shell
set -e
engraft apply --template engraft.template.yml --values "$BRAND/engraft.values.yml"
npm run build
```

## Errors you are likely to meet

| Message                                    | Usually means                                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `ENOENT … engraft.template.yml`            | The template path is wrong, or you are in the wrong directory                                                       |
| `Unknown action: "json_set". Available: …` | An action name from an older template, or a typo                                                                    |
| `XPath selector "…" matched no elements`   | The page changed, or the selector has a typo — see [`html_replace`](actions/html-replace.md)                        |
| `Pattern "…" did not match anything`       | The regex anchors on a value that has already been replaced — see [`regex_replace`](actions/regex-replace.md)       |
| `Target file does not exist: …`            | [`file_replace`](actions/file-replace.md) only swaps files that are already there                                   |
| `Source file does not exist: …`            | The source path resolves against the **values file**, not the project                                               |
| Nothing happened, exit 0                   | Every variable involved resolved to nothing — check the names in the values file against the template's `variables` |

## Installing

```shell
npm install -g @smartcompanion/engraft
```

Or without installing:

```shell
npx @smartcompanion/engraft apply --template … --values …
```

Requires Node 22.22.2 or newer. Each release is published from CI with a
provenance attestation; `npm audit signatures` verifies it.
