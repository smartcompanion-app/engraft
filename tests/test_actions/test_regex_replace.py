import pytest

from engraft.actions.regex_replace import RegexReplace


def test_basic_replacement(tmp_path):
    ts_file = tmp_path / "colors.ts"
    ts_file.write_text('export const PRIMARY_COLOR = "#ff0000";\n')

    action = RegexReplace(
        target=ts_file,
        selector=r'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"',
        value="#00ff00",
    )
    action.apply()

    assert "#00ff00" in ts_file.read_text()
    assert "#ff0000" not in ts_file.read_text()


def test_multiple_matches_in_file(tmp_path):
    ts_file = tmp_path / "config.ts"
    ts_file.write_text('const A = "old_value";\nconst B = "old_value";\n')

    action = RegexReplace(
        target=ts_file,
        selector=r'"(?P<value>old_value)"',
        value="new_value",
    )
    action.apply()

    content = ts_file.read_text()
    assert content.count('"new_value"') == 2
    assert "old_value" not in content


def test_reapplication(tmp_path):
    ts_file = tmp_path / "colors.ts"
    ts_file.write_text('export const PRIMARY_COLOR = "#ff0000";\n')

    action = RegexReplace(
        target=ts_file,
        selector=r'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"',
        value="#00ff00",
    )
    action.apply()
    assert "#00ff00" in ts_file.read_text()

    action2 = RegexReplace(
        target=ts_file,
        selector=r'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"',
        value="#0000ff",
    )
    action2.apply()
    assert "#0000ff" in ts_file.read_text()
    assert "#00ff00" not in ts_file.read_text()


def test_error_no_value_group(tmp_path):
    ts_file = tmp_path / "test.ts"
    ts_file.write_text("hello")

    action = RegexReplace(target=ts_file, selector=r"hello", value="world")
    with pytest.raises(ValueError, match="named group"):
        action.apply()


def test_error_no_match(tmp_path):
    ts_file = tmp_path / "test.ts"
    ts_file.write_text("hello world")

    action = RegexReplace(
        target=ts_file,
        selector=r'NONEXISTENT\s*=\s*"(?P<value>[^"]*)"',
        value="x",
    )
    with pytest.raises(ValueError, match="did not match"):
        action.apply()
