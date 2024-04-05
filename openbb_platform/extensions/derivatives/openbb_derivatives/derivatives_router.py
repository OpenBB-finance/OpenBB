"""Derivatives Router."""

from openbb_core.app.router import Router

from openbb_derivatives.futures.futures_router import router as futures_router
from openbb_derivatives.options.options_router import router as options_router

router = Router(prefix="", description="Derivatives market data.")
router.include_router(options_router)
router.include_router(futures_router)
