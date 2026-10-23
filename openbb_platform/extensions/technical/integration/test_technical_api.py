"""End-to-end HTTP coverage of every openbb-technical endpoint.

Hits an in-process uvicorn server (see ``api_server`` fixture) over
``http://127.0.0.1:<port>/api/v1/technical/...`` with the same CSV fixtures
used by ``test_technical_python.py``. Each test asserts a 200 response with a
non-empty ``results`` list (or, for sparse signal endpoints, an OBBject shape
regardless of length).

The OpenBB API exposes each endpoint as POST with:
* a JSON request body whose shape depends on how many "body" arguments the
  function has (a single ``data: list[Data]`` becomes the array body root; two
  or more body args are wrapped in a ``{data, ...}`` object), and
* every other scalar argument as a query-string parameter.
``_post`` accepts the body and the query params separately so each test can
mirror the function's actual call site.
"""

import pytest
import requests

pytestmark = pytest.mark.integration

DEFAULT_TIMEOUT = 60.0


def _post(
    api_server: str,
    path: str,
    *,
    body,
    params: dict | None = None,
    allow_empty: bool = False,
):
    """POST to ``{api_server}/technical/{path}`` and assert success.

    Every endpoint now declares a single ``params: XxxQueryParams`` argument,
    which FastAPI exposes as one JSON request body. ``body`` may be the bare
    ``data`` list or an already-assembled dict; ``params`` carries the scalar
    arguments. Both are merged into the single ``XxxQueryParams`` body object.
    """
    url = f"{api_server}/technical/{path}"
    if body is None:
        payload = dict(params or {})
    elif isinstance(body, list):
        payload = {"data": body, **(params or {})}
    else:
        payload = {**body, **(params or {})}
    response = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    assert response.status_code == 200, (
        f"POST {path} -> {response.status_code}: {response.text[:300]}"
    )
    payload = response.json()
    assert "results" in payload, (
        f"POST {path} response missing 'results' key: {payload}"
    )
    results = payload["results"]
    assert results is not None, f"POST {path} returned 'results=null'"
    if not allow_empty and isinstance(results, list):
        assert len(results) > 0, f"POST {path} returned empty 'results' list"
    return payload


# --------------------------------------------------------------------------- #
# Overlays                                                                    #
# --------------------------------------------------------------------------- #


class TestOverlaysAPI:
    def test_sma(self, api_server, spy_daily_or_intraday):
        _post(api_server, "sma", body=spy_daily_or_intraday, params={"length": 20})

    def test_ema(self, api_server, spy_daily_or_intraday):
        _post(api_server, "ema", body=spy_daily_or_intraday, params={"length": 20})

    def test_hma(self, api_server, spy_daily_or_intraday):
        _post(api_server, "hma", body=spy_daily_or_intraday, params={"length": 20})

    def test_wma(self, api_server, spy_daily_or_intraday):
        _post(api_server, "wma", body=spy_daily_or_intraday, params={"length": 20})

    def test_zlma(self, api_server, spy_daily_or_intraday):
        _post(api_server, "zlma", body=spy_daily_or_intraday, params={"length": 20})

    def test_tema(self, api_server, spy_daily_or_intraday):
        _post(api_server, "tema", body=spy_daily_or_intraday, params={"length": 10})

    def test_dema(self, api_server, spy_daily_or_intraday):
        _post(api_server, "dema", body=spy_daily_or_intraday, params={"length": 10})

    def test_kama(self, api_server, spy_daily_or_intraday):
        _post(api_server, "kama", body=spy_daily_or_intraday, params={"length": 10})

    def test_frama(self, api_server, spy_daily_or_intraday):
        _post(api_server, "frama", body=spy_daily_or_intraday, params={"length": 16})

    def test_vwma(self, api_server, spy_daily_or_intraday):
        _post(api_server, "vwma", body=spy_daily_or_intraday, params={"length": 20})

    def test_bbands(self, api_server, spy_daily_or_intraday):
        _post(api_server, "bbands", body=spy_daily_or_intraday, params={"length": 20})

    def test_donchian(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "donchian",
            body=spy_daily_or_intraday,
            params={"lower_length": 20, "upper_length": 20},
        )

    def test_kc(self, api_server, spy_daily_or_intraday):
        _post(api_server, "kc", body=spy_daily_or_intraday, params={"length": 20})

    def test_ichimoku(self, api_server, spy_daily_or_intraday):
        _post(api_server, "ichimoku", body=spy_daily_or_intraday)

    def test_supertrend(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "supertrend",
            body=spy_daily_or_intraday,
            params={"length": 10},
        )


# --------------------------------------------------------------------------- #
# Oscillators                                                                 #
# --------------------------------------------------------------------------- #


class TestOscillatorsAPI:
    def test_rsi(self, api_server, spy_daily_or_intraday):
        _post(api_server, "rsi", body=spy_daily_or_intraday, params={"length": 14})

    def test_stoch(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "stoch",
            body=spy_daily_or_intraday,
            params={"fast_k_period": 14, "slow_d_period": 3, "slow_k_period": 3},
        )

    def test_cci(self, api_server, spy_daily_or_intraday):
        _post(api_server, "cci", body=spy_daily_or_intraday, params={"length": 20})

    def test_fisher(self, api_server, spy_daily_or_intraday):
        _post(api_server, "fisher", body=spy_daily_or_intraday, params={"length": 9})

    def test_cg(self, api_server, spy_daily_or_intraday):
        _post(api_server, "cg", body=spy_daily_or_intraday, params={"length": 14})

    def test_williams_r(self, api_server, spy_daily_or_intraday):
        _post(
            api_server, "williams_r", body=spy_daily_or_intraday, params={"length": 14}
        )

    def test_mfi(self, api_server, spy_daily_or_intraday):
        _post(api_server, "mfi", body=spy_daily_or_intraday, params={"length": 14})

    def test_trix(self, api_server, spy_daily_or_intraday):
        _post(api_server, "trix", body=spy_daily_or_intraday, params={"length": 15})

    def test_ultimate_oscillator(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "ultimate_oscillator",
            body=spy_daily_or_intraday,
            params={"fast": 7, "medium": 14, "slow": 28},
        )

    def test_awesome_oscillator(self, api_server, spy_daily_or_intraday):
        _post(api_server, "awesome_oscillator", body=spy_daily_or_intraday)


# --------------------------------------------------------------------------- #
# Trend                                                                       #
# --------------------------------------------------------------------------- #


class TestTrendAPI:
    def test_macd(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "macd",
            body=spy_daily_or_intraday,
            params={"fast": 12, "slow": 26, "signal": 9},
        )

    def test_adx(self, api_server, spy_daily_or_intraday):
        _post(api_server, "adx", body=spy_daily_or_intraday, params={"length": 14})

    def test_di(self, api_server, spy_daily_or_intraday):
        _post(api_server, "di", body=spy_daily_or_intraday, params={"length": 14})

    def test_aroon(self, api_server, spy_daily_or_intraday):
        _post(api_server, "aroon", body=spy_daily_or_intraday, params={"length": 14})

    def test_choppiness(self, api_server, spy_daily_or_intraday):
        _post(
            api_server, "choppiness", body=spy_daily_or_intraday, params={"length": 14}
        )


# --------------------------------------------------------------------------- #
# Volume                                                                      #
# --------------------------------------------------------------------------- #


class TestVolumeAPI:
    def test_obv(self, api_server, spy_daily_or_intraday):
        _post(api_server, "obv", body=spy_daily_or_intraday)

    def test_ad(self, api_server, spy_daily_or_intraday):
        _post(api_server, "ad", body=spy_daily_or_intraday)

    def test_adosc(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "adosc",
            body=spy_daily_or_intraday,
            params={"fast": 3, "slow": 10},
        )

    def test_vwap(self, api_server, spy_daily_or_intraday):
        _post(api_server, "vwap", body=spy_daily_or_intraday)


# --------------------------------------------------------------------------- #
# Volatility                                                                  #
# --------------------------------------------------------------------------- #


class TestVolatilityAPI:
    def test_atr(self, api_server, spy_daily_or_intraday):
        _post(api_server, "atr", body=spy_daily_or_intraday, params={"length": 14})

    def test_realized_volatility(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "realized_volatility",
            body=spy_daily_or_intraday,
            params={"model": "yang_zhang", "window": 30},
        )

    def test_realized_volatility_compare(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "realized_volatility_compare",
            body={"data": spy_daily_or_intraday, "models": ["std", "parkinson"]},
            params={"window": 30},
        )

    def test_cones(self, api_server, spy_daily_or_intraday):
        _post(api_server, "cones", body=spy_daily_or_intraday, params={"model": "std"})


# --------------------------------------------------------------------------- #
# Structure                                                                   #
# --------------------------------------------------------------------------- #


class TestStructureAPI:
    def test_fib(self, api_server, spy_daily_or_intraday):
        _post(api_server, "fib", body=spy_daily_or_intraday, params={"period": 120})

    def test_demark(self, api_server, spy_daily_or_intraday):
        _post(api_server, "demark", body=spy_daily_or_intraday)

    @pytest.mark.parametrize(
        "method", ["classic", "fibonacci", "woodie", "camarilla", "demark"]
    )
    def test_pivot_points(self, api_server, spy_1d, method):
        _post(api_server, "pivot_points", body=spy_1d, params={"method": method})


# --------------------------------------------------------------------------- #
# Statistics                                                                  #
# --------------------------------------------------------------------------- #


class TestStatisticsAPI:
    def test_clenow(self, api_server, spy_daily_or_intraday):
        _post(api_server, "clenow", body=spy_daily_or_intraday, params={"period": 90})

    def test_drawdown(self, api_server, spy_daily_or_intraday):
        _post(api_server, "drawdown", body=spy_daily_or_intraday)

    def test_returns_stats(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "returns_stats",
            body=spy_daily_or_intraday,
            params={"frequency": "daily"},
        )

    def test_stationarity(self, api_server, spy_daily_or_intraday):
        _post(api_server, "stationarity", body=spy_daily_or_intraday)

    def test_hurst(self, api_server, spy_daily_or_intraday):
        _post(api_server, "hurst", body=spy_daily_or_intraday)

    def test_autocorrelation(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "autocorrelation",
            body=spy_daily_or_intraday,
            params={"max_lag": 20},
        )


# --------------------------------------------------------------------------- #
# Signals (/signals subrouter)                                                #
# --------------------------------------------------------------------------- #


class TestSignalsAPI:
    def test_crossovers(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "signals/crossovers",
            body=spy_daily_or_intraday,
            params={"fast_length": 20, "slow_length": 50, "mamode": "sma"},
            allow_empty=True,
        )

    @pytest.mark.parametrize("indicator", ["rsi", "mfi", "stoch", "williams_r", "cci"])
    def test_oscillator_signals(self, api_server, spy_1d, indicator):
        _post(
            api_server,
            "signals/oscillator_signals",
            body=spy_1d,
            params={"indicator": indicator, "length": 14},
        )

    @pytest.mark.parametrize("method", ["donchian", "bollinger"])
    def test_breakouts(self, api_server, spy_1d, method):
        _post(
            api_server,
            "signals/breakouts",
            body=spy_1d,
            params={"method": method, "length": 20},
            allow_empty=True,
        )

    @pytest.mark.parametrize("indicator", ["rsi", "macd", "stoch", "cci"])
    def test_divergences(self, api_server, spy_1d, indicator):
        _post(
            api_server,
            "signals/divergences",
            body=spy_1d,
            params={"indicator": indicator, "indicator_length": 14, "lookback": 60},
            allow_empty=True,
        )

    def test_candlestick_patterns(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "signals/candlestick_patterns",
            body={
                "data": spy_daily_or_intraday,
                "patterns": ["doji", "hammer", "shooting_star"],
            },
            allow_empty=True,
        )

    def test_regime(self, api_server, spy_daily_or_intraday):
        _post(
            api_server,
            "signals/regime",
            body=spy_daily_or_intraday,
            params={"length": 14},
        )


# --------------------------------------------------------------------------- #
# Multi-symbol endpoints (wrapped body: {data, ...})                          #
# --------------------------------------------------------------------------- #


class TestMultiSymbolAPI:
    @pytest.mark.parametrize("method", ["pearson", "spearman", "kendall"])
    def test_correlation_methods(self, api_server, dow30_multi, method):
        _post(
            api_server,
            "correlation",
            body={"data": dow30_multi, "pairs": [["AAPL", "MSFT"]]},
            params={"method": method},
        )

    def test_correlation_matrix(self, api_server, dow30_multi):
        _post(api_server, "correlation_matrix", body=dow30_multi)

    def test_correlation_matrix_window(self, api_server, dow30_multi):
        _post(
            api_server,
            "correlation_matrix",
            body=dow30_multi,
            params={"window": 60},
        )

    def test_screen_lt(self, api_server, dow30_multi):
        _post(
            api_server,
            "screen",
            body={
                "data": dow30_multi,
                "conditions": [
                    {
                        "indicator": "rsi",
                        "column": "close_RSI_14",
                        "operator": "lt",
                        "value": 100.0,
                    }
                ],
            },
            allow_empty=True,
        )

    def test_screen_between(self, api_server, dow30_multi):
        _post(
            api_server,
            "screen",
            body={
                "data": dow30_multi,
                "conditions": [
                    {
                        "indicator": "rsi",
                        "column": "close_RSI_14",
                        "operator": "between",
                        "value": [0.0, 100.0],
                    }
                ],
            },
            allow_empty=True,
        )

    def test_screen_and_combine(self, api_server, dow30_multi):
        _post(
            api_server,
            "screen",
            body={
                "data": dow30_multi,
                "conditions": [
                    {
                        "indicator": "rsi",
                        "column": "close_RSI_14",
                        "operator": "lt",
                        "value": 100.0,
                    },
                    {
                        "indicator": "sma",
                        "column": "close_SMA_20",
                        "operator": "gt",
                        "value": 0.0,
                    },
                ],
            },
            params={"combine": "and"},
            allow_empty=True,
        )

    def test_relative_rotation(self, api_server, dow30_multi):
        _post(
            api_server,
            "relative_rotation",
            body={"data": dow30_multi, "chart_params": {}},
            params={"benchmark": "AAPL"},
        )


# --------------------------------------------------------------------------- #
# Multi-indicator compose (wrapped body)                                      #
# --------------------------------------------------------------------------- #


class TestMultiComposeAPI:
    def test_multi_two_indicators(self, api_server, spy_1d):
        _post(
            api_server,
            "multi",
            body={
                "data": spy_1d,
                "indicators": [
                    {"indicator": "rsi", "params": {"length": 14}},
                    {"indicator": "sma", "params": {"length": 50}},
                ],
            },
        )

    def test_multi_intraday(self, api_server, spy_30m):
        _post(
            api_server,
            "multi",
            body={
                "data": spy_30m,
                "indicators": [
                    {"indicator": "ema", "params": {"length": 20}},
                    {
                        "indicator": "macd",
                        "params": {"fast": 12, "slow": 26, "signal": 9},
                    },
                ],
            },
        )


# --------------------------------------------------------------------------- #
# Catalog (GET-like; no body)                                                 #
# --------------------------------------------------------------------------- #


class TestCatalogAPI:
    def test_indicators_all(self, api_server):
        # ``indicators`` has no body args, so an empty body + query params work.
        _post(api_server, "indicators", body=None, params={"category": "all"})

    @pytest.mark.parametrize(
        "category",
        [
            "overlay",
            "oscillator",
            "volatility",
            "volume",
            "trend",
            "signal",
            "structure",
            "stats",
            "multi",
        ],
    )
    def test_indicators_by_category(self, api_server, category):
        _post(api_server, "indicators", body=None, params={"category": category})
