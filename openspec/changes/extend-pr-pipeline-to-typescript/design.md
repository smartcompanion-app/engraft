## Context

After `add-typescript-implementation`, the repo hosts two parallel engraft implementations (`python/` and `typescript/`) plus a shared pytest e2e harness (`e2e/`) that runs every fixture against both CLIs. The existing `.github/workflows/pr.yml` predates that reorg: it installs Python from a root-level `pyproject.toml`, runs `ruff check .` and `pytest` from the repo root, and has no awareness of the TypeScript tree or the parity harness.

Concretely, three things are now wrong or missing:

1. **Python paths are stale** — `pip install -e ".[dev]"`, `ruff check .`, and `pytest` at the root all fail because the relevant files moved to `python/`.
2. **TypeScript is unverified** — lint, type-check, build, and tests never run in CI.
3. **Parity is unverified** — the e2e harness that proves Python and TypeScript behave identically is not executed on PRs, which is exactly where divergence would first appear.

The release pipeline (`release.yml`) has the same Python-at-root problem, but adding TypeScript publishing is a separate design question (npm provenance, version-tag mapping, build-matrix ordering) and is deferred.

## Goals / Non-Goals

**Goals:**
- PRs run a working Python lint + test pipeline after the subtree move.
- PRs run a TypeScript lint job (type-check via `tsc --noEmit`) and a TypeScript test job (`npm run build && npm test`) across supported Node versions.
- PRs run the shared e2e harness (`pytest e2e/`) with both CLIs installed/built, so any cross-impl regression fails the PR.
- Jobs fail fast: a broken impl should not waste minutes on the other.

**Non-Goals:**
- Updating `release.yml` to publish the TypeScript package — deferred.
- Adding ESLint/Prettier for TypeScript. `tsc --noEmit` is the lint for now (matches the `npm run lint` script already defined in `typescript/package.json`).
- Changing the Python test matrix (stays at 3.10, 3.12, 3.13).
- Changing the Node test matrix beyond what's necessary for meaningful coverage.

## Decisions

### 1. One job per language/layer, not a monolithic job

Keep the current "job per responsibility" pattern: `py-lint`, `py-test`, `ts-lint`, `ts-test`, `e2e`. This preserves fail-fast behaviour (lint fails → tests skip), makes the PR check list legible on GitHub, and keeps each job's setup step minimal.

**Alternative considered:** one combined "validate" job that runs everything sequentially. Rejected because a failure would hide which impl broke and the matrix dimension for Python versions doesn't compose cleanly with it.

### 2. Run Python steps from `python/` via working-directory, not from the repo root

Each Python step sets `working-directory: python` and uses `pip install -e .[dev]`. This matches the `CLAUDE.md` guidance that Python commands are run from inside `python/` and avoids editing `pyproject.toml` to dodge the relocation.

**Alternative considered:** `pip install -e ./python[dev]` from the repo root. Rejected because it would leave ruff and pytest invocations still needing to `cd python/` or pass explicit paths, and mixing styles is noisier than consistently using `working-directory`.

### 3. TypeScript matrix: Node 20 only (for now)

`typescript/package.json` declares `engines.node >=20`. Testing on Node 20 covers the minimum supported version. Adding Node 22 doubles the CI footprint for little real-world signal until we have concrete Node-version-specific bugs to guard against.

**Alternative considered:** matrix over Node 20 and 22. Documented in "Open Questions" — easy to add later; start small.

### 4. E2E job installs the Python CLI with `pip install -e ./python`, builds the TypeScript CLI once, runs `pytest e2e/` once

The e2e harness already auto-detects both impls (via `shutil.which("engraft")` and the presence of `typescript/dist/cli.js`). A single job can satisfy both preconditions in a single runner. Running the harness twice (once per impl via `ENGRAFT_IMPL=...`) would double minutes without changing the outcome, since the harness already asserts both impls independently in one run.

**Alternative considered:** a matrix job over `ENGRAFT_IMPL=python` and `ENGRAFT_IMPL=typescript`. Rejected for the reason above; the in-process parametrization gives us per-impl test identifiers without splitting the job.

### 5. E2E job depends on both `py-test` and `ts-test`

`needs: [py-test, ts-test]`. If either language's own tests fail, the e2e job is skipped — no point running parity tests when one impl is already known to be broken, and it keeps the PR check list honest about which failure is the root cause.

### 6. Install steps are explicit, no `actions/cache` gymnastics beyond what `setup-python`/`setup-node` already provide

`cache: pip` and `cache: npm` on the respective setup actions handle the common case. We're not introducing custom cache keys; that's optimization we can add once CI time becomes a visible pain point.

## Risks / Trade-offs

- [E2E job depends on two language runtimes in one runner] → Accepted complexity. The alternative (orchestrating artifacts between jobs to avoid re-installing) is worth more ceremony only if the job becomes slow in practice.
- [ts-lint is only `tsc --noEmit`, not an actual linter] → Matches what `typescript/package.json` currently calls `lint`. If we later add ESLint, the PR workflow only needs the added `npm run eslint` step — the job structure stays the same.
- [release.yml continues to be broken for Python in the meantime] → Release is gated on `release: published`, not PRs. It will fail loudly the next time someone publishes, forcing the follow-up change. We explicitly do **not** silently fix it here because the TypeScript release story deserves its own design pass.
- [Longer total PR time] → Acceptable; all new jobs run in parallel where the dependency graph allows, so wall-clock impact is bounded by the e2e job's runtime.

## Migration Plan

1. Land this change as a single PR that rewrites `.github/workflows/pr.yml`.
2. The same PR exercises the new pipeline end-to-end (it triggers `pr.yml` on itself). Any misconfiguration is surfaced before merge.
3. No rollback needed beyond reverting the PR — no production systems depend on CI's shape.

## Open Questions

- Do we want Node 22 in the matrix now, or wait until we hit a concrete Node-version-specific bug? (Default in this design: wait.)
- Should the e2e job also run `ruff check` on `e2e/`? Currently it's a loose Python directory with no lint gate. Could be added here or in a follow-up. (Default in this design: follow-up — keeps this change focused.)
