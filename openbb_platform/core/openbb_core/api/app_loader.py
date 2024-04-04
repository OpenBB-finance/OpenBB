from typing import List, Optional

from fastapi import APIRouter, FastAPI
from openbb_core.app.router import RouterLoader


class AppLoader:
    """App loader."""

    @staticmethod
    def get_openapi_tags(router: APIRouter) -> List[dict]:
        """Get openapi tags."""
        root = RouterLoader.from_extensions()

        openapi_tags = []
        added = set()
        for route in router.routes:
            path = getattr(route, "path", "")
            name = path.replace(getattr(route, "name", ""), "").strip("/")
            if name not in added:
                added.add(name)
                openapi_tags.append(
                    {
                        "name": name,
                        "description": root.get_attr(path, "description"),
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
