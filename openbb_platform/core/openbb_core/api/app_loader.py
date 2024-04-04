"""App loader module."""

from typing import List, Optional

from fastapi import APIRouter, FastAPI
from openbb_core.app.router import RouterLoader


class AppLoader:
    """App loader."""

    @staticmethod
    def get_openapi_tags() -> List[dict]:
        """Get openapi tags."""
        main_router = RouterLoader.from_extensions()
        openapi_tags = []
        # Add tag data for each router in the main router
        for r in main_router.routers:
            openapi_tags.append(
                {
                    "name": r,
                    "description": main_router.get_attr(r, "description"),
                }
            )
        return openapi_tags

    @staticmethod
    def from_routers(
        app: FastAPI, routers: List[Optional[APIRouter]], prefix: str
    ) -> FastAPI:
        """Load routers to app."""
        for router in routers:
            if router:
                app.include_router(router=router, prefix=prefix)

        return app
