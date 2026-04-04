from abc import ABC, abstractmethod
from pathlib import Path


class Action(ABC):
    """Base class for all customization actions."""

    @abstractmethod
    def apply(
        self,
        variables: dict[str, str],
        work_dir: Path,
        values_dir: Path,
    ) -> None:
        """Apply this action.

        Args:
            variables: Resolved variable map (name -> value).
            work_dir: Root directory (for target file paths).
            values_dir: Directory containing the values file.
        """
        ...
