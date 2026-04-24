from dataclasses import dataclass
from pathlib import Path

import yaml

from engraft.actions import Action, create_action


@dataclass
class Variable:
    name: str
    description: str
    default: str


@dataclass
class Template:
    variables: dict[str, Variable]
    customizations: list[Action]


def parse_template(path: Path) -> Template:
    """Load a template YAML file into a Template model."""
    with open(path) as f:
        data = yaml.safe_load(f)

    variables: dict[str, Variable] = {}
    for name, var_data in (data.get("variables") or {}).items():
        variables[name] = Variable(
            name=name,
            description=var_data.get("description", ""),
            default=var_data.get("default", ""),
        )

    customizations: list[Action] = []
    for item in data.get("customizations") or []:
        action_name = item.pop("action")
        customizations.append(create_action(action_name, **item))

    return Template(variables=variables, customizations=customizations)


def parse_values(path: Path) -> dict[str, str]:
    """Load a values YAML file into a flat dict."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data or {}
