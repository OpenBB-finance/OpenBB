"""Tests for ``OptionsChainsProperties`` DataFrame analytics + pandas guard.

These tests are split into two groups:

1. The pandas-guard test (no ``requires_pandas`` marker) verifies that the
   analytics surface raises a clear, actionable ``OpenBBError`` when the
   ``[pandas]`` extra is not installed — we mock ``__import__`` to hide
   pandas/numpy from the consumer.
2. The DataFrame method tests are gated on the ``requires_pandas`` marker
   (registered in ``pytest.ini``) and exercise the most common analytics
   entry points: ``dataframe``, ``filter_data``, ``_get_stat`` aggregates,
   ``straddle``, ``strangle``, ``synthetic_long``/``_short``,
   ``vertical_call_spread``/``vertical_put_spread`` and ``skew``.

A synthetic, deterministic options chain is built in ``_build_chain`` so the
tests have no provider dependency and run in milliseconds.
"""

import builtins
from datetime import date, timedelta

import pytest

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.standard_models.options_chains import OptionsChainsData

requires_pandas = pytest.mark.requires_pandas


# ---------------------------------------------------------------------------
# Pandas-missing guard (runs without pandas installed)
# ---------------------------------------------------------------------------


def test_dataframe_raises_clear_error_without_pandas(monkeypatch):
    """``dataframe`` must surface an actionable install hint when pandas is gone."""
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pandas" or name.startswith("pandas."):
            raise ImportError("No module named 'pandas'")
        if name == "numpy" or name.startswith("numpy."):
            raise ImportError("No module named 'numpy'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    data = OptionsChainsData(
        contract_symbol=["FAKE"],
        expiration=[date(2030, 1, 17)],
        strike=[100.0],
        option_type=["call"],
        underlying_symbol=["FAKE"],
        underlying_price=[100.0],
        bid=[1.0],
        ask=[1.1],
    )
    with pytest.raises(OpenBBError, match=r"openbb-core\[pandas\]"):
        _ = data.dataframe


# ---------------------------------------------------------------------------
# DataFrame analytics — require pandas
# ---------------------------------------------------------------------------


def _build_chain(
    expirations: int = 2,
    strikes: tuple[float, ...] = (90.0, 95.0, 100.0, 105.0, 110.0),
    underlying_price: float = 100.0,
) -> OptionsChainsData:
    """Build a deterministic, balanced call/put chain across N expirations."""
    rows: list[dict] = []
    base = date.today() + timedelta(days=14)
    for e in range(expirations):
        exp = base + timedelta(days=30 * e)
        for k in strikes:
            for opt in ("call", "put"):
                # Simple, monotone bid/ask so spreads/aggregations are predictable.
                intrinsic = (
                    max(0.0, underlying_price - k)
                    if opt == "call"
                    else max(0.0, k - underlying_price)
                )
                bid = round(intrinsic + 1.0, 2)
                ask = round(bid + 0.10, 2)
                rows.append(
                    {
                        "underlying_symbol": "FAKE",
                        "underlying_price": underlying_price,
                        "contract_symbol": (
                            f"FAKE{exp:%y%m%d}{opt[0].upper()}{int(k * 1000):08d}"
                        ),
                        "eod_date": date.today(),
                        "expiration": exp,
                        "strike": k,
                        "option_type": opt,
                        "open_interest": 100 + int(k),
                        "volume": 50 + int(k),
                        "bid": bid,
                        "ask": ask,
                        "delta": 0.5 if opt == "call" else -0.5,
                        "gamma": 0.05,
                        "implied_volatility": 0.25 + (k - underlying_price) / 1000,
                    }
                )

    columns = {key: [r[key] for r in rows] for key in rows[0]}
    return OptionsChainsData(**columns)


@pytest.fixture
def chain():
    return _build_chain()


@requires_pandas
class TestDataFrame:
    """Cover ``OptionsChainsProperties.dataframe`` cached property."""

    def test_dataframe_returns_pandas_dataframe(self, chain):
        from pandas import DataFrame

        df = chain.dataframe
        assert isinstance(df, DataFrame)

    def test_dataframe_row_count_matches_input(self, chain):
        # 2 expirations × 5 strikes × 2 option types
        assert len(chain.dataframe) == 2 * 5 * 2

    def test_dataframe_has_expected_columns(self, chain):
        df = chain.dataframe
        for col in ("strike", "option_type", "expiration", "bid", "ask"):
            assert col in df.columns

    def test_dataframe_is_cached(self, chain):
        # ``cached_property`` returns the same object on repeat access.
        assert chain.dataframe is chain.dataframe


@requires_pandas
class TestFilterData:
    """Cover ``OptionsChainsProperties.filter_data``."""

    def test_filter_by_expiration_index(self, chain):
        from pandas import DataFrame

        # ``date`` accepts either a date string, an integer DTE, or an index.
        filtered = chain.filter_data(date=0)
        assert isinstance(filtered, DataFrame)
        # Single expiration → 5 strikes × 2 option types.
        assert len(filtered) == 10

    def test_filter_by_option_type_calls(self, chain):
        filtered = chain.filter_data(option_type="call")
        assert (filtered["option_type"] == "call").all()

    def test_filter_by_option_type_puts(self, chain):
        filtered = chain.filter_data(option_type="put")
        assert (filtered["option_type"] == "put").all()


@requires_pandas
class TestStatAggregates:
    """Cover the ``_get_stat`` family — open interest / volume aggregations."""

    def test_total_oi_returns_dict_or_dataframe(self, chain):
        result = chain.total_oi
        # The implementation returns a dict keyed by ('Calls', 'Puts', 'Total').
        assert result is not None

    def test_total_volume_returns_dict_or_dataframe(self, chain):
        result = chain.total_volume
        assert result is not None


@requires_pandas
class TestStrategies:
    """Cover the headline single-leg & spread strategy builders."""

    def test_straddle_returns_dataframe(self, chain):
        from pandas import DataFrame

        result = chain.straddle()
        assert isinstance(result, DataFrame)
        assert not result.empty

    def test_strangle_returns_dataframe(self, chain):
        from pandas import DataFrame

        result = chain.strangle()
        assert isinstance(result, DataFrame)
        assert not result.empty

    def test_synthetic_long_returns_dataframe(self, chain):
        from pandas import DataFrame

        result = chain.synthetic_long()
        assert isinstance(result, DataFrame)
        assert not result.empty

    def test_synthetic_short_returns_dataframe(self, chain):
        from pandas import DataFrame

        result = chain.synthetic_short()
        assert isinstance(result, DataFrame)
        assert not result.empty

    def test_vertical_call_spread_returns_dataframe(self, chain):
        from pandas import DataFrame

        # Buy 95 call, sell 105 call on the nearest expiration.
        result = chain.vertical_call_spread(sold=105.0, bought=95.0)
        assert isinstance(result, DataFrame)
        assert not result.empty

    def test_vertical_put_spread_returns_dataframe(self, chain):
        from pandas import DataFrame

        # Buy 105 put, sell 95 put.
        result = chain.vertical_put_spread(sold=95.0, bought=105.0)
        assert isinstance(result, DataFrame)
        assert not result.empty


@requires_pandas
class TestSkew:
    """Cover ``OptionsChainsProperties.skew``."""

    def test_skew_returns_dataframe(self, chain):
        from pandas import DataFrame

        result = chain.skew()
        assert isinstance(result, DataFrame)
        assert not result.empty
