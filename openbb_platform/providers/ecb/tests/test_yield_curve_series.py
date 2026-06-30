"""Unit tests for ``openbb_ecb.utils.yield_curve_series``."""

from openbb_ecb.utils.yield_curve_series import (
    MATURITIES,
    get_yield_curve_ids,
    get_yield_curve_key,
)


def test_maturities_constant():
    """There are 32 maturities (2 months + 30 years)."""
    assert len(MATURITIES) == 32
    assert MATURITIES[0] == "month_3"
    assert MATURITIES[-1] == "year_30"


def test_get_yield_curve_ids():
    """The legacy id map covers every maturity with float year values."""
    out = get_yield_curve_ids("aaa", "spot_rate")
    assert len(out["SERIES_IDS"]) == 32
    assert out["SERIES_IDS"]["year_10"].endswith("SR_10Y")
    assert out["MATURITIES"]["month_3"] == 0.25
    assert out["MATURITIES"]["year_30"] == 30


def test_get_yield_curve_key():
    """The data-API key builder OR-joins maturities and maps datatypes back."""
    key, datatype_to_maturity, years = get_yield_curve_key("all_ratings", "par_yield")
    assert key.startswith("B.U2.EUR.4F.G_N_C.SV_C_YM.PY_3M+")
    assert datatype_to_maturity["PY_10Y"] == "year_10"
    assert datatype_to_maturity["PY_6M"] == "month_6"
    assert years["month_6"] == 0.5
    assert years["year_1"] == 1.0


def test_get_yield_curve_key_ratings_and_types():
    """Rating and yield-type codes are applied to the key."""
    key_aaa, _, _ = get_yield_curve_key("aaa", "spot_rate")
    assert "G_N_A.SV_C_YM.SR_" in key_aaa
    key_fwd, _, _ = get_yield_curve_key("aaa", "instantaneous_forward")
    assert "SV_C_YM.IF_" in key_fwd
