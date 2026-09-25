"""Multi-indicator and cross-asset technical analysis endpoints."""

from openbb_core.app.router import Router

from openbb_technical.multi.catalog import router as _catalog_router
from openbb_technical.multi.compose import router as _compose_router
from openbb_technical.multi.correlation import router as _correlation_router
from openbb_technical.multi.screen import router as _screen_router

router = Router(prefix="", description="Multi-indicator / cross-asset endpoints.")
router.include_router(_compose_router)
router.include_router(_correlation_router)
router.include_router(_screen_router)
router.include_router(_catalog_router)

__all__ = ["router"]
