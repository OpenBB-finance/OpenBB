"""Indicators sub-package."""

from openbb_core.app.router import Router

from openbb_technical.indicators import (
    oscillators,
    overlays,
    relative_rotation,
    statistics,
    structure,
    trend,
    volatility,
    volume,
)

router = Router(prefix="", description="Technical indicators.")
router.include_router(overlays.router)
router.include_router(oscillators.router)
router.include_router(trend.router)
router.include_router(volume.router)
router.include_router(volatility.router)
router.include_router(structure.router)
router.include_router(statistics.router)
router.include_router(relative_rotation.router)


__all__ = [
    "overlays",
    "oscillators",
    "relative_rotation",
    "router",
    "statistics",
    "structure",
    "trend",
    "volatility",
    "volume",
]
