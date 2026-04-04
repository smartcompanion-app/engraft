
import pytest

from engraft.actions.regex_replace import RegexReplace


@pytest.fixture
def work_dir(tmp_path):
    return tmp_path


@pytest.fixture
def values_dir(tmp_path):
    return tmp_path / "values"


def test_basic_replacement(work_dir, values_dir):
    ts_file = work_dir / "colors.ts"
    ts_file.write_text('export const PRIMARY_COLOR = "#ff0000";\n')

    action = RegexReplace(file="colors.ts", replace=[
        {"selector": r'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"', "variable": "primary_color"},
    ])
    action.apply({"primary_color": "#00ff00"}, work_dir, values_dir)

    assert '#00ff00' in ts_file.read_text()
    assert '#ff0000' not in ts_file.read_text()


def test_multiple_replacements(work_dir, values_dir):
    ts_file = work_dir / "colors.ts"
    ts_file.write_text(
        'export const PRIMARY_COLOR = "#ff0000";\n'
        'export const SECONDARY_COLOR = "#00ff00";\n'
    )

    action = RegexReplace(file="colors.ts", replace=[
        {"selector": r'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"', "variable": "primary"},
        {"selector": r'(SECONDARY_COLOR\s*=\s*)"(?P<value>[^"]*)"', "variable": "secondary"},
    ])
    action.apply({"primary": "#111111", "secondary": "#222222"}, work_dir, values_dir)

    content = ts_file.read_text()
    assert "#111111" in content
    assert "#222222" in content
    assert "#ff0000" not in content
    assert "#00ff00" not in content


def test_multiple_matches_in_file(work_dir, values_dir):
    ts_file = work_dir / "config.ts"
    ts_file.write_text(
        'const A = "old_value";\nconst B = "old_value";\n'
    )

    action = RegexReplace(file="config.ts", replace=[
        {"selector": r'"(?P<value>old_value)"', "variable": "val"},
    ])
    action.apply({"val": "new_value"}, work_dir, values_dir)

    content = ts_file.read_text()
    assert content.count('"new_value"') == 2
    assert "old_value" not in content


def test_reapplication(work_dir, values_dir):
    ts_file = work_dir / "colors.ts"
    ts_file.write_text('export const PRIMARY_COLOR = "#ff0000";\n')

    action = RegexReplace(file="colors.ts", replace=[
        {"selector": r'(PRIMARY_COLOR\s*=\s*)"(?P<value>[^"]*)"', "variable": "primary_color"},
    ])

    action.apply({"primary_color": "#00ff00"}, work_dir, values_dir)
    assert "#00ff00" in ts_file.read_text()

    action.apply({"primary_color": "#0000ff"}, work_dir, values_dir)
    assert "#0000ff" in ts_file.read_text()
    assert "#00ff00" not in ts_file.read_text()


def test_error_no_value_group(work_dir, values_dir):
    ts_file = work_dir / "test.ts"
    ts_file.write_text("hello")

    action = RegexReplace(file="test.ts", replace=[
        {"selector": r"hello", "variable": "val"},
    ])
    with pytest.raises(ValueError, match="named group"):
        action.apply({"val": "world"}, work_dir, values_dir)


def test_error_no_match(work_dir, values_dir):
    ts_file = work_dir / "test.ts"
    ts_file.write_text("hello world")

    action = RegexReplace(file="test.ts", replace=[
        {"selector": r'NONEXISTENT\s*=\s*"(?P<value>[^"]*)"', "variable": "val"},
    ])
    with pytest.raises(ValueError, match="did not match"):
        action.apply({"val": "x"}, work_dir, values_dir)
