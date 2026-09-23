# Getting started

## Install

engraft needs Node 22.22.2 or newer.

```shell
npm install -g @smartcompanion/engraft
```

Or run it without installing:

```shell
npx @smartcompanion/engraft --version
```

## Your first customization

Start with a project that already works. Say it has a `config.json`:

```json
{
  "name": "DefaultApp",
  "version": "1.0.0"
}
```

### 1. Declare what can be customized

Create `engraft.template.yml`. This is the file the project's maintainer owns —
it describes the customization surface, and it ships with the repository.

```yaml
variables:
  app_name:
    description: Application name shown in the UI
    default: DefaultApp

customizations:
  - action: json_replace
    file: config.json
    replace:
      - selector: $.name
        variable: app_name
```

Two halves, and they stay separate on purpose:

- `variables` names the things that can change, documents them, and records
  what the repository currently holds.
- `customizations` says where each one lives. One entry per file, listing the
  selectors inside it.

### 2. Supply the values

Create `engraft.values.yml`. This is the consumer's file — one per brand,
customer or deployment, and it does not belong in the project repository.

```yaml
app_name: MyApp
```

### 3. Apply

From the project directory:

```shell
engraft apply --template engraft.template.yml --values engraft.values.yml
```

`config.json` now reads:

```json
{
  "name": "MyApp",
  "version": "1.0.0"
}
```

Nothing else moved. Run it again with a different values file and you get a
different result from the same repository.

## A more realistic template

Real customizations span several files and several kinds of file. Each action
handles one format:

```yaml
variables:
  app_name:
    description: Application name
    default: DefaultApp
  page_title:
    description: Browser tab title
    default: Default App
  primary_color:
    description: Brand colour, as a CSS hex value
    default: "#ff0000"
  logo:
    description: Path to a replacement logo, relative to this values file
    # No default: leave it out of the values file and the logo is untouched.

customizations:
  - action: json_replace
    file: package.json
    replace:
      - selector: $.name
        variable: app_name

  - action: html_replace
    file: public/index.html
    replace:
      - selector: //title
        variable: page_title

  - action: regex_replace
    file: src/theme.ts
    replace:
      - selector: '(PRIMARY_COLOR\s*=\s*)"(?<value>[^"]*)"'
        variable: primary_color

  - action: file_replace
    file: public/logo.svg
    variable: logo
```

```yaml
app_name: acme-portal
page_title: Acme Portal
primary_color: "#0055ff"
logo: ./brand/acme-logo.svg
```

Each action is documented in full under [Actions](actions/index.md).

## What to know before you run it on something you care about

- **engraft writes to the current working directory.** `file:` paths in the
  template resolve against wherever you run it, not against the template's
  location.
- **An apply is all-or-nothing.** Every action runs against a staging copy
  first; if one fails, your project is left exactly as it was. See
  [Architecture](architecture.md).
- **It edits in place, with no backup.** Run it on a clean git working tree so
  you can read the diff — and undo it with `git checkout` if you don't like it.

## Next

- [Concepts](concepts/index.md) — the two-file model in detail
- [Actions](actions/index.md) — the four actions and when to reach for each
- [CLI reference](cli.md)
