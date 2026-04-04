
import pytest

from engraft.actions.html_replace import HtmlReplace

SAMPLE_HTML = """\
<!DOCTYPE html>
<html dir="ltr" lang="en">
<head>
  <meta charset="utf-8">
  <title>Animals Audioguide</title>
  <meta name="Description" content="A sample audioguide app for animals">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
  <meta name="theme-color" content="#faefdc">
</head>
<body>
  <p>First paragraph</p>
  <p>Second paragraph</p>
  <p>Third paragraph</p>
</body>
</html>"""


@pytest.fixture
def work_dir(tmp_path):
    return tmp_path


@pytest.fixture
def values_dir(tmp_path):
    return tmp_path / "values"


def test_set_element_text(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": "//title", "variable": "my_title"},
    ])
    action.apply({"my_title": "New Title"}, work_dir, values_dir)

    content = f.read_text()
    assert "<title>New Title</title>" in content
    assert "Animals Audioguide" not in content


def test_set_attribute(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": '//meta[@name="Description"]/@content', "variable": "desc"},
    ])
    action.apply({"desc": "My new description"}, work_dir, values_dir)

    content = f.read_text()
    assert 'content="My new description"' in content
    assert "A sample audioguide app" not in content


def test_set_html_lang_attribute(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": "//html/@lang", "variable": "lang"},
    ])
    action.apply({"lang": "de"}, work_dir, values_dir)

    content = f.read_text()
    assert 'lang="de"' in content


def test_multiple_replacements(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": "//title", "variable": "my_title"},
        {"selector": '//meta[@name="Description"]/@content', "variable": "desc"},
    ])
    action.apply({"my_title": "New Title", "desc": "New desc"}, work_dir, values_dir)

    content = f.read_text()
    assert "<title>New Title</title>" in content
    assert 'content="New desc"' in content


def test_error_no_match(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": "//nonexistent", "variable": "val"},
    ])
    with pytest.raises(ValueError, match="matched no elements"):
        action.apply({"val": "x"}, work_dir, values_dir)


def test_error_multiple_matches(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": "//p", "variable": "val"},
    ])
    with pytest.raises(ValueError, match="matched 3 elements.*expected exactly 1"):
        action.apply({"val": "x"}, work_dir, values_dir)


def test_doctype_preserved(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": "//title", "variable": "my_title"},
    ])
    action.apply({"my_title": "Test"}, work_dir, values_dir)

    content = f.read_text()
    assert content.startswith("<!DOCTYPE html>")


def test_void_elements_not_self_closed(work_dir, values_dir):
    f = work_dir / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(file="index.html", replace=[
        {"selector": "//title", "variable": "my_title"},
    ])
    action.apply({"my_title": "Test"}, work_dir, values_dir)

    content = f.read_text()
    # meta tags should NOT be self-closed in HTML output
    assert "<meta " in content
    assert "/>" not in content or "<meta" not in content.split("/>")[0]
