## Why

The `add-typescript-implementation` change moved the Python project into `python/` and added a parallel TypeScript implementation under `typescript/`, plus a shared pytest e2e harness under `e2e/`. The existing `pr.yml` still assumes pyproject.toml sits at the repo root and has no awareness of the TypeScript code or the e2e harness — meaning PRs currently run a broken Python pipeline and no TypeScript validation at all. We need to update CI so every PR verifies both implementations and the shared parity harness before it can merge.

## What Changes

- Adapt the Python lint + test jobs to run inside `python/` (install with `pip install -e "./python[dev]"`, lint `python/src python/tests`, run `pytest` from `python/`).
- Add a **TypeScript lint** job that runs `npm ci` and `npm run lint` (tsc --noEmit) from `typescript/`.
- Add a **TypeScript test** job that runs `npm ci`, `npm run build`, and `npm test` from `typescript/` across Node 20 and 22.
- Add an **e2e parity** job that installs the Python CLI, builds the TypeScript CLI, and runs `pytest e2e/` once both impls are available; depends on both `test` jobs.
- Keep the existing `lint → test` gate for Python; add an analogous gate for TypeScript; the e2e job gates on all four upstream jobs.

## Capabilities

### New Capabilities

(none — this is a modification to existing CI capabilities)

### Modified Capabilities

- `pr-ci-pipeline`: existing requirements described a single-language (Python) workflow at the repo root; they must be rewritten to cover the dual-implementation layout (Python under `python/`, TypeScript under `typescript/`) and to add requirements for the TypeScript jobs and the e2e parity job.

## Impact

- **CI configuration**: `.github/workflows/pr.yml` is rewritten to add TS jobs, an e2e job, and corrected working directories for Python.
- **Developer workflow**: PR runtime grows (two additional jobs plus a parity job), but `fail-fast` behaviour is unchanged — a broken impl fails quickly without wasting compute on the other.
- **Release pipeline**: `.github/workflows/release.yml` has the same Python-at-repo-root assumption but is **out of scope** here; it will be addressed in a follow-up change once the TS publishing story is designed.
- **No runtime code changes**: only CI configuration and (if needed) dev-dependency declarations are touched.
