import json

import pytest
import yaml

from engraft.engine import STAGING_DIR_NAME, apply, resolve_variables
from engraft.models import Template, Variable


def _make_template(tmp_path, customizations, variables=None):
    """Write a template YAML and return its path."""
    if variables is None:
        variables = [
            {"variable": "app_name", "description": "Name", "default": "original"},
        ]
    t = tmp_path / "template.yml"
    t.write_text(yaml.dump({"variables": variables, "customizations": customizations}))
    return t


def _make_values(values_dir, overrides):
    vf = values_dir / "values.yml"
    vf.write_text(yaml.dump(overrides))
    return vf


@pytest.fixture
def project(tmp_path):
    """Create a minimal project with a JSON file and a text file."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "config.json").write_text(
        json.dumps({"name": "original"}, indent=2) + "\n"
    )
    (project_dir / "src").mkdir()
    (project_dir / "src" / "theme.ts").write_text('export const TITLE = "Original";\n')
    return project_dir


@pytest.fixture
def values_dir(tmp_path):
    vd = tmp_path / "values"
    vd.mkdir()
    return vd


class TestResolveVariables:
    """Test variable resolution logic."""

    def test_value_overrides_default(self):
        template = Template(
            variables=[Variable(name="x", description="", default="default_val")],
            customizations=[],
        )
        result = resolve_variables(template, {"x": "override"})
        assert result == {"x": "override"}

    def test_default_used_when_no_value(self):
        template = Template(
            variables=[Variable(name="x", description="", default="default_val")],
            customizations=[],
        )
        result = resolve_variables(template, {})
        assert result == {"x": "default_val"}

    def test_unset_variable_omitted(self):
        template = Template(
            variables=[Variable(name="x", description="", default=None)],
            customizations=[],
        )
        result = resolve_variables(template, {})
        assert "x" not in result

    def test_unset_variable_with_value_included(self):
        template = Template(
            variables=[Variable(name="x", description="", default=None)],
            customizations=[],
        )
        result = resolve_variables(template, {"x": "provided"})
        assert result == {"x": "provided"}

    def test_mixed_set_and_unset(self):
        template = Template(
            variables=[
                Variable(name="a", description="", default="default_a"),
                Variable(name="b", description="", default=None),
                Variable(name="c", description="", default=None),
            ],
            customizations=[],
        )
        result = resolve_variables(template, {"c": "val_c"})
        assert result == {"a": "default_a", "c": "val_c"}
        assert "b" not in result


class TestStagingDirectorySuccess:
    """Test that successful apply copies results back and cleans up."""

    def test_apply_modifies_project_files(self, tmp_path, project, values_dir):
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [{"selector": "$.name", "variable": "app_name"}],
                },
            ],
        )
        values = _make_values(values_dir, {"app_name": "NewApp"})

        apply(template, values, work_dir=project)

        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "NewApp"

    def test_staging_dir_removed_after_success(self, tmp_path, project, values_dir):
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [{"selector": "$.name", "variable": "app_name"}],
                },
            ],
        )
        values = _make_values(values_dir, {"app_name": "NewApp"})

        apply(template, values, work_dir=project)

        assert not (project / STAGING_DIR_NAME).exists()


class TestStagingDirectoryRollback:
    """Test that failed actions leave the project untouched."""

    def test_failed_action_preserves_original_files(
        self, tmp_path, project, values_dir
    ):
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [{"selector": "$.name", "variable": "app_name"}],
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
            variables=[
                {"variable": "app_name", "description": "Name", "default": "original"},
            ],
        )
        values = _make_values(values_dir, {"app_name": "NewApp"})

        with pytest.raises(ValueError):
            apply(template, values, work_dir=project)

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

    def test_preexisting_staging_dir_is_removed(self, tmp_path, project, values_dir):
        leftover = project / STAGING_DIR_NAME
        leftover.mkdir()
        (leftover / "stale.txt").write_text("leftover")

        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [{"selector": "$.name", "variable": "app_name"}],
                },
            ],
        )
        values = _make_values(values_dir, {"app_name": "NewApp"})

        apply(template, values, work_dir=project)

        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "NewApp"
        assert not (project / STAGING_DIR_NAME).exists()


class TestUnsetVariableNoop:
    """Test that unset variables result in skipped actions."""

    def test_unset_variable_skips_action(self, tmp_path, project, values_dir):
        """An action referencing an unset variable is not executed."""
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [{"selector": "$.name", "variable": "theme_color"}],
                },
            ],
            variables=[
                {"variable": "theme_color", "description": "Color"},
            ],
        )
        values = _make_values(values_dir, {})

        apply(template, values, work_dir=project)

        # File should be unchanged
        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "original"

    def test_mixed_set_and_unset_in_replace_list(self, tmp_path, project, values_dir):
        """Only the set variable's replacement is applied."""
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [
                        {"selector": "$.name", "variable": "app_name"},
                        {"selector": "$.theme", "variable": "theme_color"},
                    ],
                },
            ],
            variables=[
                {"variable": "app_name", "description": "Name", "default": "original"},
                {"variable": "theme_color", "description": "Color"},
            ],
        )
        values = _make_values(values_dir, {"app_name": "NewApp"})

        apply(template, values, work_dir=project)

        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "NewApp"
        assert "theme" not in data

    def test_all_variables_unset_no_changes(self, tmp_path, project, values_dir):
        """When all variables are unset, no actions run and files are unchanged."""
        template = _make_template(
            tmp_path,
            [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [{"selector": "$.name", "variable": "optional_var"}],
                },
            ],
            variables=[
                {"variable": "optional_var", "description": "Optional"},
            ],
        )
        values = _make_values(values_dir, {})

        apply(template, values, work_dir=project)

        data = json.loads((project / "config.json").read_text())
        assert data["name"] == "original"
