# engraft

CLI tool that applies customizations to any project without requiring
templating placeholders. Uses a two-file model: a **template** (what can be
customized) and a **values** file (the consumer's choices).

TypeScript only, published to npm as `@smartcompanion/engraft`. A parallel
Python implementation existed through v0.2.2 and was removed — no PyPI package,
no pytest, no ruff, no `openspec/` directory.

## Repository layout

```
src/            the CLI and engine
tests/unit/     unit tests (vitest project "unit")
tests/e2e/      fixture-driven e2e tests (vitest project "e2e")
docs/           user-facing documentation, Markdown, for a docs site later
.changeset/     pending release notes
```

## Architecture

```
src/cli.ts (commander)
 └─ engine.ts                # resolves variables, runs actions in order,
     │                       # stages in .engraft/, rolls back on failure
     ├─ models.ts             # parses template + values YAML via js-yaml
     └─ actions/
         ├─ registry.ts       # @register decorator + createAction()
         ├─ index.ts          # re-exports registry, imports each action module
         │                    # for its registration side effect
         ├─ base.ts           # Action interface
         ├─ jsonReplace.ts    # dot-path selectors ($.a.b[0])
         ├─ htmlReplace.ts    # XPath via jsdom document.evaluate
         ├─ regexReplace.ts   # `value` named group; (?<value>…) and (?P<value>…)
         └─ fileReplace.ts    # whole-file replacement
```

`docs/architecture.md` has the full picture, including why the staging
directory exists.

Adding an action: implement it, register it under a snake_case name, import it
from `src/actions/index.ts`, add unit tests, **add an e2e fixture**, and
document it under `docs/actions/`.

## Commands

```bash
npm install
npm run build          # tsup → dist/cli.js (single ESM file with shebang)
npm test               # builds, then runs both vitest projects
npm run test:unit      # unit project only, no build needed
npm run test:e2e       # builds, then the e2e project only
npm run lint           # oxlint --deny-warnings
npm run format         # oxfmt (format:check in CI)
npm run typecheck      # tsc --noEmit
npm run check:publish  # publint against the would-be tarball
node dist/cli.js apply --template <f> --values <f>
```

Full gate before pushing:

```bash
npm run lint && npm run format:check && npm run typecheck && npm test
```

## Conventions

- Node 22.22.2+ (the floor comes from jsdom), strict TypeScript, ESM.
- Linting is **oxlint**, formatting is **oxfmt** — not ESLint, not Prettier.
  Rules turned off in `.oxlintrc.json` carry a comment saying why; turn a rule
  off there rather than adding inline suppressions.
- `experimentalDecorators: true` for the `@register` pattern on action classes.
- Commit messages follow Conventional Commits.
- 100-column formatting, set by oxfmt's default `printWidth`.

## Testing

Two vitest projects, declared in `vitest.config.ts`:

- `unit` — imports `src/` directly.
- `e2e` — runs `dist/cli.js` as a subprocess. Its global setup fails with a
  clear message if the build is missing.

`tests/e2e/fixtures/<name>/` holds `input/`, `template.yaml`, `values.yaml`,
`expected/`, and an optional `expect_failure` marker. Adding a scenario means
adding a directory. Comparison is semantic (JSON/YAML/HTML parsed and compared
structurally, everything else as text) — see `tests/e2e/comparators.ts`.

The fixtures are the behavioural contract. A change that intentionally alters
behaviour must update the relevant fixtures alongside.

## Releasing

Changesets. `npm run changeset` with any change that alters published
behaviour; merging to `main` opens a `chore: release` PR; merging that PR
publishes to npm over trusted publishing (OIDC, no stored token). Pushing a
`vX.Y.Z` tag does nothing — that was the old, pre-changesets flow.

## CI

- `.github/workflows/ci.yml` — lint/format/typecheck, a test matrix on Node 22
  and 24, and a package job that runs publint and smoke-tests the packed
  tarball via a global install.
- `.github/workflows/release.yml` — the changesets release/publish flow.
