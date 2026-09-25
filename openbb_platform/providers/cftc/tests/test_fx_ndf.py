import asyncio
from datetime import date, timedelta

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.models.fx_forward_points import (
    CftcFxForwardPointsFetcher,
    CftcFxForwardPointsQueryParams,
)
from openbb_cftc.utils.fx import (
    _drop_ndf_spot_window,
    _ndf_spot,
    build_forward_points,
    build_forward_points_as_of,
    extract_fx_observations,
)

TRADE_DATE = date(2026, 7, 17)


def _ndf(
    days_out, rate, day=TRADE_DATE, notional=5_000_000.0, fisn="NA/Fwd NDF INR USD"
):
    return {
        "UPI FISN": fisn,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Dissemination Timestamp": f"{day.isoformat()}T10:00:00Z",
        "Expiration Date": (day + timedelta(days=days_out)).isoformat(),
        "Notional amount-Leg 1": f"{notional:,.0f}",
        "Notional currency-Leg 1": "USD",
        "Notional amount-Leg 2": f"{notional * rate:,.0f}",
        "Notional currency-Leg 2": "INR",
        "Settlement currency-Leg 1": "USD",
    }


def test_ndf_spot_extrapolates_to_settlement():
    observations = [
        {"days": 5, "rate": 96.0},
        {"days": 5, "rate": 96.2},
        {"days": 30, "rate": 97.0},
    ]

    assert _ndf_spot(observations) == pytest.approx(95.992)
    assert _ndf_spot([{"days": 5, "rate": 96.0}]) == pytest.approx(96.0)
    assert _ndf_spot([]) is None
    assert _ndf_spot([{"days": 900, "rate": 50.0}]) is None


def test_drop_ndf_spot_window_removes_near_dated_trades():
    observations = [{"days": 1}, {"days": 2}, {"days": 3}, {"days": 10}]

    assert [o["days"] for o in _drop_ndf_spot_window(observations, 2)] == [3, 10]


def test_ndf_rate_is_em_per_usd_with_a_usd_notional_floor():
    observations = extract_fx_observations(
        [_ndf(30, 96.5)], pair="USDINR", trade_date=TRADE_DATE
    )

    assert observations[0]["rate"] == pytest.approx(96.5)
    assert observations[0]["notional"] == pytest.approx(5_000_000.0)


def test_build_ndf_points_extrapolates_spot_to_settlement():
    records = [
        _ndf(5, 96.00),
        _ndf(5, 96.20),
        _ndf(30, 97.00),
        _ndf(30, 97.20),
        _ndf(90, 99.00),
        _ndf(90, 99.20),
    ]
    points = build_forward_points(records, pair="USDINR", trade_date=TRADE_DATE)
    by_tenor = {p["tenor"]: p for p in points}

    assert "SPOT" not in by_tenor
    assert points[0]["tenor"] == "1W"
    assert by_tenor["1W"]["spot_rate"] == pytest.approx(95.98)
    assert by_tenor["1W"]["forward_points"] == pytest.approx((96.10 - 95.98) * 10_000)
    assert by_tenor["1M"]["forward_rate"] == pytest.approx(97.10)
    assert by_tenor["1M"]["spot_rate"] == pytest.approx(95.98)
    assert by_tenor["1M"]["forward_points"] == pytest.approx((97.10 - 95.98) * 10_000)


def test_build_ndf_points_drops_a_stray_spot_window_print():
    records = [
        _ndf(1, 90.00),
        _ndf(5, 96.00),
        _ndf(5, 96.20),
        _ndf(30, 97.00),
        _ndf(30, 97.20),
    ]
    by_tenor = {
        p["tenor"]: p
        for p in build_forward_points(records, pair="USDINR", trade_date=TRADE_DATE)
    }

    assert "SPOT" not in by_tenor
    assert by_tenor["1W"]["spot_rate"] == pytest.approx(95.98)


def test_build_ndf_points_raises_when_only_spot_window_trades():
    records = [_ndf(1, 96.0), _ndf(2, 96.1)]

    with pytest.raises(OpenBBError, match="spot cannot be established"):
        build_forward_points(records, pair="USDINR", trade_date=TRADE_DATE)


def test_build_ndf_points_as_of_extrapolates_spot_to_settlement():
    records = [
        _ndf(5, 96.00),
        _ndf(5, 96.20),
        _ndf(30, 97.00),
        _ndf(30, 97.20),
    ]
    by_tenor = {
        p["tenor"]: p for p in build_forward_points_as_of(records, pair="USDINR")
    }

    assert "SPOT" not in by_tenor
    assert by_tenor["1W"]["spot_rate"] == pytest.approx(95.98)
    assert by_tenor["1M"]["forward_points"] == pytest.approx((97.10 - 95.98) * 10_000)


def test_build_ndf_points_as_of_raises_when_only_spot_window_trades():
    records = [_ndf(1, 96.0), _ndf(2, 96.1)]

    with pytest.raises(OpenBBError, match="spot cannot be established"):
        build_forward_points_as_of(records, pair="USDINR")


def test_fx_forward_points_fetcher_builds_an_ndf_curve(monkeypatch):
    records = [
        _ndf(5, 96.00),
        _ndf(5, 96.20),
        _ndf(30, 97.00),
        _ndf(30, 97.20),
        _ndf(90, 99.00),
        _ndf(90, 99.20),
    ]

    async def _slice(asset_class, report_date, use_cache=True):
        return records

    async def _rates(report_date, legs, use_cache=True):
        return [], report_date

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_rates_slice_for", _rates)

    query = CftcFxForwardPointsQueryParams(
        pair="USDINR", source="slice", date=TRADE_DATE
    )
    data = asyncio.run(CftcFxForwardPointsFetcher.aextract_data(query, None))
    result = CftcFxForwardPointsFetcher.transform_data(query, data)
    by_tenor = {r.tenor: r for r in result.result}

    assert result.metadata["pair"] == "USDINR"
    assert "SPOT" not in by_tenor
    assert by_tenor["1W"].spot_rate == pytest.approx(95.98)
    assert by_tenor["1M"].forward_points == pytest.approx((97.10 - 95.98) * 10_000)
    assert all(r.theoretical_points is None for r in result.result)
