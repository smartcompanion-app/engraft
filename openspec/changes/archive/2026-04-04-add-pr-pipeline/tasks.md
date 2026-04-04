## 1. Project Configuration

- [x] 1.1 Add `pytest>=7.0` to dev dependencies in `pyproject.toml`

## 2. GitHub Actions Workflow

- [x] 2.1 Create `.github/workflows/pr.yml` with PR trigger on `main`
- [x] 2.2 Add lint job: checkout, setup Python 3.13 with pip cache, install dev deps, run `ruff check .` and `ruff format --check .`
- [x] 2.3 Add test job: checkout, setup Python matrix (3.10, 3.12, 3.13) with pip cache, install dev deps, run `pytest`; set `needs: lint`

## 3. Verification

- [x] 3.1 Verify workflow YAML is valid and all action versions are pinned to major tags
