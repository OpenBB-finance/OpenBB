"""Shared fixtures for the integration test suite.

The fixtures here load deterministic OHLC(V) data from CSV files staged in
``integration/fixtures/``. Records are capped at a small per-interval limit so
the Pydantic validation cost inside the static-package container stays cheap.
"""

from pathlib import Path

import pandas as pd
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Capping rows keeps Pydantic validation fast. 400 daily bars is enough to
# warm every rolling indicator up to length 252 (relative_rotation default).
_ROW_CAP = 400


def _read_csv_records(name: str, cap: int | None = _ROW_CAP) -> list[dict]:
    """Read a fixture CSV and return long-format list[dict] records, capped."""
    df = pd.read_csv(FIXTURES_DIR / name)
    if cap is not None:
        df = df.tail(cap)
    return df.to_dict(orient="records")


@pytest.fixture(scope="session")
def spy_1d() -> list[dict]:
    """SPY daily bars (most recent 400)."""
    return _read_csv_records("SPY_1d.csv")


@pytest.fixture(scope="session")
def spy_60m() -> list[dict]:
    """SPY 60-minute bars (most recent 400)."""
    return _read_csv_records("SPY_60m.csv")


@pytest.fixture(scope="session")
def spy_30m() -> list[dict]:
    """SPY 30-minute bars (most recent 400)."""
    return _read_csv_records("SPY_30m.csv")


@pytest.fixture(scope="session")
def spy_15m() -> list[dict]:
    """SPY 15-minute bars (most recent 400)."""
    return _read_csv_records("SPY_15m.csv")


@pytest.fixture(scope="session")
def spy_5m() -> list[dict]:
    """SPY 5-minute bars (most recent 400)."""
    return _read_csv_records("SPY_5m.csv")


@pytest.fixture(scope="session")
def spy_1m() -> list[dict]:
    """SPY 1-minute bars (most recent 400)."""
    return _read_csv_records("SPY_1m.csv")


@pytest.fixture(
    scope="session",
    params=["spy_1d", "spy_30m"],
    ids=["1d", "30m"],
)
def spy_daily_or_intraday(request) -> list[dict]:
    """Single-symbol fixture parametrised across one daily + one intraday set.

    Two intervals are enough to exercise both the pure-date and the datetime
    code paths without paying for the full 6-interval matrix on every endpoint.
    """
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="session")
def dow30_multi() -> list[dict]:
    """Daily OHLCV basket for a handful of Dow 30 names (capped for speed)."""
    # Trim to a fixed symbol subset and most-recent 400 rows per symbol to keep
    # multi-symbol endpoints (correlation, screen, relative_rotation) fast.
    df = pd.read_csv(FIXTURES_DIR / "multi.csv")
    keep = ["AAPL", "MSFT", "NVDA", "AMZN", "JPM", "V"]
    df = df[df["symbol"].isin(keep)]
    df = (
        df.sort_values(["symbol", "date"]).groupby("symbol", group_keys=False).tail(400)
    )
    return df.to_dict(orient="records")


@pytest.fixture(scope="session")
def obb():
    """Lazy ``openbb.obb`` accessor."""
    import openbb

    return openbb.obb


@pytest.fixture(scope="session")
def api_server():
    """Run the OpenBB REST API in a background thread; yield its base URL.

    Starts uvicorn against ``openbb_core.api.rest_api:app`` on a free local
    port, polls the readiness endpoint until it answers, yields
    ``http://127.0.0.1:<port>/api/v1``, and shuts the server down at session
    teardown. ``OPENBB_API_AUTH`` is left at its default (``False``) so tests
    can hit endpoints without basic-auth headers.
    """
    import socket
    import threading
    import time

    import requests
    import uvicorn
    from openbb_core.api.rest_api import app

    # Bind to an ephemeral port so concurrent test runs do not collide.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    config = uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="error", access_log=False
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}/api/v1"
    # Wait for the server to start serving requests; openapi.json is cheap.
    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/openapi.json", timeout=2.0)
            if r.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.1)
    else:
        server.should_exit = True
        thread.join(timeout=5)
        raise RuntimeError(f"uvicorn did not start on port {port} within 30s")

    yield base_url

    server.should_exit = True
    thread.join(timeout=5)
