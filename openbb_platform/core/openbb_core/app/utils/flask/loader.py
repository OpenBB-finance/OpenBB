"""Mount Flask core extensions onto the FastAPI app with an OpenAPI overlay."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger("openbb_core.app.utils.flask")


def mount_flask_extensions(app: FastAPI, prefix: str = "") -> None:
    """Mount every Flask core extension onto ``app`` under ``prefix``."""
    from openbb_core.app.extension_loader import ExtensionLoader

    flask_apps = ExtensionLoader().flask_objects
    if not flask_apps:
        return

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.app.utils_optional import require_optional

    try:
        WSGIMiddleware = require_optional("a2wsgi").WSGIMiddleware  # noqa: N806
    except OpenBBError as exc:
        logger.warning("Flask extensions not mounted: %s", exc)
        return

    base = prefix.rstrip("/")
    for name, flask_app in flask_apps.items():
        app.mount(f"{base}/{name}", WSGIMiddleware(flask_app), name=name)
        _register_openapi(flask_app, name)


def merge_flask_openapi(schema: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Merge the registered Flask OpenAPI fragments into ``schema`` in place."""
    from .registry import FlaskMountRegistry

    merged = FlaskMountRegistry.aggregate(prefix)
    if merged["paths"]:
        schema.setdefault("paths", {}).update(merged["paths"])
        components = schema.setdefault("components", {})
        for section, entries in merged["components"].items():
            components.setdefault(section, {}).update(entries)
    return schema


def _register_openapi(flask_app: Any, name: str) -> None:
    """Introspect ``flask_app`` and register its OpenAPI fragment."""
    from .introspector import FlaskIntrospector
    from .openapi import OpenAPISpecGenerator
    from .registry import FlaskMountRegistry

    paths: dict[str, Any] = {}
    components: dict[str, Any] = {}
    try:
        introspector = FlaskIntrospector(flask_app, name)
        spec = introspector.try_self_spec()
        if spec is None:
            routes, models = introspector.introspect()
            spec = OpenAPISpecGenerator(routes, models).generate()
        paths = spec.get("paths", {})
        components = spec.get("components", {})
    except Exception as exc:
        logger.warning("Flask introspection failed for '%s': %s", name, exc)

    FlaskMountRegistry.register(name, paths, components)
