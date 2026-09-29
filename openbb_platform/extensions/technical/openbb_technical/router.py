"""Top-level router for the openbb-technical extension."""

from openbb_core.app.router import Router

from openbb_technical.indicators import router as _indicators_router
from openbb_technical.multi import router as _multi_router
from openbb_technical.signals import router as _signals_router

router = Router(prefix="", description="Technical Analysis tools.")
router.include_router(_indicators_router)
router.include_router(_signals_router)
router.include_router(_multi_router)


__all__ = ["router"]
