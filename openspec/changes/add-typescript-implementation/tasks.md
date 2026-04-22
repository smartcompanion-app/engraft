## 1. Repository reorganization (Python subtree move)

- [x] 1.1 `git mv src python/src` so the Python source moves under `python/`
- [x] 1.2 `git mv tests python/tests` so the Python tests move under `python/`
- [x] 1.3 `git mv pyproject.toml python/pyproject.toml` so the Python package manifest moves under `python/`
- [x] 1.4 `git mv README.md python/README.md` so the current README becomes the PyPI-facing doc
- [x] 1.5 Verify the move by running `pip install -e python/` and `(cd python && pytest)` — both SHALL pass unchanged
- [x] 1.6 Verify `ruff check python/src python/tests` passes from the repo root (using ruff config inside `python/pyproject.toml` when invoked from `python/`)

## 2. Python implementation behavior updates

- [x] 2.1 Add a YAML 1.2 loader in `python/src/engraft/` that subclasses `yaml.SafeLoader` and removes the implicit resolvers for `yes`/`no`/`on`/`off` (and their capitalized variants)
- [x] 2.2 Update the engine's YAML reads (template and values file parsing) to use the new loader
- [x] 2.3 Update `python/src/engraft/actions/regex_replace.py` to accept selectors using either `(?P<value>...)` or `(?<value>...)` by normalizing `(?<value>` → `(?P<value>` before compilation; keep the existing error when neither form is present
- [x] 2.4 Add Python unit tests covering the YAML 1.2 behavior (yes/no/on/off/Yes/No/On/Off parse as strings; true/false still parse as booleans)
- [x] 2.5 Add Python unit tests covering both regex named-group syntaxes (accepted), missing group (rejected), and the normalization preserving the rest of the pattern untouched
- [x] 2.6 Update `python/src/engraft/models.py` so `Variable.default` is `str | None` and parsing distinguishes "no default declared" (None) from `default: ""`
- [x] 2.7 Update `python/src/engraft/engine.py` so the resolved variable map is `dict[str, str | None]` — a variable with no default and no value override resolves to `None`
- [x] 2.8 Update every Python action so a `replace` entry referencing a variable whose resolved value is `None` is skipped; for `file_replace`, if the referenced variable is `None` the action is a noop
- [x] 2.9 Add Python unit tests covering the optional-variable noop semantics (unset variable with no default skips the entry; default still applied when present; explicit empty string still applied)

## 3. TypeScript project scaffold

- [x] 3.1 Create `typescript/package.json` with name `engraft`, `bin.engraft` pointing to `dist/cli.js`, `engines.node >=20`, description matching the Python impl, and the initial version aligned with the current Python version
- [x] 3.2 Create `typescript/tsconfig.json` with `strict: true`, `target: ES2022`, `module: ESNext`, `moduleResolution: Bundler`, and `experimentalDecorators: true`
- [x] 3.3 Add runtime dependencies to `typescript/package.json`: `commander`, `js-yaml`, `jsdom`
- [x] 3.4 Add dev dependencies to `typescript/package.json`: `typescript`, `vitest`, `tsup`, `@types/node`, `@types/js-yaml`, `@types/jsdom`
- [x] 3.5 Add npm scripts: `build` (tsup), `test` (vitest run), `test:watch` (vitest), `lint` (tsc --noEmit for type checking)
- [x] 3.6 Create `typescript/tsup.config.ts` producing a single-file bundle at `dist/cli.js` with a shebang (`#!/usr/bin/env node`)
- [x] 3.7 Create an empty `typescript/.gitignore` excluding `node_modules/`, `dist/`, and coverage outputs

## 4. TypeScript core: models, engine, action registry

- [x] 4.1 Port `models.py` to `typescript/src/models.ts` — types for `Variable`, `Template`, `Values`, plus YAML loader using `js-yaml`
- [x] 4.2 Port action registry to `typescript/src/actions/index.ts` — a `register(name)` decorator that populates a `Map<string, ActionCtor>`, plus `createAction(name, config)` factory
- [x] 4.3 Port `Action` interface to `typescript/src/actions/base.ts` — interface with `apply(variables, workDir, valuesDir): Promise<void>` and `targetFiles(): string[]`
- [x] 4.4 Port `engine.py` to `typescript/src/engine.ts` — variable resolution, optional-variable noop semantics, staging directory `.engraft/`, `targetFiles()` collection, copy-in/copy-back, failure rollback
- [x] 4.5 Port `cli.py` to `typescript/src/cli.ts` — commander-based CLI with `apply --template <path> --values <path>` and `--version` flag reading from `package.json`
- [x] 4.6 Add a module-level import of every action file from `typescript/src/actions/index.ts` so registration side effects fire at startup

## 5. TypeScript action implementations

- [x] 5.1 Implement `typescript/src/actions/jsonReplace.ts` with a dot-path parser equivalent to Python's (supports `a.b[2].c` syntax and `$.` prefix stripping); write JSON with `JSON.stringify(data, null, 2) + "\n"`
- [x] 5.2 Implement `typescript/src/actions/htmlReplace.ts` using jsdom — parse input, run `document.evaluate` for XPath, handle element text vs attribute results, enforce single-match requirement (error on 0 or >1 matches), preserve DOCTYPE by extracting and re-prepending
- [x] 5.3 Implement `typescript/src/actions/regexReplace.ts` — accept both `(?P<value>…)` and `(?<value>…)` by normalizing `(?P<value>` → `(?<value>` before `new RegExp`; keep error-on-missing-group; replace only the `value` named group content
- [x] 5.4 Implement `typescript/src/actions/fileReplace.ts` — resolve source from values dir, verify target and source exist, copy source over target using `fs.copyFile`
- [x] 5.5 Ensure each action's class has a `targetFiles(): string[]` method returning the relative paths it operates on

## 6. TypeScript unit tests

- [x] 6.1 Create `typescript/tests/models.test.ts` covering YAML parsing edge cases (empty variables, empty customizations, malformed YAML)
- [x] 6.2 Create `typescript/tests/engine.test.ts` covering variable resolution with defaults, value overrides, optional-variable noop, staging setup/teardown, failure rollback
- [x] 6.3 Create `typescript/tests/actions/jsonReplace.test.ts` covering simple paths, nested paths with array indices, multiple replacements
- [x] 6.4 Create `typescript/tests/actions/htmlReplace.test.ts` covering element text replacement, attribute replacement, single-match enforcement (error on 0 and >1 matches), DOCTYPE preservation
- [x] 6.5 Create `typescript/tests/actions/regexReplace.test.ts` covering both named-group syntaxes, missing-group error, no-match error, multiple replacements
- [x] 6.6 Create `typescript/tests/actions/fileReplace.test.ts` covering successful replace and missing-source error
- [x] 6.7 Create `typescript/tests/cli.test.ts` covering `--version` output and `apply` invocation end-to-end at the subprocess level
- [x] 6.8 Verify all tests pass: `(cd typescript && npm install && npm run build && npm test)`

## 7. E2E harness scaffold

- [x] 7.1 Create `e2e/conftest.py` with a pytest fixture parametrized over `["python", "typescript"]` that returns a callable invoking the selected CLI via `subprocess.run`
- [x] 7.2 In `e2e/conftest.py`, add a collection-time check that fails with a clear error if the selected implementation's entrypoint is not runnable (missing `engraft` on PATH for Python, missing `typescript/dist/cli.js` for TS)
- [x] 7.3 Create `e2e/comparators.py` with functions `compare_json`, `compare_yaml`, `compare_html`, `compare_text`, plus a dispatcher `compare_tree(expected_dir, actual_dir)` selecting the comparator by file extension
- [x] 7.4 Implement the HTML comparator: parse both trees with `lxml.html.fromstring`, walk in document order, compare tag names, attribute sets (order-independent), collapsed whitespace text content
- [x] 7.5 Create `e2e/test_scenarios.py` that discovers subdirectories under `e2e/fixtures/`, parametrizes over them, copies `input/` to a `tmp_path`, invokes the CLI, and compares the result against `expected/`

## 8. E2E fixture scenarios

- [x] 8.1 Create `e2e/fixtures/json-replace-basic/` exercising `json_replace` on a `package.json`-like file with nested path and array index
- [x] 8.2 Create `e2e/fixtures/html-replace-basic/` exercising `html_replace` with one element-text replacement and one attribute replacement, DOCTYPE preserved
- [x] 8.3 Create `e2e/fixtures/regex-replace-both-syntaxes/` with two scenarios in one template: one using `(?P<value>...)` and one using `(?<value>...)`, proving both syntaxes work in both implementations
- [x] 8.4 Create `e2e/fixtures/file-replace-basic/` replacing a whole file with a source referenced from values dir
- [x] 8.5 Create `e2e/fixtures/optional-variable-unset/` proving that unset optional variables cause the relevant `replace` entries to be skipped (noop) across both impls
- [x] 8.6 Create `e2e/fixtures/rollback-on-action-failure/` with a template where action 2 of 2 fails; assert the project files remain unchanged post-run
- [x] 8.7 Create `e2e/fixtures/yaml-12-parity/` exercising a values file containing `flag: yes` and asserting the consuming action sees the string `"yes"` in both impls

## 9. Documentation

- [x] 9.1 Update `python/README.md` development section to note that commands are run from inside `python/` (not the repo root)
- [x] 9.2 Update `python/README.md` `regex_replace` section to note both `(?P<value>...)` and `(?<value>...)` syntaxes are accepted
- [x] 9.3 Update `python/README.md` to note the YAML 1.2 semantics change (yes/no/on/off now parse as strings; quote values explicitly if boolean was intended)
- [x] 9.4 Create `typescript/README.md` with: description, `npm install -g engraft` install, quick-start example, action reference (same four actions, with the regex named-group portability note), development section (`npm install`, `npm run build`, `npm test`), Node ≥20 requirement note
- [x] 9.5 Create new minimal root `README.md` with a project overview, a link to `python/README.md` (PyPI) and `typescript/README.md` (npm), and a section describing the `e2e/` harness as the shared behavioral contract
- [x] 9.6 Update root `CLAUDE.md` to reflect the dual-implementation layout — new architecture diagram, commands adjusted to `python/` and `typescript/` subdirectories, note about the e2e harness

## 10. Verification

- [x] 10.1 Verify Python: `pip install -e python/ && (cd python && pytest && ruff check src tests)` passes
- [x] 10.2 Verify TypeScript: `(cd typescript && npm install && npm run build && npm test)` passes
- [x] 10.3 Verify E2E: `pytest e2e/` passes with every scenario running twice (once per implementation)
- [x] 10.4 Verify git history preservation: `git log --follow python/src/engraft/engine.py` shows commits from before the reorganization (rename detected as `R100` in the staged index; full traversal is available once the change is committed)
- [x] 10.5 Confirm `openspec validate add-typescript-implementation --strict` succeeds
