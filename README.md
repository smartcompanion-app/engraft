<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/engraft-logo-dark.svg">
    <img alt="engraft" src="assets/engraft-logo.svg" height="72">
  </picture>
</h1>

<p align="center">

[![ci](https://github.com/smartcompanion-app/engraft/actions/workflows/ci.yml/badge.svg)](https://github.com/smartcompanion-app/engraft/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/@smartcompanion/engraft)](https://www.npmjs.com/package/@smartcompanion/engraft)
[![node](https://img.shields.io/node/v/@smartcompanion/engraft)](https://nodejs.org)
[![license](https://img.shields.io/npm/l/@smartcompanion/engraft)](LICENSE)
[![docs](https://img.shields.io/badge/docs-smartcompanion--app.github.io%2Fengraft-1fbc7e)](https://smartcompanion-app.github.io/engraft/)

</p>

**Apply customizations to any project without templating placeholders.**

Your repository stays clean and runnable. The customization lives beside it, in
two files: one the maintainer writes, one the consumer writes.

```shell
npm install -g @smartcompanion/engraft
```

## The problem

White-labelling a project usually means picking the least bad option:

- **Templating tools** (Cookiecutter, Copier, Yeoman) put `{{ placeholders }}`
  in your source. The repository stops being a working app — you cannot run it,
  test it or open it without rendering it first.
- **Forking** gives you a working app and then two codebases that drift apart.
- **Editing by hand** works once, and nobody remembers which twelve files
  needed touching.

## How engraft works

Nothing in your source changes shape. `config.json` stays valid JSON,
`index.html` stays a page you can open. The customization is described
separately, by two files:

**The template** — written by the maintainer, shipped with the project. It
declares what can be customized and where it lives.

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

**The values** — written by the consumer, kept outside the project. One per
brand, customer or deployment.

```yaml
app_name: MyApp
```

Then, from the project directory:

```shell
engraft apply --template engraft.template.yml --values engraft.values.yml
```

```diff
  {
-   "name": "DefaultApp",
+   "name": "MyApp",
    "version": "1.0.0"
  }
```

One repository, many customizations, no forks. Re-runnable: point it at
different values and you get a different result from the same starting tree.

## Actions

| Action                                                                                | For                               | Selector                               |
| ------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------- |
| [`json_replace`](https://smartcompanion-app.github.io/engraft/actions/json-replace)   | JSON files                        | `$.expo.extra.items[0].label`          |
| [`html_replace`](https://smartcompanion-app.github.io/engraft/actions/html-replace)   | HTML files                        | `//meta[@name='description']/@content` |
| [`regex_replace`](https://smartcompanion-app.github.io/engraft/actions/regex-replace) | Any text file — source, INI, TOML | `'VERSION = "(?<value>[^"]*)"'`        |
| [`file_replace`](https://smartcompanion-app.github.io/engraft/actions/file-replace)   | Whole files, including binaries   | —                                      |

A worked example using all four is in
[Getting started](https://smartcompanion-app.github.io/engraft/getting-started#a-more-realistic-template).

## Why it holds up

- **All-or-nothing.** Every action runs against a staging copy first. If one
  fails, your project is left exactly as it was — no half-applied state.
  ([Architecture](https://smartcompanion-app.github.io/engraft/architecture))
- **Loud about drift.** An HTML selector that matches nothing, or matches three
  elements, is an error. A regex that stops matching is an error. A
  customization that silently stopped working is the failure mode engraft
  exists to prevent.
- **Optional by design.** A variable with no default and no value leaves its
  target untouched, so one template can serve consumers who want the logo
  replaced and consumers who do not.
  ([Variables](https://smartcompanion-app.github.io/engraft/concepts/variables))

## Documentation

The full documentation lives at
**[smartcompanion-app.github.io/engraft](https://smartcompanion-app.github.io/engraft/)**.

| Page                                                                                 | What it covers                                     |
| ------------------------------------------------------------------------------------ | -------------------------------------------------- |
| [Getting started](https://smartcompanion-app.github.io/engraft/getting-started)      | Install, first customization, a realistic template |
| [Concepts](https://smartcompanion-app.github.io/engraft/concepts)                    | The two-file model, path resolution, idempotence   |
| [Template file](https://smartcompanion-app.github.io/engraft/concepts/template-file) | Full template reference                            |
| [Values file](https://smartcompanion-app.github.io/engraft/concepts/values-file)     | Full values reference                              |
| [Variables](https://smartcompanion-app.github.io/engraft/concepts/variables)         | Resolution rules and optional variables            |
| [Actions](https://smartcompanion-app.github.io/engraft/actions)                      | The four actions in detail                         |
| [CLI reference](https://smartcompanion-app.github.io/engraft/cli)                    | Commands, flags, exit codes, common errors         |
| [Architecture](https://smartcompanion-app.github.io/engraft/architecture)            | What happens on disk, and why                      |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, the test layout and the
release process. Taking part means following our
[Code of Conduct](CODE_OF_CONDUCT.md). Security issues go through
[private reporting](SECURITY.md), not the issue tracker.

## Project history

engraft shipped as two parallel implementations — a Python package on PyPI and
this one on npm — through v0.2.2. Keeping two codebases byte-identical cost
more than it returned, so TypeScript is now the only implementation.

The [`engraft` package on PyPI](https://pypi.org/project/engraft/) is archived.
It will receive no further releases, but it was deliberately not yanked, so an
existing pin keeps installing. `@smartcompanion/engraft` accepts the same
template and values files — migrating is a change of install command, not of
configuration.

## License

[BSD 2-Clause](LICENSE).
