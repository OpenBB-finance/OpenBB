"""TMX Derivatives sub-router."""

from openbb_core.app.router import Router

from openbb_tmx.routers.futures import router as futures_router
from openbb_tmx.routers.options import router as options_router

router = Router(prefix="/derivatives", description="TMX derivatives data.")

router.include_router(options_router)
router.include_router(futures_router)
