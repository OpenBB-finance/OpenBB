"""App-level registry of mounted Flask apps and their OpenAPI fragments."""

from __future__ import annotations

from typing import Any, ClassVar


class FlaskMountRegistry:
    """Process-wide registry mapping a mount name to its OpenAPI fragment."""

    _mounts: ClassVar[dict[str, dict[str, Any]]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        paths: dict[str, Any],
        components: dict[str, Any],
    ) -> None:
        """Register or replace the OpenAPI fragment for a mount."""
        cls._mounts[name] = {
            "paths": paths or {},
            "components": components or {},
            "mount_prefix": f"/{name.strip('/')}",
        }

    @classmethod
    def get(cls, name: str) -> dict[str, Any] | None:
        """Return the stored fragment for ``name`` or ``None``."""
        return cls._mounts.get(name)

    @classmethod
    def names(cls) -> list[str]:
        """Return the registered mount names."""
        return list(cls._mounts)

    @classmethod
    def reset(cls) -> None:
        """Remove all registered mounts."""
        cls._mounts.clear()

    @classmethod
    def aggregate(cls, global_prefix: str = "") -> dict[str, Any]:
        """Merge every mount into one ``{"paths", "components"}`` fragment."""
        prefix = global_prefix.rstrip("/")
        out_paths: dict[str, Any] = {}
        out_schemas: dict[str, Any] = {}
        out_security: dict[str, Any] = {}

        for name, mount in cls._mounts.items():
            base = f"{prefix}{mount['mount_prefix']}".rstrip("/")
            for path, item in mount["paths"].items():
                out_paths[f"{base}{path}"] = item
            components = mount["components"]
            for sname, schema in components.get("schemas", {}).items():
                key = sname if sname not in out_schemas else f"{name}__{sname}"
                out_schemas[key] = schema
            for sname, scheme in components.get("securitySchemes", {}).items():
                out_security[sname] = scheme

        components_out: dict[str, Any] = {}
        if out_schemas:
            components_out["schemas"] = out_schemas
        if out_security:
            components_out["securitySchemes"] = out_security
        return {"paths": out_paths, "components": components_out}
