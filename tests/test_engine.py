import json

import pytest
import yaml

from engraft.actions.file_replace import FileReplace
from engraft.actions.html_replace import HtmlReplace
from engraft.actions.json_replace import JsonReplace
from engraft.actions.regex_replace import RegexReplace
from engraft.engine import STAGING_DIR_NAME, apply


@pytest.fixture
def project(tmp_path):
    """Create a minimal project with a JSON file and a text file."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "config.json").write_text(
        json.dumps({"name": "original"}, indent=2) + "\n"
    )
    (project_dir / "src").mkdir()
    (project_dir / "src" / "theme.ts").write_text(
        'export const TITLE = "Original";\n'
    )
    return project_dir


@pytest.fixture
def values_dir(tmp_path):
    vd = tmp_path / "values"
    vd.mkdir()
    return vd


def _make_template(tmp_path, customizations, variables=None):
    """Write a template YAML and return its path."""
    if variables is None:
        variables = {
            "app_name": {"description": "Name", "default": "original"},
        }
    t = tmp_path / "template.yml"
    t.write_text(yaml.dump({
        "variables": variables,
        "customizations": customizations,
    }))
    return t


def _make_values(values_dir, overrides):
    vf = values_dir / "values.yml"
    vf.write_text(yaml.dump(overrides))
    return vf


class TestStagingDirectorySuccess:
    """Test that successful apply copies results back and cleans up."""

    def test_apply_modifies_project_files(self, tmp_path, project, values_dir):
        template = _make_template(tmp_path, [
            {
                "action": "json_replace",
                "file": "config.json",
                "replace": [{"selector": "$.name", "variable": "app_name"}],
            },
        ])
        values = _make_values(values_dir, {"app_name": "NewApp"})

        apply(template, values, work_dir=project)

        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "NewApp"

    def test_staging_dir_removed_after_success(self, tmp_path, project, values_dir):
        template = _make_template(tmp_path, [
            {
                "action": "json_replace",
                "file": "config.json",
                "replace": [{"selector": "$.name", "variable": "app_name"}],
            },
        ])
        values = _make_values(values_dir, {"app_name": "NewApp"})

        apply(template, values, work_dir=project)

        assert not (project / STAGING_DIR_NAME).exists()


class TestStagingDirectoryRollback:
    """Test that failed actions leave the project untouched."""

    def test_failed_action_preserves_original_files(
        self, tmp_path, project, values_dir
    ):
        """When second action fails, first action's changes are rolled back."""
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [
                        {"selector": "$.name", "variable": "app_name"},
                    ],
                },
                {
                    "action": "regex_replace",
                    "file": "src/theme.ts",
                    "replace": [
                        {
                            "selector": r'NONEXISTENT\s*=\s*"(?P<value>[^"]*)"',
                            "variable": "app_name",
                        },
                    ],
                },
            ],
            variables={
                "app_name": {"description": "Name", "default": "original"},
            },
        )
        values = _make_values(values_dir, {"app_name": "NewApp"})

        with pytest.raises(ValueError):
            apply(template, values, work_dir=project)

        # Original files should be untouched
        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "original"

        theme = (project / "src" / "theme.ts").read_text()
        assert "Original" in theme

    def test_staging_dir_removed_after_failure(self, tmp_path, project, values_dir):
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "regex_replace",
                    "file": "src/theme.ts",
                    "replace": [
                        {
                            "selector": r'NONEXISTENT\s*=\s*"(?P<value>[^"]*)"',
                            "variable": "app_name",
                        },
                    ],
                },
            ],
        )
        values = _make_values(values_dir, {"app_name": "NewApp"})

        with pytest.raises(ValueError):
            apply(template, values, work_dir=project)

        assert not (project / STAGING_DIR_NAME).exists()


class TestStagingDirectoryPreexisting:
    """Test that a pre-existing .engraft/ directory is handled."""

    def test_preexisting_staging_dir_is_removed(
        self, tmp_path, project, values_dir
    ):
        # Create a leftover .engraft/ directory
        leftover = project / STAGING_DIR_NAME
        leftover.mkdir()
        (leftover / "stale.txt").write_text("leftover")

        template = _make_template(tmp_path, [
            {
                "action": "json_replace",
                "file": "config.json",
                "replace": [{"selector": "$.name", "variable": "app_name"}],
            },
        ])
        values = _make_values(values_dir, {"app_name": "NewApp"})

        apply(template, values, work_dir=project)

        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "NewApp"
        assert not (project / STAGING_DIR_NAME).exists()


class TestTargetFiles:
    """Test that target_files() returns correct paths for each action type."""

    def test_json_replace_target_files(self):
        action = JsonReplace(file="config.json", replace=[])
        assert action.target_files() == ["config.json"]

    def test_regex_replace_target_files(self):
        action = RegexReplace(file="src/theme.ts", replace=[])
        assert action.target_files() == ["src/theme.ts"]

    def test_file_replace_target_files(self):
        action = FileReplace(file="assets/logo.png", variable="logo")
        assert action.target_files() == ["assets/logo.png"]

    def test_html_replace_target_files(self):
        action = HtmlReplace(file="index.html", replace=[])
        assert action.target_files() == ["index.html"]
