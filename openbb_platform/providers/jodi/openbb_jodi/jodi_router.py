"""JODI Router."""

from contextlib import asynccontextmanager

from openbb_core.app.router import Router

from openbb_jodi.gas_router import router as gas_router
from openbb_jodi.oil_router import router as oil_router


@asynccontextmanager
async def lifespan(_):
    """Warm the JODI table cache in the background at application startup."""
    from openbb_jodi.utils.helpers import start_prefetch

    start_prefetch()
    yield


router = Router(
    prefix="",
    description="Monthly petroleum and natural gas supply, demand, and stock"
    + " statistics, self-reported by over 100 countries, from the Joint"
    + " Organisations Data Initiative (JODI) World Databases.",
)
router.api_router.lifespan_context = lifespan
router.include_router(oil_router)
router.include_router(gas_router)


@router.api_router.get("/apps.json", include_in_schema=False)
async def jodi_apps() -> list:
    """Serve the bundled JODI dashboard template (``assets/apps.json``)."""
    import json  # noqa
    from pathlib import Path

    apps_json = Path(__file__).parent / "assets" / "apps.json"

    return json.loads(apps_json.read_text(encoding="utf-8"))
