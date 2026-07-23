"""Tests for SEC investment adviser searches."""

from __future__ import annotations

import asyncio
from datetime import date
from json import dumps
from urllib.parse import parse_qs, urlparse

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_sec.models import adviser_search
from openbb_sec.models.adviser_search import (
    SecAdviserFirmsData,
    SecAdviserFirmsFetcher,
    SecAdviserIndividualsData,
    SecAdviserIndividualsFetcher,
    SecAdviserSearchQueryParams,
)


@pytest.mark.parametrize("query", [None, "", "   "])
def test_adviser_search_requires_query(query: str | None) -> None:
    """Adviser searches require nonblank text."""
    params = {} if query is None else {"query": query}

    with pytest.raises(ValidationError):
        SecAdviserSearchQueryParams(**params)


def test_adviser_search_normalizes_query_and_bounds_limit() -> None:
    """Adviser searches strip query text and bound result counts."""
    query = SecAdviserSearchQueryParams(query="  123456  ")

    assert query.query == "123456"
    assert query.limit == 20
    assert query.use_cache is True

    with pytest.raises(ValidationError):
        SecAdviserSearchQueryParams(query="adviser", limit=101)


@pytest.mark.parametrize("address_as_json", [False, True])
def test_firm_search_normalizes_flat_results(
    monkeypatch,
    address_as_json: bool,
) -> None:
    """Firm search uses IAPD and returns flat records."""
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
                        "firm_branches_count": 7,
                        "firm_ia_address_details": address,
                    },
                    "highlight": {"firm_name": ["<em>BLACKROCK</em> ADVISORS, LLC"]},
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
    query = SecAdviserSearchQueryParams(
        query="blackrock",
        limit=12,
        use_cache=False,
    )

    records = asyncio.run(SecAdviserFirmsFetcher.aextract_data(query, None))

    assert urlparse(calls[0][0]).path == "/search/firm"
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
            "branch_count": 7,
            "address_line_1": "50 HUDSON YARDS",
            "address_line_2": "FLOOR 12",
            "city": "NEW YORK",
            "state": "NY",
            "postal_code": "10001",
            "country": "United States",
        }
    ]


def test_firm_search_keeps_state_advisers_without_sec_number() -> None:
    """State-registered adviser firms remain valid without an SEC number."""
    record = adviser_search._firm_record(
        {
            "firm_source_id": "123456",
            "firm_name": "STATE ADVISER LLC",
            "firm_ia_scope": "ACTIVE",
        }
    )

    assert record is not None
    assert record["crd"] == "123456"
    assert record["sec_number"] is None


def test_firm_search_filters_broker_dealers() -> None:
    """Broker-dealer-only firms are not exposed as investment advisers."""
    record = adviser_search._firm_record(
        {
            "firm_source_id": "38642",
            "firm_bd_full_sec_number": "8-48436",
            "firm_name": "BLACKROCK INVESTMENTS, LLC",
        }
    )

    assert record is None


def test_individual_search_normalizes_flat_results(monkeypatch) -> None:
    """Individual search returns scalar identity and adviser status fields."""
    payload = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "ind_source_id": "4346806",
                        "ind_firstname": "JOHN",
                        "ind_middlename": "T.",
                        "ind_lastname": "SMITH",
                        "ind_ia_scope": "Active",
                        "ind_bc_scope": "InActive",
                        "ind_industry_cal_date_iapd": "2001-05-01",
                        "ind_employments_count": 3,
                        "ind_approved_finra_registration_count": 1,
                        "ind_ia_current_employments": [
                            {
                                "firm_id": "104555",
                                "firm_name": "STRATEGIC ADVISERS LLC",
                                "firm_ia_full_sec_number": "801-13243",
                                "firm_bd_full_sec_number": "8-11111",
                            },
                            {
                                "firm_id": "104555",
                                "firm_name": "STRATEGIC ADVISERS LLC",
                                "firm_ia_full_sec_number": "801-13243",
                                "firm_bd_full_sec_number": "8-11111",
                            },
                            {
                                "firm_id": "7784",
                                "firm_name": "FIDELITY BROKERAGE SERVICES LLC",
                                "firm_bd_full_sec_number": "8-23292",
                            },
                        ],
                    }
                }
            ]
        }
    }
    calls: list[str] = []

    async def fake_cached_request(url: str, **_kwargs: object) -> object:
        calls.append(url)
        return payload

    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_request",
        fake_cached_request,
    )
    query = SecAdviserSearchQueryParams(query="john smith", limit=1)

    records = asyncio.run(SecAdviserIndividualsFetcher.aextract_data(query, None))

    assert urlparse(calls[0]).path == "/search/individual"
    assert parse_qs(urlparse(calls[0]).query) == {
        "query": ["john smith"],
        "nrows": ["100"],
    }
    assert records == [
        {
            "crd": "4346806",
            "first_name": "JOHN",
            "middle_name": "T.",
            "last_name": "SMITH",
            "suffix": None,
            "status": "Active",
            "broker_dealer_status": "InActive",
            "industry_start_date": date(2001, 5, 1),
            "industry_days": None,
            "employment_count": 3,
            "finra_registration_count": 1,
            "current_firm_crd": "104555",
            "current_firm_name": "STRATEGIC ADVISERS LLC",
            "current_firm_ia_sec_number": "801-13243",
            "current_firm_bd_sec_number": "8-11111",
        },
    ]


@pytest.mark.parametrize("status", [None, "NotInScope", "notinscope"])
def test_individual_search_filters_non_advisers(status: str | None) -> None:
    """Individuals outside IAPD adviser scope are excluded."""
    records = adviser_search._individual_records(
        {
            "ind_source_id": "6808119",
            "ind_firstname": "John",
            "ind_lastname": "Smith",
            "ind_ia_scope": status,
            "ind_bc_scope": "Active",
        }
    )

    assert records == []


def test_individual_search_exposes_suffix_and_industry_days() -> None:
    """Individual search retains scalar identity fields from IAPD."""
    records = adviser_search._individual_records(
        {
            "ind_source_id": "2265605",
            "ind_firstname": "John",
            "ind_middlename": "Charles",
            "ind_lastname": "Smith",
            "ind_namesuffix": "Jr",
            "ind_other_names": ["CHUCK SMITH"],
            "ind_ia_scope": "InActive",
            "ind_industry_days_iapd": "7190",
        }
    )

    assert records[0]["suffix"] == "Jr"
    assert records[0]["industry_days"] == 7190


@pytest.mark.parametrize(
    ("fetcher", "query"),
    [
        (
            SecAdviserFirmsFetcher,
            SecAdviserSearchQueryParams(query="blackrock", limit=1),
        ),
        (
            SecAdviserIndividualsFetcher,
            SecAdviserSearchQueryParams(query="john smith", limit=1),
        ),
    ],
)
def test_adviser_search_applies_limit_after_filtering(
    monkeypatch,
    fetcher,
    query,
) -> None:
    """Non-adviser hits do not consume the requested result count."""
    if fetcher is SecAdviserFirmsFetcher:
        sources = [
            {
                "firm_source_id": "38642",
                "firm_bd_full_sec_number": "8-48436",
                "firm_name": "BROKER DEALER LLC",
            },
            {
                "firm_source_id": "164594",
                "firm_ia_full_sec_number": "801-76926",
                "firm_name": "ADVISER ONE LLC",
                "firm_ia_scope": "ACTIVE",
            },
            {
                "firm_source_id": "106843",
                "firm_ia_full_sec_number": "801-51087",
                "firm_name": "ADVISER TWO LLC",
                "firm_ia_scope": "ACTIVE",
            },
        ]
    else:
        sources = [
            {
                "ind_source_id": "1",
                "ind_firstname": "Broker",
                "ind_lastname": "Only",
                "ind_ia_scope": "NotInScope",
            },
            {
                "ind_source_id": "2",
                "ind_firstname": "Adviser",
                "ind_lastname": "One",
                "ind_ia_scope": "Active",
            },
            {
                "ind_source_id": "3",
                "ind_firstname": "Adviser",
                "ind_lastname": "Two",
                "ind_ia_scope": "Active",
            },
        ]
    payload = {"hits": {"hits": [{"_source": source} for source in sources]}}

    async def fake_cached_request(*_args: object, **_kwargs: object) -> object:
        return payload

    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_request",
        fake_cached_request,
    )

    records = asyncio.run(fetcher.aextract_data(query, None))

    assert len(records) == 1
    assert records[0]["crd"] in {"164594", "2"}


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
    with pytest.raises(OpenBBError, match="Invalid IAPD search response"):
        adviser_search.iapd_sources(payload, "search")


def test_parser_rejects_iapd_application_error() -> None:
    """HTTP-200 IAPD error envelopes are surfaced to callers."""
    with pytest.raises(OpenBBError, match="IAPD search failed with error 400"):
        adviser_search.iapd_sources(
            {
                "errorCode": "400",
                "errorMessage": "Invalid query",
            },
            "search",
        )


def test_firm_search_rejects_malformed_address() -> None:
    """Malformed embedded address JSON is an explicit provider error."""
    with pytest.raises(OpenBBError, match="invalid JSON in firm address details"):
        adviser_search._firm_record(
            {
                "firm_source_id": "164594",
                "firm_ia_full_sec_number": "801-76926",
                "firm_name": "BLACKROCK ADVISORS, LLC",
                "firm_ia_address_details": "not-json",
            }
        )


@pytest.mark.parametrize(
    ("fetcher", "query", "message"),
    [
        (
            SecAdviserFirmsFetcher,
            SecAdviserSearchQueryParams(query="no such firm"),
            "No investment adviser firms",
        ),
        (
            SecAdviserIndividualsFetcher,
            SecAdviserSearchQueryParams(query="no such individual"),
            "No investment adviser individuals",
        ),
    ],
)
def test_adviser_search_raises_for_empty_results(
    monkeypatch,
    fetcher,
    query,
    message: str,
) -> None:
    """Valid searches without adviser results raise explicit empty errors."""

    async def fake_cached_request(*_args: object, **_kwargs: object) -> object:
        return {"hits": {"hits": []}}

    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_request",
        fake_cached_request,
    )

    with pytest.raises(EmptyDataError, match=message):
        asyncio.run(fetcher.aextract_data(query, None))


def test_adviser_models_are_flat() -> None:
    """Firm and individual models contain scalar values only."""
    firm = SecAdviserFirmsData.model_validate(
        {
            "crd": "164594",
            "sec_number": None,
            "name": "BLACKROCK ADVISORS, LLC",
            "status": "ACTIVE",
            "branch_count": 7,
        }
    )
    individual = SecAdviserIndividualsData.model_validate(
        {
            "crd": "4346806",
            "first_name": "JOHN",
            "middle_name": "T.",
            "last_name": "SMITH",
            "suffix": None,
            "status": "Active",
            "broker_dealer_status": "InActive",
            "industry_start_date": date(2001, 5, 1),
            "industry_days": None,
            "employment_count": 3,
            "finra_registration_count": 1,
            "current_firm_crd": "104555",
            "current_firm_name": "STRATEGIC ADVISERS LLC",
            "current_firm_ia_sec_number": "801-13243",
            "current_firm_bd_sec_number": "8-11111",
        }
    )

    for record in (firm, individual):
        assert all(
            value is None or isinstance(value, date | str | int)
            for value in record.model_dump().values()
        )
