"""Resolve the active OBBject charting engine for every Platform interface."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openbb_core.app.charting.abstract import ChartingExtension
    from openbb_core.app.model.extension import Extension

DEFAULT_CHARTING_ACCESSOR = "charting"


class ChartingManager:
    """Resolve and query the active charting engine.

    The engine is the OBBject extension whose accessor name matches
    ``system_settings.charting_extension`` when set, otherwise the extension
    registered under the default ``charting`` accessor. This indirection lets a
    developer ship a drop-in replacement for ``openbb-charting`` without any
    interface (Python, API, CLI, MCP) hard-coding the package name.
    """

    @staticmethod
    def _configured_name() -> str | None:
        """Return the configured charting extension override, if any."""
        from openbb_core.app.service.system_service import SystemService

        return SystemService().system_settings.charting_extension

    @classmethod
    def get_extension(cls) -> Extension | None:
        """Return the resolved charting ``Extension``, honoring the override.

        Returns
        -------
        Extension | None
            The resolved extension, or ``None`` when no charting engine is
            installed (or the configured override cannot be found).
        """
        from openbb_core.app.extension_loader import ExtensionLoader

        objects = ExtensionLoader().obbject_objects
        configured = cls._configured_name()

        if configured:
            if configured in objects:
                return objects[configured]
            return next(
                (
                    ext
                    for ext in objects.values()
                    if getattr(ext, "name", None) == configured
                ),
                None,
            )

        return next(
            (
                ext
                for ext in objects.values()
                if getattr(ext, "name", None) == DEFAULT_CHARTING_ACCESSOR
            ),
            None,
        )

    @classmethod
    def accessor_name(cls) -> str:
        """Return the OBBject accessor name the engine is registered under."""
        ext = cls.get_extension()
        return (
            getattr(ext, "name", None)
            or cls._configured_name()
            or DEFAULT_CHARTING_ACCESSOR
        )

    @classmethod
    def get_charting_class(cls) -> type[ChartingExtension] | None:
        """Return the engine accessor class (e.g. ``Charting``), if installed.

        Class-level attribute access returns the registered accessor class
        rather than instantiating it, so this is cheap and side-effect free.
        """
        ext = cls.get_extension()
        if ext is None:
            return None

        from openbb_core.app.model.obbject import OBBject

        return getattr(OBBject, ext.name, None)

    @classmethod
    def is_installed(cls) -> bool:
        """Return whether a charting engine is available."""
        return cls.get_extension() is not None

    @classmethod
    def functions(cls) -> list[str]:
        """Return the route names the resolved engine can chart."""
        charting = cls.get_charting_class()
        if charting is None or not hasattr(charting, "functions"):
            return []
        try:
            return list(charting.functions())
        except Exception:  # noqa: BLE001
            return []

    @classmethod
    def has_chart(cls, route: str) -> bool:
        """Return whether a command route has a registered chart view.

        Parameters
        ----------
        route : str
            The command route, e.g. ``/equity/price/historical``.
        """
        return route.replace("/", "_")[1:] in cls.functions()
