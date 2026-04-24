import json

import pytest
import yaml

from engraft.engine import apply


@pytest.fixture
def project(tmp_path):
    """Create a mock project with JSON file, TS file, and image."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # JSON file
    (project_dir / "app.json").write_text(
        json.dumps(
            {
                "expo": {
                    "name": "DefaultApp",
                    "slug": "default-app",
                    "extra": {
                        "items": [
                            {"label": "Item One"},
                            {"label": "Item Two"},
                        ]
                    },
                }
            },
            indent=2,
        )
        + "\n"
    )

    # TS file
    (project_dir / "src").mkdir()
    (project_dir / "src" / "theme.ts").write_text(
        'export const PRIMARY_COLOR = "#ff0000";\n'
        'export const APP_TITLE = "Default App";\n'
    )

    # Image file
    (project_dir / "assets").mkdir()
    (project_dir / "assets" / "logo.png").write_bytes(b"\x89PNG default logo data")

    return project_dir


@pytest.fixture
def template_file(tmp_path):
    t = tmp_path / "engraft.template.yml"
    t.write_text(
        yaml.dump(
            {
                "variables": {
                    "app_name": {
                        "description": "Application name",
                        "default": "DefaultApp",
                    },
                    "app_slug": {"description": "URL slug", "default": "default-app"},
                    "primary_color": {
                        "description": "Primary color hex",
                        "default": "#ff0000",
                    },
                    "app_title": {"description": "App title", "default": "Default App"},
                    "item_one_label": {
                        "description": "First item label",
                        "default": "Item One",
                    },
                    "logo": {"description": "Path to logo file", "default": "logo.png"},
                },
                "customizations": [
                    {
                        "action": "json_replace",
                        "file": "app.json",
                        "replace": [
                            {"selector": "$.expo.name", "variable": "app_name"},
                            {"selector": "$.expo.slug", "variable": "app_slug"},
                            {
                                "selector": "$.expo.extra.items[0].label",
                                "variable": "item_one_label",
                            },
                        ],
                    },
                    {
                        "action": "regex_replace",
                        "file": "src/theme.ts",
                        "replace": [
                            {
                                "selector": r'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"',
                                "variable": "primary_color",
                            },
                            {
                                "selector": r'(APP_TITLE\s*=\s*)"(?P<value>[^"]*)"',
                                "variable": "app_title",
                            },
                        ],
                    },
                    {
                        "action": "file_replace",
                        "file": "assets/logo.png",
                        "variable": "logo",
                    },
                ],
            }
        )
    )
    return t


@pytest.fixture
def values_dir(tmp_path):
    vd = tmp_path / "my_values"
    vd.mkdir()
    return vd


def _make_values(values_dir, overrides):
    vf = values_dir / "engraft.values.yml"
    vf.write_text(yaml.dump(overrides))
    return vf


def test_full_apply(project, template_file, values_dir):
    # Set up custom logo
    (values_dir / "custom_logo.png").write_bytes(b"\x89PNG custom logo")

    values_file = _make_values(
        values_dir,
        {
            "app_name": "MyApp",
            "app_slug": "my-app",
            "primary_color": "#00ff00",
            "app_title": "My Application",
            "item_one_label": "Custom Item",
            "logo": "custom_logo.png",
        },
    )

    apply(template_file, values_file, work_dir=project)

    # Check JSON
    app_json = json.loads((project / "app.json").read_text())
    assert app_json["expo"]["name"] == "MyApp"
    assert app_json["expo"]["slug"] == "my-app"
    assert app_json["expo"]["extra"]["items"][0]["label"] == "Custom Item"
    assert app_json["expo"]["extra"]["items"][1]["label"] == "Item Two"

    # Check TS
    theme = (project / "src" / "theme.ts").read_text()
    assert "#00ff00" in theme
    assert "My Application" in theme
    assert "#ff0000" not in theme

    # Check logo
    assert (project / "assets" / "logo.png").read_bytes() == b"\x89PNG custom logo"


def test_reapplication(project, template_file, values_dir):
    (values_dir / "logo1.png").write_bytes(b"logo1")
    (values_dir / "logo2.png").write_bytes(b"logo2")

    # First apply
    v1 = _make_values(
        values_dir,
        {
            "app_name": "App1",
            "app_slug": "app-1",
            "primary_color": "#111111",
            "app_title": "Title One",
            "item_one_label": "Label1",
            "logo": "logo1.png",
        },
    )
    apply(template_file, v1, work_dir=project)

    theme = (project / "src" / "theme.ts").read_text()
    assert "#111111" in theme

    # Second apply with different values
    v2 = _make_values(
        values_dir,
        {
            "app_name": "App2",
            "app_slug": "app-2",
            "primary_color": "#222222",
            "app_title": "Title Two",
            "item_one_label": "Label2",
            "logo": "logo2.png",
        },
    )
    apply(template_file, v2, work_dir=project)

    # Verify second apply took effect
    app_json = json.loads((project / "app.json").read_text())
    assert app_json["expo"]["name"] == "App2"

    theme = (project / "src" / "theme.ts").read_text()
    assert "#222222" in theme
    assert "#111111" not in theme
    assert "Title Two" in theme

    assert (project / "assets" / "logo.png").read_bytes() == b"logo2"
