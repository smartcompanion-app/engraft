# engraft

CLI tool that applies customizations to any project without requiring templating placeholders. Uses a two-file model: a **template** (what can be customized) and a **values** file (the consumer's choices).

Ships as **two parallel implementations** with identical behaviour:

- `python/` — published to PyPI as `engraft`
- `typescript/` — published to npm as `engraft`

Both implementations accept the same template/values YAML format, ship the same four actions (`json_replace`, `html_replace`, `regex_replace`, `file_replace`), and must produce the same output for any given input.

## Repository layout

```
python/              # Python implementation (pyproject.toml, src/, tests/)
typescript/          # TypeScript implementation (package.json, src/, tests/)
e2e/                 # Shared pytest harness — runs every fixture against both CLIs
openspec/            # OpenSpec change proposals and specs
README.md            # Top-level overview pointing at both impls
```

## Architecture (per implementation)

Python (`python/src/engraft/`):

```
cli.py
 └─ engine.apply()          # resolves variables, runs actions in order, rollback on failure
     ├─ models.py            # parses template + values YAML files
     ├─ yaml_loader.py       # YAML 1.2 SafeLoader (yes/no/on/off are strings)
     └─ actions/             # plugin registry
         ├─ __init__.py      # @register decorator + create_action()
         ├─ base.py          # Action ABC
         ├─ json_replace.py  # dot-path selectors ($.a.b[0])
         ├─ html_replace.py  # XPath selectors via lxml
         ├─ regex_replace.py # named group, accepts both (?P<value>…) and (?<value>…)
         └─ file_replace.py  # whole-file replacement
```

TypeScript (`typescript/src/`):

```
cli.ts (commander)
 └─ engine.ts                # mirrors the Python engine, staging dir .engraft/
     ├─ models.ts             # template + values parsing via js-yaml
     └─ actions/
         ├─ registry.ts       # @register decorator + createAction()
         ├─ index.ts          # re-exports registry + triggers action-module side effects
         ├─ base.ts           # Action interface
         ├─ jsonReplace.ts
         ├─ htmlReplace.ts    # XPath via jsdom document.evaluate
         ├─ regexReplace.ts   # accepts both (?<value>…) and (?P<value>…)
         └─ fileReplace.ts
```

Adding a new action: implement it in **both** impls, register under the same string name, and add an e2e fixture exercising it.

## Commands

### Python (run from `python/`)

```bash
cd python/
pip install -e ".[dev]"                 # install with dev dependencies
pytest                                   # run unit tests
ruff check src/ tests/                   # lint
engraft apply --template <f> --values <f>  # run the CLI
```

### TypeScript (run from `typescript/`)

```bash
cd typescript/
npm install
npm run build                            # produces dist/cli.js
npm test                                  # vitest
npm run lint                              # tsc --noEmit
node dist/cli.js apply --template <f> --values <f>
```

### E2E harness (run from repo root)

```bash
pytest e2e/                              # runs every fixture against both impls
ENGRAFT_IMPL=python pytest e2e/          # restrict to Python
ENGRAFT_IMPL=typescript pytest e2e/      # restrict to TypeScript
```

The e2e harness is the behavioural source of truth for cross-impl parity. A change that intentionally alters behaviour in both impls must update the relevant e2e fixture(s) alongside.

## Conventions

### Python
- Python 3.10+, type hints throughout
- Build: hatchling (`python/pyproject.toml`)
- Versioning: hatch-vcs, derived from git tags (`raw-options = { root = ".." }` because pyproject.toml now lives in `python/`)
- Linting: ruff (rules: E, F, I, UP, B)
- Testing: pytest, tests mirror src structure (`python/tests/test_actions/`)
- Line length: 88 characters

### TypeScript
- Node.js 20+, strict TypeScript, ESM modules
- Build: tsup (esbuild) → single-file bundle at `typescript/dist/cli.js` with shebang
- Testing: vitest
- `experimentalDecorators: true` for the `@register` pattern on action classes

## CI/CD

- **Python PR pipeline** (`.github/workflows/pr.yml`): lint, format check, test matrix (3.10, 3.12, 3.13)
- **Python release pipeline** (`.github/workflows/release.yml`): triggered on GitHub Release publish → lint → format check → test matrix → build → publish to PyPI (Trusted Publisher OIDC + Sigstore signing)
- TypeScript CI/CD is not yet wired up (see OpenSpec change history for the scope that has been added).
