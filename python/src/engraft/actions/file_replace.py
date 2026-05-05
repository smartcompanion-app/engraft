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
        variables: dict[str, str | None],
        work_dir: Path,
        values_dir: Path,
    ) -> None:
        value = variables[self.variable]
        if value is None:
            return

        source_path = values_dir / value
        target_path = work_dir / self.file

        if not source_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        if not target_path.exists():
            raise FileNotFoundError(f"Target file does not exist: {target_path}")

        shutil.copy2(source_path, target_path)

    def target_files(self) -> list[str]:
        """Return project-relative file paths this action operates on."""
        return [self.file]
