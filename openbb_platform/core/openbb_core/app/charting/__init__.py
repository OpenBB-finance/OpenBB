"""Engine-agnostic charting contracts and managers for the OpenBB Platform.

This package decouples the Platform interfaces (Python, API, CLI, MCP) from any
single charting implementation. Interfaces resolve the active charting engine
through :class:`ChartingManager` instead of importing ``openbb_charting``
directly, which lets a developer ship a drop-in replacement engine, lifecycle
hooks, and a rendering backend purely through entry points.
"""

from openbb_core.app.charting.abstract import (
    AbstractChartingBackend,
    ChartingExtension,
)
from openbb_core.app.charting.backend import (
    CHARTING_BACKEND_GROUP,
    get_charting_backend_class,
)
from openbb_core.app.charting.hooks import (
    CHARTING_HOOKS_GROUP,
    ChartingHook,
    ChartingHooksManager,
    ChartLifecycle,
    HookContext,
    get_hooks_manager,
)
from openbb_core.app.charting.manager import (
    DEFAULT_CHARTING_ACCESSOR,
    ChartingManager,
)

__all__ = [
    "CHARTING_BACKEND_GROUP",
    "CHARTING_HOOKS_GROUP",
    "DEFAULT_CHARTING_ACCESSOR",
    "AbstractChartingBackend",
    "ChartLifecycle",
    "ChartingExtension",
    "ChartingHook",
    "ChartingHooksManager",
    "ChartingManager",
    "HookContext",
    "get_charting_backend_class",
    "get_hooks_manager",
]
