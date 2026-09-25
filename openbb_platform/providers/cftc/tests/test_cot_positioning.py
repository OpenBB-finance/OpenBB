import asyncio

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models.cot_positioning import (
    CftcCotPositioningData,
    CftcCotPositioningFetcher,
    CftcCotPositioningQueryParams,
    _rolling_scores,
    build_series,
    readout,
)
from openbb_cftc.utils.cot_markets import market_for_code

MARKET = {
    "code": "CFTC_13874+",
    "label": "S&P 500",
    "asset_class": "indices_bonds",
    "contract": "S&P 500 Consolidated",
}


def _report(week: int, net: int, open_interest: str = "1000") -> dict:
    return {
        "report_date_as_yyyy_mm_dd": f"2026-01-{week:02d}T00:00:00.000",
        "open_interest_all": open_interest,
        "noncomm_positions_long_all": str(max(net, 0)),
        "noncomm_positions_short_all": str(max(-net, 0)),
        "comm_positions_long_all": str(max(-net, 0)),
        "comm_positions_short_all": str(max(net, 0)),
        "nonrept_positions_long_all": "0",
        "nonrept_positions_short_all": "0",
    }


def _patch_cot(monkeypatch, rows, seen=None):
    async def _extract(query, credentials, **kwargs):
        if seen is not None:
            seen.append((query.code, query.futures_only))

        return rows

    monkeypatch.setattr("openbb_cftc.models.cot.CftcCotFetcher.aextract_data", _extract)


def test_rolling_scores_use_a_trailing_window():
    assert _rolling_scores([0.0, 50.0, 100.0], 52, "large_specs") == [
        50.0,
        100.0,
        100.0,
    ]
    assert _rolling_scores([0.0, 50.0, 100.0, 0.0], 2, "large_specs") == [
        50.0,
        100.0,
        100.0,
        0.0,
    ]
    assert _rolling_scores([None, None], 52, "large_specs") == [None, None]


def test_build_series_scores_every_week():
    rows = [_report(w, net) for w, net in enumerate([0, 50, 100, 20], start=1)]
    series = build_series(rows, 52)

    assert [r["report_date"] for r in series] == [
        "2026-01-01",
        "2026-01-02",
        "2026-01-03",
        "2026-01-04",
    ]
    assert series[-1]["large_specs_net"] == 20
    assert series[-1]["large_specs_net_pct_oi"] == 2.0
    assert series[-1]["commercials_net"] == -20
    assert series[-1]["large_specs_score"] == 20.0
    assert series[-1]["open_interest"] == 1000


def test_build_series_survives_missing_figures():
    rows = [
        {"report_date_as_yyyy_mm_dd": "2026-01-01T00:00:00.000"},
        {**_report(2, 100), "open_interest_all": "0"},
        {"open_interest_all": "10"},
    ]
    series = build_series(rows, 52)

    assert len(series) == 2
    assert series[0]["large_specs_net"] is None
    assert series[0]["open_interest"] is None
    assert series[1]["large_specs_net_pct_oi"] is None


def test_readout_summarizes_the_latest_reading():
    rows = [_report(w, net) for w, net in enumerate([0, 20, 40, 60, 80, 100], start=1)]
    series = build_series(rows, 52)
    latest = readout(series, "large_specs")

    assert latest["score"] == 100.0
    assert latest["zone"] == "crowded"
    assert latest["is_extreme"] is True
    assert latest["net"] == 100
    assert latest["net_pct_oi"] == 10.0
    assert latest["change_1w"] == 0.0
    assert latest["change_1m"] == 0.0
    assert latest["score_low"] == 50.0
    assert latest["score_high"] == 100.0
    assert latest["net_pct_oi_low"] == 0.0
    assert latest["net_pct_oi_high"] == 10.0

    commercials = readout(series, "commercials")

    assert commercials["score"] == 100.0
    assert commercials["zone"] == "heavily hedged"


def test_readout_without_enough_history():
    series = build_series([_report(1, 10)], 52)
    latest = readout(series, "large_specs")

    assert latest["change_1w"] is None
    assert latest["change_1m"] is None
    assert readout([], "large_specs")["score"] is None


def test_market_for_code_returns_a_curated_market():
    assert market_for_code("CFTC_13874+")["label"] == "S&P 500"
    assert market_for_code(" CFTC_088691 ")["contract"] == "GOLD"


def test_market_for_code_falls_back_to_a_bare_entry():
    assert market_for_code("CFTC_124606") == {
        "code": "CFTC_124606",
        "label": "CFTC_124606",
        "asset_class": "all",
        "contract": "CFTC_124606",
    }


def test_transform_query():
    query = CftcCotPositioningFetcher.transform_query({"code": "CFTC_088691"})

    assert isinstance(query, CftcCotPositioningQueryParams)
    assert query.code == "CFTC_088691"
    assert query.futures_only is True
    assert query.lookback_weeks == 52


def test_transform_query_defaults_to_the_sp_500():
    assert CftcCotPositioningFetcher.transform_query({}).code == "CFTC_13874+"


def test_aextract_fetches_the_market_history(monkeypatch):
    seen: list = []
    _patch_cot(monkeypatch, [_report(1, 0), _report(2, 100)], seen)

    market, rows = asyncio.run(
        CftcCotPositioningFetcher.aextract_data(
            CftcCotPositioningQueryParams(code="CFTC_088691"), None
        )
    )

    assert seen == [("CFTC_088691", True)]
    assert market["label"] == "Gold"
    assert len(rows) == 2


def test_aextract_names_an_uncurated_code_from_its_report(monkeypatch):
    rows = [
        {
            **_report(1, 0),
            "contract_market_name": " DOW JONES U.S. REAL ESTATE IDX ",
        },
        _report(2, 100),
    ]
    _patch_cot(monkeypatch, rows)

    market, _ = asyncio.run(
        CftcCotPositioningFetcher.aextract_data(
            CftcCotPositioningQueryParams(code="CFTC_124606"), None
        )
    )

    assert market["label"] == "DOW JONES U.S. REAL ESTATE IDX"
    assert market["contract"] == "DOW JONES U.S. REAL ESTATE IDX"


def test_aextract_keeps_the_code_when_the_report_has_no_name(monkeypatch):
    _patch_cot(monkeypatch, [_report(1, 0)])

    market, _ = asyncio.run(
        CftcCotPositioningFetcher.aextract_data(
            CftcCotPositioningQueryParams(code="CFTC_999999"), None
        )
    )

    assert market["label"] == "CFTC_999999"


def test_aextract_raises_without_history(monkeypatch):
    _patch_cot(monkeypatch, [])

    with pytest.raises(EmptyDataError, match="No CFTC report history"):
        asyncio.run(
            CftcCotPositioningFetcher.aextract_data(
                CftcCotPositioningQueryParams(), None
            )
        )


def test_transform_data_builds_the_series_and_its_readouts():
    rows = [_report(w, net) for w, net in enumerate([0, 50, 100], start=1)]
    result = CftcCotPositioningFetcher.transform_data(
        CftcCotPositioningQueryParams(), (MARKET, rows)
    )

    assert all(isinstance(r, CftcCotPositioningData) for r in result.result)
    assert len(result.result) == 3

    meta = result.metadata

    assert meta["market"] == "S&P 500"
    assert meta["contract"] == "S&P 500 Consolidated"
    assert meta["weeks"] == 3
    assert meta["report_date"] == "2026-01-03"
    assert meta["window_start"] == "2026-01-01"
    assert meta["large_specs"]["score"] == 100.0
    assert meta["commercials"]["zone"] == "heavily hedged"
    assert meta["small_specs"]["score"] == 50.0
