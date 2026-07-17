"""Tests for SEC investment adviser firm search."""

from __future__ import annotations

import asyncio
from json import dumps
from urllib.parse import parse_qs, urlparse

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_sec.models import investment_advisers
from openbb_sec.models.investment_advisers import (
    SecInvestmentAdvisersData,
    SecInvestmentAdvisersFetcher,
    SecInvestmentAdvisersQueryParams,
)


@pytest.mark.parametrize("query", [None, "", "   "])
def test_investment_advisers_requires_query(query: str | None) -> None:
    """Firm search requires a nonblank query."""
    params = {} if query is None else {"query": query}

    with pytest.raises(ValidationError):
        SecInvestmentAdvisersQueryParams(**params)


def test_investment_advisers_query_is_normalized() -> None:
    """Search text is stripped and limits are bounded at the query boundary."""
    query = SecInvestmentAdvisersQueryParams(query="  801-12345  ")

    assert query.query == "801-12345"
    assert query.limit == 20
    assert query.use_cache is True

    with pytest.raises(ValidationError):
        SecInvestmentAdvisersQueryParams(query="blackrock", limit=101)


@pytest.mark.parametrize("address_as_json", [False, True])
def test_fetcher_searches_iapd_and_normalizes_results(
    monkeypatch,
    address_as_json: bool,
) -> None:
    """The fetcher uses the async cache and returns flat firm rows."""
    address: dict[str, object] | str = {
        "officeAddress": {
            "street1": "50 HUDSON YARDS",
            "street2": "FLOOR 12",
            "city": "NEW YORK",
            "state": "NY",
            "postalCode": "10001",
            "country": "United States",
        }
    }
    if address_as_json:
        address = dumps(address)
    payload = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "firm_source_id": "164594",
                        "firm_ia_full_sec_number": "801-76926",
                        "firm_name": "BLACKROCK ADVISORS, LLC",
                        "firm_ia_scope": "ACTIVE",
                        "firm_ia_address_details": address,
                    }
                }
            ]
        }
    }
    calls: list[tuple[str, dict[str, object]]] = []

    async def fake_cached_request(url: str, **kwargs: object) -> object:
        calls.append((url, kwargs))
        return payload

    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_request",
        fake_cached_request,
    )
    query = SecInvestmentAdvisersQueryParams(
        query="blackrock",
        limit=12,
        use_cache=False,
    )

    records = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))

    assert parse_qs(urlparse(calls[0][0]).query) == {
        "query": ["blackrock"],
        "nrows": ["100"],
    }
    assert calls[0][1]["use_cache"] is False
    assert records == [
        {
            "crd": "164594",
            "sec_number": "801-76926",
            "name": "BLACKROCK ADVISORS, LLC",
            "status": "ACTIVE",
            "address_line_1": "50 HUDSON YARDS",
            "address_line_2": "FLOOR 12",
            "city": "NEW YORK",
            "state": "NY",
            "postal_code": "10001",
            "country": "United States",
        }
    ]


def test_state_registered_adviser_does_not_require_sec_number() -> None:
    """IAPD state advisers remain valid without an SEC file number."""
    records = investment_advisers._parse_iapd_records(
        {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "firm_source_id": "123456",
                            "firm_name": "STATE ADVISER LLC",
                            "firm_ia_scope": "ACTIVE",
                        }
                    }
                ]
            }
        }
    )

    assert records[0]["crd"] == "123456"
    assert records[0]["sec_number"] is None


def test_broker_dealer_only_hits_are_filtered() -> None:
    """Broker-dealer-only hits are not exposed as investment advisers."""
    records = investment_advisers._parse_iapd_records(
        {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "firm_source_id": "38642",
                            "firm_bd_full_sec_number": "8-48436",
                            "firm_name": "BLACKROCK INVESTMENTS, LLC",
                        }
                    }
                ]
            }
        }
    )

    assert records == []


def test_fetcher_applies_limit_after_filtering_broker_dealers(monkeypatch) -> None:
    """Broker-dealer hits do not consume the requested adviser result count."""
    hits = [
        {
            "_source": {
                "firm_source_id": "38642",
                "firm_bd_full_sec_number": "8-48436",
                "firm_name": "BLACKROCK INVESTMENTS, LLC",
            }
        },
        {
            "_source": {
                "firm_source_id": "164594",
                "firm_ia_full_sec_number": "801-76926",
                "firm_name": "BLACKROCK ADVISORS, LLC",
                "firm_ia_scope": "ACTIVE",
            }
        },
        {
            "_source": {
                "firm_source_id": "106843",
                "firm_ia_full_sec_number": "801-51087",
                "firm_name": "BLACKROCK INTERNATIONAL LIMITED",
                "firm_ia_scope": "ACTIVE",
            }
        },
    ]

    async def fake_cached_request(*_args: object, **_kwargs: object) -> object:
        return {"hits": {"hits": hits}}

    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_request",
        fake_cached_request,
    )
    query = SecInvestmentAdvisersQueryParams(query="blackrock", limit=1)

    records = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))

    assert [record["crd"] for record in records] == ["164594"]


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"hits": []},
        {"hits": {"hits": {}}},
        {"hits": {"hits": [None]}},
        {"hits": {"hits": [{}]}},
    ],
)
def test_parser_rejects_invalid_iapd_response(payload: object) -> None:
    """Malformed IAPD responses raise an actionable provider error."""
    with pytest.raises(OpenBBError, match="Invalid IAPD firm search response"):
        investment_advisers._parse_iapd_records(payload)


def test_parser_rejects_iapd_application_error() -> None:
    """HTTP-200 IAPD error envelopes are surfaced to callers."""
    with pytest.raises(OpenBBError, match="IAPD firm search failed with error 400"):
        investment_advisers._parse_iapd_records(
            {
                "errorCode": "400",
                "errorMessage": "Invalid query",
            }
        )


def test_parser_rejects_malformed_address() -> None:
    """Malformed embedded address JSON is an explicit provider error."""
    payload = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "firm_source_id": "164594",
                        "firm_ia_full_sec_number": "801-76926",
                        "firm_name": "BLACKROCK ADVISORS, LLC",
                        "firm_ia_address_details": "not-json",
                    }
                }
            ]
        }
    }

    with pytest.raises(OpenBBError, match="address details contain invalid JSON"):
        investment_advisers._parse_iapd_records(payload)


def test_fetcher_raises_for_valid_empty_result(monkeypatch) -> None:
    """A valid search with no adviser firms is an explicit empty result."""

    async def fake_cached_request(*_args: object, **_kwargs: object) -> object:
        return {"hits": {"hits": []}}

    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_request",
        fake_cached_request,
    )
    query = SecInvestmentAdvisersQueryParams(query="no such adviser")

    with pytest.raises(EmptyDataError, match="No investment adviser firms"):
        asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))


def test_investment_adviser_data_model_is_flat() -> None:
    """The public record is a scalar, DataFrame-compatible row."""
    record = SecInvestmentAdvisersData.model_validate(
        {
            "crd": "164594",
            "sec_number": None,
            "name": "BLACKROCK ADVISORS, LLC",
            "status": "ACTIVE",
            "address_line_1": "50 HUDSON YARDS",
            "address_line_2": None,
            "city": "NEW YORK",
            "state": "NY",
            "postal_code": "10001",
            "country": "United States",
        }
    )

    assert all(
        value is None or isinstance(value, str)
        for value in record.model_dump().values()
    )
