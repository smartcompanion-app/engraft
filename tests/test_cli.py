import json

import yaml
from click.testing import CliRunner

from engraft.cli import main


def _setup_project(tmp_path):
    """Create a minimal project with template and values for CLI testing."""
    project = tmp_path / "project"
    project.mkdir()
    config = json.dumps({"name": "default"}, indent=2) + "\n"
    (project / "config.json").write_text(config)

    template = tmp_path / "template.yml"
    template.write_text(
        yaml.dump(
            {
                "variables": {
                    "app_name": {"description": "App name", "default": "default"},
                },
                "customizations": [
                    {
                        "action": "json_replace",
                        "file": "config.json",
                        "replace": [{"selector": "$.name", "variable": "app_name"}],
                    },
                ],
            }
        )
    )

    values = tmp_path / "values.yml"
    values.write_text(yaml.dump({"app_name": "TestApp"}))

    return project, template, values


def test_apply_success(tmp_path, monkeypatch):
    project, template, values = _setup_project(tmp_path)
    monkeypatch.chdir(project)
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "apply",
            "--template",
            str(template),
            "--values",
            str(values),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    assert "Done" in result.output


def test_apply_missing_template(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "apply",
            "--template",
            str(tmp_path / "nonexistent.yml"),
            "--values",
            str(tmp_path / "values.yml"),
        ],
    )
    assert result.exit_code != 0


def test_apply_missing_values(tmp_path):
    template = tmp_path / "template.yml"
    template.write_text(yaml.dump({"variables": {}, "customizations": []}))

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "apply",
            "--template",
            str(template),
            "--values",
            str(tmp_path / "nonexistent.yml"),
        ],
    )
    assert result.exit_code != 0
