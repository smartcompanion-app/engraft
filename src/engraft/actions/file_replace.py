import shutil
from dataclasses import dataclass
from pathlib import Path

from engraft.actions import register
from engraft.actions.base import Action


@register("file_replace")
@dataclass
class FileReplace(Action):
    """Replace a file in the working directory with a source file."""

    target: Path
    source_path: Path

    def apply(self) -> None:
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {self.source_path}")

        if not self.target.exists():
            raise FileNotFoundError(f"Target file does not exist: {self.target}")

        shutil.copy2(self.source_path, self.target)
