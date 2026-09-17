"""App loader module."""

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import ResponseValidationError
from pydantic import ValidationError

from openbb_core.api.exception_handlers import ExceptionHandlers
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.route_iter import iter_included_routers
from openbb_core.app.router import RouterLoader
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError


class AppLoader:
    """App loader."""

    @staticmethod
    def add_routers(app: FastAPI, routers: list[APIRouter | None], prefix: str):
        """Add routers."""
        for router in routers:
            if router:
                app.include_router(router=router, prefix=prefix)
        AppLoader.deduplicate_router_event_handlers(app)

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
        app.add_exception_handler(Exception, ExceptionHandlers.exception)
        app.add_exception_handler(ValidationError, ExceptionHandlers.validation)  # ty: ignore[invalid-argument-type]
        app.add_exception_handler(ResponseValidationError, ExceptionHandlers.validation)  # ty: ignore[invalid-argument-type]
        app.add_exception_handler(OpenBBError, ExceptionHandlers.openbb)  # ty: ignore[invalid-argument-type]
        app.add_exception_handler(EmptyDataError, ExceptionHandlers.empty_data)  # ty: ignore[invalid-argument-type]
        app.add_exception_handler(UnauthorizedError, ExceptionHandlers.unauthorized)  # ty: ignore[invalid-argument-type]

    @staticmethod
    def deduplicate_router_event_handlers(app: FastAPI) -> None:
        """Clear startup/shutdown handlers on included routers after assembly."""
        for included in iter_included_routers(app.router):
            on_startup = getattr(included, "on_startup", None)
            on_shutdown = getattr(included, "on_shutdown", None)
            if isinstance(on_startup, list):
                on_startup.clear()
            if isinstance(on_shutdown, list):
                on_shutdown.clear()
