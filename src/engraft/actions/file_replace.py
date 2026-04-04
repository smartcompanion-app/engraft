import shutil
from dataclasses import dataclass
from pathlib import Path

from engraft.actions import register
from engraft.actions.base import Action


@register("file_replace")
@dataclass
class FileReplace(Action):
    """Replace a file in the working directory with a source file."""

    file: str
    variable: str

    def apply(
        self,
        variables: dict[str, str],
        work_dir: Path,
        values_dir: Path,
    ) -> None:
        source_path = values_dir / variables[self.variable]
        target_path = work_dir / self.file

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {source_path}"
            )

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
