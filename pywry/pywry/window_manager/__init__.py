"""Window manager package."""

from .controller import WindowController
from .lifecycle import WindowLifecycle, WindowResources, get_lifecycle
from .modes import (
    BrowserMode,
    MultiWindowMode,
    NewWindowMode,
    SingleWindowMode,
    WindowModeBase,
)


__all__ = [
    "BrowserMode",
    "MultiWindowMode",
    "NewWindowMode",
    "SingleWindowMode",
    "WindowController",
    "WindowLifecycle",
    "WindowModeBase",
    "WindowResources",
    "get_lifecycle",
]
