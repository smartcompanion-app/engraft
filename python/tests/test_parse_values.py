from engraft.models import parse_values


def test_string_values_pass_through(tmp_path):
    p = tmp_path / "values.yaml"
    p.write_text("name: acme\nversion: 1.2.3\n")
    assert parse_values(p) == {"name": "acme", "version": "1.2.3"}


def test_numeric_values_are_coerced_to_strings(tmp_path):
    p = tmp_path / "values.yaml"
    p.write_text("port: 8443\nretries: 3\nratio: 0.75\n")
    result = parse_values(p)
    assert result == {"port": "8443", "retries": "3", "ratio": "0.75"}
    for v in result.values():
        assert isinstance(v, str)


def test_boolean_values_are_coerced_to_strings(tmp_path):
    p = tmp_path / "values.yaml"
    p.write_text("flag: true\nother: false\n")
    assert parse_values(p) == {"flag": "True", "other": "False"}


def test_null_values_are_dropped(tmp_path):
    p = tmp_path / "values.yaml"
    p.write_text("set_key: hello\nomitted_key:\n")
    assert parse_values(p) == {"set_key": "hello"}


def test_empty_file_returns_empty_dict(tmp_path):
    p = tmp_path / "values.yaml"
    p.write_text("")
    assert parse_values(p) == {}
