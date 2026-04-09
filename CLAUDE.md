# engraft

CLI tool that applies customizations to any project without requiring templating placeholders. Uses a two-file model: a **template** (what can be customized) and a **values** file (the consumer's choices).

## Architecture

```
CLI (cli.py)
 └─ engine.apply()          # resolves variables, builds actions, runs them
     ├─ models.py            # parses template + values YAML files
     └─ actions/             # plugin registry for action types
         ├─ __init__.py      # registry: @register decorator + get_action_class()
         ├─ base.py          # Action ABC (zero-arg apply method)
         ├─ json_replace.py  # JSONPath-like selectors
         ├─ html_replace.py  # XPath selectors via lxml
         ├─ regex_replace.py # named capture group (?P<value>...)
         └─ file_replace.py  # whole-file replacement
```

Actions are fully resolved at construction: each holds `target: Path`, `selector: str`, `value: str` (or `target: Path`, `source_path: Path` for file_replace). `apply()` takes no arguments. The engine expands multi-entry `replace` lists into individual actions and skips entries for unset variables.

New actions: create a dataclass in `actions/`, use `@register("name")`, import it in `actions/__init__.py`.

## Commands

```bash
pip install -e ".[dev]"    # install with dev dependencies
pytest                      # run tests
ruff check src/ tests/      # lint
engraft apply --template <file> --values <file>  # run the tool
```

## Conventions

- Python 3.10+, type hints throughout
- Build: hatchling (configured in pyproject.toml)
- Linting: ruff (rules: E, F, I, UP, B)
- Testing: pytest, tests mirror src structure (`tests/test_actions/`)
- Line length: 88 characters
- Versioning: hatch-vcs (version derived from git tags, not hardcoded)

## CI/CD

- **PR pipeline** (`.github/workflows/pr.yml`): lint, format check, test matrix (3.10, 3.12, 3.13)
- **Release pipeline** (`.github/workflows/release.yml`): triggered on GitHub Release publish → lint → format check → test matrix → build → publish to PyPI (Trusted Publisher OIDC + Sigstore signing)
