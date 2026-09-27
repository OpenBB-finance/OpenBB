"""Offline provider acceptance tests using SEC-derived facts fixtures."""

import asyncio
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

import pytest
from openbb_arkleon import arkleon_provider
from openbb_arkleon.models.balance_sheet import (
    BALANCE_SHEET_TAGS,
    ArkleonBalanceSheetData,
    ArkleonBalanceSheetFetcher,
    ArkleonBalanceSheetQueryParams,
)
from openbb_arkleon.models.cash_flow import (
    CASH_FLOW_TAGS,
    ArkleonCashFlowStatementData,
    ArkleonCashFlowStatementFetcher,
    ArkleonCashFlowStatementQueryParams,
)
from openbb_arkleon.models.income_statement import (
    INCOME_STATEMENT_TAGS,
    ArkleonIncomeStatementData,
    ArkleonIncomeStatementFetcher,
    ArkleonIncomeStatementQueryParams,
)
from openbb_arkleon.utils import client
from openbb_arkleon.utils.statements import (
    build_records,
    is_consolidated,
    order_and_limit,
    validate_cik,
)
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic import ValidationError

FIXTURES = Path(__file__).parent / "fixtures"
TEST_KEY = "ak_fixture_test_key"
CIK_MESSAGE = (
    "Arkleon /v1 is addressed by CIK: pass the company's SEC CIK (digits only) "
    "as symbol. Tickers are not served by /v1."
)
QUERY_TYPES = (
    ArkleonBalanceSheetQueryParams,
    ArkleonIncomeStatementQueryParams,
    ArkleonCashFlowStatementQueryParams,
)


def read_fixture(tag="Assets", duration=0, unit="USD", suffix=""):
    """Load the facts fixture for the requested tag, duration, unit, and page."""
    return json.loads(
        (FIXTURES / f"facts_{tag}_{duration}_{unit.replace('/', '_')}{suffix}.json").read_text()
    )


class FakeResponse:
    """Represent an HTTP response with a configurable body and status."""

    def __init__(self, body, status_code=200):
        """Store the response body and HTTP status."""
        self.body = body
        self.status_code = status_code

    def json(self):
        """Return the response body."""
        return self.body


@pytest.fixture
def fake_requests(monkeypatch):
    """Replace HTTP requests with fixture responses and record each call."""
    calls = []

    def fake(url, *, method, timeout, headers, params):
        """Record request parameters and return facts within the filing cutoff."""
        calls.append({
            "url": url, "method": method, "timeout": timeout,
            "headers": dict(headers), "params": dict(params),
        })
        suffix = ""
        if params["tag"] == "Assets":
            cursor = params.get("cursor")
            assert cursor in (None, "fixture-cursor-2")
            suffix = "_page2" if cursor else "_page1"
        else:
            assert "cursor" not in params
        body = read_fixture(
            params["tag"], params["duration_quarters"], params["unit"], suffix
        )
        # The server contract filters filing dates, including on later pages.
        body["data"] = [fact for fact in body["data"] if fact["filed"] <= params["as_of"]]
        return FakeResponse(body)

    monkeypatch.setattr(client, "make_request", fake)
    return calls


def test_provider_registration():
    """Check the provider name, credentials, and registered statement fetchers."""
    assert arkleon_provider.name == "arkleon"
    assert arkleon_provider.credentials == ["arkleon_api_key"]
    assert arkleon_provider.fetcher_dict == {
        "BalanceSheet": ArkleonBalanceSheetFetcher,
        "IncomeStatement": ArkleonIncomeStatementFetcher,
        "CashFlowStatement": ArkleonCashFlowStatementFetcher,
    }
    assert all(not fetcher.require_credentials for fetcher in arkleon_provider.fetcher_dict.values())


@pytest.mark.parametrize("symbol", ["320193", " 0000320193 "])
def test_valid_cik(symbol):
    """Check that numeric CIK inputs are normalized to integers."""
    assert validate_cik(symbol) == 320193


@pytest.mark.parametrize("symbol", ["AAPL", "", "12345678901", "32.0193", "٣٢٠١٩٣"])
def test_invalid_cik(symbol):
    """Check that invalid CIK inputs raise the expected error."""
    with pytest.raises(OpenBBError) as error:
        validate_cik(symbol)
    assert str(error.value) == CIK_MESSAGE


@pytest.mark.parametrize("query_type", QUERY_TYPES)
def test_as_of_is_required(query_type):
    """Check that every statement query requires a filing cutoff date."""
    with pytest.raises(ValidationError) as error:
        query_type(symbol="320193")
    assert any(item["loc"] == ("as_of",) and item["type"] == "missing" for item in error.value.errors())


def test_api_key_resolution(monkeypatch):
    """Check credential precedence, environment fallback, and missing key errors."""
    monkeypatch.setenv("ARKLEON_API_KEY", "ak_environment_test")
    assert client.resolve_api_key({"arkleon_api_key": TEST_KEY}) == TEST_KEY
    for credentials in (None, {}, {"arkleon_api_key": ""}, {"arkleon_api_key": None}):
        assert client.resolve_api_key(credentials) == "ak_environment_test"
    monkeypatch.delenv("ARKLEON_API_KEY")
    with pytest.raises(OpenBBError) as error:
        client.resolve_api_key(None)
    assert str(error.value) == (
        "Missing Arkleon API key: set ARKLEON_API_KEY or obb.user.credentials.arkleon_api_key."
    )
    assert TEST_KEY not in str(error.value)
    assert "ak_environment_test" not in str(error.value)
    monkeypatch.setenv("ARKLEON_API_KEY", "")
    with pytest.raises(OpenBBError):
        client.resolve_api_key({"arkleon_api_key": ""})


def test_assets_pagination(fake_requests):
    """Check that fact requests follow pagination and preserve request parameters."""
    facts = client.fetch_facts(TEST_KEY, 320193, "2021-12-31", "Assets", 0, "USD")
    assert facts == read_fixture()["data"]
    assert len(fake_requests) == 2
    first, second = fake_requests
    assert "cursor" not in first["params"]
    assert second["params"] == {**first["params"], "cursor": "fixture-cursor-2"}
    for call in fake_requests:
        assert call["url"] == "https://arkleon.com/v1/facts"
        assert call["method"] == "GET"
        assert call["timeout"] == 30
        assert call["headers"] == {"Authorization": f"Bearer {TEST_KEY}"}
        assert call["params"]["as_of"] == "2021-12-31"
        assert call["params"]["cik"] == 320193
        assert call["params"]["duration_quarters"] == 0
        assert call["params"]["unit"] == "USD"
        assert call["params"]["limit"] == 1000


def test_balance_sheet_preserves_filings(fake_requests):
    """Check that multiple filings for the same reporting period are preserved."""
    by_period = defaultdict(set)
    for fact in read_fixture()["data"]:
        if is_consolidated(fact):
            by_period[fact["period_end"]].add((fact["accession_id"], fact["filed"]))
    period = next(
        period for period, filings in by_period.items()
        if len({filed for _, filed in filings}) >= 2
    )
    records = asyncio.run(ArkleonBalanceSheetFetcher.fetch_data(
        {"symbol": "320193", "as_of": "2021-12-31", "limit": None},
        {"arkleon_api_key": TEST_KEY},
    ))
    matching = [
        record for record in records
        if record.period_ending.isoformat() == period and record.total_assets is not None
    ]
    assert {(record.accession_id, record.filed.isoformat()) for record in matching} == by_period[period]
    assert len({record.filed for record in matching}) >= 2


def test_synthetic_segment_is_dropped():
    """Check that segmented facts are excluded from consolidated records."""
    facts = read_fixture()["data"]
    segmented = [fact for fact in facts if fact["segments"] == "fixture-segment"]
    assert len(segmented) == 1
    assert build_records({"total_assets": segmented}, BALANCE_SHEET_TAGS) == []
    consolidated = [fact for fact in facts if is_consolidated(fact)]
    # Put the segment first with a distinguishable value to expose accidental selection.
    segment = {**segmented[0], "value": -123.0}
    assert build_records({"total_assets": [segment, *consolidated]}, BALANCE_SHEET_TAGS) == build_records(
        {"total_assets": consolidated}, BALANCE_SHEET_TAGS
    )


@pytest.mark.parametrize("segments,coreg,expected", [
    (None, None, True), ("", None, True), (None, "", True), ("", "", True),
    ("segment", "", False), ("", "subsidiary", False),
])
def test_consolidated_identity(segments, coreg, expected):
    """Check which segment and coreg values identify consolidated facts."""
    assert is_consolidated({"segments": segments, "coreg": coreg}) is expected


def test_revenue_precedence_and_first_response_value():
    """Check revenue tag precedence, duplicate selection, and filing separation."""
    base = {
        "accession_id": "0000320193-21-000001", "tag": "Revenues", "taxonomy": "us-gaap",
        "period_end": "2020-09-26", "duration_quarters": 4, "unit": "USD",
        "segments": "", "coreg": "", "value": 10, "form": "10-K",
        "filed": "2021-01-01", "cik": 320193, "source_url": None,
    }
    preferred = {**base, "tag": INCOME_STATEMENT_TAGS["revenue"][0], "value": 20}
    duplicate = {**preferred, "value": 30}
    later_filing = {**base, "accession_id": "0000320193-21-000002", "filed": "2021-02-01", "value": 40}
    records = build_records(
        {"revenue": [base, preferred, duplicate, later_filing]}, INCOME_STATEMENT_TAGS
    )
    assert len(records) == 2
    assert records[0]["revenue"] == 20.0
    assert records[1]["revenue"] == 40.0
    assert records[0]["gross_profit"] is None
    assert records[0]["cost_of_revenue"] is None
    assert isinstance(records[0]["revenue"], float)
    assert records[0]["filed"] == date(2021, 1, 1)


@pytest.mark.parametrize("limit,expected", [(2, ["e", "d", "c", "b"]), (0, []), (None, ["e", "d", "c", "b", "a"])])
def test_order_and_distinct_period_limit(limit, expected):
    """Check record ordering and limits on distinct reporting periods."""
    records = [
        {"period_ending": date(2020, 1, 1), "filed": date(2021, 1, 1), "accession_id": "a"},
        {"period_ending": date(2021, 1, 1), "filed": date(2021, 2, 1), "accession_id": "b"},
        {"period_ending": date(2021, 1, 1), "filed": date(2021, 3, 1), "accession_id": "c"},
        {"period_ending": date(2021, 1, 1), "filed": date(2021, 3, 1), "accession_id": "d"},
        {"period_ending": date(2022, 1, 1), "filed": date(2022, 2, 1), "accession_id": "e"},
    ]
    assert [record["accession_id"] for record in order_and_limit(records, limit)] == expected
    assert records[0]["accession_id"] == "a"


@pytest.mark.parametrize("body,code", [
    ({"error": "invalid_request", "message": "Bad request"}, "invalid_request"),
    ({"message": "Missing error code"}, "unknown"),
    (None, "unknown"),
])
def test_http_error(monkeypatch, body, code):
    """Check HTTP error messages and ensure they omit the API key."""
    monkeypatch.setattr(client, "make_request", lambda *args, **kwargs: FakeResponse(body, 400))
    with pytest.raises(OpenBBError) as error:
        client.fetch_facts(TEST_KEY, 320193, "2021-12-31", "Assets", 0, "USD")
    assert str(error.value) == f"Arkleon /v1/facts returned 400: {code}"
    assert TEST_KEY not in str(error.value)


def test_non_json_http_error(monkeypatch):
    """Check that a non-JSON HTTP error produces an unknown error code."""
    class NonJsonResponse:
        """Represent an HTTP error response whose body is not JSON."""

        status_code = 502

        def json(self):
            """Raise an error when the response body is parsed as JSON."""
            raise ValueError("Not JSON")

    monkeypatch.setattr(client, "make_request", lambda *args, **kwargs: NonJsonResponse())
    with pytest.raises(OpenBBError, match="502: unknown"):
        client.fetch_facts(TEST_KEY, 320193, "2021-12-31", "Assets", 0, "USD")


@pytest.mark.parametrize("fetcher,data_type,tag_map,period,duration", [
    (ArkleonBalanceSheetFetcher, ArkleonBalanceSheetData, BALANCE_SHEET_TAGS, None, 0),
    (ArkleonIncomeStatementFetcher, ArkleonIncomeStatementData, INCOME_STATEMENT_TAGS, "annual", 4),
    (ArkleonIncomeStatementFetcher, ArkleonIncomeStatementData, INCOME_STATEMENT_TAGS, "quarter", 1),
    (ArkleonCashFlowStatementFetcher, ArkleonCashFlowStatementData, CASH_FLOW_TAGS, "annual", 4),
    (ArkleonCashFlowStatementFetcher, ArkleonCashFlowStatementData, CASH_FLOW_TAGS, "quarter", 1),
])
def test_full_pipeline_as_filed(fake_requests, monkeypatch, fetcher, data_type, tag_map, period, duration):
    """Check statement values, filing cutoffs, periods, and request parameters against fixtures."""
    monkeypatch.setenv("ARKLEON_API_KEY", TEST_KEY)
    params = {"symbol": "0000320193", "as_of": "2020-12-31", "limit": 2}
    if period:
        params["period"] = period
    records = asyncio.run(fetcher.fetch_data(params, credentials=None))
    assert records
    assert all(isinstance(record, data_type) for record in records)
    assert all(record.filed <= date(2020, 12, 31) for record in records)
    assert all(record.duration_quarters == duration for record in records)
    assert all(record.fiscal_year is None and record.fiscal_period is None for record in records)
    assert len({record.period_ending for record in records}) == 2
    assert {call["params"]["tag"] for call in fake_requests} == {
        tag for tags in tag_map.values() for tag in tags
    }
    for call in fake_requests:
        assert call["params"]["as_of"] == "2020-12-31"
        assert call["params"]["duration_quarters"] == duration
        assert call["params"]["cik"] == 320193
        assert "ticker" not in call["params"]
        assert call["headers"] == {"Authorization": f"Bearer {TEST_KEY}"}
        expected_unit = "USD/shares" if call["params"]["tag"].startswith("EarningsPerShare") else "USD"
        assert call["params"]["unit"] == expected_unit
    for record in records:
        for field, tags in tag_map.items():
            unit = "USD/shares" if field in ("eps_basic", "eps_diluted") else "USD"
            expected = None
            for tag in tags:
                matches = [
                    fact for fact in read_fixture(tag, duration, unit)["data"]
                    if fact["accession_id"] == record.accession_id
                    and fact["period_end"] == record.period_ending.isoformat()
                    and is_consolidated(fact)
                ]
                if matches:
                    expected = float(matches[0]["value"])
                    assert record.source_url == matches[0]["source_url"]
                    break
            assert getattr(record, field) == expected


@pytest.mark.parametrize("query_type", QUERY_TYPES[1:])
def test_duration_period_validation(query_type):
    """Check the default annual period and rejection of year-to-date queries."""
    assert query_type(symbol="320193", as_of="2021-12-31").period == "annual"
    with pytest.raises(ValidationError):
        query_type(symbol="320193", as_of="2021-12-31", period="ytd")
