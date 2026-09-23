# Contributing

Thanks for helping out. This guide covers working on engraft itself — the CLI,
its actions, and the documentation under [`docs/`](docs/).

Taking part in this project — issues, discussions, pull requests — means
following our [Code of Conduct](CODE_OF_CONDUCT.md).

## Developing

### Local setup

1. Fork and clone the repo.
1. Install the dependencies.

   ```shell
   npm install
   ```

You need Node 22.22.2 or newer (or 24.15+, or 26+). That floor comes from
jsdom, which engraft uses for the XPath selectors in `html_replace`.

### Scripts

#### `npm run build`

Bundles `src/cli.ts` into a single ESM file at `dist/cli.js` with tsup
(esbuild). That file, with its shebang, is the entire published artefact.

#### `npm test`

Builds, then runs both Vitest projects.

- `npm run test:unit` — the unit project alone, against the TypeScript sources.
  Fast, no build needed.
- `npm run test:e2e` — builds, then runs the e2e project alone.
- `npm run test:watch` — watch mode. It does not rebuild `dist/`, so run
  `npm run build` after changing `src/` if you are watching e2e tests.

See [Testing](#testing) for what the two projects cover.

#### `npm run lint` / `npm run lint:fix`

[oxlint](https://oxc.rs/docs/guide/usage/linter), configured in
[`.oxlintrc.json`](.oxlintrc.json). CI runs it with `--deny-warnings`, so a
warning fails the build. A rule turned off in that file has a comment saying
why; if you hit a rule that is wrong for this codebase, turn it off the same
way rather than sprinkling inline suppressions.

#### `npm run format` / `npm run format:check`

[oxfmt](https://oxc.rs), configured in [`.oxfmtrc.json`](.oxfmtrc.json). It
formats TypeScript, JSON, YAML and Markdown at a 100-column width. `format`
rewrites files; `format:check` is what CI runs.

The e2e fixtures are excluded on purpose — they are byte-for-byte inputs and
expected outputs, and reformatting them changes what the suite asserts.

#### `npm run typecheck`

`tsc --noEmit`. oxlint does not type-check, so this is a separate gate.

#### `npm run check:publish`

[`publint`](https://publint.dev/) against the tarball that would actually be
published: entry points resolve, `bin` points somewhere real, nothing is
missing from `files`.

## Architecture

```
src/
  cli.ts                 commander entry point; the published bin
  engine.ts              resolves variables, stages, applies, copies back
  models.ts              parses the template and values YAML
  actions/
    registry.ts          @register decorator + createAction() factory
    base.ts              the Action interface
    index.ts             re-exports the registry and imports every action
    jsonReplace.ts       dot-path selectors ($.a.b[0])
    htmlReplace.ts       XPath selectors via jsdom's document.evaluate
    regexReplace.ts      named capture group; both (?<value>…) and (?P<value>…)
    fileReplace.ts       whole-file replacement
```

[`docs/architecture.md`](docs/architecture.md) covers how an apply actually
runs, including the staging directory that makes it atomic.

### Adding an action

1. Create `src/actions/<name>.ts` exporting a class that implements `Action`
   and is decorated with `@register("<snake_case_name>")`.
2. Import it from `src/actions/index.ts` — registration is a side effect of
   the import, so an action nobody imports does not exist.
3. Implement `targetFiles()`. The engine uses it to decide which files to copy
   into the staging directory; an action that touches a file it does not
   declare will write outside the transaction and break rollback.
4. Skip any `replace` entry whose variable resolves to `null`. That is how
   optional variables work — see
   [`docs/concepts/variables.md`](docs/concepts/variables.md).
5. Add unit tests under `tests/unit/actions/`.
6. Add an e2e fixture under `tests/e2e/fixtures/`. This is not optional: the
   fixtures are the behavioural contract.
7. Document it under `docs/actions/`.

## Testing

Two Vitest projects, declared in [`vitest.config.ts`](vitest.config.ts):

| Project | Files           | What it exercises                          |
| ------- | --------------- | ------------------------------------------ |
| `unit`  | `tests/unit/**` | The TypeScript sources, imported directly. |
| `e2e`   | `tests/e2e/**`  | `dist/cli.js`, run as a real subprocess.   |

The e2e project treats engraft as an opaque binary — no module imports, no
internal state. Anything it asserts, a user could observe.

### Fixtures

Most of the e2e suite is data. Each directory under `tests/e2e/fixtures/` is
one scenario:

```
tests/e2e/fixtures/<name>/
  input/           the project tree before the apply
  template.yaml    what the repo author declares as customizable
  values.yaml      what the consumer chose
  expected/        the project tree the apply must produce
  expect_failure   optional marker: the CLI must exit non-zero, and
                   expected/ describes the untouched input tree
```

Adding a scenario means adding a directory — no code changes. The comparison
is semantic, not byte-for-byte: JSON, YAML and HTML files are parsed and
compared structurally, so key order and indentation do not matter, while a
changed value does. Everything else is compared as text with line endings
normalised. See [`tests/e2e/comparators.ts`](tests/e2e/comparators.ts).

## Documentation

[`docs/`](docs/) is plain Markdown with relative links between pages, readable
as-is on GitHub and ready to be built into a static site later. Keep it that
way: no site-generator-specific syntax, no absolute URLs into the repository,
and no front matter until whichever generator we pick actually needs it.

`docs/index.md` is the entry point and carries the table of contents. A new
page belongs in it, and usually in the README's documentation table too.

oxfmt formats Markdown along with everything else, so run `npm run format`
after editing a page — otherwise `format:check` fails in CI over table
alignment.

## Pull requests

Run the full gate before pushing:

```shell
npm run lint && npm run format:check && npm run typecheck && npm test
```

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org).

## Releasing

Releases run on [changesets](https://github.com/changesets/changesets).
Publishing is never done from a laptop, and pushing a `vX.Y.Z` tag does
nothing — that was the old flow, from when engraft also shipped a Python
package to PyPI.

1. **Add a changeset with your change.** Anything that alters published
   behaviour needs one:

   ```shell
   npm run changeset
   ```

   Pick the bump level and describe the change in the consumer's terms — the
   text lands verbatim in `CHANGELOG.md`. Commit the generated file in
   `.changeset/` with your pull request.

   Changes that publish nothing — CI config, docs, tooling — do not need one.

2. **Merge to `main`.** The `release` workflow collects all pending changesets
   into a `chore: release` pull request that applies the version bump and
   writes the changelog.

3. **Merge the `chore: release` pull request.** That triggers the publish.
   The package goes to npm over
   [trusted publishing](https://docs.npmjs.com/trusted-publishers) — the
   workflow's OIDC identity is exchanged for a short-lived token and signs the
   provenance attestation, so there is no npm token stored in this repository.

### One-time setup

Trusted publishing has to be configured once, on npm, for
`@smartcompanion/engraft`: publisher GitHub Actions, repository
`smartcompanion-app/engraft`, workflow `release.yml`. A `RELEASE_TOKEN` secret
(a PAT with contents and pull-request write access) is optional but
recommended, so the release pull request gets CI checks.
