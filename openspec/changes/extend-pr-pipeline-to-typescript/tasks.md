## 1. Rewrite `.github/workflows/pr.yml`

- [x] 1.1 Rename the existing `lint` job to `py-lint`; add `working-directory: python` to the lint and format steps; change the install step to `pip install -e .[dev]`; leave the `actions/setup-python` cache and Python version pinned at 3.13
- [x] 1.2 Rename the existing `test` job to `py-test`; point its `needs:` at `py-lint`; add `working-directory: python` to the install and pytest steps; keep the 3.10 / 3.12 / 3.13 matrix intact
- [x] 1.3 Add a new `ts-lint` job that runs on `ubuntu-latest`, checks out the repo, uses `actions/setup-node@v4` with Node 20 and `cache: npm` / `cache-dependency-path: typescript/package-lock.json`, then runs `npm ci` and `npm run lint` with `working-directory: typescript`
- [x] 1.4 Add a new `ts-test` job with `needs: ts-lint` that sets up Node 20 the same way and runs `npm ci`, `npm run build`, and `npm test` with `working-directory: typescript`
- [x] 1.5 Add a new `e2e` job with `needs: [py-test, ts-test]` that: checks out the repo, sets up Python 3.13 and Node 20, installs the Python CLI with `pip install -e ./python[dev]`, builds the TypeScript CLI with `npm ci && npm run build` in `typescript/`, installs the e2e harness runtime deps (`pip install pyyaml lxml pytest`) if not already covered by the Python dev extras, and runs `pytest e2e/` from the repo root
- [x] 1.6 Confirm the workflow still triggers only on `pull_request: branches: [main]` — the trigger block is unchanged

## 2. Verify a `typescript/package-lock.json` exists and is committed

- [x] 2.1 From `typescript/`, run `npm install` if a lock file is missing, so `npm ci` in CI works deterministically
- [x] 2.2 Commit the lock file if it isn't already tracked (update `typescript/.gitignore` only if it currently excludes lock files)

## 3. Verify the e2e harness can be installed without the full Python dev extras

- [x] 3.1 Confirm the e2e harness only needs `pytest`, `pyyaml`, and `lxml` at runtime (review `e2e/conftest.py`, `e2e/comparators.py`, `e2e/test_scenarios.py` imports)
- [x] 3.2 If any of those are missing from `python/pyproject.toml`'s `[project.optional-dependencies] dev` list, add them so `pip install -e ./python[dev]` is sufficient for the e2e job; otherwise install them explicitly in the e2e job — `pyyaml` and `lxml` are already runtime deps, `pytest` is in the `dev` extra, so no changes needed

## 4. Local dry run of the new workflow

- [x] 4.1 From `python/`, run `ruff check .` and `ruff format --check .` — SHALL pass (one pre-existing file reformatted so `ruff format --check .` passes cleanly)
- [x] 4.2 From `python/`, run `pip install -e .[dev] && pytest` on the developer's primary Python version — SHALL pass (71 tests green on 3.10.15)
- [x] 4.3 From `typescript/`, run `npm ci && npm run lint` — SHALL pass (`tsc --noEmit` clean)
- [x] 4.4 From `typescript/`, run `npm ci && npm run build && npm test` — SHALL pass (build → dist/cli.js 13.18 KB; 39 vitest tests green)
- [x] 4.5 From the repo root, run `pytest e2e/` — every fixture SHALL pass against both implementations (14 tests green: 7 fixtures × 2 impls)

## 5. Verification

- [ ] 5.1 Push the change to a branch and open a draft PR; observe that every job (`py-lint`, `py-test` × 3, `ts-lint`, `ts-test`, `e2e`) runs and the dependency graph matches the design (`py-test` waits for `py-lint`; `ts-test` waits for `ts-lint`; `e2e` waits for both `py-test` and `ts-test`)
- [ ] 5.2 Intentionally break a Python test locally, push, and confirm `py-test` fails and `e2e` is skipped (can also be simulated by adding a deliberately failing `@pytest.mark.xfail(strict=True)` test, then reverting before merge)
- [ ] 5.3 Revert the intentional failure
- [x] 5.4 Confirm `openspec validate extend-pr-pipeline-to-typescript --strict` succeeds
