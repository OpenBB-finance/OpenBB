"""End-to-end coverage of every openbb-technical endpoint against real CSV data.

Single-symbol endpoints run against one daily and one intraday SPY fixture
(``spy_daily_or_intraday``) so both date and datetime code paths are exercised
without a full 6-interval matrix explosion. Multi-symbol endpoints use the
``dow30_multi`` fixture loaded from ``multi.csv``. The catalog endpoint takes
no data and is exercised once per category.

Every test asserts the response is an ``OBBject`` whose ``results`` is a
non-empty list (or, for sparse signal endpoints, ``allow_empty=True``).
"""

import pytest
from openbb_core.app.model.obbject import OBBject

pytestmark = pytest.mark.integration


def _assert_obbject(result, *, allow_empty: bool = False) -> None:
    """Assert ``result`` is an OBBject with usable ``results``."""
    assert isinstance(result, OBBject), f"expected OBBject, got {type(result).__name__}"
    res = result.results
    assert res is not None, "OBBject.results is None"
    if not allow_empty and isinstance(res, list):
        assert len(res) > 0, "OBBject.results is empty list"


# --------------------------------------------------------------------------- #
# Overlays                                                                    #
# --------------------------------------------------------------------------- #


class TestOverlays:
    def test_sma(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.sma(data=spy_daily_or_intraday, length=20))

    def test_ema(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.ema(data=spy_daily_or_intraday, length=20))

    def test_hma(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.hma(data=spy_daily_or_intraday, length=20))

    def test_wma(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.wma(data=spy_daily_or_intraday, length=20))

    def test_zlma(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.zlma(data=spy_daily_or_intraday, length=20))

    def test_tema(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.tema(data=spy_daily_or_intraday, length=10))

    def test_dema(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.dema(data=spy_daily_or_intraday, length=10))

    def test_kama(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.kama(data=spy_daily_or_intraday, length=10))

    def test_frama(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.frama(data=spy_daily_or_intraday, length=16))

    def test_vwma(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.vwma(data=spy_daily_or_intraday, length=20))

    def test_bbands(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.bbands(data=spy_daily_or_intraday, length=20))

    def test_donchian(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.donchian(
                data=spy_daily_or_intraday, lower_length=20, upper_length=20
            )
        )

    def test_kc(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.kc(data=spy_daily_or_intraday, length=20))

    def test_ichimoku(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.ichimoku(data=spy_daily_or_intraday))

    def test_supertrend(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.supertrend(data=spy_daily_or_intraday, length=10))


# --------------------------------------------------------------------------- #
# Oscillators                                                                 #
# --------------------------------------------------------------------------- #


class TestOscillators:
    def test_rsi(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.rsi(data=spy_daily_or_intraday, length=14))

    def test_stoch(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.stoch(
                data=spy_daily_or_intraday,
                fast_k_period=14,
                slow_d_period=3,
                slow_k_period=3,
            )
        )

    def test_cci(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.cci(data=spy_daily_or_intraday, length=20))

    def test_fisher(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.fisher(data=spy_daily_or_intraday, length=9))

    def test_cg(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.cg(data=spy_daily_or_intraday, length=14))

    def test_williams_r(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.williams_r(data=spy_daily_or_intraday, length=14))

    def test_mfi(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.mfi(data=spy_daily_or_intraday, length=14))

    def test_trix(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.trix(data=spy_daily_or_intraday, length=15))

    def test_ultimate_oscillator(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.ultimate_oscillator(
                data=spy_daily_or_intraday, fast=7, medium=14, slow=28
            )
        )

    def test_awesome_oscillator(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.awesome_oscillator(data=spy_daily_or_intraday))


# --------------------------------------------------------------------------- #
# Trend                                                                       #
# --------------------------------------------------------------------------- #


class TestTrend:
    def test_macd(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.macd(data=spy_daily_or_intraday, fast=12, slow=26, signal=9)
        )

    def test_adx(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.adx(data=spy_daily_or_intraday, length=14))

    def test_di(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.di(data=spy_daily_or_intraday, length=14))

    def test_aroon(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.aroon(data=spy_daily_or_intraday, length=14))

    def test_choppiness(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.choppiness(data=spy_daily_or_intraday, length=14))


# --------------------------------------------------------------------------- #
# Volume                                                                      #
# --------------------------------------------------------------------------- #


class TestVolume:
    def test_obv(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.obv(data=spy_daily_or_intraday))

    def test_ad(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.ad(data=spy_daily_or_intraday))

    def test_adosc(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.adosc(data=spy_daily_or_intraday, fast=3, slow=10)
        )

    def test_vwap(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.vwap(data=spy_daily_or_intraday))


# --------------------------------------------------------------------------- #
# Volatility                                                                  #
# --------------------------------------------------------------------------- #


class TestVolatility:
    def test_atr(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.atr(data=spy_daily_or_intraday, length=14))

    def test_realized_volatility(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.realized_volatility(
                data=spy_daily_or_intraday, model="yang_zhang", window=30
            )
        )

    def test_realized_volatility_compare(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.realized_volatility_compare(
                data=spy_daily_or_intraday, window=30
            )
        )

    def test_cones(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.cones(data=spy_daily_or_intraday, model="std"))


# --------------------------------------------------------------------------- #
# Structure                                                                   #
# --------------------------------------------------------------------------- #


class TestStructure:
    def test_fib(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.fib(data=spy_daily_or_intraday, period=120))

    def test_demark(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.demark(data=spy_daily_or_intraday))

    @pytest.mark.parametrize(
        "method", ["classic", "fibonacci", "woodie", "camarilla", "demark"]
    )
    def test_pivot_points(self, obb, spy_1d, method):
        _assert_obbject(obb.technical.pivot_points(data=spy_1d, method=method))


# --------------------------------------------------------------------------- #
# Statistics                                                                  #
# --------------------------------------------------------------------------- #


class TestStatistics:
    def test_clenow(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.clenow(data=spy_daily_or_intraday, period=90))

    def test_drawdown(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.drawdown(data=spy_daily_or_intraday))

    def test_returns_stats(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.returns_stats(data=spy_daily_or_intraday, frequency="daily")
        )

    def test_stationarity(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.stationarity(data=spy_daily_or_intraday))

    def test_hurst(self, obb, spy_daily_or_intraday):
        _assert_obbject(obb.technical.hurst(data=spy_daily_or_intraday))

    def test_autocorrelation(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.autocorrelation(data=spy_daily_or_intraday, max_lag=20)
        )


# --------------------------------------------------------------------------- #
# Signals (/signals subrouter)                                                #
# --------------------------------------------------------------------------- #


class TestSignals:
    def test_crossovers(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.signals.crossovers(
                data=spy_daily_or_intraday,
                fast_length=20,
                slow_length=50,
                mamode="sma",
            ),
            allow_empty=True,
        )

    @pytest.mark.parametrize("indicator", ["rsi", "mfi", "stoch", "williams_r", "cci"])
    def test_oscillator_signals(self, obb, spy_1d, indicator):
        _assert_obbject(
            obb.technical.signals.oscillator_signals(
                data=spy_1d, indicator=indicator, length=14
            )
        )

    @pytest.mark.parametrize("method", ["donchian", "bollinger"])
    def test_breakouts(self, obb, spy_1d, method):
        _assert_obbject(
            obb.technical.signals.breakouts(data=spy_1d, method=method, length=20),
            allow_empty=True,
        )

    @pytest.mark.parametrize("indicator", ["rsi", "macd", "stoch", "cci"])
    def test_divergences(self, obb, spy_1d, indicator):
        _assert_obbject(
            obb.technical.signals.divergences(
                data=spy_1d,
                indicator=indicator,
                indicator_length=14,
                lookback=60,
            ),
            allow_empty=True,
        )

    def test_candlestick_patterns(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.signals.candlestick_patterns(data=spy_daily_or_intraday),
            allow_empty=True,
        )

    def test_regime(self, obb, spy_daily_or_intraday):
        _assert_obbject(
            obb.technical.signals.regime(data=spy_daily_or_intraday, length=14)
        )


# --------------------------------------------------------------------------- #
# Multi-symbol endpoints (/multi subrouter + relative_rotation)               #
# --------------------------------------------------------------------------- #


class TestMultiSymbol:
    def test_correlation_pearson(self, obb, dow30_multi):
        _assert_obbject(
            obb.technical.correlation(
                data=dow30_multi,
                pairs=[("AAPL", "MSFT")],
                method="pearson",
            )
        )

    @pytest.mark.parametrize("method", ["pearson", "spearman", "kendall"])
    def test_correlation_methods(self, obb, dow30_multi, method):
        _assert_obbject(
            obb.technical.correlation(
                data=dow30_multi,
                pairs=[("AAPL", "MSFT"), ("AAPL", "NVDA")],
                method=method,
            )
        )

    def test_correlation_matrix(self, obb, dow30_multi):
        _assert_obbject(obb.technical.correlation_matrix(data=dow30_multi))

    def test_correlation_matrix_window(self, obb, dow30_multi):
        _assert_obbject(obb.technical.correlation_matrix(data=dow30_multi, window=60))

    def test_screen_oversold_rsi(self, obb, dow30_multi):
        result = obb.technical.screen(
            data=dow30_multi,
            conditions=[
                {
                    "indicator": "rsi",
                    "column": "close_RSI_14",
                    "operator": "lt",
                    "value": 100.0,
                }
            ],
        )
        _assert_obbject(result, allow_empty=True)

    def test_screen_between(self, obb, dow30_multi):
        result = obb.technical.screen(
            data=dow30_multi,
            conditions=[
                {
                    "indicator": "rsi",
                    "column": "close_RSI_14",
                    "operator": "between",
                    "value": [0.0, 100.0],
                }
            ],
        )
        _assert_obbject(result, allow_empty=True)

    def test_screen_and_combine(self, obb, dow30_multi):
        result = obb.technical.screen(
            data=dow30_multi,
            conditions=[
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
            combine="and",
        )
        _assert_obbject(result, allow_empty=True)

    def test_relative_rotation(self, obb, dow30_multi):
        # relative_rotation requires daily data with >252 bars; multi.csv is daily
        # with ~1600 bars per symbol so it satisfies the constraint.
        _assert_obbject(
            obb.technical.relative_rotation(
                data=dow30_multi,
                benchmark="AAPL",
            )
        )


# --------------------------------------------------------------------------- #
# Multi-indicator compose                                                     #
# --------------------------------------------------------------------------- #


class TestMultiCompose:
    def test_multi_two_indicators(self, obb, spy_1d):
        result = obb.technical.multi(
            data=spy_1d,
            indicators=[
                {"indicator": "rsi", "params": {"length": 14}},
                {"indicator": "sma", "params": {"length": 50}},
            ],
        )
        _assert_obbject(result)

    def test_multi_intraday(self, obb, spy_30m):
        result = obb.technical.multi(
            data=spy_30m,
            indicators=[
                {"indicator": "ema", "params": {"length": 20}},
                {"indicator": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
            ],
        )
        _assert_obbject(result)


# --------------------------------------------------------------------------- #
# Catalog                                                                     #
# --------------------------------------------------------------------------- #


class TestCatalog:
    def test_indicators_all(self, obb):
        result = obb.technical.indicators(category="all")
        _assert_obbject(result)

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
    def test_indicators_by_category(self, obb, category):
        result = obb.technical.indicators(category=category)
        _assert_obbject(result)
