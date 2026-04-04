from pathlib import Path

from engraft.models import parse_template, parse_values


def apply(
    template_path: str | Path,
    values_path: str | Path,
    work_dir: Path | None = None,
) -> None:
    """Apply a template with the given values to the working directory."""
    template_path = Path(template_path).resolve()
    values_path = Path(values_path).resolve()

    if work_dir is None:
        work_dir = Path.cwd()
    else:
        work_dir = Path(work_dir).resolve()

    values_dir = values_path.parent

    template = parse_template(template_path)
    values = parse_values(values_path)

    # Resolve variables: values override defaults
    variables: dict[str, str] = {}
    for name, var in template.variables.items():
        variables[name] = values.get(name, var.default)

    # Execute customizations in order
    for action in template.customizations:
        action.apply(variables, work_dir, values_dir)
