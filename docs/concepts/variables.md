# Variables

A variable connects a name in the values file to one or more places in the
project. Actions never contain literal values — they reference a variable, and
engraft resolves it once, before any action runs.

## Resolution

For each variable declared in the template:

1. If the values file provides it, that value wins.
2. Otherwise, the template's `default` is used.
3. If there is no `default` either, the variable resolves to **nothing**.

```yaml
# template
variables:
  app_name:
    description: Application name
    default: DefaultApp
```

| Values file           | `app_name` resolves to |
| --------------------- | ---------------------- |
| `app_name: CustomApp` | `CustomApp`            |
| `app_name: ""`        | `""` (empty string)    |
| `app_name: null`      | `DefaultApp`           |
| (not mentioned)       | `DefaultApp`           |

Resolution happens once, up front. Every action sees the same resolved values,
so an action cannot change what a later action reads.

## Optional variables

A variable declared with no `default` and left out of the values file resolves
to nothing — and every customization referring to it is **skipped**. The
target file is left exactly as it is.

```yaml
variables:
  logo:
    description: Replacement logo, relative to the values file
    # no default

customizations:
  - action: file_replace
    file: public/logo.svg
    variable: logo
```

With no `logo:` line in the values file, `public/logo.svg` is untouched. Supply
one and it is replaced.

This is how a template offers customizations that not every consumer wants. The
alternative — a default pointing at the file that is already there — would make
every apply rewrite a file with its own contents.

Skipping is per entry, not per action. In a `replace` list, entries whose
variables resolved to nothing are skipped and the rest still apply.

### Empty string is not "nothing"

```yaml
app_name: ""
```

This is a value. It resolves to the empty string and is written. Use `null` or
omit the key to mean "leave it alone".

## Undeclared variables

An action may reference a variable the template does not declare under
`variables`. It resolves to nothing, so the entry is skipped — the same as an
optional variable with no value.

This is deliberate: a values file can outlive a template edit without the apply
falling over. It also means a typo in a variable name fails silently, so check
the diff after adding a customization.

## Naming

Names are plain YAML keys. `snake_case` is the convention, matching the action
names:

```yaml
variables:
  app_name:
  primary_color:
  support_email:
```

Because names are the contract between the template and every values file
written against it, renaming one is a breaking change for consumers: their
existing key becomes an ignored unknown key, and the variable silently falls
back to its default.
