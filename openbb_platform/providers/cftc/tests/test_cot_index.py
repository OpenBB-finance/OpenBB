import asyncio

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models.cot_index import (
    CftcCotIndexData,
    CftcCotIndexFetcher,
    CftcCotIndexQueryParams,
    is_extreme,
    positioning_score,
    score_market,
    zone_for,
)
from openbb_cftc.utils.cot_markets import COT_MARKETS, markets_for

MARKET = {
    "code": "CFTC_13874+",
    "label": "S&P 500",
    "asset_class": "indices_bonds",
    "contract": "S&P 500 Consolidated",
}


def _report(week: int, noncomm_net: int, comm_net: int, nonrept_net: int = 0) -> dict:
    return {
        "report_date_as_yyyy_mm_dd": f"2026-01-{week:02d}T00:00:00.000",
        "open_interest_all": "1000",
        "noncomm_positions_long_all": str(max(noncomm_net, 0)),
        "noncomm_positions_short_all": str(max(-noncomm_net, 0)),
        "comm_positions_long_all": str(max(comm_net, 0)),
        "comm_positions_short_all": str(max(-comm_net, 0)),
        "nonrept_positions_long_all": str(max(nonrept_net, 0)),
        "nonrept_positions_short_all": str(max(-nonrept_net, 0)),
    }


def test_positioning_score_spans_its_own_range():
    assert positioning_score([10.0, 20.0, 30.0]) == 100.0
    assert positioning_score([30.0, 20.0, 10.0]) == 0.0
    assert positioning_score([10.0, 30.0, 20.0]) == 50.0
    assert positioning_score([5.0, 5.0, 5.0]) == 50.0
    assert positioning_score([]) is None


@pytest.mark.parametrize(
    ("score", "group", "expected"),
    [
        (0.0, "large_specs", "under-owned"),
        (15.0, "large_specs", "under-owned"),
        (50.0, "small_specs", "neutral"),
        (85.0, "large_specs", "crowded"),
        (100.0, "small_specs", "crowded"),
        (0.0, "commercials", "exposed"),
        (50.0, "commercials", "neutral"),
        (100.0, "commercials", "heavily hedged"),
        (None, "large_specs", None),
    ],
)
def test_zone_for_uses_each_groups_vocabulary(score, group, expected):
    assert zone_for(score, group) == expected


def test_score_market_scores_every_group_and_flags_extremes():
    rows = [
        _report(1, -100, 100, -20),
        _report(2, 0, 0, 0),
        _report(3, 100, -100, 20),
    ]
    scored = score_market(MARKET, rows, 52)

    assert scored["report_date"] == "2026-01-03"
    assert scored["market"] == "S&P 500"
    assert scored["open_interest"] == 1000
    assert scored["large_specs"] == 100.0
    assert scored["commercials"] == 100.0
    assert scored["large_specs_zone"] == "crowded"
    assert scored["commercials_zone"] == "heavily hedged"
    assert scored["large_specs_net_pct_oi"] == 10.0
    assert scored["commercials_net_pct_oi"] == -10.0
    assert scored["large_specs_change"] == 0.0
    assert is_extreme(scored) is True


def test_score_market_rolls_the_prior_window_rather_than_shrinking_it():
    rows = [_report(w, net, -net) for w, net in enumerate([0, 50, 100, 20], start=1)]
    scored = score_market(MARKET, rows, 3)

    assert scored["large_specs"] == 0.0
    assert scored["large_specs_change"] == -100.0


def test_score_market_ignores_unparseable_figures():
    rows = [
        _report(1, 0, 0),
        {
            **_report(2, 100, -100),
            "noncomm_positions_long_all": "n/a",
            "open_interest_all": ".",
        },
    ]
    scored = score_market(MARKET, rows, 52)

    assert scored["open_interest"] is None
    assert scored["large_specs"] == 50.0
    assert scored["large_specs_net_pct_oi"] is None
    assert scored["commercials"] == 100.0


def test_score_market_without_extremes():
    rows = [_report(1, 0, 0), _report(2, 100, -100), _report(3, 50, -50)]
    scored = score_market(MARKET, rows, 52)

    assert scored["large_specs"] == 50.0
    assert is_extreme(scored) is False


def test_score_market_honours_the_lookback_window():
    rows = [_report(1, 1000, -1000), _report(2, 0, 0), _report(3, 100, -100)]
    full = score_market(MARKET, rows, 52)
    short = score_market(MARKET, rows, 2)

    assert full["large_specs"] == 10.0
    assert short["large_specs"] == 100.0


def test_score_market_returns_none_without_rows():
    assert score_market(MARKET, [], 52) is None


def test_score_market_survives_missing_figures():
    rows = [
        {"report_date_as_yyyy_mm_dd": "2026-01-01T00:00:00.000"},
        {"report_date_as_yyyy_mm_dd": "2026-01-08T00:00:00.000"},
    ]
    scored = score_market(MARKET, rows, 52)

    assert scored["large_specs"] is None
    assert scored["large_specs_change"] is None
    assert scored["large_specs_net_pct_oi"] is None
    assert scored["open_interest"] is None
    assert is_extreme(scored) is False


def test_markets_for_filters_by_asset_class():
    assert len(markets_for("all")) == len(COT_MARKETS) == 34
    assert len(markets_for("indices_bonds")) == 8
    assert len(markets_for("currencies")) == 6
    assert len(markets_for("hard_commodities")) == 9
    assert len(markets_for("soft_commodities")) == 11


def test_curated_markets_are_unique_and_complete():
    codes = [m["code"] for m in COT_MARKETS]
    labels = [m["label"] for m in COT_MARKETS]

    assert len(set(codes)) == len(codes)
    assert len(set(labels)) == len(labels)
    assert all(m["code"].startswith("CFTC_") for m in COT_MARKETS)
    assert all(m["contract"] for m in COT_MARKETS)


def test_transform_query():
    query = CftcCotIndexFetcher.transform_query({"asset_class": "currencies"})

    assert isinstance(query, CftcCotIndexQueryParams)
    assert query.asset_class == "currencies"
    assert query.lookback_weeks == 52


def _patch_cot(monkeypatch, rows, seen=None):
    async def _extract(query, credentials, **kwargs):
        if seen is not None:
            seen.append(query.code)

        return rows

    monkeypatch.setattr("openbb_cftc.models.cot.CftcCotFetcher.aextract_data", _extract)


def test_aextract_scores_each_market_in_the_asset_class(monkeypatch):
    seen: list = []
    _patch_cot(monkeypatch, [_report(1, 0, 0), _report(2, 100, -100)], seen)

    rows = asyncio.run(
        CftcCotIndexFetcher.aextract_data(
            CftcCotIndexQueryParams(asset_class="currencies"), None
        )
    )

    assert len(rows) == 6
    assert seen == [m["code"] for m in markets_for("currencies")]


def test_aextract_skips_markets_the_source_cannot_serve(monkeypatch):
    from openbb_core.app.model.abstract.error import OpenBBError

    calls: list = []

    async def _extract(query, credentials, **kwargs):
        calls.append(query.code)

        if query.code == "CFTC_099741":
            raise OpenBBError("no data")

        return [_report(1, 0, 0), _report(2, 100, -100)]

    monkeypatch.setattr("openbb_cftc.models.cot.CftcCotFetcher.aextract_data", _extract)

    rows = asyncio.run(
        CftcCotIndexFetcher.aextract_data(
            CftcCotIndexQueryParams(asset_class="currencies"), None
        )
    )

    assert len(calls) == 6
    assert len(rows) == 5
    assert all(r["market"] != "Euro" for r in rows)


def test_aextract_raises_when_no_market_scores(monkeypatch):
    _patch_cot(monkeypatch, [])

    with pytest.raises(EmptyDataError, match="No curated COT market"):
        asyncio.run(CftcCotIndexFetcher.aextract_data(CftcCotIndexQueryParams(), None))


def test_transform_data_orders_markets_and_ranks_the_movers():
    data = [
        score_market(
            {**MARKET, "label": "30Y Bond"},
            [_report(1, 0, 0), _report(2, 100, -100)],
            52,
        ),
        score_market(MARKET, [_report(1, 100, -100), _report(2, 0, 0)], 52),
    ]
    result = CftcCotIndexFetcher.transform_data(CftcCotIndexQueryParams(), data)

    assert [r.market for r in result.result] == ["S&P 500", "30Y Bond"]
    assert all(isinstance(r, CftcCotIndexData) for r in result.result)

    meta = result.metadata

    assert meta["markets"] == 2
    assert meta["extremes"] == 2
    assert meta["lookback_weeks"] == 52
    assert meta["asset_classes"] == {"indices_bonds": "Indices & Bonds"}
    assert meta["largest_changes"]
    assert abs(meta["largest_changes"][0]["change"]) >= abs(
        meta["largest_changes"][-1]["change"]
    )


def test_aextract_requests_the_futures_only_report_by_default(monkeypatch):
    seen: list = []

    async def _extract(query, credentials, **kwargs):
        seen.append(query.futures_only)
        return [_report(1, 0, 0), _report(2, 100, -100)]

    monkeypatch.setattr("openbb_cftc.models.cot.CftcCotFetcher.aextract_data", _extract)

    asyncio.run(
        CftcCotIndexFetcher.aextract_data(
            CftcCotIndexQueryParams(asset_class="currencies"), None
        )
    )
    asyncio.run(
        CftcCotIndexFetcher.aextract_data(
            CftcCotIndexQueryParams(asset_class="currencies", futures_only=False), None
        )
    )

    assert seen[:6] == [True] * 6
    assert seen[6:] == [False] * 6
