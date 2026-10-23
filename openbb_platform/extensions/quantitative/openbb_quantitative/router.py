"""Top-level router for the openbb-quantitative extension."""

from openbb_core.app.router import Router

from openbb_quantitative.attribution import router as _attribution_router
from openbb_quantitative.factors import router as _factors_router
from openbb_quantitative.metrics import router as _metrics_router
from openbb_quantitative.performance import router as _performance_router
from openbb_quantitative.risk_decomposition import (
    router as _risk_decomposition_router,
)
from openbb_quantitative.rolling import router as _rolling_router
from openbb_quantitative.stats import router as _stats_router

router = Router(prefix="", description="Quantitative analysis tools.")
router.include_router(_metrics_router)
router.include_router(_rolling_router)
router.include_router(_stats_router)
router.include_router(_performance_router)
router.include_router(_factors_router)
router.include_router(_risk_decomposition_router)
router.include_router(_attribution_router)

__all__ = ["router"]
