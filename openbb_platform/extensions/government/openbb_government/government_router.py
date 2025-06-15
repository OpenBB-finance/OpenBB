"""Government Router."""

# pylint: disable=unused-argument


from openbb_core.app.router import Router

from openbb_government.us.us_router import router as us_router

router = Router(prefix="", description="Government data.")
router.include_router(us_router)
