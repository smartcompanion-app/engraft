import pytest

from engraft.actions.file_replace import FileReplace


@pytest.fixture
def work_dir(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    return project


@pytest.fixture
def values_dir(tmp_path):
    vd = tmp_path / "values"
    vd.mkdir()
    return vd


def test_basic_replacement(work_dir, values_dir):
    target = work_dir / "logo.png"
    target.write_text("old logo")

    source = values_dir / "my_logo.png"
    source.write_text("new logo")

    action = FileReplace(file="logo.png", variable="logo_path")
    action.apply({"logo_path": "my_logo.png"}, work_dir, values_dir)

    assert target.read_text() == "new logo"


def test_binary_file(work_dir, values_dir):
    target = work_dir / "icon.png"
    target.write_bytes(b"\x89PNG old")

    source = values_dir / "new_icon.png"
    source.write_bytes(b"\x89PNG new")

    action = FileReplace(file="icon.png", variable="icon_path")
    action.apply({"icon_path": "new_icon.png"}, work_dir, values_dir)

    assert target.read_bytes() == b"\x89PNG new"


def test_error_source_missing(work_dir, values_dir):
    action = FileReplace(file="logo.png", variable="logo_path")
    with pytest.raises(FileNotFoundError):
        action.apply({"logo_path": "nonexistent.png"}, work_dir, values_dir)


def test_error_target_missing(work_dir, values_dir):
    source = values_dir / "img.png"
    source.write_text("image data")

    action = FileReplace(file="assets/images/logo.png", variable="img_path")
    with pytest.raises(FileNotFoundError):
        action.apply({"img_path": "img.png"}, work_dir, values_dir)
