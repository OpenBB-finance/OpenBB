"""Resolve a charting rendering backend from entry points / configuration.

A backend is an opt-in override for the engine's built-in renderer (for example
the reference engine's PyWry-backed window). Register one under the
``openbb_charting_backend`` entry-point group::

    [project.entry-points."openbb_charting_backend"]
    my_backend = "my_pkg.backend:MyBackend"

The override is explicit: ``system_settings.charting_backend`` selects which
registered backend to use by entry-point name. Without a selection the engine
keeps its built-in backend.
"""

from __future__ import annotations

from importlib_metadata import entry_points

CHARTING_BACKEND_GROUP = "openbb_charting_backend"


def _configured_backend() -> str | None:
    """Return the configured backend override name, if any."""
    from openbb_core.app.service.system_service import SystemService

    return SystemService().system_settings.charting_backend


def get_charting_backend_class(name: str | None = None) -> type | None:
    """Return the selected charting backend class, or ``None`` to fall back.

    Parameters
    ----------
    name : str | None
        Explicit entry-point name to resolve. Defaults to
        ``system_settings.charting_backend``. When neither is set, no override is
        applied and the engine keeps its built-in backend.

    Returns
    -------
    type | None
        The backend class, or ``None`` when nothing is selected or the selected
        name is not registered.
    """
    target = name or _configured_backend()
    if not target:
        return None

    entry_point = next(
        (ep for ep in entry_points(group=CHARTING_BACKEND_GROUP) if ep.name == target),
        None,
    )
    return entry_point.load() if entry_point is not None else None
