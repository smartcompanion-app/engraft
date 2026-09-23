# engraft

[![ci](https://github.com/smartcompanion-app/engraft/actions/workflows/ci.yml/badge.svg)](https://github.com/smartcompanion-app/engraft/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/@smartcompanion/engraft)](https://www.npmjs.com/package/@smartcompanion/engraft)
[![node](https://img.shields.io/node/v/@smartcompanion/engraft)](https://nodejs.org)
[![license](https://img.shields.io/npm/l/@smartcompanion/engraft)](LICENSE)

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

| Action                                           | For                               | Selector                               |
| ------------------------------------------------ | --------------------------------- | -------------------------------------- |
| [`json_replace`](docs/actions/json-replace.md)   | JSON files                        | `$.expo.extra.items[0].label`          |
| [`html_replace`](docs/actions/html-replace.md)   | HTML files                        | `//meta[@name='description']/@content` |
| [`regex_replace`](docs/actions/regex-replace.md) | Any text file — source, INI, TOML | `'VERSION = "(?<value>[^"]*)"'`        |
| [`file_replace`](docs/actions/file-replace.md)   | Whole files, including binaries   | —                                      |

A worked example using all four is in
[Getting started](docs/getting-started.md#a-more-realistic-template).

## Why it holds up

- **All-or-nothing.** Every action runs against a staging copy first. If one
  fails, your project is left exactly as it was — no half-applied state.
  ([Architecture](docs/architecture.md))
- **Loud about drift.** An HTML selector that matches nothing, or matches three
  elements, is an error. A regex that stops matching is an error. A
  customization that silently stopped working is the failure mode engraft
  exists to prevent.
- **Optional by design.** A variable with no default and no value leaves its
  target untouched, so one template can serve consumers who want the logo
  replaced and consumers who do not.
  ([Variables](docs/concepts/variables.md))

## Documentation

| Page                                            | What it covers                                     |
| ----------------------------------------------- | -------------------------------------------------- |
| [Getting started](docs/getting-started.md)      | Install, first customization, a realistic template |
| [Concepts](docs/concepts/index.md)              | The two-file model, path resolution, idempotence   |
| [Template file](docs/concepts/template-file.md) | Full template reference                            |
| [Values file](docs/concepts/values-file.md)     | Full values reference                              |
| [Variables](docs/concepts/variables.md)         | Resolution rules and optional variables            |
| [Actions](docs/actions/index.md)                | The four actions in detail                         |
| [CLI reference](docs/cli.md)                    | Commands, flags, exit codes, common errors         |
| [Architecture](docs/architecture.md)            | What happens on disk, and why                      |

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
