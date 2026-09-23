import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models.cot import CftcCotData, CftcCotFetcher, CftcCotQueryParams
from openbb_cftc.models.cot_search import (
    CftcCotSearchFetcher,
    CftcCotSearchQueryParams,
)

COT_RECORD = {
    "report_date_as_yyyy_mm_dd": "2024-08-20T00:00:00.000",
    "market_and_exchange_names": "GOLD - COMMODITY EXCHANGE INC.",
    "cftc_contract_market_code": "088691",
    "commodity_name": "GOLD",
    "commodity_group_name": "NATURAL RESOURCES",
    "commodity_subgroup_name": "PRECIOUS METALS",
    "contract_units": "(TROY OUNCES)",
    "open_interest_all": "500000",
    "noncomm_positions_long_all": "250000",
    "noncomm_positions_short_all": "100000",
    "change_in_noncomm_long_all": "1500",
    "change_in_noncomm_short_all": "-500",
    "pct_of_oi_noncomm_long_all": "50.0",
    "traders_noncomm_long_all": "120",
    "conc_gross_le_4_tdr_long": "22.5",
    "yyyy_report_week_ww": "2024 Report Week 34",
}


def _capture_url(monkeypatch, response=None):
    calls: list[str] = []

    async def _request(url, **kwargs):
        calls.append(url)
        return response if response is not None else [COT_RECORD]

    monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", _request)

    return calls


def test_cot_extract_builds_a_code_query(monkeypatch):
    calls = _capture_url(monkeypatch)
    asyncio.run(
        CftcCotFetcher.aextract_data(CftcCotQueryParams(code="CFTC_088691"), None)
    )

    assert "088691" in calls[0]
    assert "CFTC_" not in calls[0]
    assert "1995-01-01" in calls[0]


def test_cot_extract_serves_a_repeat_from_the_response_cache(monkeypatch):
    calls = _capture_url(monkeypatch)
    first = asyncio.run(
        CftcCotFetcher.aextract_data(CftcCotQueryParams(code="CFTC_088691"), None)
    )
    second = asyncio.run(
        CftcCotFetcher.aextract_data(CftcCotQueryParams(code="CFTC_088691"), None)
    )

    assert first == second
    assert len(calls) == 1


def test_cot_search_serves_a_repeat_from_the_response_cache(monkeypatch):
    calls: list[str] = []

    async def _request(url, **kwargs):
        calls.append(url)
        return [COT_RECORD]

    monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", _request)

    first = asyncio.run(
        CftcCotSearchFetcher.aextract_data(CftcCotSearchQueryParams(query="gold"), None)
    )
    second = asyncio.run(
        CftcCotSearchFetcher.aextract_data(CftcCotSearchQueryParams(query="gold"), None)
    )

    assert first == second
    assert len(calls) == 1


def test_cot_extract_all_returns_the_latest_week(monkeypatch):
    calls = _capture_url(monkeypatch)
    asyncio.run(CftcCotFetcher.aextract_data(CftcCotQueryParams(code="all"), None))

    assert "like UPPER" not in calls[0]
    assert "1995-01-01" not in calls[0]


def test_cot_extract_wraps_a_name_query(monkeypatch):
    calls = _capture_url(monkeypatch)
    asyncio.run(CftcCotFetcher.aextract_data(CftcCotQueryParams(code="gold"), None))

    assert "%gold%" in calls[0]


def test_cot_extract_escapes_reserved_characters(monkeypatch):
    calls = _capture_url(monkeypatch)
    asyncio.run(CftcCotFetcher.aextract_data(CftcCotQueryParams(code="S&P 500+"), None))

    assert "%26" in calls[0]
    assert "%2B" in calls[0]


@pytest.mark.parametrize(
    ("report_type", "futures_only", "expected"),
    [
        ("legacy", True, "6dca-aqww"),
        ("legacy", False, "jun7-fc8e"),
        ("disaggregated", True, "72hh-3qpy"),
        ("financial", False, "yw9f-hn96"),
        ("supplemental", True, "4zgm-a668"),
    ],
)
def test_cot_extract_selects_the_dataset(
    monkeypatch, report_type, futures_only, expected
):
    calls = _capture_url(monkeypatch)
    asyncio.run(
        CftcCotFetcher.aextract_data(
            CftcCotQueryParams(
                code="088691", report_type=report_type, futures_only=futures_only
            ),
            None,
        )
    )

    assert expected in calls[0]


def test_cot_extract_appends_the_app_token(monkeypatch):
    calls = _capture_url(monkeypatch)
    asyncio.run(
        CftcCotFetcher.aextract_data(
            CftcCotQueryParams(code="088691"), {"cftc_app_token": "SECRET"}
        )
    )

    assert "$$app_token=SECRET" in calls[0]


def test_cot_extract_honours_explicit_dates(monkeypatch):
    calls = _capture_url(monkeypatch)
    asyncio.run(
        CftcCotFetcher.aextract_data(
            CftcCotQueryParams(
                code="088691",
                start_date=date(2024, 8, 19),
                end_date=date(2024, 8, 21),
            ),
            None,
        )
    )

    assert "2024-08-19" in calls[0]
    assert "2024-08-21" in calls[0]


def test_cot_extract_propagates_errors(monkeypatch):

    async def _raise(url, **kwargs):
        raise OpenBBError("upstream down")

    monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", _raise)

    with pytest.raises(OpenBBError, match="upstream down"):
        asyncio.run(CftcCotFetcher.aextract_data(CftcCotQueryParams(code="x"), None))


def test_cot_extract_raises_on_empty(monkeypatch):
    _capture_url(monkeypatch, response=[])

    with pytest.raises(EmptyDataError, match="No data found"):
        asyncio.run(CftcCotFetcher.aextract_data(CftcCotQueryParams(code="x"), None))


def test_cot_transform_types_and_scales():
    results = CftcCotFetcher.transform_data(
        CftcCotQueryParams(code="088691"), [COT_RECORD]
    )
    record = results[0]

    assert isinstance(record, CftcCotData)
    assert record.date == date(2024, 8, 20)
    assert record.open_interest_all == 500000
    assert record.contract_units == "TROY OUNCES"
    assert record.commodity == "GOLD"
    assert record.open_interest_pct_non_commercial_long_all == pytest.approx(0.5)
    assert record.concentration_gross_top_4_traders_long == pytest.approx(22.5)


def test_cot_transform_skips_empty_records():
    assert (
        CftcCotFetcher.transform_data(CftcCotQueryParams(code="x"), [{"a": None}]) == []
    )


def test_cot_transform_keeps_unparseable_values():
    results = CftcCotFetcher.transform_data(
        CftcCotQueryParams(code="x"),
        [{**COT_RECORD, "futonly_or_combined": "FutOnly"}],
    )

    assert results[0].futonly_or_combined == "FutOnly"


@pytest.mark.parametrize(
    ("measure", "present", "absent"),
    [
        (
            "changes",
            "change_in_non_commercial_long_all",
            "traders_non_commercial_long_all",
        ),
        (
            "traders",
            "traders_non_commercial_long_all",
            "change_in_non_commercial_long_all",
        ),
        (
            "percent_of_oi",
            "open_interest_pct_non_commercial_long_all",
            "traders_non_commercial_long_all",
        ),
        (
            "concentration",
            "concentration_gross_top_4_traders_long",
            "change_in_non_commercial_long_all",
        ),
        (
            "positions",
            "non_commercial_positions_long_all",
            "change_in_non_commercial_long_all",
        ),
    ],
)
def test_cot_transform_measure_filter(measure, present, absent):
    results = CftcCotFetcher.transform_data(
        CftcCotQueryParams(code="088691", measure=measure), [COT_RECORD]
    )
    dumped = results[0].model_dump()

    assert dumped.get(present) is not None
    assert dumped.get(absent) is None
    assert dumped["open_interest_all"] == 500000
    assert dumped["date"] == date(2024, 8, 20)


def test_cot_transform_limit_keeps_the_latest():
    older = {**COT_RECORD, "report_date_as_yyyy_mm_dd": "2024-08-13T00:00:00.000"}
    results = CftcCotFetcher.transform_data(
        CftcCotQueryParams(code="088691", limit=1), [older, COT_RECORD]
    )

    assert len(results) == 1
    assert results[0].date == date(2024, 8, 20)


def test_cot_transform_blanks_duplicated_crop_year_columns():
    record = {
        **COT_RECORD,
        "noncomm_positions_long_old": "250000",
        "noncomm_positions_long_other": "250000",
    }
    results = CftcCotFetcher.transform_data(CftcCotQueryParams(code="x"), [record])

    assert results[0].non_commercial_positions_long_all == 250000
    assert results[0].non_commercial_positions_long_old is None


def test_cot_search_extract_filters(monkeypatch):
    calls = _capture_url(
        monkeypatch, response=[{"cftc_contract_market_code": "088691"}]
    )
    asyncio.run(
        CftcCotSearchFetcher.aextract_data(
            CftcCotSearchQueryParams(
                query="gold's",
                category="natural_resources",
                subcategory="precious_metals",
                futures_only=True,
            ),
            {"cftc_app_token": "SECRET"},
        )
    )
    url = calls[0]

    assert "6dca-aqww" in url
    assert "NATURAL%20RESOURCES" in url
    assert "PRECIOUS%20METALS" in url
    assert "$$app_token=SECRET" in url
    assert "gold%27%27s" in url


@pytest.mark.parametrize(
    ("subcategory", "expected"),
    [
        ("currency_non_major", "CURRENCY(NON-MAJOR)"),
        ("foodstuffs_softs", "FOODSTUFFS/SOFTS"),
        ("interest_rates_us_treasury", "INTEREST RATES - U.S. TREASURY"),
        ("base_metals", "BASE METALS"),
    ],
)
def test_cot_search_subcategory_mapping(monkeypatch, subcategory, expected):
    from urllib.parse import unquote

    calls = _capture_url(monkeypatch, response=[{"cftc_contract_market_code": "1"}])
    asyncio.run(
        CftcCotSearchFetcher.aextract_data(
            CftcCotSearchQueryParams(subcategory=subcategory), None
        )
    )

    assert expected in unquote(calls[0])


def test_cot_search_supplemental_is_not_suffixed(monkeypatch):
    calls = _capture_url(monkeypatch, response=[{"cftc_contract_market_code": "1"}])
    asyncio.run(
        CftcCotSearchFetcher.aextract_data(
            CftcCotSearchQueryParams(report_type="supplemental", futures_only=True),
            None,
        )
    )

    assert "4zgm-a668" in calls[0]


def test_cot_search_propagates_errors(monkeypatch):

    async def _raise(url, **kwargs):
        raise OpenBBError("upstream down")

    monkeypatch.setattr("openbb_core.provider.utils.helpers.amake_request", _raise)

    with pytest.raises(OpenBBError, match="upstream down"):
        asyncio.run(
            CftcCotSearchFetcher.aextract_data(CftcCotSearchQueryParams(), None)
        )


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({"query": "nothing"}, "No results found for 'nothing'"),
        ({}, "No results returned"),
    ],
)
def test_cot_search_raises_on_empty(monkeypatch, params, message):
    _capture_url(monkeypatch, response=[])

    with pytest.raises(EmptyDataError, match=message):
        asyncio.run(
            CftcCotSearchFetcher.aextract_data(CftcCotSearchQueryParams(**params), None)
        )


def test_cot_search_transform_prefixes_and_dedupes():
    row = {
        "cftc_contract_market_code": "088691",
        "contract_market_name": "GOLD",
        "commodity_name": "GOLD",
        "commodity_group_name": "NATURAL RESOURCES",
        "commodity_subgroup_name": "PRECIOUS METALS",
    }
    results = CftcCotSearchFetcher.transform_data(
        CftcCotSearchQueryParams(), [row, dict(row)]
    )

    assert len(results) == 1
    assert results[0].code == "CFTC_088691"


@pytest.mark.parametrize(
    ("name", "category", "subcategory"),
    [
        ("S&P 500 INDICES", "FINANCIAL INSTRUMENTS", "STOCK INDICES"),
        ("CRYPTO ASSET", "FINANCIAL INSTRUMENTS", "DIGITAL ASSET (NON-MAJOR)"),
    ],
)
def test_cot_search_transform_infers_missing_groups(name, category, subcategory):
    results = CftcCotSearchFetcher.transform_data(
        CftcCotSearchQueryParams(),
        [
            {
                "cftc_contract_market_code": "1",
                "contract_market_name": name,
                "commodity_name": name,
            }
        ],
    )

    assert results[0].category == category
    assert results[0].subcategory == subcategory


def test_cot_search_transform_skips_rows_without_a_code():
    assert (
        CftcCotSearchFetcher.transform_data(
            CftcCotSearchQueryParams(), [{"contract_market_name": "GOLD"}]
        )
        == []
    )
