from dataclasses import dataclass
from pathlib import Path

from engraft.actions import Action, create_action
from engraft.yaml_loader import safe_load


@dataclass
class Variable:
    name: str
    description: str
    default: str | None


@dataclass
class Template:
    variables: dict[str, Variable]
    customizations: list[Action]


def parse_template(path: Path) -> Template:
    """Load a template YAML file into a Template model."""
    with open(path) as f:
        data = safe_load(f)

    variables: dict[str, Variable] = {}
    for name, var_data in (data.get("variables") or {}).items():
        raw_default = var_data.get("default")
        variables[name] = Variable(
            name=name,
            description=var_data.get("description", ""),
            default=None if raw_default is None else str(raw_default),
        )

    customizations: list[Action] = []
    for item in data.get("customizations") or []:
        action_name = item.pop("action")
        customizations.append(create_action(action_name, **item))

    return Template(variables=variables, customizations=customizations)


def parse_values(path: Path) -> dict[str, str]:
    """Load a values YAML file into a flat dict of strings.

    Non-string scalars (ints, booleans) are coerced to strings so that
    downstream actions can treat every resolved variable as text. Keys
    whose value is null are skipped entirely — this mirrors "omit the
    key", which lets an optional variable fall back to its default or
    resolve to the noop sentinel.
    """
    with open(path) as f:
        data = safe_load(f)
    if data is None:
        return {}
    return {k: str(v) for k, v in data.items() if v is not None}
