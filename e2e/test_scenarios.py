"""E2E scenario runner.

Discovers each subdirectory under ``e2e/fixtures/``, copies its ``input/``
tree into a pytest tmp_path, invokes the selected engraft implementation
with the fixture's ``template.yaml`` and ``values.yaml``, then compares
the result against ``expected/`` using the semantic comparators.

Fixtures may include:
- ``expect_failure`` file (any content): assert the CLI exits non-zero and
  that ``expected/`` matches the UNCHANGED input tree (rollback scenarios).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from comparators import compare_tree

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _discover_scenarios() -> list[str]:
    if not FIXTURES_DIR.exists():
        return []
    return sorted(
        p.name
        for p in FIXTURES_DIR.iterdir()
        if p.is_dir() and (p / "template.yaml").exists()
    )


@pytest.mark.parametrize("scenario", _discover_scenarios())
def test_scenario(engraft_cli, scenario: str, tmp_path: Path) -> None:
    fixture = FIXTURES_DIR / scenario
    input_dir = fixture / "input"
    expected_dir = fixture / "expected"
    template = fixture / "template.yaml"
    values = fixture / "values.yaml"
    expect_failure = (fixture / "expect_failure").exists()

    work = tmp_path / "work"
    shutil.copytree(input_dir, work)

    result = engraft_cli(
        [
            "apply",
            "--template",
            str(template),
            "--values",
            str(values),
        ],
        cwd=work,
        check=not expect_failure,
    )

    if expect_failure:
        assert result.returncode != 0, (
            f"Expected failure but CLI exited 0\n"
            f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
        )

    compare_tree(expected_dir, work)
