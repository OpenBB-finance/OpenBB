"""App loader module."""

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import ResponseValidationError
from pydantic import ValidationError
from starlette.routing import Mount

from openbb_core.api.exception_handlers import ExceptionHandlers
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.router import RouterLoader
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError


class AppLoader:
    """App loader."""

    @staticmethod
    def add_routers(app: FastAPI, routers: list[APIRouter | None], prefix: str):
        """Add routers."""

        def _join_paths(p1: str, p2: str) -> str:
            if not p1:
                return p2 or "/"
            if not p2:
                return p1 or "/"
            joined = p1.rstrip("/") + "/" + p2.lstrip("/")
            return joined.rstrip("/") or "/"

        for router in routers:
            if router:
                # FastAPI's include_router doesn't propagate Starlette Mount routes.
                # If an APIRouter contains mounted sub-apps (e.g. WSGIMiddleware for Flask),
                # mount them directly on the FastAPI app with the same prefix.
                for route in getattr(router, "routes", []):
                    if not isinstance(route, Mount):
                        continue
                    mount_path = _join_paths(prefix, route.path)
                    if any(
                        isinstance(existing, Mount) and existing.path == mount_path
                        for existing in app.router.routes
                    ):
                        continue
                    app.mount(mount_path, route.app, name=route.name)
                app.include_router(router=router, prefix=prefix)

    @staticmethod
    def add_openapi_tags(app: FastAPI):
        """Add openapi tags."""
        main_router = RouterLoader.from_extensions()
        # Add tag data for each router in the main router
        app.openapi_tags = [
            {
                "name": r,
                "description": main_router.get_attr(r, "description"),
            }
            for r in main_router.routers
        ]

    @staticmethod
    def add_exception_handlers(app: FastAPI):
        """Add exception handlers."""
        app.exception_handlers[Exception] = ExceptionHandlers.exception
        app.exception_handlers[ValidationError] = ExceptionHandlers.validation
        app.exception_handlers[ResponseValidationError] = ExceptionHandlers.validation
        app.exception_handlers[OpenBBError] = ExceptionHandlers.openbb
        app.exception_handlers[EmptyDataError] = ExceptionHandlers.empty_data
        app.exception_handlers[UnauthorizedError] = ExceptionHandlers.unauthorized
