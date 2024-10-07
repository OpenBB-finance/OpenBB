"""App loader module."""

from typing import List, Optional

from fastapi import APIRouter, FastAPI
from openbb_core.api.exception_handlers import ExceptionHandlers
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.router import RouterLoader
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError


class AppLoader:
    """App loader."""

    @staticmethod
    def add_routers(app: FastAPI, routers: List[Optional[APIRouter]], prefix: str):
        """Add routers."""
        for router in routers:
            if router:
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
        app.exception_handlers[OpenBBError] = ExceptionHandlers.openbb
        app.exception_handlers[EmptyDataError] = ExceptionHandlers.empty_data
