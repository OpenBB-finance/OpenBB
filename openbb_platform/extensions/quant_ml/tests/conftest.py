"""Common pytest fixtures for quant_ml extension tests."""

from __future__ import annotations

import os

import pytest

try:
    from openbb_quant_ml import quant_ml_router as qmr
except ModuleNotFoundError:  # pragma: no cover - local path setup dependent
    qmr = None


os.environ.setdefault("FRED_API_KEY", "test-fred-api-key")


@pytest.fixture(autouse=True)
def clear_quant_router_caches() -> None:
    if qmr is None:
        yield
        return
    caches = [
        qmr._RUN_SNAPSHOT_CACHE,
        qmr._HEALTH_CACHE,
        qmr._PERFORMANCE_ROLLING_CACHE,
        qmr._PERFORMANCE_REGIME_CACHE,
        qmr._MODEL_IC_DECAY_CACHE,
        qmr._REGIME_CURRENT_CACHE,
        qmr._REGIME_HISTORY_CACHE,
        qmr._ALERTS_CURRENT_CACHE,
    ]
    for cache in caches:
        cache.clear()
    yield
    for cache in caches:
        cache.clear()
