"""Signals sub-package — derived events on top of raw indicators."""

from openbb_core.app.router import Router

from openbb_technical.signals import (
    breakouts,
    crossovers,
    divergences,
    patterns,
    regime,
    thresholds,
)

router = Router(
    prefix="/signals", description="Signal-layer endpoints on technical indicators."
)
router.include_router(crossovers.router)
router.include_router(thresholds.router)
router.include_router(divergences.router)
router.include_router(breakouts.router)
router.include_router(patterns.router)
router.include_router(regime.router)


__all__ = [
    "breakouts",
    "crossovers",
    "divergences",
    "patterns",
    "regime",
    "router",
    "thresholds",
]
