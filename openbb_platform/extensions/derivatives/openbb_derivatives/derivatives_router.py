"""Derivatives Router."""

# pylint: disable=unused-argument

from openbb_core.app.router import Router

from openbb_derivatives.options.options_router import router as options_router

router = Router(prefix="")
router.include_router(options_router)
