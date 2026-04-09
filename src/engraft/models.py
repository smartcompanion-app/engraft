from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Variable:
    """A template variable definition."""

    name: str
    description: str
    default: str | None = None


@dataclass
class Template:
    """Parsed template with variable definitions and raw customization entries."""

    variables: list[Variable]
    customizations: list[dict]


def parse_template(path: Path) -> Template:
    """Load a template YAML file into a Template model.

    Variables are parsed from array format. Customization entries are
    stored as raw dicts for later expansion by the engine.
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    variables: list[Variable] = []
    seen_names: set[str] = set()
    for var_data in data.get("variables") or []:
        name = var_data["variable"]
        if name in seen_names:
            raise ValueError(f"Duplicate variable name: {name!r}")
        seen_names.add(name)
        variables.append(
            Variable(
                name=name,
                description=var_data.get("description", ""),
                default=var_data.get("default"),
            )
        )

    customizations: list[dict] = []
    for item in data.get("customizations") or []:
        customizations.append(dict(item))

    return Template(variables=variables, customizations=customizations)


def parse_values(path: Path) -> dict[str, str]:
    """Load a values YAML file into a flat dict."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data or {}
