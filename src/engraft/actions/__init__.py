from engraft.actions.base import Action

_REGISTRY: dict[str, type[Action]] = {}


def register(name: str):
    """Decorator to register an action class under a name."""
    def decorator(cls: type[Action]) -> type[Action]:
        _REGISTRY[name] = cls
        return cls
    return decorator


def create_action(action_name: str, **config) -> Action:
    """Instantiate an action by name with the given config."""
    if action_name not in _REGISTRY:
        available = list(_REGISTRY.keys())
        raise ValueError(
            f"Unknown action: {action_name!r}. Available: {available}"
        )
    return _REGISTRY[action_name](**config)


# Import action modules to trigger registration
from engraft.actions import (  # noqa: E402
    file_replace,  # noqa: F401
    html_replace,  # noqa: F401
    json_replace,  # noqa: F401
    regex_replace,  # noqa: F401
)

__all__ = ["Action", "create_action", "register"]
