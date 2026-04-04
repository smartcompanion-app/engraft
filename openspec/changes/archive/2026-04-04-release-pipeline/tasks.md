## 1. Dynamic Versioning

- [x] 1.1 Update `pyproject.toml`: add `hatch-vcs` to `[build-system] requires`
- [x] 1.2 Update `pyproject.toml`: remove hardcoded `version`, add `dynamic = ["version"]`, add `[tool.hatch.version]` with `source = "vcs"`

## 2. Release Workflow

- [x] 2.1 Create `.github/workflows/release.yml` with `on: release: types: [published]` trigger
- [x] 2.2 Add lint job: checkout, setup Python 3.13, install deps, run `ruff check .` and `ruff format --check .`
- [x] 2.3 Add test job (depends on lint): checkout, setup Python matrix (3.10, 3.12, 3.13), install deps, run `pytest`
- [x] 2.4 Add build job (depends on test): checkout, setup Python 3.13, install `build`, run `python -m build`, upload `dist/` as artifact
- [x] 2.5 Add publish job (depends on build): use `pypi` environment, download artifact, publish with `pypa/gh-action-pypi-publish` with `attestations: true`, set `id-token: write` permission
