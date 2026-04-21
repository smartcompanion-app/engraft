import pytest

from engraft.actions.file_replace import FileReplace


def test_basic_replacement(tmp_path):
    target = tmp_path / "logo.png"
    target.write_text("old logo")

    source = tmp_path / "values" / "my_logo.png"
    source.parent.mkdir()
    source.write_text("new logo")

    action = FileReplace(target=target, source_path=source)
    action.apply()

    assert target.read_text() == "new logo"


def test_binary_file(tmp_path):
    target = tmp_path / "icon.png"
    target.write_bytes(b"\x89PNG old")

    source = tmp_path / "values" / "new_icon.png"
    source.parent.mkdir()
    source.write_bytes(b"\x89PNG new")

    action = FileReplace(target=target, source_path=source)
    action.apply()

    assert target.read_bytes() == b"\x89PNG new"


def test_error_source_missing(tmp_path):
    target = tmp_path / "logo.png"
    target.write_text("existing")

    action = FileReplace(target=target, source_path=tmp_path / "nonexistent.png")
    with pytest.raises(FileNotFoundError):
        action.apply()


def test_error_target_missing(tmp_path):
    source = tmp_path / "img.png"
    source.write_text("image data")

    action = FileReplace(target=tmp_path / "missing.png", source_path=source)
    with pytest.raises(FileNotFoundError):
        action.apply()
