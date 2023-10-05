from typing import List, Optional

from fastapi import APIRouter, FastAPI


class AppLoader:
    """App loader."""

    @staticmethod
    def from_routers(
        app: FastAPI, routers: List[Optional[APIRouter]], prefix: str
    ) -> FastAPI:
        """Load routers to app."""
        for router in routers:
            if router:
                app.include_router(router=router, prefix=prefix)

        return app
