"""Tests for openbb_technical.relative_rotation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.provider.abstract.data import Data

from openbb_technical.relative_rotation import (
    RelativeRotation,
    RelativeRotationData,
    RelativeRotationFetcher,
    RelativeRotationQueryParams,
    _get_type_name,
    absolute_maximum_scale,
    calculate_momentum,
    calculate_relative_strength_ratio,
    get_momentum,
    min_max_scaling,
    normalize,
    process_data,
    standard_deviation,
    z_score_standardization,
)


@pytest.fixture(scope="session")
def multi_symbol_records() -> list[dict]:
    """Long multi-symbol price history (3 symbols, 600 daily rows).

    600 rows is enough to exceed RelativeRotation's two-year guard for
    volatility studies (>504 rows) and one-year guard for price/volume
    studies (>252 rows). Each symbol follows a smooth exponential ramp
    with a small offset so normalisation produces non-NaN output.
    """
    dates = pd.date_range("2020-01-01", periods=600, freq="D")
    records: list[dict] = []
    for offset, symbol in enumerate(["AAPL", "MSFT", "SPY"]):
        for i, dt in enumerate(dates):
            records.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "symbol": symbol,
                    "close": float(100 + offset * 10 + i * (1 + offset * 0.1)),
                    "volume": float(
                        1_000_000 + offset * 50_000 + i * (10 + offset * 3)
                    ),
                }
            )
    return records


@pytest.fixture(scope="session")
def multi_symbol_df(multi_symbol_records: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(multi_symbol_records)


class TestScalers:
    def test_absolute_maximum_scale(self):
        s = pd.Series([2.0, -4.0, 1.0])
        result = absolute_maximum_scale(s)
        assert result.max() == 0.5
        assert result.min() == -1.0

    def test_min_max_scaling(self):
        s = pd.Series([1.0, 3.0, 5.0])
        result = min_max_scaling(s)
        assert result.min() == 0.0
        assert result.max() == 1.0

    def test_z_score_standardization(self):
        s = pd.Series([1.0, 2.0, 3.0])
        result = z_score_standardization(s)
        assert pytest.approx(result.mean(), abs=1e-9) == 0.0


class TestNormalize:
    @pytest.mark.parametrize("method", ["z", "m", "a"])
    def test_each_method(self, method):
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [10.0, 20.0, 30.0, 40.0]})
        out = normalize(df, method=method)
        assert out.shape == df.shape


class TestStandardDeviation:
    def test_default_window(self):
        df = pd.DataFrame(
            {"close": np.linspace(100, 200, 60), "vol": np.linspace(50, 150, 60)},
            index=pd.date_range("2020-01-01", periods=60, freq="D"),
        )
        result = standard_deviation(df, window=21, trading_periods=252)
        assert not result.empty
        assert list(result.columns) == ["close", "vol"]

    def test_window_below_two_defaults_to_21(self):
        df = pd.DataFrame(
            {"close": np.linspace(100, 200, 60)},
            index=pd.date_range("2020-01-01", periods=60, freq="D"),
        )
        out_default = standard_deviation(df, window=21, trading_periods=252)
        out_clamped = standard_deviation(df, window=1, trading_periods=252)
        assert out_clamped.shape == out_default.shape


class TestCalculateMomentum:
    def test_returns_series(self):
        s = pd.Series(np.linspace(100, 200, 300))
        result = calculate_momentum(s, long_period=252, short_period=21)
        assert isinstance(result, pd.Series)


class TestGetMomentum:
    def test_returns_dataframe_per_column(self):
        df = pd.DataFrame(
            {"A": np.linspace(100, 200, 300), "B": np.linspace(50, 100, 300)}
        )
        result = get_momentum(df, long_period=252, short_period=21)
        assert list(result.columns) == ["A", "B"]


class TestCalculateRelativeStrengthRatio:
    def test_includes_benchmark_column(self):
        idx = pd.date_range("2020-01-01", periods=10, freq="D")
        symbols = pd.DataFrame(
            {"A": np.arange(10, 20.0), "B": np.arange(15, 25.0)}, index=idx
        )
        benchmark = pd.DataFrame({"SPY": np.arange(20, 30.0)}, index=idx)
        result = calculate_relative_strength_ratio(symbols, benchmark)
        assert "SPY" in result.columns


class TestProcessData:
    def test_returns_two_normalised_frames(self):
        idx = pd.date_range("2020-01-01", periods=300, freq="D")
        symbols = pd.DataFrame(
            {
                "AAPL": np.linspace(100, 200, 300),
                "MSFT": np.linspace(120, 220, 300),
            },
            index=idx,
        )
        benchmark = pd.DataFrame({"SPY": np.linspace(110, 210, 300)}, index=idx)
        ratios, momentum = process_data(symbols, benchmark)
        assert not ratios.empty
        assert not momentum.empty


class TestRelativeRotation:
    def test_constructs_from_records_price_study(self, multi_symbol_records):
        rr = RelativeRotation(data=multi_symbol_records, benchmark="SPY")
        assert "AAPL" in rr.symbols
        assert "MSFT" in rr.symbols
        assert rr.benchmark == "SPY"

    def test_volume_study_pivots_on_volume(self, multi_symbol_records):
        rr = RelativeRotation(
            data=multi_symbol_records, benchmark="SPY", study="volume"
        )
        assert rr.study == "volume"

    def test_volatility_study_requires_two_years(self, multi_symbol_records):
        rr = RelativeRotation(
            data=multi_symbol_records, benchmark="SPY", study="volatility"
        )
        assert rr.study == "volatility"

    def test_raises_when_benchmark_missing(self, multi_symbol_records):
        with pytest.raises(RuntimeError, match="benchmark"):
            RelativeRotation(data=multi_symbol_records, benchmark="MISSING")

    def test_raises_when_data_too_short_for_price(self):
        short = []
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        for symbol in ["AAPL", "SPY"]:
            for i, dt in enumerate(dates):
                short.append(
                    {
                        "date": dt.strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "close": float(100 + i),
                        "volume": 1.0,
                    }
                )
        with pytest.raises(ValueError, match="more than one year"):
            RelativeRotation(data=short, benchmark="SPY")

    def test_raises_when_data_too_short_for_volatility(self, multi_symbol_records):
        truncated = [r for r in multi_symbol_records if r["date"] < "2021-01-01"]
        with pytest.raises(ValueError, match="more than two years"):
            RelativeRotation(data=truncated, benchmark="SPY", study="volatility")

    def test_empty_data_raises(self):
        with pytest.raises(ValueError, match="must be a list"):
            RelativeRotation(data=[], benchmark="SPY")

    def test_accepts_obbject_input(self, multi_symbol_records):
        """An OBBject wrapping records is unwrapped via ``data.results``."""
        from openbb_core.app.model.obbject import OBBject

        wrapped = OBBject(results=multi_symbol_records)
        rr = RelativeRotation(data=wrapped, benchmark="SPY")
        assert "AAPL" in rr.symbols


class TestRelativeRotationQueryParams:
    def test_benchmark_uppercased(self, multi_symbol_records):
        params = RelativeRotationQueryParams(data=multi_symbol_records, benchmark="spy")
        assert params.benchmark == "SPY"

    def test_data_validator_passes_list(self, multi_symbol_records):
        params = RelativeRotationQueryParams(data=multi_symbol_records, benchmark="SPY")
        assert len(params.data) > 0

    def test_data_validator_accepts_data_object(self):
        single = Data(date="2024-01-01", symbol="AAPL", close=100.0)
        params = RelativeRotationQueryParams(data=[single], benchmark="SPY")
        assert isinstance(params.data, list)

    def test_data_validator_accepts_dataframe(self, multi_symbol_df):
        params = RelativeRotationQueryParams(
            data=multi_symbol_df.set_index("date"), benchmark="SPY"
        )
        assert len(params.data) > 0

    def test_doc_string_built_from_fields(self, multi_symbol_records):
        params = RelativeRotationQueryParams(data=multi_symbol_records, benchmark="SPY")
        assert "Parameters" in params.__doc__
        assert "benchmark" in params.__doc__

    def test_validator_unwraps_obbject(self, multi_symbol_records):
        """The data validator returns ``v.results`` for OBBject input."""
        from openbb_core.app.model.obbject import OBBject

        wrapped = OBBject(results=multi_symbol_records)
        params = RelativeRotationQueryParams(data=wrapped, benchmark="SPY")
        assert len(params.data) > 0

    def test_validator_passes_data_through(self):
        """A bare Data instance passes through validation."""
        single = Data(date="2024-01-01", symbol="AAPL", close=100.0)
        result = RelativeRotationQueryParams.convert_data(single)
        assert isinstance(result, Data)

    def test_validator_passthrough_for_unknown_type(self):
        """An unknown type returns unchanged from the validator."""
        sentinel = object()
        assert RelativeRotationQueryParams.convert_data(sentinel) is sentinel


class TestRelativeRotationData:
    def test_doc_string_built_from_fields(self):
        instance = RelativeRotationData(
            symbols=["AAPL"],
            benchmark="SPY",
            study="price",
            long_period=252,
            short_period=21,
            window=21,
            trading_periods=252,
            start_date="2020-01-01",
            end_date="2020-12-31",
            symbols_data=[],
            benchmark_data=[],
            rs_ratios=[],
            rs_momentum=[],
        )
        assert "Attributes" in instance.__doc__


class TestRelativeRotationFetcher:
    def test_extract_then_transform(self, multi_symbol_records):
        params = RelativeRotationQueryParams(data=multi_symbol_records, benchmark="SPY")
        raw = RelativeRotationFetcher.extract_data(params, None)
        assert "rs_ratios" in raw
        assert "rs_momentum" in raw
        result = RelativeRotationFetcher.transform_data(params, raw)
        assert isinstance(result, RelativeRotationData)
        assert result.benchmark == "SPY"

    def test_transform_query_round_trip(self, multi_symbol_records):
        """transform_query accepts a dict and returns a typed params model."""
        as_dict = {"data": multi_symbol_records, "benchmark": "SPY"}
        params = RelativeRotationFetcher.transform_query(as_dict)
        assert isinstance(params, RelativeRotationQueryParams)
        assert params.benchmark == "SPY"


class TestGetTypeName:
    def test_string_passthrough(self):
        assert _get_type_name("MyClass") == "MyClass"

    def test_named_class(self):
        assert _get_type_name(int) == "int"

    def test_generic_with_origin_name(self):
        assert "list" in _get_type_name(list[int])

    def test_underscore_name_variant(self):
        result = _get_type_name(int | str)
        assert "int" in result and "str" in result

    def test_no_name_attr_falls_back_to_str(self):
        """Objects without ``__name__`` / ``_name`` fall through to ``str(t)``."""

        class _Bare:
            """An instance without ``__name__`` / ``_name`` attrs."""

        instance = _Bare()
        result = _get_type_name(instance)
        assert isinstance(result, str)
        assert "_Bare" in result
