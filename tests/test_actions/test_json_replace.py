import json

import pytest

from engraft.actions.json_replace import JsonReplace


@pytest.fixture
def work_dir(tmp_path):
    return tmp_path


@pytest.fixture
def values_dir(tmp_path):
    return tmp_path / "values"


def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def _read_json(path):
    return json.loads(path.read_text())


def test_simple_path(work_dir, values_dir):
    f = work_dir / "app.json"
    _write_json(f, {"name": "old"})

    action = JsonReplace(
        file="app.json",
        replace=[
            {"selector": "$.name", "variable": "app_name"},
        ],
    )
    action.apply({"app_name": "MyApp"}, work_dir, values_dir)

    assert _read_json(f)["name"] == "MyApp"


def test_nested_path(work_dir, values_dir):
    f = work_dir / "app.json"
    _write_json(f, {"expo": {"name": "old", "version": "1.0"}})

    action = JsonReplace(
        file="app.json",
        replace=[
            {"selector": "$.expo.name", "variable": "app_name"},
        ],
    )
    action.apply({"app_name": "NewApp"}, work_dir, values_dir)

    data = _read_json(f)
    assert data["expo"]["name"] == "NewApp"
    assert data["expo"]["version"] == "1.0"


def test_array_index(work_dir, values_dir):
    f = work_dir / "app.json"
    _write_json(f, {"items": [{"label": "first"}, {"label": "second"}]})

    action = JsonReplace(
        file="app.json",
        replace=[
            {"selector": "$.items[0].label", "variable": "lbl"},
        ],
    )
    action.apply({"lbl": "updated"}, work_dir, values_dir)

    assert _read_json(f)["items"][0]["label"] == "updated"
    assert _read_json(f)["items"][1]["label"] == "second"


def test_missing_intermediate_key(work_dir, values_dir):
    f = work_dir / "app.json"
    _write_json(f, {})

    action = JsonReplace(
        file="app.json",
        replace=[
            {"selector": "$.a.b.c", "variable": "val"},
        ],
    )
    action.apply({"val": "deep"}, work_dir, values_dir)

    assert _read_json(f)["a"]["b"]["c"] == "deep"


def test_multiple_replacements(work_dir, values_dir):
    f = work_dir / "app.json"
    _write_json(f, {"name": "old", "version": "0.0"})

    action = JsonReplace(
        file="app.json",
        replace=[
            {"selector": "$.name", "variable": "app_name"},
            {"selector": "$.version", "variable": "app_version"},
        ],
    )
    action.apply({"app_name": "MyApp", "app_version": "1.0"}, work_dir, values_dir)

    data = _read_json(f)
    assert data["name"] == "MyApp"
    assert data["version"] == "1.0"


def test_preserves_formatting(work_dir, values_dir):
    f = work_dir / "app.json"
    _write_json(f, {"key": "val"})

    action = JsonReplace(
        file="app.json",
        replace=[
            {"selector": "$.key", "variable": "v"},
        ],
    )
    action.apply({"v": "new"}, work_dir, values_dir)

    content = f.read_text()
    assert content.startswith("{\n")
    assert "  " in content
    assert content.endswith("\n")
