from datetime import date, timedelta
from math import exp

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models.fx_forward_points import (
    CftcFxForwardPointsFetcher,
    CftcFxForwardPointsQueryParams,
)
from openbb_cftc.utils import fx_vol
from openbb_cftc.utils.constants import rate_curve_fisns

TRADE_DATE = date(2026, 7, 17)


@pytest.mark.parametrize(
    ("currency", "expected"),
    [
        ("USD", ["NA/Swap OIS USD", "NA/Swap Fxd Flt USD", "NA/Swap Fxd Flt USD USD"]),
        ("INR", ["NA/Swap OIS INR", "NA/Swap Fxd Flt INR", "NA/Swap Fxd Flt INR USD"]),
        ("CNY", ["NA/Swap Fxd Flt CNY", "NA/Swap Fxd Flt CNY USD"]),
        ("twd", ["NA/Swap Fxd Flt TWD", "NA/Swap Fxd Flt TWD USD"]),
        ("KRW", ["NA/Swap Fxd Flt KRW", "NA/Swap Fxd Flt KRW USD"]),
    ],
)
def test_rate_curve_fisns(currency, expected):
    assert rate_curve_fisns(currency) == expected


def _cny_irs(tenor_days, rate, notional=50_000_000.0):
    return {
        "UPI FISN": "NA/Swap Fxd Flt CNY",
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": "CNY",
        "Notional currency-Leg 2": "CNY",
        "Fixed rate-Leg 1": f"{rate}",
        "Effective Date": TRADE_DATE.isoformat(),
        "Expiration Date": (TRADE_DATE + timedelta(days=tenor_days)).isoformat(),
        "Notional amount-Leg 1": f"{notional:.0f}",
        "Fixed rate day count convention-leg 1": "A005",
        "Cleared": "Y",
    }


def test_rate_discount_factor_builds_a_fixed_float_curve():
    records = [_cny_irs(365, 0.014), _cny_irs(730, 0.0142), _cny_irs(1826, 0.0146)]
    df = fx_vol.rate_discount_factor(records, "CNY", TRADE_DATE, min_trades=1)

    assert df(1.0) < 1.0
    assert df(2.0) < df(1.0)


def test_rate_discount_factor_raises_without_a_curve():
    with pytest.raises(EmptyDataError, match="No rate curve"):
        fx_vol.rate_discount_factor([], "KRW", TRADE_DATE, min_trades=1)


def _cny_ndf(days_out, rate, notional=5_000_000.0):
    return {
        "UPI FISN": "NA/Fwd NDF CNY USD",
        "UPI Underlier Name": "CNY USD",
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Dissemination Timestamp": f"{TRADE_DATE.isoformat()}T10:00:00Z",
        "Expiration Date": (TRADE_DATE + timedelta(days=days_out)).isoformat(),
        "Notional amount-Leg 1": f"{notional:,.0f}",
        "Notional currency-Leg 1": "USD",
        "Notional amount-Leg 2": f"{notional * rate:,.0f}",
        "Notional currency-Leg 2": "CNY",
        "Settlement currency-Leg 1": "USD",
    }


def test_ndf_pair_gets_cip_points_and_basis(monkeypatch):

    def _flat_df(records, currency, trade_date, min_trades, forward_aware=False):
        rate = 0.04 if currency == "USD" else 0.015
        return lambda years: exp(-rate * years)

    monkeypatch.setattr("openbb_cftc.utils.fx_vol.rate_discount_factor", _flat_df)

    forex = [
        _cny_ndf(5, 6.80),
        _cny_ndf(5, 6.81),
        _cny_ndf(30, 6.78),
        _cny_ndf(30, 6.79),
        _cny_ndf(90, 6.74),
        _cny_ndf(90, 6.75),
    ]
    query = CftcFxForwardPointsQueryParams(
        pair="USDCNY", source="slice", date=TRADE_DATE
    )
    result = CftcFxForwardPointsFetcher.transform_data(
        query, (forex, [], TRADE_DATE.isoformat(), TRADE_DATE.isoformat())
    )
    by_tenor = {r.tenor: r for r in result.result}

    assert by_tenor["1M"].theoretical_points is not None
    assert by_tenor["1M"].theoretical_points < 0
    assert by_tenor["1M"].basis_points == pytest.approx(
        by_tenor["1M"].forward_points - by_tenor["1M"].theoretical_points
    )
