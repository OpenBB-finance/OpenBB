"""Integration-test fixtures for openbb-quantitative."""

import threading
import time

import numpy as np
import pandas as pd
import pytest

_SEED = 20240517
_N_ROWS = 500


@pytest.fixture(scope="session", autouse=True)
def api_server(pytestconfig):
    """Run the OpenBB REST API on 0.0.0.0:8000 for the integration session."""
    if pytestconfig.getoption("markexpr") == "not integration":
        yield None
        return

    import uvicorn
    from openbb_core.api.rest_api import app

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")  # noqa: S104
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 60
    while time.time() < deadline:
        if server.started:
            break
        time.sleep(0.25)
    else:  # pragma: no cover
        raise RuntimeError("The OpenBB REST API did not start within 60s.")

    yield server

    server.should_exit = True
    thread.join(timeout=15)


def _timeseries_records() -> list[dict]:
    """Build a deterministic OHLCV time series as JSON-ready records."""
    rng = np.random.default_rng(_SEED)
    t = np.arange(_N_ROWS)
    base = 100 + 0.1 * t + rng.normal(0, 1, _N_ROWS).cumsum() * 0.3
    close = np.abs(base + rng.normal(0, 1, _N_ROWS)) + 1.0
    open_ = close + rng.normal(0, 0.5, _N_ROWS)
    high = np.maximum(open_, close) + np.abs(rng.normal(1, 0.5, _N_ROWS))
    low = np.minimum(open_, close) - np.abs(rng.normal(1, 0.5, _N_ROWS))
    volume = 1_000_000 + rng.normal(0, 100_000, _N_ROWS) + 5_000 * t
    dates = pd.date_range("2021-01-04", periods=_N_ROWS, freq="B")
    return [
        {
            "date": day.strftime("%Y-%m-%d"),
            "open": round(float(o), 4),
            "high": round(float(h), 4),
            "low": round(float(lo), 4),
            "close": round(float(c), 4),
            "volume": round(float(v), 2),
        }
        for day, o, h, lo, c, v in zip(dates, open_, high, low, close, volume)
    ]


@pytest.fixture(scope="session")
def prices_data() -> list[dict]:
    """Deterministic OHLCV records for the quantitative command tests."""
    return _timeseries_records()
