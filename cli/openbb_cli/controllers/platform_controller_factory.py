"""Platform controller factory.

Builds a per-router ``PlatformController`` class with ``CHOICES_MENUS`` /
``CHOICES_COMMANDS`` populated from a ``Backend`` (either ``LocalBackend``
walking in-process ``obb`` or ``SpecBackend`` reading a precomputed spec).

The factory exposes the per-router pre-built ``translators`` + ``paths``
dicts on the class so the controller's ``__init__`` can pick them up
without re-walking the source.
"""

from __future__ import annotations

from typing import Any

from openbb_cli.backend import Backend, LocalBackend
from openbb_cli.controllers.base_platform_controller import PlatformController


class PlatformControllerFactory:
    """Factory to create a platform controller from a ``Backend``.

    Two construction styles are supported:

    * ``PlatformControllerFactory(backend=..., router_name=...)`` — the new,
      pluggable form. The backend supplies translators + sub-paths.
    * ``PlatformControllerFactory(platform_router=..., reference=...)`` —
      legacy form, kept for callers that still pass an in-process ``obb``
      target. Internally wraps a ``LocalBackend``.
    """

    def __init__(
        self,
        platform_router: type | None = None,
        *,
        backend: Backend | None = None,
        router_name: str | None = None,
        reference: dict[str, Any] | None = None,
    ) -> None:
        if backend is None and platform_router is None:
            raise ValueError("Either ``backend`` or ``platform_router`` is required.")

        if backend is not None:
            if router_name is None:
                raise ValueError("``router_name`` is required when ``backend`` is set.")
            self._backend: Backend = backend
            self._router_name: str = router_name
        else:
            del reference
            assert platform_router is not None  # noqa: S101 — narrowed by L40-41
            self._backend = LocalBackend()
            self._router_name = _derive_router_name(platform_router)

        self._translators, self._paths = self._backend.get_translators_for_path(
            self._router_name
        )

    @property
    def router_name(self) -> str:
        return self._router_name

    @property
    def controller_name(self) -> str:
        return f"{self._router_name.capitalize()}Controller"

    def create(self) -> type:
        """Create the platform controller class for this router."""
        choices_menus: list[str] = []
        choices_commands: list[str] = []
        for key, value in self._paths.items():
            if value == "path":
                continue
            choices_menus.append(key)
        for name in self._translators:
            if any(
                f"{self._router_name}_{path}_" in f"{name}_" for path in self._paths
            ):
                continue
            choices_commands.append(name.replace(f"{self._router_name}_", ""))

        attributes: dict[str, Any] = {
            "CHOICES_GENERATION": True,
            "CHOICES_MENUS": choices_menus,
            "CHOICES_COMMANDS": choices_commands,
            "_factory_backend": self._backend,
            "_factory_translators": self._translators,
            "_factory_paths": self._paths,
        }
        return type(self.controller_name, (PlatformController,), attributes)


def _derive_router_name(platform_router: type) -> str:
    """Replicate the legacy class-name → router-name derivation."""
    return (
        str(type(platform_router))
        .rsplit(".", maxsplit=1)[-1]
        .replace("'>", "")
        .replace("ROUTER_", "")
        .lower()
    )
