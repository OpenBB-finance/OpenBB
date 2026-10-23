import asyncio

import pytest

from openbb_cftc.models.cot_movers import (
    CftcCotMoversData,
    CftcCotMoversFetcher,
    CftcCotMoversQueryParams,
    build_movers,
    describe_move,
    mover_score,
)

SCORED = [
    {
        "market": "10Y Treasury",
        "report_date": "2026-07-21",
        "large_specs": 18.9,
        "large_specs_change": 2.0,
        "small_specs": 0.0,
        "small_specs_change": -1.0,
        "commercials": 0.0,
        "commercials_change": -22.0,
    },
    {
        "market": "Bean Meal",
        "report_date": "2026-07-21",
        "large_specs": 40.0,
        "large_specs_change": 3.0,
        "small_specs": 66.0,
        "small_specs_change": -20.0,
        "commercials": None,
        "commercials_change": None,
    },
]


@pytest.mark.parametrize(
    ("group", "score", "change", "expected"),
    [
        ("commercials", 95.0, 4.0, "Moved to max hedged"),
        ("commercials", 0.0, -22.0, "Moved to max exposed"),
        ("commercials", 50.0, 11.0, "Eased off max exposed"),
        ("commercials", 50.0, -11.0, "Eased off max hedged"),
        ("large_specs", 92.0, 17.0, "Pushed into one-year highs"),
        ("large_specs", 92.0, -2.0, "Held near one-year highs"),
        ("small_specs", 14.0, -11.0, "Dropped to one-year lows"),
        ("small_specs", 14.0, 1.0, "Held near one-year lows"),
        ("small_specs", 21.0, 10.0, "Lifted off one-year lows"),
        ("small_specs", 80.0, -9.0, "Pulled back from highs"),
    ],
)
def test_describe_move(group, score, change, expected):
    assert describe_move(group, score, change) == expected


def test_build_movers_ranks_by_absolute_change():
    movers = build_movers(SCORED, 8)

    assert [m["market"] for m in movers] == ["10Y Treasury", "Bean Meal"]
    assert movers[0]["change"] == -22.0
    assert movers[0]["trader_group"] == "Commercials"
    assert movers[0]["signal"] == "Moved to max exposed"
    assert movers[1]["trader_group"] == "Small Specs"
    assert movers[1]["signal"] == "Pulled back from highs"


def test_build_movers_scores_each_group_in_its_own_column():
    movers = build_movers(SCORED, 8)

    assert movers[0]["commercial_score"] == 0.0
    assert movers[0]["spec_score"] is None
    assert movers[1]["spec_score"] == 66.0
    assert movers[1]["commercial_score"] is None
    assert [mover_score(m) for m in movers] == [0.0, 66.0]


def test_each_score_column_carries_its_own_ramp():
    fields = CftcCotMoversData.model_fields
    ramp = lambda name: [  # noqa: E731
        rule["color"]
        for rule in fields[name].json_schema_extra["x-widget_config"]["renderFnParams"][
            "colorRules"
        ]
    ]

    assert ramp("spec_score") == list(reversed(ramp("commercial_score")))
    assert ramp("spec_score")[-1] == "#15803d"


def test_build_movers_keeps_one_row_per_market():
    movers = build_movers(SCORED, 8)

    assert len({m["market"] for m in movers}) == len(movers)


def test_build_movers_skips_groups_without_a_change():
    movers = build_movers(SCORED, 0)

    assert all(
        m["trader_group"] != "Commercials" or m["market"] != "Bean Meal" for m in movers
    )


def test_build_movers_honours_the_limit():
    assert len(build_movers(SCORED, 1)) == 1


def test_transform_query():
    query = CftcCotMoversFetcher.transform_query({"limit": 4})

    assert isinstance(query, CftcCotMoversQueryParams)
    assert query.limit == 4


def test_aextract_delegates_to_the_index_fetcher(monkeypatch):
    async def _extract(query, credentials, **kwargs):
        return SCORED

    monkeypatch.setattr(
        "openbb_cftc.models.cot_index.CftcCotIndexFetcher.aextract_data", _extract
    )

    assert (
        asyncio.run(
            CftcCotMoversFetcher.aextract_data(CftcCotMoversQueryParams(), None)
        )
        == SCORED
    )


def test_transform_data_ranks_and_summarizes():
    result = CftcCotMoversFetcher.transform_data(CftcCotMoversQueryParams(), SCORED)

    assert all(isinstance(r, CftcCotMoversData) for r in result.result)
    assert result.result[0].market == "10Y Treasury"
    assert result.result[0].trader_group == "Commercials"
    assert result.result[0].signal == "Moved to max exposed"

    meta = result.metadata

    assert meta["report_date"] == "2026-07-21"
    assert meta["markets"] == 2
    assert meta["largest_move"] == -22.0
    assert meta["extremes"] == 1


def test_transform_data_without_markets():
    result = CftcCotMoversFetcher.transform_data(CftcCotMoversQueryParams(), [])

    assert result.result == []
    assert result.metadata["report_date"] is None
    assert result.metadata["largest_move"] is None
