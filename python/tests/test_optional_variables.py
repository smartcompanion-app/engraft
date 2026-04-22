"""Tests for optional-variable noop semantics.

A variable declared in a template without a `default` field AND not set in the
values file resolves to None. Replace entries referencing such a variable are
skipped, leaving the target untouched.
"""

import json

import pytest
import yaml

from engraft.engine import apply


@pytest.fixture
def project(tmp_path):
    proj = tmp_path / "project"
    proj.mkdir()
    return proj


@pytest.fixture
def values_dir(tmp_path):
    vd = tmp_path / "values"
    vd.mkdir()
    return vd


def _write_template(path, data):
    path.write_text(yaml.dump(data))
    return path


def _write_values(path, data):
    path.write_text(yaml.dump(data))
    return path


def test_json_replace_skips_entry_when_variable_unset(tmp_path, project, values_dir):
    (project / "config.json").write_text(
        json.dumps({"name": "original", "version": "1.0.0"}, indent=2) + "\n"
    )

    template = _write_template(
        tmp_path / "template.yml",
        {
            "variables": {
                "app_name": {"description": "Name"},
                "app_version": {"description": "Version", "default": "2.0.0"},
            },
            "customizations": [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [
                        {"selector": "$.name", "variable": "app_name"},
                        {"selector": "$.version", "variable": "app_version"},
                    ],
                },
            ],
        },
    )
    values = _write_values(values_dir / "values.yml", {})

    apply(template, values, work_dir=project)

    data = json.loads((project / "config.json").read_text())
    assert data["name"] == "original"  # untouched — variable was unset
    assert data["version"] == "2.0.0"  # default applied


def test_regex_replace_skips_entry_when_variable_unset(tmp_path, project, values_dir):
    (project / "colors.ts").write_text(
        'export const PRIMARY = "#ff0000";\nexport const SECONDARY = "#00ff00";\n'
    )

    template = _write_template(
        tmp_path / "template.yml",
        {
            "variables": {
                "primary": {"description": "P"},  # no default
                "secondary": {"description": "S", "default": "#222222"},
            },
            "customizations": [
                {
                    "action": "regex_replace",
                    "file": "colors.ts",
                    "replace": [
                        {
                            "selector": r'(PRIMARY\s*=\s*)"(?P<value>[^"]*)"',
                            "variable": "primary",
                        },
                        {
                            "selector": r'(SECONDARY\s*=\s*)"(?P<value>[^"]*)"',
                            "variable": "secondary",
                        },
                    ],
                },
            ],
        },
    )
    values = _write_values(values_dir / "values.yml", {})

    apply(template, values, work_dir=project)

    content = (project / "colors.ts").read_text()
    assert "#ff0000" in content  # untouched
    assert "#222222" in content  # default applied
    assert "#00ff00" not in content


def test_file_replace_is_noop_when_variable_unset(tmp_path, project, values_dir):
    (project / "logo.png").write_bytes(b"ORIGINAL")

    template = _write_template(
        tmp_path / "template.yml",
        {
            "variables": {
                "logo_path": {"description": "Logo"},
            },
            "customizations": [
                {
                    "action": "file_replace",
                    "file": "logo.png",
                    "variable": "logo_path",
                },
            ],
        },
    )
    values = _write_values(values_dir / "values.yml", {})

    apply(template, values, work_dir=project)

    assert (project / "logo.png").read_bytes() == b"ORIGINAL"


def test_explicit_empty_default_is_not_skipped(tmp_path, project, values_dir):
    """default: "" should substitute empty, not skip the entry."""
    (project / "config.json").write_text(json.dumps({"prefix": "XXX"}, indent=2) + "\n")

    template = _write_template(
        tmp_path / "template.yml",
        {
            "variables": {
                "prefix": {"description": "P", "default": ""},
            },
            "customizations": [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [
                        {"selector": "$.prefix", "variable": "prefix"},
                    ],
                },
            ],
        },
    )
    values = _write_values(values_dir / "values.yml", {})

    apply(template, values, work_dir=project)

    data = json.loads((project / "config.json").read_text())
    assert data["prefix"] == ""


def test_explicit_empty_value_in_values_file_is_not_skipped(
    tmp_path, project, values_dir
):
    (project / "config.json").write_text(json.dumps({"note": "old"}, indent=2) + "\n")

    template = _write_template(
        tmp_path / "template.yml",
        {
            "variables": {
                "note": {"description": "N"},
            },
            "customizations": [
                {
                    "action": "json_replace",
                    "file": "config.json",
                    "replace": [
                        {"selector": "$.note", "variable": "note"},
                    ],
                },
            ],
        },
    )
    values = _write_values(values_dir / "values.yml", {"note": ""})

    apply(template, values, work_dir=project)

    data = json.loads((project / "config.json").read_text())
    assert data["note"] == ""
