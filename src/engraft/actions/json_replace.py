import json
import re
from dataclasses import dataclass
from pathlib import Path

from engraft.actions import register
from engraft.actions.base import Action


def _parse_path(dot_path: str) -> list[str | int]:
    """Parse a dot-path like 'a.b[2].c' into ['a', 'b', 2, 'c']."""
    parts: list[str | int] = []
    for segment in re.split(r"\.", dot_path):
        # Handle array indices: "items[0]" -> "items", 0
        bracket_match = re.match(r"^([^\[]*)\[(\d+)\]$", segment)
        if bracket_match:
            key, index = bracket_match.groups()
            if key:
                parts.append(key)
            parts.append(int(index))
        else:
            parts.append(segment)
    return parts


def _set_at_path(obj: dict | list, path: list[str | int], value: str) -> None:
    """Set a value at a nested path, creating intermediate dicts if needed."""
    for i, key in enumerate(path[:-1]):
        next_key = path[i + 1]
        if isinstance(key, int):
            if isinstance(obj, list) and key < len(obj):
                obj = obj[key]
            else:
                raise IndexError(f"Array index {key} out of range")
        else:
            if key not in obj:
                obj[key] = [] if isinstance(next_key, int) else {}
            obj = obj[key]

    last = path[-1]
    if isinstance(last, int):
        obj[last] = value
    else:
        obj[last] = value


@register("json_replace")
@dataclass
class JsonReplace(Action):
    """Replace a value in a JSON file using a JSONPath-like selector."""

    target: Path
    selector: str
    value: str

    def apply(self) -> None:
        data = json.loads(self.target.read_text())

        selector = self.selector
        if selector.startswith("$."):
            selector = selector[2:]

        parsed = _parse_path(selector)
        _set_at_path(data, parsed, self.value)

        self.target.write_text(json.dumps(data, indent=2) + "\n")
