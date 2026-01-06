"""Base window manager interface.

This module is deprecated. Use window_manager.modes.base instead.
"""

from .modes.base import WindowModeBase


WindowManagerBase = WindowModeBase

__all__ = ["WindowManagerBase", "WindowModeBase"]
