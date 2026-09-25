import asyncio
from datetime import date, timedelta

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.models.fx_forward_points import (
    CftcFxForwardPointsData,
    CftcFxForwardPointsFetcher,
    CftcFxForwardPointsQueryParams,
)
from openbb_cftc.models.fx_implied_vol import (
    CftcFxImpliedVolData,
    CftcFxImpliedVolFetcher,
    CftcFxImpliedVolQueryParams,
)
from openbb_cftc.utils.fx_theory import garman_kohlhagen

AS_OF = date(2026, 7, 15)
SPOT = 1.10


def _forward(effective_days, quote_per_base):
    return {
        "UPI FISN": "NA/Fwd EUR USD",
        "Action type": "NEWT",
        "Effective Date": (AS_OF + timedelta(days=effective_days)).isoformat(),
        "Notional amount-Leg 1": "10,000,000",
        "Notional currency-Leg 1": "EUR",
        "Notional amount-Leg 2": f"{10_000_000 * quote_per_base}",
        "Notional currency-Leg 2": "USD",
    }


def _option(strike, tenor_days, vol, is_call):
    per_unit = garman_kohlhagen(
        SPOT, strike, tenor_days / 365.0, 0.04, 0.02, vol, is_call
    )
    return {
        "UPI FISN": f"NA/O Van {'Call' if is_call else 'Put'} EUR USD",
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Execution Timestamp": f"{AS_OF.isoformat()}T10:00:00Z",
        "Strike Price": f"{strike}",
        "Strike price currency/currency pair": "EUR/USD",
        "Call currency": "EUR" if is_call else "USD",
        "Call amount": f"{10_000_000 if is_call else 10_000_000 * strike}",
        "Put currency": "USD" if is_call else "EUR",
        "Put amount": f"{10_000_000 * strike if is_call else 10_000_000}",
        "Option Premium Amount": f"{per_unit * 10_000_000}",
        "Option Premium Currency": "USD",
        "Expiration Date": (AS_OF + timedelta(days=tenor_days)).isoformat(),
        "Notional amount-Leg 1": "10,000,000",
        "Notional currency-Leg 1": "EUR",
        "Notional amount-Leg 2": f"{10_000_000 * SPOT}",
        "Notional currency-Leg 2": "USD",
    }


def _forex_dataset():
    records = [_forward(1, 1.10), _forward(2, 1.101)]
    strikes = [1.03, 1.06, 1.09, 1.105, 1.12, 1.15, 1.18]

    for tenor in (90, 182):
        for strike in strikes:
            records.append(_option(strike, tenor, 0.10, True))
            records.append(_option(strike, tenor, 0.10, False))

    return records


def test_fx_implied_vol_surface(slice_records):
    query = CftcFxImpliedVolQueryParams(pair="EURUSD", min_trades=5)
    result = CftcFxImpliedVolFetcher.transform_data(
        query, (_forex_dataset(), slice_records, AS_OF.isoformat(), AS_OF.isoformat())
    )

    assert result.metadata["spot"] == pytest.approx(1.1005, abs=1e-3)
    assert result.metadata["basis"] == "empirical"
    assert all(isinstance(r, CftcFxImpliedVolData) for r in result.result)
    assert all(1.0 < r.strike < 1.25 for r in result.result)

    populated = [
        v for r in result.result for v in (r.vol_3m, r.vol_6m) if v is not None
    ]
    assert len(populated) > 2
    assert all(v == pytest.approx(10.0, abs=1.0) for v in populated)
    dumped = [r.model_dump(exclude_unset=True) for r in result.result]
    assert all("vol_1w" not in d for d in dumped)
    assert any("vol_3m" in d for d in dumped)


def test_fx_implied_vol_theoretical_basis(slice_records):
    query = CftcFxImpliedVolQueryParams(
        pair="EURUSD", basis="theoretical", min_trades=5
    )
    result = CftcFxImpliedVolFetcher.transform_data(
        query, (_forex_dataset(), slice_records, AS_OF.isoformat(), AS_OF.isoformat())
    )

    assert result.metadata["basis"] == "theoretical"
    assert result.metadata["sabr_fits"]
    spot_row = next(r for r in result.result if r.strike_offset == 0.0)
    assert spot_row.strike == pytest.approx(result.metadata["spot"], abs=1e-4)
    assert spot_row.vol_3m == pytest.approx(10.0, abs=1.5)
    strikes = [r.strike for r in result.result]
    assert min(strikes) < result.metadata["spot"] < max(strikes)
    assert spot_row.num_options > 0


def test_fx_implied_vol_theoretical_raises_when_unfittable(slice_records):
    one_sided = [
        o
        for o in _forex_dataset()
        if not o["UPI FISN"].startswith("NA/O") or float(o["Strike Price"]) < 1.10
    ]

    with pytest.raises(OpenBBError, match="theoretical"):
        CftcFxImpliedVolFetcher.transform_data(
            CftcFxImpliedVolQueryParams(
                pair="EURUSD", basis="theoretical", min_trades=5
            ),
            (one_sided, slice_records, AS_OF.isoformat(), AS_OF.isoformat()),
        )


def test_fx_implied_vol_raises_without_spot(slice_records):
    options = [o for o in _forex_dataset() if o["UPI FISN"].startswith("NA/O")]

    with pytest.raises(OpenBBError, match="spot"):
        CftcFxImpliedVolFetcher.transform_data(
            CftcFxImpliedVolQueryParams(pair="EURUSD"),
            (options, slice_records, AS_OF.isoformat(), AS_OF.isoformat()),
        )


def test_fx_implied_vol_raises_without_options(slice_records):
    spot_only = [_forward(1, 1.10), _forward(2, 1.101)]

    with pytest.raises(OpenBBError, match="volatility"):
        CftcFxImpliedVolFetcher.transform_data(
            CftcFxImpliedVolQueryParams(pair="EURUSD"),
            (spot_only, slice_records, AS_OF.isoformat(), AS_OF.isoformat()),
        )


def test_fx_implied_vol_query_accepts_lower_case():
    assert CftcFxImpliedVolQueryParams(pair="usdjpy").pair == "USDJPY"


def test_fx_implied_vol_aextract(monkeypatch, slice_records):

    async def _dates(asset_class):
        return ["2026-07-13", "2026-07-14", "2026-07-15"]

    async def _slice(asset_class, report_date, use_cache=True):
        return _forex_dataset() if asset_class == "forex" else slice_records

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)

    _, rates, report_date, rates_date = asyncio.run(
        CftcFxImpliedVolFetcher.aextract_data(
            CftcFxImpliedVolQueryParams(pair="EURUSD"), None
        )
    )
    assert report_date == "2026-07-15"
    assert rates_date == "2026-07-15"
    assert rates is slice_records

    _, _, hist_date, hist_rates_date = asyncio.run(
        CftcFxImpliedVolFetcher.aextract_data(
            CftcFxImpliedVolQueryParams(pair="EURUSD", date=date(2026, 7, 14)), None
        )
    )
    assert hist_date == "2026-07-14"
    assert hist_rates_date == "2026-07-14"


def test_fx_implied_vol_walks_back_to_a_day_with_spot(monkeypatch, slice_records):
    options_only = [
        _option(strike, tenor, 0.10, is_call)
        for tenor in (90, 182)
        for strike in (1.06, 1.10, 1.14)
        for is_call in (True, False)
    ]

    async def _dates(asset_class):
        return ["2026-07-15", "2026-07-18", "2026-07-19"]

    async def _slice(asset_class, report_date, use_cache=True):
        if asset_class == "rates":
            return slice_records
        if report_date in ("2026-07-18", "2026-07-19"):
            return options_only
        return _forex_dataset()

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)

    _, _, report_date, _ = asyncio.run(
        CftcFxImpliedVolFetcher.aextract_data(
            CftcFxImpliedVolQueryParams(pair="EURUSD"), None
        )
    )
    assert report_date == "2026-07-15"


def test_fx_forward_points_theoretical(fx_records, slice_records):
    query = CftcFxForwardPointsQueryParams(pair="EURUSD", source="slice")
    result = CftcFxForwardPointsFetcher.transform_data(
        query, (fx_records, slice_records, AS_OF.isoformat(), AS_OF.isoformat())
    )

    assert all(isinstance(r, CftcFxForwardPointsData) for r in result.result)
    tenor = next(r for r in result.result if r.theoretical_points is not None)
    assert tenor.quotation in ("premium", "discount")
    assert tenor.basis_points == pytest.approx(
        tenor.forward_points - tenor.theoretical_points, abs=1e-9
    )
    assert tenor.carry == ("earn" if tenor.forward_points < 0 else "pay")
    assert (tenor.quotation == "premium") == (tenor.forward_points > 0)


def test_fx_forward_points_no_theoretical_without_two_ois_legs(
    fx_records, slice_records
):
    query = CftcFxForwardPointsQueryParams(pair="AUDUSD", source="slice")
    result = CftcFxForwardPointsFetcher.transform_data(
        query, (fx_records, slice_records, AS_OF.isoformat(), AS_OF.isoformat())
    )

    assert all(r.theoretical_points is None for r in result.result)
    priced = [r for r in result.result if r.forward_points]
    assert priced
    assert all(r.quotation in ("premium", "discount") for r in priced)
    assert all(r.carry in ("earn", "pay") for r in priced)


def test_fx_forward_points_tolerates_an_unbuildable_ois_curve(fx_records):
    query = CftcFxForwardPointsQueryParams(pair="EURUSD", source="slice")
    result = CftcFxForwardPointsFetcher.transform_data(
        query, (fx_records, [], AS_OF.isoformat(), AS_OF.isoformat())
    )

    assert all(r.theoretical_points is None for r in result.result)
    assert "theoretical_points" not in result.result[0].model_dump(exclude_unset=True)
    priced = [r for r in result.result if r.forward_points]
    assert priced and all(r.carry in ("earn", "pay") for r in priced)
