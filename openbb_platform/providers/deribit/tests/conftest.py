"""Shared fixtures for the openbb_deribit test suite."""

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


def payload(name: str):
    """Return one captured Deribit payload."""
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture
def load():
    """Return the loader for a captured Deribit payload."""
    return payload


@pytest.fixture(autouse=True)
def _no_network(request, monkeypatch):
    """Fail loudly rather than reaching the exchange from a unit test.

    A test marked ``uses_session`` builds its own sessions and is left alone;
    a session is only a connection pool until something asks it for a URL.
    """
    if request.node.get_closest_marker("uses_session"):
        return

    async def _forbidden(*args, **kwargs):
        raise AssertionError(
            "A unit test opened a session. Patch the client or the session."
        )

    monkeypatch.setattr("openbb_deribit.utils.session.get_session", _forbidden)
    monkeypatch.setattr("openbb_deribit.utils.session.get_cached_session", _forbidden)


@pytest.fixture
def responder(monkeypatch):
    """Answer client calls from a mapping of method name to payload."""

    def install(mapping: dict):
        async def _request(method, params=None, use_cache=True):
            if method not in mapping:
                raise AssertionError(f"No fixture registered for public/{method}.")

            answer = mapping[method]

            return answer(params) if callable(answer) else answer

        async def _gather(calls, use_cache=True):
            return [await _request(method, params) for method, params in calls]

        monkeypatch.setattr("openbb_deribit.utils.client.request", _request)
        monkeypatch.setattr("openbb_deribit.utils.client.gather", _gather)

        return mapping

    return install


def _chain_rows(inverse: bool, spot: float, size: float):
    """Build a small, well-formed chain around a spot price."""
    from datetime import date, timedelta

    today = date.today()
    rows = []

    for days in (1, 30):
        expiration = today + timedelta(days=days)

        for step in range(-4, 5):
            strike = round(spot * (1 + step * 0.02), 4)

            for option_type in ("call", "put"):
                moneyness = (
                    max(0.0, spot - strike)
                    if option_type == "call"
                    else max(0.0, strike - spot)
                )
                extrinsic = spot * 0.01 * (days / 30) ** 0.5
                mark = moneyness + extrinsic
                rows.append(
                    {
                        "contract_symbol": (
                            f"TEST-{days}-{strike:g}-{option_type[0].upper()}"
                        ),
                        "expiration": expiration,
                        "dte": days,
                        "strike": float(strike),
                        "option_type": option_type,
                        "contract_size": size,
                        "tick_size": 0.0001,
                        "is_inverse": inverse,
                        "mark": mark,
                        "bid": mark * 0.98,
                        "ask": mark * 1.02,
                        "implied_volatility": 50.0 + abs(step) * 2,
                        "open_interest": 10.0 + step,
                        "volume": 5.0,
                        "underlying_spot_price": spot,
                        "delta": 0.5,
                        "gamma": 0.001,
                        "theta": -1.0,
                        "vega": 10.0,
                        "rho": 1.0,
                    }
                )

    return rows


@pytest.fixture
def chain_frame():
    """Return a builder for a synthetic option chain."""
    from pandas import DataFrame

    def build(inverse: bool = True, spot: float = 100.0, size: float = 1.0):
        return DataFrame(_chain_rows(inverse, spot, size))

    return build


@pytest.fixture
def loaded_chain(monkeypatch, chain_frame):
    """Serve a synthetic chain wherever a chain would be loaded."""

    def install(inverse: bool = True, spot: float = 100.0, size: float = 1.0):
        frame = chain_frame(inverse, spot, size)

        async def _load(symbol, use_cache=True):
            return frame.copy()

        monkeypatch.setattr("openbb_deribit.utils.options.chain.load_chain", _load)

        return frame

    return install
