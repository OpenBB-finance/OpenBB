from openbb_core.app.router import Router

from openbb_forecast.regression.regression_router import router as regression_router
from openbb_forecast.statistical.statistical_router import router as statistical_router
from openbb_forecast.torch.torch_router import router as torch_router


router = Router(prefix="")


# Regression Models
router.include_router(regression_router)

# Statistical Models
router.include_router(statistical_router)

# Torch Models
router.include_router(torch_router)
