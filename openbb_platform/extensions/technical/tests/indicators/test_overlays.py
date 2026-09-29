"""Tests for openbb_technical.indicators.overlays."""

from __future__ import annotations

import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.indicators.overlays import (
    BbandsData,
    BbandsQueryParams,
    DemaData,
    DemaQueryParams,
    DonchianData,
    DonchianQueryParams,
    EmaData,
    EmaQueryParams,
    FramaData,
    FramaQueryParams,
    HmaData,
    HmaQueryParams,
    IchimokuData,
    IchimokuQueryParams,
    KamaData,
    KamaQueryParams,
    KcData,
    KcQueryParams,
    SmaData,
    SmaQueryParams,
    SupertrendData,
    SupertrendQueryParams,
    TemaData,
    TemaQueryParams,
    VwmaData,
    VwmaQueryParams,
    WmaData,
    WmaQueryParams,
    ZlmaData,
    ZlmaQueryParams,
    _nan_to_none,
    bbands,
    dema,
    donchian,
    ema,
    frama,
    hma,
    ichimoku,
    kama,
    kc,
    sma,
    supertrend,
    tema,
    vwma,
    wma,
    zlma,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Convert the standard OHLCV fixture into ``list[Data]``."""
    return df_to_basemodel(ohlcv_df.reset_index())


class TestSma:
    def test_default(self, long_records):
        result = sma(SmaQueryParams(data=long_records, length=20))
        assert result.results
        assert all(isinstance(r, SmaData) for r in result.results)
        assert result.results[0].sma is not None

    def test_offset(self, long_records):
        result = sma(SmaQueryParams(data=long_records, length=20, offset=1))
        assert result.results

    def test_alt_target(self, long_records):
        result = sma(SmaQueryParams(data=long_records, length=20, target="open"))
        assert result.results


class TestEma:
    def test_default(self, long_records):
        result = ema(EmaQueryParams(data=long_records, length=20))
        assert result.results
        assert all(isinstance(r, EmaData) for r in result.results)

    def test_offset(self, long_records):
        result = ema(EmaQueryParams(data=long_records, length=20, offset=1))
        assert result.results


class TestHma:
    def test_default(self, long_records):
        result = hma(HmaQueryParams(data=long_records, length=20))
        assert result.results
        assert all(isinstance(r, HmaData) for r in result.results)

    def test_offset(self, long_records):
        result = hma(HmaQueryParams(data=long_records, length=20, offset=1))
        assert result.results


class TestWma:
    def test_default(self, long_records):
        result = wma(WmaQueryParams(data=long_records, length=20))
        assert result.results
        assert all(isinstance(r, WmaData) for r in result.results)

    def test_offset(self, long_records):
        result = wma(WmaQueryParams(data=long_records, length=20, offset=1))
        assert result.results


class TestZlma:
    def test_default(self, long_records):
        result = zlma(ZlmaQueryParams(data=long_records, length=20))
        assert result.results
        assert all(isinstance(r, ZlmaData) for r in result.results)

    def test_offset(self, long_records):
        result = zlma(ZlmaQueryParams(data=long_records, length=20, offset=1))
        assert result.results


class TestTema:
    def test_default(self, long_records):
        result = tema(TemaQueryParams(data=long_records, length=10))
        assert result.results
        assert all(isinstance(r, TemaData) for r in result.results)

    def test_offset(self, long_records):
        result = tema(TemaQueryParams(data=long_records, length=10, offset=1))
        assert result.results


class TestDema:
    def test_default(self, long_records):
        result = dema(DemaQueryParams(data=long_records, length=10))
        assert result.results
        assert all(isinstance(r, DemaData) for r in result.results)

    def test_offset(self, long_records):
        result = dema(DemaQueryParams(data=long_records, length=10, offset=1))
        assert result.results


class TestKama:
    def test_default(self, long_records):
        result = kama(KamaQueryParams(data=long_records, length=10))
        assert result.results
        assert all(isinstance(r, KamaData) for r in result.results)

    def test_fast_slow(self, long_records):
        result = kama(KamaQueryParams(data=long_records, length=10, fast=3, slow=15))
        assert result.results

    def test_offset(self, long_records):
        result = kama(KamaQueryParams(data=long_records, length=10, offset=1))
        assert result.results


class TestFrama:
    def test_default(self, long_records):
        result = frama(FramaQueryParams(data=long_records, window=10))
        assert result.results
        assert all(isinstance(r, FramaData) for r in result.results)
        assert result.results[0].frama is not None

    def test_odd_window_rejected(self, long_records):
        with pytest.raises(ValueError, match="frama requires an even window"):
            FramaQueryParams(data=long_records, window=9)

    def test_larger_even_window(self, long_records):
        result = frama(FramaQueryParams(data=long_records, window=20))
        assert result.results


class TestVwma:
    def test_default(self, long_records):
        result = vwma(VwmaQueryParams(data=long_records, length=10))
        assert result.results
        assert all(isinstance(r, VwmaData) for r in result.results)

    def test_offset(self, long_records):
        result = vwma(VwmaQueryParams(data=long_records, length=10, offset=1))
        assert result.results


class TestBbands:
    def test_default(self, long_records):
        result = bbands(BbandsQueryParams(data=long_records, length=20))
        assert result.results
        assert all(isinstance(r, BbandsData) for r in result.results)
        first = result.results[0]
        assert first.lower is not None
        assert first.middle is not None
        assert first.upper is not None
        assert first.bandwidth is not None
        assert first.percent is not None

    @pytest.mark.parametrize("mamode", ["sma", "ema", "wma", "rma"])
    def test_each_mamode(self, long_records, mamode):
        result = bbands(BbandsQueryParams(data=long_records, length=20, mamode=mamode))
        assert result.results

    def test_std_offset(self, long_records):
        result = bbands(
            BbandsQueryParams(data=long_records, length=20, std=2.5, offset=1)
        )
        assert result.results

    def test_alt_target(self, long_records):
        result = bbands(BbandsQueryParams(data=long_records, length=20, target="open"))
        assert result.results


class TestDonchian:
    def test_default(self, long_records):
        result = donchian(DonchianQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, DonchianData) for r in result.results)
        first = result.results[0]
        assert first.lower is not None
        assert first.middle is not None
        assert first.upper is not None

    def test_asymmetric_lengths(self, long_records):
        result = donchian(
            DonchianQueryParams(
                data=long_records, lower_length=10, upper_length=30, offset=1
            )
        )
        assert result.results


class TestKc:
    def test_default(self, long_records):
        result = kc(KcQueryParams(data=long_records, length=20))
        assert result.results
        assert all(isinstance(r, KcData) for r in result.results)

    @pytest.mark.parametrize("mamode", ["ema", "sma"])
    def test_each_mamode(self, long_records, mamode):
        result = kc(KcQueryParams(data=long_records, length=20, mamode=mamode))
        assert result.results

    def test_scalar_offset(self, long_records):
        result = kc(KcQueryParams(data=long_records, length=20, scalar=2.5, offset=1))
        assert result.results


class TestIchimoku:
    def test_default(self, long_records):
        result = ichimoku(IchimokuQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, IchimokuData) for r in result.results)
        assert all(r.chikou_span is None for r in result.results)

    def test_lookahead_includes_chikou(self, long_records):
        result = ichimoku(IchimokuQueryParams(data=long_records, lookahead=True))
        assert any(r.chikou_span is not None for r in result.results)

    def test_alt_periods(self, long_records):
        result = ichimoku(
            IchimokuQueryParams(
                data=long_records, conversion=5, base=10, lagging=20, offset=5
            )
        )
        assert result.results


class TestSupertrend:
    def test_default(self, long_records):
        result = supertrend(SupertrendQueryParams(data=long_records, length=7))
        assert result.results
        assert all(isinstance(r, SupertrendData) for r in result.results)
        directions = {r.direction for r in result.results if r.direction is not None}
        assert directions.issubset({-1, 1})

    def test_multiplier(self, long_records):
        result = supertrend(
            SupertrendQueryParams(data=long_records, length=7, multiplier=2.0)
        )
        assert result.results

    def test_short_band_path(self, ohlcv_df):
        """Use a monotone-falling close to force the short-band branch."""
        import numpy as np
        import pandas as pd

        periods = 99
        base = np.arange(periods, 0, -1, dtype="float64")
        df = pd.DataFrame(
            {
                "open": base,
                "high": base + 0.5,
                "low": base - 0.5,
                "close": base,
                "volume": base * 100,
            },
            index=pd.date_range("2021-01-01", periods=periods, freq="D", name="date"),
        )
        records = df_to_basemodel(df.reset_index())
        result = supertrend(
            SupertrendQueryParams(data=records, length=7, multiplier=3.0)
        )
        assert any(r.direction == -1 for r in result.results)
        assert any(r.short_band is not None for r in result.results)


class TestNanHelper:
    def test_replaces_nan(self):
        out = _nan_to_none({"a": float("nan"), "b": 1.0, "c": "x"})
        assert out == {"a": None, "b": 1.0, "c": "x"}


class TestQueryParamModels:
    """Field-level coverage of QueryParams classes."""

    def test_sma_defaults(self, long_records):
        params = SmaQueryParams(data=long_records)
        assert params.length == 50
        assert params.target == "close"

    def test_ema_defaults(self, long_records):
        assert EmaQueryParams(data=long_records).length == 50

    def test_hma_defaults(self, long_records):
        assert HmaQueryParams(data=long_records).length == 50

    def test_wma_defaults(self, long_records):
        assert WmaQueryParams(data=long_records).length == 50

    def test_zlma_defaults(self, long_records):
        assert ZlmaQueryParams(data=long_records).length == 50

    def test_tema_defaults(self, long_records):
        assert TemaQueryParams(data=long_records).length == 10

    def test_dema_defaults(self, long_records):
        assert DemaQueryParams(data=long_records).length == 10

    def test_kama_defaults(self, long_records):
        params = KamaQueryParams(data=long_records)
        assert params.fast == 2
        assert params.slow == 30

    def test_frama_defaults(self, long_records):
        assert FramaQueryParams(data=long_records).window == 10

    def test_vwma_defaults(self, long_records):
        assert VwmaQueryParams(data=long_records).length == 10

    def test_bbands_defaults(self, long_records):
        params = BbandsQueryParams(data=long_records)
        assert params.length == 20
        assert params.std == 2.0
        assert params.mamode == "sma"

    def test_donchian_defaults(self, long_records):
        params = DonchianQueryParams(data=long_records)
        assert params.lower_length == 20
        assert params.upper_length == 20

    def test_kc_defaults(self, long_records):
        params = KcQueryParams(data=long_records)
        assert params.length == 20
        assert params.scalar == 2.0
        assert params.mamode == "ema"

    def test_ichimoku_defaults(self, long_records):
        params = IchimokuQueryParams(data=long_records)
        assert params.conversion == 9
        assert params.base == 26
        assert params.lagging == 52
        assert params.lookahead is False

    def test_supertrend_defaults(self, long_records):
        params = SupertrendQueryParams(data=long_records)
        assert params.length == 7
        assert params.multiplier == 3.0
