import shutil
from pathlib import Path

from engraft.models import parse_template, parse_values

STAGING_DIR_NAME = ".engraft"


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

    # Resolve variables: values override defaults
    variables: dict[str, str] = {}
    for name, var in template.variables.items():
        variables[name] = values.get(name, var.default)

    staging_dir = work_dir / STAGING_DIR_NAME

    # Step 1: Collect target files from all actions
    target_files: set[str] = set()
    for action in template.customizations:
        target_files.update(action.target_files())

    # Step 2: Create staging directory (remove if exists)
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()

    try:
        # Copy target files into staging directory
        for rel_path in target_files:
            src = work_dir / rel_path
            dst = staging_dir / rel_path
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Step 3: Execute all actions against the staging directory
        for action in template.customizations:
            action.apply(variables, staging_dir, values_dir)

        # Step 4: Copy back all files from staging to work directory
        for staged_file in staging_dir.rglob("*"):
            if staged_file.is_file():
                rel_path = staged_file.relative_to(staging_dir)
                dest = work_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staged_file, dest)
    finally:
        # Step 5: Always remove staging directory
        shutil.rmtree(staging_dir, ignore_errors=True)
