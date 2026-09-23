# Template file

The template declares what a project exposes for customization. It ships with
the project, and it is the only engraft-specific file in the repository.

There is no required filename; `engraft.template.yml` is the convention.

## Shape

```yaml
variables:
  <name>:
    description: <what this controls>
    default: <the value the repository currently holds>

customizations:
  - action: <action name>
    file: <path, relative to the working directory>
    # ...action-specific fields
```

Both top-level keys are optional. A template with no `variables` resolves
nothing; a template with no `customizations` does nothing. Neither is an error.

## `variables`

A mapping from variable name to its declaration.

| Field         | Required | Meaning                                                                                                                                                           |
| ------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `description` | No       | What this variable controls. Not used at apply time — it is documentation for whoever writes the values file, and it is the only place that documentation exists. |
| `default`     | No       | The value to use when the values file does not provide one.                                                                                                       |

Leaving `default` out is meaningful: it makes the variable **optional**, and
any customization referring to it is skipped when no value is supplied. See
[Variables](variables.md).

Defaults should record what the repository actually contains today. That makes
the template double as a map of the customization surface — read the defaults
and you know what the unbranded product looks like.

```yaml
variables:
  app_name:
    description: Application name shown in the UI and the app store listing
    default: DefaultApp

  support_email:
    description: Address shown on the error screen
    default: support@example.com

  logo:
    description: Replacement logo, as a path relative to the values file
    # Optional: no default means "leave the bundled logo alone".
```

## `customizations`

An ordered list. Each entry names an `action` and the `file` it targets;
everything else depends on the action.

```yaml
customizations:
  - action: json_replace
    file: package.json
    replace:
      - selector: $.name
        variable: app_name
      - selector: $.author.email
        variable: support_email

  - action: file_replace
    file: public/logo.svg
    variable: logo
```

Actions run **in the order they appear**. Two actions targeting the same file
both see the earlier one's result, because both work against the same staging
copy.

`file` paths resolve against the current working directory — the project being
customized — not against the template's own location.

An `action` name that is not registered is an error naming the ones that are.
The four available actions are documented under [Actions](../actions/index.md).

## Grouping

Group by file, not by variable. One action entry covers one file and lists
every selector inside it:

```yaml
# Good — one pass over package.json
- action: json_replace
  file: package.json
  replace:
    - selector: $.name
      variable: app_name
    - selector: $.description
      variable: app_description
```

```yaml
# Works, but reads the file twice and scatters package.json across the template
- action: json_replace
  file: package.json
  replace:
    - selector: $.name
      variable: app_name
- action: json_replace
  file: package.json
  replace:
    - selector: $.description
      variable: app_description
```

## YAML notes

Templates are parsed as YAML 1.2, so `yes`, `no`, `on` and `off` are strings,
not booleans. See [Values file](values-file.md#yaml-12) — the same rules apply
to both files.

Quote regex selectors in single quotes so backslashes survive:

```yaml
- selector: '(PRIMARY_COLOR\s*=\s*)"(?<value>[^"]*)"'
```
