"""Semantic comparators for e2e output comparison.

The harness compares the post-apply working tree against an ``expected/``
tree using a format-aware comparator selected by file extension. See the
e2e-harness spec for the full contract.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml
from lxml import html as lxml_html
from lxml.etree import _Element


def _read_text(p: Path) -> str:
    return p.read_text().replace("\r\n", "\n")


def compare_text(expected: Path, actual: Path) -> None:
    assert _read_text(expected) == _read_text(actual), (
        f"text content differs: {expected} vs {actual}"
    )


def compare_json(expected: Path, actual: Path) -> None:
    exp = json.loads(expected.read_text())
    act = json.loads(actual.read_text())
    assert exp == act, f"JSON content differs: {expected} vs {actual}"


def compare_yaml(expected: Path, actual: Path) -> None:
    exp = yaml.safe_load(expected.read_text())
    act = yaml.safe_load(actual.read_text())
    assert exp == act, f"YAML content differs: {expected} vs {actual}"


def _normalize_whitespace(text: str | None) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _element_signature(el: _Element) -> dict[str, Any]:
    return {
        "tag": el.tag,
        "attrib": dict(el.attrib),
        "text": _normalize_whitespace(el.text),
        "tail": _normalize_whitespace(el.tail),
        "children": [_element_signature(c) for c in el],
    }


def compare_html(expected: Path, actual: Path) -> None:
    exp_tree = lxml_html.fromstring(expected.read_text())
    act_tree = lxml_html.fromstring(actual.read_text())
    exp_sig = _element_signature(exp_tree)
    act_sig = _element_signature(act_tree)
    assert exp_sig == act_sig, (
        f"HTML structure differs: {expected} vs {actual}\n"
        f"expected={exp_sig!r}\nactual  ={act_sig!r}"
    )


_COMPARATORS = {
    ".json": compare_json,
    ".yaml": compare_yaml,
    ".yml": compare_yaml,
    ".html": compare_html,
    ".htm": compare_html,
}


def compare_tree(expected_dir: Path, actual_dir: Path) -> None:
    """Compare every file under expected_dir against actual_dir."""
    expected_files = sorted(
        p for p in expected_dir.rglob("*") if p.is_file()
    )
    for exp in expected_files:
        rel = exp.relative_to(expected_dir)
        act = actual_dir / rel
        assert act.exists(), f"Missing expected file: {rel} under {actual_dir}"
        comparator = _COMPARATORS.get(exp.suffix.lower(), compare_text)
        comparator(exp, act)
