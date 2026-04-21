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


def test_set_element_text(tmp_path):
    f = tmp_path / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(target=f, selector="//title", value="New Title")
    action.apply()

    content = f.read_text()
    assert "<title>New Title</title>" in content
    assert "Animals Audioguide" not in content


def test_set_attribute(tmp_path):
    f = tmp_path / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(
        target=f,
        selector='//meta[@name="Description"]/@content',
        value="My new description",
    )
    action.apply()

    content = f.read_text()
    assert 'content="My new description"' in content
    assert "A sample audioguide app" not in content


def test_set_html_lang_attribute(tmp_path):
    f = tmp_path / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(target=f, selector="//html/@lang", value="de")
    action.apply()

    content = f.read_text()
    assert 'lang="de"' in content


def test_error_no_match(tmp_path):
    f = tmp_path / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(target=f, selector="//nonexistent", value="x")
    with pytest.raises(ValueError, match="matched no elements"):
        action.apply()


def test_error_multiple_matches(tmp_path):
    f = tmp_path / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(target=f, selector="//p", value="x")
    with pytest.raises(ValueError, match="matched 3 elements.*expected exactly 1"):
        action.apply()


def test_doctype_preserved(tmp_path):
    f = tmp_path / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(target=f, selector="//title", value="Test")
    action.apply()

    content = f.read_text()
    assert content.startswith("<!DOCTYPE html>")


def test_void_elements_not_self_closed(tmp_path):
    f = tmp_path / "index.html"
    f.write_text(SAMPLE_HTML)

    action = HtmlReplace(target=f, selector="//title", value="Test")
    action.apply()

    content = f.read_text()
    assert "<meta " in content
    assert "/>" not in content or "<meta" not in content.split("/>")[0]
