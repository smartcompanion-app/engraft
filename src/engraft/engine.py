import shutil
from pathlib import Path

from engraft.actions import Action, get_action_class
from engraft.actions.file_replace import FileReplace
from engraft.models import Template, parse_template, parse_values

STAGING_DIR_NAME = ".engraft"


def resolve_variables(template: Template, values: dict[str, str]) -> dict[str, str]:
    """Merge template defaults with provided values.

    Returns a dict containing only variables that have a resolved value
    (either from values or from a default). Variables with no default
    and no provided value are omitted.
    """
    resolved: dict[str, str] = {}
    for var in template.variables:
        if var.name in values:
            resolved[var.name] = values[var.name]
        elif var.default is not None:
            resolved[var.name] = var.default
    return resolved


def _collect_target_files(customizations: list[dict]) -> set[str]:
    """Extract deduplicated target file paths from raw customization entries."""
    targets: set[str] = set()
    for entry in customizations:
        file_path = entry.get("file")
        if file_path:
            targets.add(file_path)
    return targets


def _build_actions(
    customizations: list[dict],
    variables: dict[str, str],
    staging_dir: Path,
    values_dir: Path,
) -> list[Action]:
    """Expand raw customization entries into fully resolved Action objects.

    Multi-entry replace lists are expanded into individual actions.
    Entries referencing unset variables are skipped.
    """
    actions: list[Action] = []

    for entry in customizations:
        action_name = entry["action"]
        file_path = entry["file"]
        target = staging_dir / file_path

        # Validate action name
        action_cls = get_action_class(action_name)

        if action_cls is FileReplace:
            var_name = entry["variable"]
            if var_name not in variables:
                continue
            source_path = values_dir / variables[var_name]
            actions.append(FileReplace(target=target, source_path=source_path))
        else:
            # Actions with replace lists (json_replace, regex_replace, html_replace)
            for replace_entry in entry.get("replace", []):
                var_name = replace_entry["variable"]
                if var_name not in variables:
                    continue
                actions.append(
                    action_cls(
                        target=target,
                        selector=replace_entry["selector"],
                        value=variables[var_name],
                    )
                )

    return actions


def apply(
    template_path: str | Path,
    values_path: str | Path,
    work_dir: Path | None = None,
) -> None:
    """Apply a template with the given values to the working directory.

    Uses a staging directory (.engraft/) to ensure atomicity: all actions
    are executed against the staging copy first, and results are only
    copied back to the project if all actions succeed.
    """
    template_path = Path(template_path).resolve()
    values_path = Path(values_path).resolve()

    if work_dir is None:
        work_dir = Path.cwd()
    else:
        work_dir = Path(work_dir).resolve()

    values_dir = values_path.parent

    template = parse_template(template_path)
    values = parse_values(values_path)

    # Step 1: Resolve variables (only set ones)
    variables = resolve_variables(template, values)

    # Step 2: Collect target files from raw customization entries
    target_files = _collect_target_files(template.customizations)

    # Step 3: Create staging directory
    staging_dir = work_dir / STAGING_DIR_NAME
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()

    try:
        # Step 4: Copy target files into staging directory
        for rel_path in target_files:
            src = work_dir / rel_path
            dst = staging_dir / rel_path
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Step 5: Build fully resolved actions (skipping unset variables)
        actions = _build_actions(
            template.customizations, variables, staging_dir, values_dir
        )

        # Step 6: Execute all actions
        for action in actions:
            action.apply()

        # Step 7: Copy back all files from staging to work directory
        for staged_file in staging_dir.rglob("*"):
            if staged_file.is_file():
                rel_path = staged_file.relative_to(staging_dir)
                dest = work_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staged_file, dest)
    finally:
        # Always remove staging directory
        shutil.rmtree(staging_dir, ignore_errors=True)
