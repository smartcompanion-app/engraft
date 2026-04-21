import json

from engraft.actions.json_replace import JsonReplace


def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def _read_json(path):
    return json.loads(path.read_text())


def test_simple_path(tmp_path):
    f = tmp_path / "app.json"
    _write_json(f, {"name": "old"})

    action = JsonReplace(target=f, selector="$.name", value="MyApp")
    action.apply()

    assert _read_json(f)["name"] == "MyApp"


def test_nested_path(tmp_path):
    f = tmp_path / "app.json"
    _write_json(f, {"expo": {"name": "old", "version": "1.0"}})

    action = JsonReplace(target=f, selector="$.expo.name", value="NewApp")
    action.apply()

    data = _read_json(f)
    assert data["expo"]["name"] == "NewApp"
    assert data["expo"]["version"] == "1.0"


def test_array_index(tmp_path):
    f = tmp_path / "app.json"
    _write_json(f, {"items": [{"label": "first"}, {"label": "second"}]})

    action = JsonReplace(target=f, selector="$.items[0].label", value="updated")
    action.apply()

    assert _read_json(f)["items"][0]["label"] == "updated"
    assert _read_json(f)["items"][1]["label"] == "second"


def test_missing_intermediate_key(tmp_path):
    f = tmp_path / "app.json"
    _write_json(f, {})

    action = JsonReplace(target=f, selector="$.a.b.c", value="deep")
    action.apply()

    assert _read_json(f)["a"]["b"]["c"] == "deep"


def test_preserves_formatting(tmp_path):
    f = tmp_path / "app.json"
    _write_json(f, {"key": "val"})

    action = JsonReplace(target=f, selector="$.key", value="new")
    action.apply()

    content = f.read_text()
    assert content.startswith("{\n")
    assert "  " in content
    assert content.endswith("\n")
