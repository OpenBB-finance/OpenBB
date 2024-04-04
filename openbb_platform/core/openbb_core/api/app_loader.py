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
        added = set()
        # Add tag data for each router in the main router
        for r in main_router.routers:
            path = getattr(r, "path", "").split("/")[1]
            if path not in added:
                added.add(path)
                openapi_tags.append(
                    {
                        "name": path,
                        "description": main_router.get_attr(path, "description"),
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
