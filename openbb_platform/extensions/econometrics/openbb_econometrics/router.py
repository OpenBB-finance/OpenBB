"""Top-level router for the openbb-econometrics extension."""

from openbb_core.app.router import Router

from openbb_econometrics.diagnostics import router as _diagnostics_router
from openbb_econometrics.panel import router as _panel_router
from openbb_econometrics.regression import router as _regression_router
from openbb_econometrics.time_series import router as _time_series_router
from openbb_econometrics.tools import router as _tools_router

router = Router(prefix="", description="Econometrics analysis tools.")
router.include_router(_tools_router)
router.include_router(_regression_router)
router.include_router(_diagnostics_router)
router.include_router(_time_series_router)
router.include_router(_panel_router)

__all__ = ["router"]
