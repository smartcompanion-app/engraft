# `file_replace`

Replaces a file wholesale with one supplied by the consumer. Binary-safe — the
file is copied, not parsed.

```yaml
- action: file_replace
  file: public/logo.svg
  variable: logo
```

| Field      | Meaning                                                             |
| ---------- | ------------------------------------------------------------------- |
| `file`     | The file to replace, relative to the working directory              |
| `variable` | A variable holding the **source path**, relative to the values file |

This action has no `replace` list. There is nothing inside the file to select:
the file is the unit.

## Source paths

The variable's value is a path resolved against the directory holding the
[values file](../concepts/values-file.md), not the working directory. That
keeps a consumer's assets next to their values:

```
brands/
  acme/
    engraft.values.yml
    logo.svg
    icon-512.png
  globex/
    engraft.values.yml
    logo.svg
```

```yaml
# brands/acme/engraft.values.yml
logo: ./logo.svg
app_icon: ./icon-512.png
```

The whole `brands/acme/` folder can then be moved, committed elsewhere or
handed to someone else as one self-contained thing.

## Example

```yaml
# template
variables:
  logo:
    description: Replacement logo, relative to this values file
  app_icon:
    description: 512×512 app icon, relative to this values file

customizations:
  - action: file_replace
    file: public/logo.svg
    variable: logo
  - action: file_replace
    file: public/icon-512.png
    variable: app_icon
```

```yaml
# values
logo: ./logo.svg
app_icon: ./icon-512.png
```

```shell
cd my-project
engraft apply \
  --template engraft.template.yml \
  --values ../brands/acme/engraft.values.yml
```

## The target must already exist

Replacing a file that is not there is an error, not a copy:

```
Target file does not exist: /path/to/project/public/logo.svg
```

`file_replace` swaps something out; it does not add files to a project. A file
the project does not have is not part of its customization surface, and a
template that could create arbitrary paths would be a much bigger thing to
trust. If you need a new file, add it to the project with sensible default
contents and make it replaceable.

## Leaving the original in place

Declare the variable with **no default** and omit it from the values file. The
action is then skipped and the bundled file is untouched — see
[optional variables](../concepts/variables.md#optional-variables).

```yaml
variables:
  logo:
    description: Replacement logo — omit to keep the bundled one
    # no default
```

This is the right way to make an asset optional. A default pointing at the file
that is already there would make every apply rewrite the file with its own
contents.

## Errors

| Situation                        | Result                                       |
| -------------------------------- | -------------------------------------------- |
| The target file does not exist   | Error naming the target path                 |
| The source file does not exist   | Error naming the resolved source path        |
| The variable resolved to nothing | The action is skipped; the file is untouched |

Since source paths resolve against the values file, a "source file does not
exist" error usually means the path was written relative to the project
instead. The error message shows the path engraft actually looked at.
