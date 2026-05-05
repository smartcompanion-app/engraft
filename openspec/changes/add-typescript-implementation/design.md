## Context

engraft today is a Python-only CLI shipped through PyPI. Its architecture — a small engine that reads two YAML files (template + values), resolves variables, and runs a sequence of typed actions against a staging directory — is language-agnostic. The four action types (`json_replace`, `html_replace`, `regex_replace`, `file_replace`) are thin adapters over format-specific libraries (`json`, `lxml`, `re`, plain file copy).

To reach Node/TypeScript consumers without forcing them to install Python, we want a second implementation published to npm. The two implementations must accept the same template and values files and produce semantically equivalent output. A shared end-to-end test suite enforces that.

The repository is reorganized to host both implementations side-by-side. The existing Python tree moves verbatim into `python/` so the follow-up CI/release work can target that subdirectory cleanly. The TypeScript implementation lives in `typescript/`. A pytest-based e2e harness at the repo root exercises both via their CLI boundary.

## Goals / Non-Goals

**Goals:**
- Feature-equivalent TypeScript CLI: every command, flag, action type, and variable-resolution rule matches the Python impl's observable behavior.
- Template portability: a template authored for one implementation works unchanged on the other, with the single caveat of the regex named-group syntax (which both implementations accept in either form).
- One place to assert behavioral contracts: the e2e suite runs every scenario against both implementations with semantic comparison of outputs.
- Git history preserved for the Python subtree via `git mv`.
- Zero changes to the Python implementation's internal API, module layout, or package name.

**Non-Goals:**
- CI/CD workflow updates. `.github/workflows/*.yml` intentionally break after this change and are fixed in the follow-up.
- Automated release synchronization (PyPI + npm in lockstep). Versioning mechanics live in the follow-up.
- New features. This change adds an implementation; it does not expand engraft's capabilities.
- Byte-identical output between the two implementations. Semantic equivalence is the contract; byte-identity is not pursued.
- Convenience scripts (Makefile, justfile) for local e2e bootstrap. Steps are documented in prose; automation can follow later.

## Decisions

### 1. Repository layout: `python/`, `typescript/`, `e2e/`, shared root docs

**Decision:** Move Python code into `python/` (verbatim subtree: `pyproject.toml`, `src/`, `tests/`, `README.md`). Create `typescript/` with package.json-rooted TS project. Create `e2e/` for the shared test harness. Keep `LICENSE`, `CLAUDE.md`, `openspec/`, and a new minimal `README.md` at the repo root.

**Alternatives considered:**
- Keep Python at root, nest TS under `typescript/`. Rejected because it privileges one implementation and complicates the mental model; the two should be symmetric.
- Monorepo with `packages/engraft-py/` and `packages/engraft-ts/`. Rejected as over-structured for two packages and introduces conventions from JS-monorepo tooling we don't otherwise need.

**Rationale:** Symmetric layout is unambiguous. Implementation-specific tooling (pytest config, hatchling build, tsup build, vitest) stays scoped to each subdirectory. The e2e harness sits above both because it tests the public boundary of either.

### 2. TypeScript stack

**Decision:**
- Runtime: Node ≥20 LTS
- Language: TypeScript with `strict: true`
- CLI framework: `commander` (closest ergonomic match to Click)
- YAML: `js-yaml`
- HTML: `jsdom` with `document.evaluate` for XPath
- Test runner: `vitest`
- Build: `tsup` (esbuild under the hood) producing a single executable JS file referenced from `package.json`'s `bin` field
- Package manager: `npm` (fewest assumptions; no workspace features needed)

**Alternatives considered:**
- `yargs`/`clipanion` for CLI → commander is more idiomatic for the click-style subcommand+option shape engraft uses.
- `parse5` + a standalone `xpath` library for HTML → lighter weight but more plumbing to replicate lxml's HTML-tolerant parse; jsdom is heavier but provides a real DOM with `document.evaluate` built-in, reducing the surface area for divergence.
- `jest` or `node:test` → vitest integrates with TS+esbuild out of the box with less config.
- `pnpm` → fine but adds a workspace assumption.

**Rationale:** Every choice optimizes for correctness-equivalence with Python rather than JS-ecosystem breadth. jsdom is the single heavyweight dependency; its cost is acceptable for a dev-tool CLI.

### 3. Action registry pattern in TypeScript

**Decision:** Mirror Python's decorator-based registry with a `register(name)` function invoked at module load. Each action module exports a class implementing an `Action` interface, and registers itself via a side-effecting call.

```typescript
// actions/base.ts
export interface Action {
  apply(variables: Record<string, string>, workDir: string, valuesDir: string): Promise<void>;
  targetFiles(): string[];
}

// actions/index.ts
const registry = new Map<string, ActionCtor>();
export const register = (name: string) => (ctor: ActionCtor) => { registry.set(name, ctor); };
export const createAction = (name: string, config: unknown): Action => { /* … */ };

// actions/jsonReplace.ts
@register("json_replace")
export class JsonReplace implements Action { /* … */ }
```

**Alternatives considered:**
- Explicit registry in `actions/index.ts` listing all actions. Rejected because it introduces a second place to update when adding an action; decorator-style is a one-file change.
- Class-less approach with factory functions. Rejected; the Python code uses dataclass-style state on actions, and a class maps cleanly.

**Rationale:** Matches Python's plugin model one-for-one, keeping the mental model consistent for contributors who work across both impls. Requires `experimentalDecorators` (TypeScript ≥5 stage-3 decorators work fine).

### 4. Regex named-group syntax normalization

**Decision:** Both implementations accept both `(?P<value>…)` and `(?<value>…)` in `regex_replace` selectors. At action-construction time, each implementation normalizes to its native form:
- Python: `(?<value>…)` → `(?P<value>…)` by string substitution before `re.compile`.
- TypeScript: `(?P<value>…)` → `(?<value>…)` by string substitution before `new RegExp`.

**Alternatives considered:**
- Pick one syntax, force migration. Rejected because existing templates already use `(?P<value>…)` and users shouldn't edit them to adopt the TS impl.
- Keep each implementation language-native, templates get implementation-specific. Rejected because it breaks the portability promise.

**Rationale:** Cheap one-line transformation at the edge preserves both the existing Python templates and a native-feeling surface for TS-first template authors. The `value` group name is the only named group engraft cares about; unnamed groups, other named groups, and the rest of the regex body are untouched.

### 5. JSON output format

**Decision:** TypeScript implementation writes JSON with `JSON.stringify(data, null, 2) + "\n"`. This matches the Python output (`json.dumps(data, indent=2) + "\n"`) for the inputs engraft handles (object/array/string/number/bool/null).

**Alternatives considered:**
- Byte-identical JSON output required. Investigated: the two serializers agree on key order (insertion order), indentation, separators, and escaping for the set of characters engraft touches. For engraft's narrow input space they produce identical bytes. No additional normalization needed at the e2e layer; the semantic JSON comparator covers us if they diverge on an edge case.

**Rationale:** Relying on semantic comparison for e2e means we don't need to pursue byte-identity contractually, but getting it for free on the happy path is a nice property.

### 6. HTML serialization

**Decision:** HTML output is not byte-identical across implementations. The e2e HTML comparator parses both actual and expected HTML with `lxml.html`, walks the tree, and asserts structural equivalence: same tag names, same attribute sets (order-independent), same text content (whitespace-collapsed between tags), same document order. DOCTYPE presence is preserved by both implementations when present in the input.

**Alternatives considered:**
- Canonicalize both outputs through a single formatter (e.g., `prettier` with HTML plugin) before byte-compare. Rejected: adds a Node dependency to the Python-only e2e harness, and prettier's rules are opinionated.
- Require lxml-identical output from the TS impl. Rejected: lxml's serialization quirks (attribute quoting choices, void element handling) are not something we can realistically replicate in jsdom without custom post-processing.

**Rationale:** Semantic structure is what users care about. The comparator's documented normalizations (attribute order, collapsible whitespace) are explicit in the e2e spec.

### 7. YAML 1.2 parity in the Python implementation

**Decision:** The Python implementation loads template and values YAML with a PyYAML `SafeLoader` subclass that removes the YAML 1.1 implicit resolvers for `yes`/`no`/`on`/`off`/`Yes`/`No`/`On`/`Off`, so these parse as strings. The only booleans remain `true`/`false` (matching YAML 1.2 / js-yaml).

```python
class YamlLoader(yaml.SafeLoader): pass
# remove the yes/no/on/off bool resolver
YamlLoader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != 'tag:yaml.org,2002:bool']
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
} | { /* re-add strict true/false resolver */ }
```

**Alternatives considered:**
- Use `ruamel.yaml` with 1.2 mode. Rejected: introduces a new Python dependency for one behavior tweak.
- Document "quote your yes/no values" without changing the loader. Rejected: the portability promise breaks silently — a YAML that works in TS surprisingly breaks in Python. Better to fix it once in the loader.
- Change js-yaml to YAML 1.1. Rejected: YAML 1.2 is the modern default; locking TS to 1.1 is a step backward.

**Rationale:** One-time, well-understood transformation in the Python loader. Documented as a breaking change in the proposal for users who may have relied on `yes` → `True`.

### 8. Staging directory and rollback port to TypeScript

**Decision:** The TS engine implements the same `.engraft/` staging strategy as the Python engine:
1. Remove `.engraft/` if it exists.
2. Collect every action's `targetFiles()` set.
3. Copy each target into `.engraft/` preserving relative paths.
4. Run all actions against `.engraft/`.
5. On success: copy modified files from `.engraft/` back to the project, then remove `.engraft/`.
6. On any failure: remove `.engraft/`, re-throw the error.

Implementation uses Node's `fs/promises` and `path` modules; no third-party staging library.

**Rationale:** The behavior is spec'd in the existing `engine` capability and applies equally to both implementations.

### 9. Version reporting

**Decision:** `engraft --version` prints the same version string in both implementations. The Python implementation reads it from package metadata (already in place via hatch-vcs). The TypeScript implementation reads it from `package.json`'s `version` field.

During this change, the TypeScript `package.json` ships with `version` set to match the Python impl's current tag. Keeping the two strings in sync across releases is out of scope (lives in the follow-up release change).

**Rationale:** Identical version output is what matters to users; the mechanism for staying in sync is a build-time concern that belongs to the release pipeline change.

### 10. Python `pyproject.toml` after the move

**Decision:** `pyproject.toml` moves from repo root to `python/pyproject.toml` with no content edits required. Its internal paths (`packages = ["src/engraft"]`, `testpaths = ["tests"]`, `[tool.ruff.lint.per-file-ignores]` for `tests/**`) are already relative and resolve correctly inside `python/`.

**Consumer impact:** Anyone who ran `pip install -e .` from the repo root must now run `pip install -e python/`. Editable installs on PyPI are unaffected (wheel build from `python/` produces the same artifact structure).

### 11. E2E harness design

**Decision:** pytest suite at `e2e/` parametrized by a fixture over `["python", "typescript"]`. The fixture resolves to a subprocess invocation:
- `python`: `engraft` binary (assumes `pip install -e python/` was run).
- `typescript`: `node typescript/dist/cli.js` (assumes `npm install && npm run build` was run in `typescript/`).

Test scenarios live in `e2e/fixtures/<scenario>/`:
- `template.yaml`, `values.yaml` — the inputs.
- `input/` — the initial project directory state.
- `expected/` — the expected post-apply state.

Each test copies `input/` to a temp directory, invokes the CLI pointing at the copied directory, and asserts `expected/` matches using semantic comparators keyed on file extension:
- `.json` → `json.loads` + deep equal
- `.yaml`/`.yml` → `yaml.safe_load` + deep equal
- `.html` → lxml parse + structural walk (see §6)
- otherwise → text equality with normalized line endings

If either CLI isn't available (missing binary / missing build artifact), the harness fails loudly rather than silently skipping.

## Risks / Trade-offs

- **[Risk]** HTML serialization divergence between lxml and jsdom produces false failures in e2e → **Mitigation:** semantic HTML comparator with documented normalization rules; escalate to byte-compare only when the structure is guaranteed to match.
- **[Risk]** YAML 1.2 change silently breaks user templates that relied on `yes`/`no` being booleans → **Mitigation:** mark as **BREAKING** in the proposal; update python/README.md with a migration note; the breakage is loud (`True` vs `"yes"` produces a clear downstream error in most templates).
- **[Risk]** Regex flavor differences beyond named groups (lookbehind variable-width, Unicode property escapes) cause silent behavior divergence → **Mitigation:** document the portable regex subset in both READMEs; the e2e suite's fixtures only use portable patterns; users targeting a single impl can use its full regex flavor at their own risk.
- **[Risk]** Contributors forget to build the TS impl before running e2e and see confusing failures → **Mitigation:** e2e conftest probes for the `dist/cli.js` artifact at collection time and raises a clear error (with the build command) if missing.
- **[Risk]** `.github/workflows/` break during the window between this change and the follow-up CI change → **Accepted:** flagged in the proposal; the follow-up change is the first thing to land afterward.
- **[Risk]** Two codebases drift over time — a bug fixed in Python doesn't get fixed in TS → **Mitigation:** e2e contract is the shared source of truth; any bug not caught by e2e is a gap in fixtures, not in the architecture. Adding a fixture is the PR discipline.
- **[Trade-off]** Two codebases cost roughly 2× the maintenance. This is intentional: reaching Node consumers is worth it, and the action surface is small enough (≈4 action types, ≈2 small modules of engine/model code) that the maintenance cost is bounded.

## Migration Plan

1. Create `python/` directory and `git mv` the Python subtree into it:
   - `src/` → `python/src/`
   - `tests/` → `python/tests/`
   - `pyproject.toml` → `python/pyproject.toml`
   - Root `README.md` → `python/README.md` (as-is for now; root gets a new minimal README)
2. Update the YAML loader in `python/src/engraft/` to use YAML 1.2 semantics.
3. Update `python/src/engraft/actions/regex_replace.py` to accept both named-group syntaxes.
4. Create `typescript/` with `package.json`, `tsconfig.json`, `src/` (ports of engine/models/actions), `tests/` (vitest), and a `tsup`-produced `dist/cli.js`.
5. Create `typescript/README.md` tailored for npm.
6. Create new minimal root `README.md`.
7. Update root `CLAUDE.md` to describe the dual-implementation layout.
8. Create `e2e/` harness with conftest, comparators, at least two fixture scenarios (one covering each action type), and the parametrized test module.
9. Verify locally: `pip install -e python/`, `(cd typescript && npm install && npm run build)`, `pytest e2e/`, `pytest python/`, `(cd typescript && npm test)`.
10. Update CLAUDE.md's architecture diagram to point at `python/src/engraft/`.

**Rollback**: if the change needs to be reverted, the Python subtree's `git mv` is reversible via a single revert commit; the TS and e2e subtrees are additions and can be deleted cleanly.

## Open Questions

- **Does the TS `engraft` binary support `engraft --help` formatting identically to click's?** commander's default help format differs from click's. We treat help-text format as non-contractual (it's not exercised by e2e and isn't in any spec). If users complain, a follow-up can address it.
- **Should the e2e suite run the Python CLI via `subprocess.run(["engraft", …])` or `python -m engraft`?** Both work. Defaulting to `engraft` (the installed entry point) since that's what users run. Fall back to `python -m engraft` if `engraft` is not on PATH.
