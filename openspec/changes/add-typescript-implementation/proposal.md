## Why

engraft is only available to Python users today, but the problems it solves (applying customizations without templating placeholders) are equally relevant in Node/TypeScript projects where `pip install engraft` is friction. Providing a second implementation published to npm — with identical CLI, features, and template format — lets any repo consume engraft with its native package manager. Shipping both from a single repo with a shared end-to-end test suite keeps the two implementations honest: the template format and observable behavior stay in lockstep.

## What Changes

- Reorganize the repository to host two sibling implementations under `python/` and `typescript/`. The current Python code moves verbatim into `python/` (same package name, same module layout — just reparented).
- Add a new TypeScript implementation in `typescript/` with feature parity: same CLI (`engraft apply …`), same action types (`json_replace`, `html_replace`, `regex_replace`, `file_replace`), same variable resolution including optional-variable noop semantics, same staging-directory rollback behavior.
- Add a shared end-to-end test suite at `e2e/` (repo root). The harness is pytest-based, parametrized over both implementations, and compares actual vs expected output **semantically** (format-aware parsers + structural equality) rather than byte-identical.
- **BREAKING** for the template format: `regex_replace` selectors now accept both `(?P<value>…)` (Python named-group syntax) and `(?<value>…)` (ECMAScript named-group syntax). Each implementation normalizes to its native form on load. Templates authored for the Python impl continue to work unchanged.
- **BREAKING** for YAML parsing in the Python impl: template and values files are now parsed with YAML 1.2 semantics (via a configured PyYAML loader) so `yes`/`no`/`on`/`off` resolve as strings, matching js-yaml's defaults. Templates that relied on these being booleans must quote the value explicitly.
- Split the README into three files: a minimal root `README.md` introducing the dual-implementation project, `python/README.md` (current README moved verbatim, becomes the PyPI page), and `typescript/README.md` (tailored for npm audience).
- Update root `CLAUDE.md` to reflect the dual-implementation layout.

**Explicitly out of scope** (deferred to a follow-up change): `.github/workflows/*.yml` updates (PR and release pipelines will break on the reorg and need their own change), PyPI + npm release mechanics, version synchronization automation between the two implementations.

## Capabilities

### New Capabilities
- `repo-layout`: the top-level folder structure contract — Python and TypeScript implementations as siblings under `python/` and `typescript/`, e2e harness at repo root, shared docs/license/openspec at the root.
- `typescript-cli`: the TypeScript engraft CLI — npm-published binary with identical command surface to the Python impl, Node ≥20 runtime, and behavioral conformance to all existing engine/action/variable specs.
- `e2e-harness`: the shared end-to-end test suite — implementation-parametrized pytest runner with semantic comparators for JSON/YAML/HTML/text output and a fixture scenario format.

### Modified Capabilities
- `unified-action-format`: `regex_replace` selector SHALL accept both `(?P<value>…)` and `(?<value>…)` named-group syntaxes; the existing error-on-missing-group requirement still applies to both.
- `engine`: template and values YAML parsing SHALL use YAML 1.2 semantics (previously PyYAML default of 1.1-ish) so `yes`/`no`/`on`/`off` parse as strings, making behavior consistent across the Python and TypeScript implementations.
- `readme`: project documentation is now split into a minimal root README plus one README per implementation; PyPI continues to render `python/README.md` and npm renders `typescript/README.md`.

## Impact

- **Affected code**: every file currently under `src/` and `tests/` moves (git mv) to `python/src/` and `python/tests/`. `pyproject.toml` moves to `python/pyproject.toml` with its internal paths unchanged (all still relative to `python/`). A new `typescript/` tree is introduced. A new `e2e/` tree is introduced.
- **Affected workflows**: `.github/workflows/pr.yml` and `.github/workflows/release.yml` will stop finding their targets (they reference `src/`, `tests/`, `pyproject.toml` at the repo root). These remain **untouched** in this change; fixing them is the follow-up change's sole responsibility. Contributors working locally during the transition window will install with `pip install -e python/` instead of `pip install -e .`.
- **Consumer impact — Python**: `pip install engraft` continues to work unchanged (PyPI artifact is produced from `python/`, module import path `engraft.*` stays the same). Templates that relied on YAML 1.1 boolean coercion for `yes`/`no`/`on`/`off` must quote those values — this is a breaking change in input parsing.
- **Consumer impact — TypeScript (new)**: Node-project consumers can run `npm install -g engraft` (or `npx engraft`) and get the same CLI. Runtime requirement: Node ≥20.
- **Template authoring**: `regex_replace` templates become portable across the two implementations; no migration needed for existing templates. Authors targeting only the TS impl may use the native ES syntax.
- **New external dependencies** (TS impl): `commander`, `js-yaml`, `jsdom`. Dev dependencies: `typescript`, `vitest`, `tsup`. No new Python dependencies.
- **Git history**: preserved across the reorg by using `git mv` for the Python subtree.
- **Versioning**: the version string reported by `engraft --version` is identical across implementations. The mechanism for keeping them in sync is deferred to the CI/release change.
