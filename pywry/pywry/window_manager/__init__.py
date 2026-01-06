"""Window manager package."""

from .controller import WindowController
from .lifecycle import WindowLifecycle, WindowResources, get_lifecycle
from .modes import (
    MultiWindowMode,
    NewWindowMode,
    SingleWindowMode,
    WindowModeBase,
)


__all__ = [
    "MultiWindowMode",
    "NewWindowMode",
    "SingleWindowMode",
    "WindowController",
    "WindowLifecycle",
    "WindowModeBase",
    "WindowResources",
    "get_lifecycle",
]
