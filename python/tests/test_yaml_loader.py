import io

import pytest

from engraft.yaml_loader import safe_load


@pytest.mark.parametrize(
    "literal",
    ["yes", "no", "on", "off", "Yes", "No", "On", "Off", "YES", "NO", "ON", "OFF"],
)
def test_yaml_12_bool_literals_parse_as_strings(literal):
    data = safe_load(io.StringIO(f"flag: {literal}\n"))
    assert data == {"flag": literal}


@pytest.mark.parametrize(
    "literal,expected",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
    ],
)
def test_true_false_still_parse_as_booleans(literal, expected):
    data = safe_load(io.StringIO(f"flag: {literal}\n"))
    assert data == {"flag": expected}


def test_nested_and_list_values():
    doc = """
variables:
  enabled: yes
  debug: true
flags:
  - yes
  - no
  - true
"""
    data = safe_load(io.StringIO(doc))
    assert data["variables"]["enabled"] == "yes"
    assert data["variables"]["debug"] is True
    assert data["flags"] == ["yes", "no", True]


def test_quoted_booleans_remain_strings():
    data = safe_load(io.StringIO('flag: "yes"\n'))
    assert data == {"flag": "yes"}
    data = safe_load(io.StringIO('flag: "true"\n'))
    assert data == {"flag": "true"}
