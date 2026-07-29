import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.models.fx_forward_curve import (
    CftcFxForwardCurveData,
    CftcFxForwardCurveFetcher,
    CftcFxForwardCurveQueryParams,
)
from openbb_cftc.utils.fx import (
    _per_usd_curve,
    build_forward_points,
    build_fx_forward_curve,
    build_fx_forward_curve_as_of,
)

FIXTURE_DATE = date(2026, 7, 15)


def _fx(
    base, base_amt, usd_amt, expiration, effective="2026-07-15", fisn="NA/Fwd JPY USD"
):
    return {
        "UPI FISN": fisn,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Effective Date": effective,
        "Expiration Date": expiration,
        "Notional currency-Leg 1": base,
        "Notional amount-Leg 1": str(base_amt),
        "Notional currency-Leg 2": "USD",
        "Notional amount-Leg 2": str(usd_amt),
        "Dissemination Timestamp": "2026-07-15T10:00:00Z",
    }


def test_per_usd_curve_orientation():
    points = [
        {
            "tenor": "1M",
            "tenor_days": 21,
            "spot_rate": 2.0,
            "forward_rate": 4.0,
            "min_rate": 2.0,
            "max_rate": 8.0,
            "num_trades": 3,
            "total_notional": 1.0,
            "date": FIXTURE_DATE,
            "as_of_date": FIXTURE_DATE,
            "staleness_days": 0,
        }
    ]
    kept = _per_usd_curve(points, "USDJPY")[0]
    assert kept["rate"] == pytest.approx(4.0)
    assert (kept["min_rate"], kept["max_rate"]) == (2.0, 8.0)

    inverted = _per_usd_curve(points, "EURUSD")[0]
    assert inverted["rate"] == pytest.approx(0.25)
    assert inverted["spot"] == pytest.approx(0.5)
    assert inverted["min_rate"] == pytest.approx(1.0 / 8.0)
    assert inverted["max_rate"] == pytest.approx(1.0 / 2.0)


def test_build_fx_forward_curve_matches_forward_points(fx_records):
    points = {
        p["tenor"]: p["forward_rate"]
        for p in build_forward_points(fx_records, "USDJPY", FIXTURE_DATE)
    }
    curve = build_fx_forward_curve(fx_records, "USDJPY", FIXTURE_DATE)

    assert curve
    for node in curve:
        assert node["rate"] == pytest.approx(points[node["tenor"]])
        assert "index" not in node
        assert node["spot"] > 0


def test_build_fx_forward_curve_as_of(fx_records):
    records = [
        _fx("JPY", 163_000_000, 1_000_000, "2026-07-17"),
        _fx("JPY", 162_500_000, 1_000_000, "2026-08-14"),
        _fx("JPY", 162_500_000, 1_000_000, "2026-08-14"),
    ]
    curve = build_fx_forward_curve_as_of(records, "USDJPY")

    assert curve
    assert all(node["rate"] > 0 for node in curve)


def test_fx_forward_curve_transform_query():
    query = CftcFxForwardCurveFetcher.transform_query({"pair": "usdjpy"})

    assert isinstance(query, CftcFxForwardCurveQueryParams)
    assert query.pair == "USDJPY"


def test_fx_forward_curve_aextract_slice(monkeypatch, fx_records):

    async def _viable(asset_class, predicate, **kwargs):
        assert asset_class == "forex"
        return fx_records, "2026-07-15"

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_latest_viable_slice", _viable)
    records, report_date = asyncio.run(
        CftcFxForwardCurveFetcher.aextract_data(
            CftcFxForwardCurveQueryParams(pair="USDJPY", source="slice"), None
        )
    )

    assert records is fx_records
    assert report_date == "2026-07-15"


def test_fx_forward_curve_aextract_slice_with_date(monkeypatch, fx_records):

    async def _slice(asset_class, report_date, use_cache=True):
        return fx_records

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)
    records, report_date = asyncio.run(
        CftcFxForwardCurveFetcher.aextract_data(
            CftcFxForwardCurveQueryParams(
                pair="USDJPY", source="slice", date=FIXTURE_DATE
            ),
            None,
        )
    )

    assert report_date == "2026-07-15"


def test_fx_forward_curve_aextract_search(monkeypatch):
    seen: list = []

    async def _search(asset_class, **kwargs):
        seen.append(kwargs["upi_short_name"])
        return [{"x": 1}]

    monkeypatch.setattr("openbb_cftc.utils.search.search_trades", _search)
    records, report_date = asyncio.run(
        CftcFxForwardCurveFetcher.aextract_data(
            CftcFxForwardCurveQueryParams(pair="USDJPY", source="search"), None
        )
    )

    assert report_date is None
    assert seen == ["NA/Fwd JPY USD", "NA/Swaps JPY USD"]
    assert len(records) == 2


def test_fx_forward_curve_transform(fx_records):
    result = CftcFxForwardCurveFetcher.transform_data(
        CftcFxForwardCurveQueryParams(pair="USDJPY"), (fx_records, "2026-07-15")
    )

    assert all(isinstance(r, CftcFxForwardCurveData) for r in result.result)
    assert result.result[0].index == "SPOT"
    assert result.metadata["pair"] == "USDJPY"
    assert result.metadata["spot"] > 0


def test_fx_forward_curve_transform_search_path(monkeypatch):
    records = [
        _fx("JPY", 163_000_000, 1_000_000, "2026-07-17"),
        _fx("JPY", 162_500_000, 1_000_000, "2026-08-14"),
        _fx("JPY", 162_500_000, 1_000_000, "2026-08-14"),
    ]
    result = CftcFxForwardCurveFetcher.transform_data(
        CftcFxForwardCurveQueryParams(pair="USDJPY", source="search"), (records, None)
    )

    assert result.metadata["pair"] == "USDJPY"
    assert all(r.rate > 0 for r in result.result)


def test_fx_forward_curve_raises_without_trades():
    with pytest.raises(OpenBBError):
        build_fx_forward_curve([], "USDJPY", FIXTURE_DATE)
