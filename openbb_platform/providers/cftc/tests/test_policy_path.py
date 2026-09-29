import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models.ois_policy_path import (
    CftcOisPolicyPathData,
    CftcOisPolicyPathFetcher,
    CftcOisPolicyPathQueryParams,
)
from openbb_cftc.utils.policy import build_policy_path, extract_forward_observations

FISN = "NA/Swap OIS USD"
REF = date(2026, 7, 17)


def _fwd(
    rate,
    effective,
    expiration,
    disseminated="2026-07-17",
    currency="USD",
    fisn=FISN,
    **extra,
):
    record = {
        "UPI FISN": fisn,
        "Action type": "NEWT",
        "Event type": "TRAD",
        "Notional currency-Leg 1": currency,
        "Fixed rate-Leg 1": str(rate),
        "Notional amount-Leg 1": "1,000,000",
        "Effective Date": effective,
        "Expiration Date": expiration,
        "Dissemination Timestamp": f"{disseminated}T10:00:00Z",
    }
    record.update(extra)
    return record


def test_extract_forward_observations_keeps_only_forward_starting():
    records = [
        _fwd(0.03, "2026-09-01", "2026-10-16"),
        _fwd(0.03, "2026-07-18", "2026-09-01"),
        _fwd(0.03, "2026-07-10", "2026-08-24"),
        _fwd(0.03, "2026-09-01", "2026-10-16", fisn="NA/Swap OIS EUR"),
        _fwd(0.03, "2026-09-01", "2026-10-16", currency="EUR"),
        _fwd(0.03, "2026-09-01", "2066-09-01"),
        {**_fwd(0.03, "2026-09-01", "2026-10-16"), "Fixed rate-Leg 1": ""},
    ]
    observations = extract_forward_observations(records, FISN, "USD", REF)

    assert len(observations) == 1
    assert observations[0]["forward_days"] == 46


def test_extract_forward_observations_drops_non_vanilla():
    records = [
        _fwd(0.03, "2026-09-01", "2026-10-16"),
        _fwd(0.03, "2026-09-01", "2026-10-16", **{"Package indicator": "TRUE"}),
        _fwd(0.03, "2026-09-01", "2026-10-16", **{"Other payment amount": "5000"}),
        _fwd(0.03, "2026-09-01", "2026-10-16", **{"Spread-Leg 1": "0.001"}),
    ]
    observations = extract_forward_observations(records, FISN, "USD", REF)

    assert len(observations) == 1


def test_build_policy_path_single_period_strip():
    records = [
        _fwd(0.036, "2026-08-20", "2026-10-08"),
        _fwd(0.037, "2026-08-20", "2026-10-08"),
        _fwd(0.038, "2026-08-20", "2026-10-08"),
        _fwd(0.040, "2026-10-08", "2026-11-26"),
        _fwd(0.041, "2026-10-08", "2026-11-26"),
        _fwd(0.042, "2026-10-08", "2026-11-26"),
    ]
    path = build_policy_path(records, FISN, "USD", REF)

    assert [node["start_date"] for node in path] == [
        date(2026, 8, 20),
        date(2026, 10, 8),
    ]
    assert path[0]["rate"] == pytest.approx(0.037)
    assert path[0]["num_trades"] == 3
    assert path[1]["rate"] == pytest.approx(0.041)


def test_build_policy_path_excludes_long_tenor():
    records = [
        _fwd(0.036, "2026-08-20", "2026-10-08"),
        _fwd(0.037, "2026-08-20", "2026-10-08"),
        _fwd(0.038, "2026-08-20", "2026-10-08"),
        _fwd(0.030, "2026-08-20", "2028-08-20"),
        _fwd(0.031, "2026-08-20", "2028-08-20"),
        _fwd(0.032, "2026-08-20", "2028-08-20"),
    ]
    path = build_policy_path(records, FISN, "USD", REF)

    assert len(path) == 1
    assert path[0]["tenor_days"] == 49


def test_build_policy_path_min_trades_drops_thin_start():
    records = [
        _fwd(0.036, "2026-08-20", "2026-10-08"),
        _fwd(0.037, "2026-08-20", "2026-10-08"),
        _fwd(0.038, "2026-08-20", "2026-10-08"),
        _fwd(0.050, "2026-10-08", "2026-11-26"),
    ]
    path = build_policy_path(records, FISN, "USD", REF)

    assert [node["start_date"] for node in path] == [date(2026, 8, 20)]


def test_build_policy_path_percentile_trims_node_outlier():
    records = [
        _fwd(r, "2026-08-20", "2026-10-08")
        for r in (0.036, 0.037, 0.037, 0.038, 0.038, -5.0)
    ]
    path = build_policy_path(records, FISN, "USD", REF, min_trades=3)

    assert path[0]["min_rate"] > 0.0
    assert path[0]["rate"] == pytest.approx(0.037, abs=1e-3)


def test_build_policy_path_raises_without_forward_prints():
    records = [_fwd(0.03, "2026-07-18", "2026-09-01")]

    with pytest.raises(EmptyDataError, match="single-period"):
        build_policy_path(records, FISN, "USD", REF)


def test_build_policy_path_raises_when_min_trades_unmet():
    records = [
        _fwd(0.036, "2026-08-20", "2026-10-08"),
        _fwd(0.037, "2026-08-20", "2026-10-08"),
    ]

    with pytest.raises(EmptyDataError, match="min_trades"):
        build_policy_path(records, FISN, "USD", REF, min_trades=3)


def test_observed_forward_grid_smooths_traded_forwards():
    from openbb_cftc.utils.policy import observed_forward_grid

    records = [
        _fwd(0.041, "2027-01-20", "2028-01-20"),
        _fwd(0.041, "2027-01-20", "2028-01-20"),
        _fwd(0.041, "2027-01-20", "2028-01-20"),
        _fwd(0.043, "2027-07-20", "2028-07-20"),
        _fwd(0.043, "2027-07-20", "2028-07-20"),
        _fwd(0.043, "2027-07-20", "2028-07-20"),
    ]
    grid = observed_forward_grid(
        records,
        FISN,
        "USD",
        REF,
        forward_tenor_days=365,
        step_years=0.25,
        count=None,
        min_trades=3,
        spot_rate=0.040,
    )

    assert grid[0]["tenor_years"] == 0.0
    assert grid[0]["forward_rate"] == pytest.approx(0.040)
    assert all(point["forward_rate"] is not None for point in grid)
    assert grid[-1]["forward_rate"] > grid[0]["forward_rate"]


def test_observed_forward_grid_empty_without_the_tenor():
    from openbb_cftc.utils.policy import observed_forward_grid

    records = [_fwd(0.04, "2027-01-20", "2027-02-20")]

    assert (
        observed_forward_grid(
            records,
            FISN,
            "USD",
            REF,
            forward_tenor_days=365,
            step_years=0.25,
            count=None,
            min_trades=1,
            spot_rate=0.04,
        )
        == []
    )


def test_observed_forward_grid_excludes_a_meeting_dated_tenor_from_1m():
    from openbb_cftc.utils.policy import observed_forward_grid

    records = [_fwd(0.03, "2026-08-16", "2026-10-04")]

    assert (
        observed_forward_grid(
            records,
            FISN,
            "USD",
            REF,
            forward_tenor_days=30,
            step_years=0.25,
            count=None,
            min_trades=1,
            spot_rate=0.04,
        )
        == []
    )


def test_observed_forward_grid_reports_the_nearest_buckets_trade_count():
    from openbb_cftc.utils.policy import observed_forward_grid

    records = [
        _fwd(0.041, "2026-10-15", "2026-11-14"),
        _fwd(0.043, "2027-08-16", "2027-09-15"),
        _fwd(0.043, "2027-08-16", "2027-09-15"),
    ]
    grid = observed_forward_grid(
        records,
        FISN,
        "USD",
        REF,
        forward_tenor_days=30,
        step_years=1.0,
        count=None,
        min_trades=1,
        spot_rate=0.038,
    )

    trades = {round(point["tenor_years"], 2): point["num_trades"] for point in grid}
    assert trades[0.0] == 1
    assert trades[1.0] == 2


def test_ois_policy_path_transform_query():
    query = CftcOisPolicyPathFetcher.transform_query({"currency": "eur"})

    assert isinstance(query, CftcOisPolicyPathQueryParams)
    assert query.currency == "EUR"


def test_ois_policy_path_aextract_combines_slices(monkeypatch):

    async def _dates(asset_class):
        return ["2026-07-14", "2026-07-15", "2026-07-16", "2026-07-17"]

    async def _slice(asset_class, report_date, use_cache=True):
        return [
            {"UPI FISN": FISN, "Fixed rate-Leg 1": "0.04"},
            {"UPI FISN": "NA/Swap OIS EUR", "Fixed rate-Leg 1": "0.02"},
        ]

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)

    records, reference = asyncio.run(
        CftcOisPolicyPathFetcher.aextract_data(
            CftcOisPolicyPathQueryParams(
                currency="USD", lookback_days=3, date=date(2026, 7, 16)
            ),
            None,
        )
    )

    assert reference == "2026-07-16"
    assert all(r["UPI FISN"] == FISN for r in records)
    assert {r["Dissemination Timestamp"] for r in records} == {
        "2026-07-14T00:00:00Z",
        "2026-07-15T00:00:00Z",
        "2026-07-16T00:00:00Z",
    }


def test_ois_policy_path_aextract_raises_without_files(monkeypatch):
    from openbb_core.app.model.abstract.error import OpenBBError

    async def _dates(asset_class):
        return ["2026-07-16"]

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)

    with pytest.raises(OpenBBError, match="published"):
        asyncio.run(
            CftcOisPolicyPathFetcher.aextract_data(
                CftcOisPolicyPathQueryParams(currency="USD", date=date(2020, 1, 1)),
                None,
            )
        )


def test_ois_policy_path_transform():
    records = [
        _fwd(0.036, "2026-08-20", "2026-10-08"),
        _fwd(0.037, "2026-08-20", "2026-10-08"),
        _fwd(0.038, "2026-08-20", "2026-10-08"),
    ]
    result = CftcOisPolicyPathFetcher.transform_data(
        CftcOisPolicyPathQueryParams(currency="USD"), (records, "2026-07-17")
    )

    assert all(isinstance(r, CftcOisPolicyPathData) for r in result.result)
    node = result.result[0]

    assert node.index == "2026-08-20"
    assert node.rate == pytest.approx(3.7)
    assert result.metadata["benchmark"] == "SOFR"
    assert result.metadata["central_bank"] == "Federal Reserve"
    assert result.metadata["nodes"] == 1
