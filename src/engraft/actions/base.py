from abc import ABC, abstractmethod


class Action(ABC):
    """Base class for all customization actions.

    Actions are fully resolved at construction time — they hold their
    target path, resolved value, and any other dependencies. The apply()
    method takes no arguments.
    """

    @abstractmethod
    def apply(self) -> None:
        """Apply this action."""
        ...
