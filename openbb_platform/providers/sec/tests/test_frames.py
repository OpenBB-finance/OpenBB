"""Unit tests for ``openbb_sec.utils.frames``.

These exercise the frame URL-building and parsing functions directly with
crafted synthetic inputs and mocked transport, covering branches the
fetcher/VCR suites never reach.  No real HTTP is performed: ``cached_request``
and ``fetch_data`` are patched at the import site (``openbb_sec.utils.frames``).
"""

import asyncio
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_sec.utils.frames as fr


def test_fetch_data_expire_by_persist():
    """fetch_data sets a 24h expiry for historical frames and None when persisting.

    cached_request is imported at module scope in frames, so it is patched there.
    """
    seen = {}

    async def _fake_cr(url, headers=None, use_cache=True, expire=None):
        seen["expire"] = expire
        return {"ok": True}

    with patch.object(fr, "cached_request", _fake_cr):
        # persist=False -> historical, 24h TTL.
        out = asyncio.run(fr.fetch_data("http://x", True, False))
        assert seen["expire"] == 3600 * 24
        assert out == {"ok": True}
        # persist=True -> current-year frame, no expiry.
        asyncio.run(fr.fetch_data("http://x", True, True))
        assert seen["expire"] is None


def _frame_companies():
    from pandas import DataFrame

    return DataFrame(
        {
            "cik": ["320193", "789019"],
            "symbol": ["AAPL", "MSFT"],
            "name": ["Apple", "Microsoft"],
        }
    )


_FRAME_RESP = {
    "ccp": "CY2023Q1",
    "tag": "Revenues",
    "label": "Revenues",
    "description": "desc",
    "taxonomy": "us-gaap",
    "uom": "USD",
    "pts": 2,
    "data": [{"cik": 320193, "val": 100}, {"cik": 789019, "val": 200}],
}


def test_get_frame_quarter():
    """get_frame builds a quarterly URL, sorts data, and maps CIK->symbol."""

    async def _fetch(url, use_cache, persist):
        assert url.endswith("CY2023Q1.json")
        return _FRAME_RESP

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        res = asyncio.run(
            fr.get_frame(fact="Revenues", year=2023, calendar_period="q1")
        )
    assert res["metadata"]["frame"] == "CY2023Q1"
    assert res["metadata"]["unit"] == "USD"
    # Sorted by val descending -> MSFT (200) first.
    assert res["data"][0]["symbol"] == "MSFT"
    assert res["data"][0]["fact"] == "Revenues"


def test_get_frame_defaults_to_current_period():
    """With no year/period, get_frame derives them from today's date."""
    from datetime import datetime

    captured = {}

    async def _fetch(url, use_cache, persist):
        captured["url"] = url
        captured["persist"] = persist
        return _FRAME_RESP

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        asyncio.run(fr.get_frame(fact="Revenues"))
    year = datetime.now().date().year
    assert f"CY{year}" in captured["url"]
    assert captured["persist"] is True  # current year persists


def test_get_frame_period_without_year_defaults_year():
    """A calendar_period with no year defaults the year to the current calendar year."""
    from datetime import datetime

    captured = {}

    async def _fetch(url, use_cache, persist):
        captured["url"] = url
        return _FRAME_RESP

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        asyncio.run(fr.get_frame(fact="Revenues", year=None, calendar_period="q1"))
    year = datetime.now().date().year
    # quarter is set (Q1) so the default-both branch is skipped; only year defaults.
    assert captured["url"].endswith(f"CY{year}Q1.json")


def test_get_frame_shares_units():
    """A SHARES_FACTS fact forces the 'shares' unit in the URL."""
    captured = {}

    async def _fetch(url, use_cache, persist):
        captured["url"] = url
        return _FRAME_RESP

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        asyncio.run(
            fr.get_frame(
                fact="WeightedAverageNumberOfSharesOutstandingBasic", year=2023
            )
        )
    assert "/shares/" in captured["url"]


def test_get_frame_per_share_units_instantaneous():
    """A USD_PER_SHARE_FACTS fact sets the per-share unit; instantaneous adds 'I'."""
    captured = {}

    async def _fetch(url, use_cache, persist):
        captured["url"] = url
        return _FRAME_RESP

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        asyncio.run(
            fr.get_frame(fact="EarningsPerShareBasic", year=2023, instantaneous=True)
        )
    assert "/USD-per-shares/" in captured["url"]
    assert captured["url"].endswith("I.json")


def test_get_frame_instantaneous_retry():
    """An instantaneous request that fails retries without the 'I' suffix."""
    urls = []

    async def _fetch(url, use_cache, persist):
        urls.append(url)
        if url.endswith("I.json"):
            raise RuntimeError("no instant frame")
        return _FRAME_RESP

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        with pytest.warns(Warning):
            res = asyncio.run(
                fr.get_frame(
                    fact="Revenues",
                    year=2023,
                    calendar_period="q1",
                    instantaneous=True,
                )
            )
    assert urls[0].endswith("I.json")
    assert urls[1].endswith("Q1.json")
    assert res["metadata"]["tag"] == "Revenues"


def test_get_frame_quarter_retry_instantaneous():
    """A quarterly request that fails retries as instantaneous."""
    urls = []

    async def _fetch(url, use_cache, persist):
        urls.append(url)
        if url.endswith("I.json"):
            return _FRAME_RESP
        raise RuntimeError("no quarter frame")

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        with pytest.warns(Warning):
            res = asyncio.run(
                fr.get_frame(fact="Revenues", year=2023, calendar_period="q1")
            )
    assert urls[0].endswith("Q1.json")
    assert urls[1].endswith("Q1I.json")
    assert res["data"]  # parsed successfully on retry


def test_get_frame_instantaneous_double_failure_raises():
    """An instantaneous request whose retry also fails raises OpenBBError."""

    async def _fetch(url, use_cache, persist):
        raise RuntimeError("nothing here")

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        with pytest.warns(Warning):
            with pytest.raises(OpenBBError, match="No frame was found"):
                asyncio.run(
                    fr.get_frame(
                        fact="Revenues",
                        year=2023,
                        calendar_period="q1",
                        instantaneous=True,
                    )
                )


def test_get_frame_quarter_double_failure_raises():
    """A quarterly request whose instantaneous retry also fails raises OpenBBError."""

    async def _fetch(url, use_cache, persist):
        raise RuntimeError("nothing here")

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        with pytest.warns(Warning):
            with pytest.raises(OpenBBError, match="No frame was found"):
                asyncio.run(
                    fr.get_frame(fact="Revenues", year=2023, calendar_period="q1")
                )


def test_get_frame_annual_failure_raises():
    """A non-quarter, non-instant request that fails raises OpenBBError."""

    async def _fetch(url, use_cache, persist):
        raise RuntimeError("no frame")

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        with pytest.raises(OpenBBError, match="No frame was found"):
            asyncio.run(fr.get_frame(fact="Revenues", year=2023))


_CONCEPT_RESP = {
    "cik": 320193,
    "taxonomy": "us-gaap",
    "tag": "Revenues",
    "label": "Revenues",
    "description": "d",
    "entityName": "Apple",
    "units": {
        "USD": [
            {
                "fy": 2023,
                "fp": "FY",
                "filed": "2024-01-01",
                "end": "2023-12-31",
                "val": 100,
            },
            {
                "fy": 2022,
                "fp": "FY",
                "filed": "2023-01-01",
                "end": "2022-12-31",
                "val": 90,
            },
        ]
    },
}


def test_get_concept_happy_path_with_year_filter():
    """get_concept attaches metadata, flattens units, and filters by year."""

    async def _symbol_map(ticker, *a, **k):
        return "0000320193"

    async def _fetch(url, use_cache, persist):
        return _CONCEPT_RESP

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        res = asyncio.run(fr.get_concept("AAPL", fact="Revenues", year=2023))
    assert res["metadata"]["AAPL"]["units"] == "USD"  # single unit unwrapped
    assert len(res["data"]) == 1
    item = res["data"][0]
    assert item["symbol"] == "AAPL"
    assert item["unit"] == "USD"
    assert item["fact"] == "Revenues"
    assert item["name"] == "Apple"


def test_get_concept_year_filter_miss_returns_all():
    """A year with no matches warns and returns the full result set."""

    async def _symbol_map(ticker, *a, **k):
        return "0000320193"

    async def _fetch(url, use_cache, persist):
        return _CONCEPT_RESP

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        with pytest.warns(Warning):
            res = asyncio.run(fr.get_concept("AAPL", fact="Revenues", year=1999))
    assert len(res["data"]) == 2  # falls back to all entries


def test_get_concept_multi_unit():
    """A concept disclosed in multiple units lists them all in metadata."""
    resp = {
        "cik": 1,
        "taxonomy": "us-gaap",
        "tag": "Revenues",
        "label": "Revenues",
        "entityName": "Foo",
        "units": {
            "USD": [
                {
                    "fy": 2023,
                    "fp": "FY",
                    "filed": "2024-01-01",
                    "end": "2023-12-31",
                    "val": 1,
                }
            ],
            "CAD": [
                {
                    "fy": 2023,
                    "fp": "FY",
                    "filed": "2024-01-01",
                    "end": "2023-12-31",
                    "val": 2,
                }
            ],
        },
    }

    async def _symbol_map(ticker, *a, **k):
        return "0000000001"

    async def _fetch(url, use_cache, persist):
        return resp

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        res = asyncio.run(fr.get_concept("FOO"))
    assert set(res["metadata"]["FOO"]["units"]) == {"USD", "CAD"}
    assert len(res["data"]) == 2


def test_get_concept_no_cik_raises_empty():
    """A symbol with no CIK warns and ultimately raises EmptyDataError."""

    async def _symbol_map(ticker, *a, **k):
        return ""

    async def _fetch(url, use_cache, persist):
        return {}

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        with pytest.warns(Warning):
            with pytest.raises(EmptyDataError):
                asyncio.run(fr.get_concept("BADSYM"))


def test_get_concept_fetch_error_warns_and_raises_empty():
    """A valid CIK whose fetch raises is caught, warned, and ends in EmptyDataError.

    Unlike the no-CIK case, this exercises the try/except around fetch_data: the
    symbol resolves, the request raises, the error message is warned and recorded,
    and with no response collected the function raises EmptyDataError.
    """

    async def _symbol_map(ticker, *a, **k):
        return "0000320193"

    async def _fetch(url, use_cache, persist):
        raise RuntimeError("frame fetch failed")

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        with pytest.warns(Warning):
            with pytest.raises(EmptyDataError):
                asyncio.run(fr.get_concept("AAPL", fact="Revenues"))


def test_nearest_quarter_alignment():
    """Period ends round to the nearest calendar quarter-end (SEC alignment)."""
    assert fr._nearest_quarter("2023-03-31") == (2023, "Q1")
    assert fr._nearest_quarter("2023-06-30") == (2023, "Q2")
    assert fr._nearest_quarter("2023-09-30") == (2023, "Q3")
    assert fr._nearest_quarter("2023-12-31") == (2023, "Q4")
    # An off-calendar fiscal quarter-end rounds to the nearest calendar grid:
    assert fr._nearest_quarter("2023-09-26") == (2023, "Q3")
    # Walmart's fiscal Q1 ends Apr 30 -> nearest Mar 31 -> calendar Q1 (not Q2).
    assert fr._nearest_quarter("2026-04-30") == (2026, "Q1")
    # A January fiscal year-end rolls back to the prior December (Q4).
    assert fr._nearest_quarter("2027-01-31") == (2026, "Q4")
    # An unparseable date yields (None, None).
    assert fr._nearest_quarter("garbage") == (None, None)


def test_parse_frame():
    """SEC frame ids parse into (calendar_year, calendar_period)."""
    assert fr._parse_frame("CY2026") == (2026, "FY")
    assert fr._parse_frame("CY2026Q1") == (2026, "Q1")
    assert fr._parse_frame("CY2026Q4I") == (2026, "Q4")  # trailing I ignored
    assert fr._parse_frame("") == (None, "FY")


def test_span_helpers():
    """Day counting and span bucketing."""
    assert fr._span_days({"start": "2023-01-01", "end": "2023-03-31"}) == 90
    assert fr._span_days({"end": "2023-12-31"}) is None
    assert fr._classify_span(None) == "instant"
    assert fr._classify_span(90) == "quarter"
    assert fr._classify_span(181) == "h1"
    assert fr._classify_span(273) == "nine_month"
    assert fr._classify_span(365) == "annual"


def test_dedup_latest_filed_keeps_reference():
    """A restated value keeps the most recently filed figure for a period."""
    records = [
        {
            "symbol": "AAPL",
            "unit": "USD",
            "start": "2023-01-01",
            "end": "2023-12-31",
            "span": "annual",
            "filed": "2024-01-01",
            "accn": "a",
            "val": 455,
        },
        {
            "symbol": "AAPL",
            "unit": "USD",
            "start": "2023-01-01",
            "end": "2023-12-31",
            "span": "annual",
            "filed": "2024-01-15",
            "accn": "b",
            "val": 460,
        },
    ]
    out = fr._dedup_latest_filed(records)
    assert len(out) == 1
    assert out[0]["val"] == 460


def test_derive_standalone_quarters_including_q4():
    """A cumulative YTD chain is reduced to standalone quarters; Q4 = FY - 9M."""
    base = {"symbol": "AAPL", "unit": "USD", "fy": 2023}
    records = [
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-03-31",
            "val": 100,
            "span": "quarter",
            "calendar_period": "Q1",
            "calendar_year": 2023,
        },
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-06-30",
            "val": 210,
            "span": "h1",
            "calendar_period": "Q2",
            "calendar_year": 2023,
        },
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-09-30",
            "val": 330,
            "span": "nine_month",
            "calendar_period": "Q3",
            "calendar_year": 2023,
        },
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-12-31",
            "val": 460,
            "span": "annual",
            "calendar_period": "FY",
            "calendar_year": 2023,
        },
    ]
    derived = fr._derive_standalone_quarters(records)
    by_q = {d["calendar_period"]: d["val"] for d in derived}
    assert by_q == {"Q2": 110, "Q3": 120, "Q4": 130}
    assert all(d["derived"] for d in derived)
    assert all(d["span"] == "quarter" for d in derived)


def test_derive_skips_chain_gap():
    """A gap in the cumulative chain never yields a bogus multi-quarter value."""
    base = {"symbol": "AAPL", "unit": "USD", "fy": 2023}
    records = [
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-03-31",
            "val": 100,
            "span": "quarter",
            "calendar_period": "Q1",
            "calendar_year": 2023,
        },
        # No 6-month link: the only other cumulative is the 9-month figure.
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-09-30",
            "val": 330,
            "span": "nine_month",
            "calendar_period": "Q3",
            "calendar_year": 2023,
        },
    ]
    derived = fr._derive_standalone_quarters(records)
    # 330 - 100 spans two quarters (~6 months), so nothing is emitted.
    assert derived == []


_CHAIN_CONCEPT_RESP = {
    "cik": 320193,
    "taxonomy": "us-gaap",
    "tag": "Revenues",
    "label": "Revenues",
    "description": "d",
    "entityName": "Apple",
    "units": {
        "USD": [
            {
                "fy": 2023,
                "fp": "Q1",
                "filed": "2023-05-01",
                "start": "2023-01-01",
                "end": "2023-03-31",
                "val": 100,
                "accn": "q1",
            },
            {
                "fy": 2023,
                "fp": "Q2",
                "filed": "2023-08-01",
                "start": "2023-01-01",
                "end": "2023-06-30",
                "val": 210,
                "accn": "q2",
            },
            {
                "fy": 2023,
                "fp": "Q3",
                "filed": "2023-11-01",
                "start": "2023-01-01",
                "end": "2023-09-30",
                "val": 330,
                "accn": "q3",
            },
            {
                "fy": 2023,
                "fp": "FY",
                "filed": "2024-02-01",
                "start": "2023-01-01",
                "end": "2023-12-31",
                "val": 460,
                "accn": "fy",
            },
        ]
    },
}


def test_get_concept_quarter_selects_standalone():
    """calendar_period='q4' returns the derived standalone fourth quarter."""

    async def _symbol_map(ticker, *a, **k):
        return "0000320193"

    async def _fetch(url, use_cache, persist):
        return _CHAIN_CONCEPT_RESP

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        res = asyncio.run(
            fr.get_concept("AAPL", fact="Revenues", year=2023, calendar_period="q4")
        )
    assert len(res["data"]) == 1
    assert res["data"][0]["val"] == 130
    assert res["data"][0]["calendar_period"] == "Q4"
    assert res["data"][0]["derived"] is True


def test_get_concept_no_period_returns_annual_and_quarters():
    """With no calendar_period, annual + four standalone quarters are returned."""

    async def _symbol_map(ticker, *a, **k):
        return "0000320193"

    async def _fetch(url, use_cache, persist):
        return _CHAIN_CONCEPT_RESP

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        res = asyncio.run(fr.get_concept("AAPL", fact="Revenues", year=2023))
    periods = sorted(d["calendar_period"] for d in res["data"])
    assert periods == ["FY", "Q1", "Q2", "Q3", "Q4"]


def test_get_concept_fy_selects_annual():
    """calendar_period='fy' returns only the annual figure."""

    async def _symbol_map(ticker, *a, **k):
        return "0000320193"

    async def _fetch(url, use_cache, persist):
        return _CHAIN_CONCEPT_RESP

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        res = asyncio.run(
            fr.get_concept("AAPL", fact="Revenues", year=2023, calendar_period="fy")
        )
    assert len(res["data"]) == 1
    assert res["data"][0]["calendar_period"] == "FY"
    assert res["data"][0]["val"] == 460


def test_get_universe_quarter4_derives_q4():
    """Universe Q4 = FY - (Q1+Q2+Q3) per filer; incomplete filers are dropped."""
    frames_data = {
        "annual": {
            "tag": "Revenues",
            "label": "Revenues",
            "uom": "USD",
            "taxonomy": "us-gaap",
            "data": [
                {"cik": 320193, "val": 400, "accn": "a", "entityName": "Apple"},
                {"cik": 789019, "val": 300, "accn": "b", "entityName": "Microsoft"},
            ],
        },
        "Q1": {"data": [{"cik": 320193, "val": 100}, {"cik": 789019, "val": 70}]},
        "Q2": {"data": [{"cik": 320193, "val": 110}, {"cik": 789019, "val": 80}]},
        "Q3": {"data": [{"cik": 320193, "val": 90}]},  # MSFT missing Q3
    }

    async def _fetch(url, use_cache, persist):
        if url.endswith("Q1.json"):
            return frames_data["Q1"]
        if url.endswith("Q2.json"):
            return frames_data["Q2"]
        if url.endswith("Q3.json"):
            return frames_data["Q3"]
        return frames_data["annual"]

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        res = asyncio.run(fr.get_universe_quarter4(fact="Revenues", year=2023))
    assert res["metadata"]["frame"] == "CY2023Q4"
    # AAPL: 400 - (100+110+90) = 100; MSFT dropped (only two quarters reported).
    assert len(res["data"]) == 1
    row = res["data"][0]
    assert row["symbol"] == "AAPL"
    assert row["val"] == 100
    assert row["calendar_period"] == "Q4"
    assert row["calendar_year"] == 2023


def test_instant_facts_classification():
    """INSTANT_FACTS is a clean subset of FACTS and excludes flow concepts."""
    from openbb_sec.utils.definitions import FACTS, INSTANT_FACTS

    facts = set(FACTS)
    instant = set(INSTANT_FACTS)
    # Every instant fact is pickable and the list carries no duplicates.
    assert instant <= facts
    assert len(INSTANT_FACTS) == len(instant)
    # Canonical flow (income / cash-flow) concepts must never be instant.
    for flow in (
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "NetIncomeLoss",
        "OperatingIncomeLoss",
        "NetCashProvidedByUsedInOperatingActivities",
        "PaymentsForRepurchaseOfCommonStock",
        "ResearchAndDevelopmentExpense",
        "Depreciation",
    ):
        assert flow not in instant
    # Canonical balance-sheet concepts must be instant.
    for bal in (
        "Assets",
        "Liabilities",
        "StockholdersEquity",
        "Goodwill",
        "LongTermDebt",
        "InventoryNet",
    ):
        assert bal in instant


_Q4I_FRAME_RESP = {
    "ccp": "CY2023Q4I",
    "tag": "Assets",
    "label": "Assets",
    "description": "desc",
    "taxonomy": "us-gaap",
    "uom": "USD",
    "pts": 2,
    "data": [{"cik": 320193, "val": 1000}, {"cik": 789019, "val": 2000}],
}


def test_get_universe_quarter4_instant_fetches_q4i():
    """An instant (balance-sheet) fact fetches the year-end Q4I frame directly.

    No FY - (Q1+Q2+Q3) subtraction occurs: the values are the reported balances,
    and only the single instant frame is requested.
    """
    urls = []

    async def _fetch(url, use_cache, persist):
        urls.append(url)
        return _Q4I_FRAME_RESP

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        res = asyncio.run(fr.get_universe_quarter4(fact="Assets", year=2023))
    assert len(urls) == 1  # only the instant frame, no annual/Q1/Q2/Q3 fetches
    assert urls[0].endswith("CY2023Q4I.json")
    assert "/USD/" in urls[0]
    assert res["metadata"]["frame"] == "CY2023Q4I"
    vals = {r["symbol"]: r["val"] for r in res["data"]}
    assert vals == {"AAPL": 1000, "MSFT": 2000}
    assert all(r["calendar_period"] == "Q4" for r in res["data"])


def test_get_universe_quarter4_instant_shares_units():
    """An instant fact that is also a shares fact fetches Q4I in 'shares' units."""
    urls = []

    async def _fetch(url, use_cache, persist):
        urls.append(url)
        return {
            "ccp": "CY2023Q4I",
            "tag": "PreferredStockSharesOutstanding",
            "label": "Preferred Stock, Shares Outstanding",
            "uom": "shares",
            "data": [{"cik": 320193, "val": 5}],
        }

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        res = asyncio.run(
            fr.get_universe_quarter4(fact="PreferredStockSharesOutstanding", year=2023)
        )
    assert urls[0].endswith("CY2023Q4I.json")
    assert "/shares/" in urls[0]
    assert res["metadata"]["frame"] == "CY2023Q4I"


def test_get_universe_quarter4_flow_fallback_to_instant_when_no_annual():
    """A concept with no annual duration frame falls back to the Q4I frame.

    This guards the case where a point-in-time concept is not listed in
    INSTANT_FACTS: rather than erroring on the missing annual frame, the year-end
    instant frame is used so the request still resolves.
    """
    urls = []

    async def _fetch(url, use_cache, persist):
        urls.append(url)
        if url.endswith("CY2023Q4I.json"):
            return _Q4I_FRAME_RESP
        raise RuntimeError("no annual frame")  # annual duration frame absent

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        res = asyncio.run(fr.get_universe_quarter4(fact="Revenues", year=2023))
    assert any(u.endswith("CY2023.json") for u in urls)  # annual attempted first
    assert any(u.endswith("CY2023Q4I.json") for u in urls)  # instant fallback used
    assert res["metadata"]["frame"] == "CY2023Q4I"
    assert {r["symbol"]: r["val"] for r in res["data"]} == {"AAPL": 1000, "MSFT": 2000}


def test_span_days_invalid_date():
    """A malformed start/end date yields None rather than raising."""
    assert fr._span_days({"start": "not-a-date", "end": "2023-03-31"}) is None
    assert fr._span_days({"start": "2023-01-01", "end": "garbage"}) is None


def test_derive_standalone_quarters_no_start_skips():
    """A cumulative group with no resolvable fiscal-year start derives nothing."""
    records = [
        {
            "symbol": "AAPL",
            "unit": "USD",
            "fy": 2023,
            "span": "annual",
            "end": "2023-12-31",
            "val": 100,
            # no "start" anywhere in the group -> fy_start is None
        }
    ]
    assert fr._derive_standalone_quarters(records) == []


def test_derive_standalone_quarters_skips_already_reported():
    """A calendar quarter reported directly is not re-derived from the chain."""
    base = {"symbol": "AAPL", "unit": "USD", "fy": 2023}
    records = [
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-03-31",
            "val": 100,
            "span": "quarter",
            "calendar_period": "Q1",
            "calendar_year": 2023,
        },
        # Q2 already reported directly as a standalone three-month quarter.
        {
            **base,
            "start": "2023-04-01",
            "end": "2023-06-30",
            "val": 110,
            "span": "quarter",
            "calendar_period": "Q2",
            "calendar_year": 2023,
        },
        # A six-month cumulative whose Q2 difference must not double-count Q2.
        {
            **base,
            "start": "2023-01-01",
            "end": "2023-06-30",
            "val": 210,
            "span": "h1",
            "calendar_period": "Q2",
            "calendar_year": 2023,
        },
    ]
    assert fr._derive_standalone_quarters(records) == []


def test_select_periods_fy_instant_only_fallback():
    """calendar_period='fy' on an instant-only concept uses the year-end (Q4) point."""
    records = [
        {"span": "instant", "calendar_period": "Q4", "calendar_year": 2023, "val": 5},
        {"span": "instant", "calendar_period": "Q2", "calendar_year": 2023, "val": 4},
    ]
    out = fr._select_periods(records, year=2023, calendar_period="fy")
    assert len(out) == 1
    assert out[0]["calendar_period"] == "Q4"
    assert out[0]["val"] == 5


def test_get_universe_quarter4_defaults_year_and_skips_incomplete():
    """year=None defaults to the current year; a failed quarter frame and null
    rows are skipped, dropping filers that lack all three earlier quarters."""
    from datetime import datetime

    urls = []

    async def _fetch(url, use_cache, persist):
        urls.append(url)
        if url.endswith("Q2.json"):
            raise RuntimeError("no Q2 frame")  # one quarter unavailable
        if url.endswith("Q1.json"):
            return {
                "data": [
                    {"cik": 320193, "val": 100},
                    {"cik": None, "val": 5},  # null cik -> skipped
                    {"cik": 789019, "val": None},  # null val -> skipped
                ]
            }
        if url.endswith("Q3.json"):
            return {"data": [{"cik": 320193, "val": 90}]}
        return {  # annual
            "tag": "Revenues",
            "label": "Revenues",
            "uom": "USD",
            "taxonomy": "us-gaap",
            "data": [{"cik": 320193, "val": 400, "accn": "a", "entityName": "Apple"}],
        }

    async def _companies(use_cache=True):
        return _frame_companies()

    with (
        patch.object(fr, "fetch_data", _fetch),
        patch.object(fr, "get_all_companies", _companies),
    ):
        res = asyncio.run(fr.get_universe_quarter4(fact="Revenues", year=None))
    year = datetime.now().date().year
    assert res["metadata"]["frame"] == f"CY{year}Q4"
    assert any(u.endswith(f"CY{year}.json") for u in urls)  # year defaulted
    # AAPL reported only Q1 and Q3 (Q2 frame failed) -> dropped; result empty.
    assert res["data"] == []


def test_get_universe_quarter4_unit_overrides():
    """A flow fact in SHARES_FACTS / USD_PER_SHARE_FACTS selects the matching
    unit segment for the derived-Q4 frame URLs."""
    captured: dict = {}

    def _make_fetch(store_key):
        async def _fetch(url, use_cache, persist):
            captured.setdefault(store_key, []).append(url)
            if url.endswith(("Q1.json", "Q2.json", "Q3.json")):
                return {"data": [{"cik": 320193, "val": 1}]}
            return {  # annual
                "tag": "x",
                "label": "x",
                "uom": "u",
                "taxonomy": "us-gaap",
                "data": [
                    {"cik": 320193, "val": 10, "accn": "a", "entityName": "Apple"}
                ],
            }

        return _fetch

    async def _companies(use_cache=True):
        return _frame_companies()

    with patch.object(fr, "get_all_companies", _companies):
        with patch.object(fr, "fetch_data", _make_fetch("shares")):
            asyncio.run(
                fr.get_universe_quarter4(
                    fact="WeightedAverageNumberOfDilutedSharesOutstanding", year=2023
                )
            )
        with patch.object(fr, "fetch_data", _make_fetch("per_share")):
            asyncio.run(
                fr.get_universe_quarter4(fact="EarningsPerShareBasic", year=2023)
            )
    assert captured["shares"] and all("/shares/" in u for u in captured["shares"])
    assert captured["per_share"] and all(
        "/USD-per-shares/" in u for u in captured["per_share"]
    )


def test_enrich_entry_prefers_frame_over_end_month():
    """A frame id drives calendar alignment; without one, the nearest-quarter
    heuristic still aligns an Apr 30 period end to Q1 (not the end-month Q2)."""
    framed = fr._enrich_entry(
        {"start": "2026-02-01", "end": "2026-04-30", "val": 1, "frame": "CY2026Q1"}
    )
    assert framed["calendar_period"] == "Q1"
    assert framed["calendar_year"] == 2026
    unframed = fr._enrich_entry({"start": "2026-02-01", "end": "2026-04-30", "val": 1})
    assert unframed["calendar_period"] == "Q1"
    assert unframed["calendar_year"] == 2026


_OFFCAL_CONCEPT_RESP = {
    "cik": 104169,
    "taxonomy": "us-gaap",
    "tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
    "label": "Revenue from Contract with Customer, Excluding Assessed Tax",
    "description": "d",
    "entityName": "WALMART INC.",
    "units": {
        "USD": [
            {  # fiscal Q1 (Feb-Apr); SEC frames it as calendar Q1
                "fy": 2027,
                "fp": "Q1",
                "filed": "2026-05-30",
                "start": "2026-02-01",
                "end": "2026-04-30",
                "val": 175_680_000_000,
                "accn": "q1",
                "frame": "CY2026Q1",
            },
            {  # fiscal Q2 standalone (May-Jul); SEC frames it as calendar Q2
                "fy": 2027,
                "fp": "Q2",
                "filed": "2026-08-30",
                "start": "2026-05-01",
                "end": "2026-07-31",
                "val": 180_000_000_000,
                "accn": "q2",
                "frame": "CY2026Q2",
            },
        ]
    },
}


def test_get_concept_offcalendar_filer_aligned_by_frame():
    """An off-calendar filer's quarter is aligned by its SEC frame, not the month
    of the period end.

    Regression: Walmart's Feb-Apr 2026 quarter (frame CY2026Q1) must answer a
    calendar-Q1 request, not a Q2 request (its period ends Apr 30).
    """
    fact = "RevenueFromContractWithCustomerExcludingAssessedTax"

    async def _symbol_map(ticker, *a, **k):
        return "0000104169"

    async def _fetch(url, use_cache, persist):
        return _OFFCAL_CONCEPT_RESP

    with (
        patch.object(fr, "symbol_map", _symbol_map),
        patch.object(fr, "fetch_data", _fetch),
    ):
        q1 = asyncio.run(
            fr.get_concept("WMT", fact=fact, year=2026, calendar_period="q1")
        )
        q2 = asyncio.run(
            fr.get_concept("WMT", fact=fact, year=2026, calendar_period="q2")
        )
    # Calendar Q1 -> the Feb-Apr period (ends 2026-04-30), labelled Q1.
    assert len(q1["data"]) == 1
    assert q1["data"][0]["end"] == "2026-04-30"
    assert q1["data"][0]["calendar_period"] == "Q1"
    # Calendar Q2 -> the May-Jul period, not the Feb-Apr one.
    assert len(q2["data"]) == 1
    assert q2["data"][0]["end"] == "2026-07-31"
    assert q2["data"][0]["calendar_period"] == "Q2"
