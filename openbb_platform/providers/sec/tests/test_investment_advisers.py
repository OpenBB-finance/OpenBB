"""Tests for SEC investment adviser records."""

from __future__ import annotations

import asyncio
from json import dumps
from urllib.parse import parse_qs, urlparse

import pytest

from openbb_sec.models import investment_advisers
from openbb_sec.models.investment_advisers import (
    AdviserReportLink,
    SecInvestmentAdvisersFetcher,
    SecInvestmentAdvisersQueryParams,
    load_investment_adviser_records,
    normalize_adviser_report_bytes,
    select_current_adviser_report_links,
)


def test_investment_advisers_requires_selector_or_explicit_snapshot() -> None:
    """Adviser lookup should not bulk-load the current snapshot by accident."""
    with pytest.raises(ValueError, match="query, crd, sec_number, or include_all"):
        SecInvestmentAdvisersQueryParams()
    with pytest.raises(ValueError, match="include_all cannot be combined"):
        SecInvestmentAdvisersQueryParams(query="blackrock", include_all=True)


def test_investment_advisers_include_all_allows_snapshot(monkeypatch) -> None:
    """Full current adviser snapshots require an explicit opt-in."""
    records = [
        {
            "crd": "123",
            "sec_number": "801-123",
            "legal_name": "Acme Capital Management LP",
        }
    ]

    monkeypatch.setattr(
        "openbb_sec.models.investment_advisers.load_investment_adviser_records",
        lambda **_kwargs: records,
    )

    query = SecInvestmentAdvisersQueryParams(include_all=True)
    data = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))

    assert data == records


def test_investment_advisers_fetcher_filters_by_query_and_limit(monkeypatch) -> None:
    """Targeted adviser searches use IAPD instead of current roster files."""
    records = [
        {
            "crd": "123",
            "sec_number": "801-123",
            "legal_name": "Acme Capital Management LP",
            "primary_business_name": "Acme Capital",
            "status": "Approved",
        },
        {
            "crd": "456",
            "sec_number": "801-456",
            "legal_name": "Beta Advisors LLC",
            "primary_business_name": "Beta",
            "status": "Approved",
        },
    ]

    monkeypatch.setattr(
        "openbb_sec.models.investment_advisers.search_investment_adviser_records",
        lambda **_kwargs: records,
    )
    monkeypatch.setattr(
        "openbb_sec.models.investment_advisers.load_investment_adviser_records",
        lambda **_kwargs: pytest.fail("targeted search loaded current roster files"),
    )

    query = SecInvestmentAdvisersQueryParams(query="capital", limit=1)
    data = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))
    result = SecInvestmentAdvisersFetcher.transform_data(query, data)

    assert len(result) == 1
    assert result[0].crd == "123"
    assert result[0].legal_name == "Acme Capital Management LP"
    assert "source_snapshot" not in result[0].model_dump()


def test_investment_advisers_preserves_iapd_phrase_matches(monkeypatch) -> None:
    """IAPD ranking is not discarded by punctuation-sensitive local filtering."""
    record = {
        "crd": "164594",
        "sec_number": "801-76926",
        "legal_name": "BLACKROCK (SINGAPORE) LIMITED",
    }
    monkeypatch.setattr(
        "openbb_sec.models.investment_advisers.search_investment_adviser_records",
        lambda **_kwargs: [record],
    )

    query = SecInvestmentAdvisersQueryParams(query="blackrock singapore")
    data = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))

    assert data == [record]


def test_investment_advisers_fetcher_filters_by_identifiers(monkeypatch) -> None:
    """CRD and SEC number filters are exact identifier filters."""
    records = [
        {
            "crd": "123",
            "sec_number": "801-123",
            "legal_name": "Acme Capital Management LP",
        },
        {
            "crd": "456",
            "sec_number": "801-456",
            "legal_name": "Beta Advisors LLC",
        },
    ]

    monkeypatch.setattr(
        "openbb_sec.models.investment_advisers.search_investment_adviser_records",
        lambda **_kwargs: records,
    )

    query = SecInvestmentAdvisersQueryParams(crd="456", sec_number="801-456")
    data = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))

    assert data == [records[1]]


def test_search_investment_adviser_records_normalizes_iapd_response(
    monkeypatch,
) -> None:
    """IAPD firm search rows map to the public adviser model fields."""
    payload = dumps(
        {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "firm_source_id": "164594",
                            "firm_ia_full_sec_number": "801-76926",
                            "firm_name": "BLACKROCK (SINGAPORE) LIMITED",
                            "firm_other_names": ["BLACKROCK (SINGAPORE) LIMITED"],
                            "firm_ia_scope": "ACTIVE",
                            "firm_ia_address_details": (
                                '{"officeAddress":{"city":"SINGAPORE",'
                                '"country":"Singapore"}}'
                            ),
                        }
                    },
                    {
                        "_source": {
                            "firm_source_id": "38642",
                            "firm_bd_full_sec_number": "8-48436",
                            "firm_name": "BLACKROCK INVESTMENTS, LLC",
                        }
                    },
                ]
            }
        }
    )

    calls: list[tuple[str, dict[str, object]]] = []

    def fake_cached_text(url: str, **kwargs: object) -> str:
        calls.append((url, kwargs))
        return payload

    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_text",
        fake_cached_text,
    )

    records = investment_advisers.search_investment_adviser_records(
        query="blackrock",
        limit=12,
        use_cache=False,
    )

    assert records == [
        {
            "crd": "164594",
            "sec_number": "801-76926",
            "legal_name": "BLACKROCK (SINGAPORE) LIMITED",
            "primary_business_name": "BLACKROCK (SINGAPORE) LIMITED",
            "status": "ACTIVE",
            "city": "SINGAPORE",
            "state": None,
            "country": "Singapore",
            "phone": None,
        }
    ]
    assert calls[0][0].startswith("https://api.adviserinfo.sec.gov/search/firm?")
    assert parse_qs(urlparse(calls[0][0]).query) == {
        "query": ["blackrock"],
        "hl": ["true"],
        "includePrevious": ["true"],
        "nrows": ["12"],
        "start": ["0"],
        "r": ["12"],
        "sort": ["score desc"],
        "wt": ["json"],
    }
    assert calls[0][1]["use_cache"] is False


def test_select_current_adviser_report_links_keeps_latest_registered_and_exempt() -> (
    None
):
    """Only the latest registered and exempt report links are selected."""
    links = [
        AdviserReportLink(
            url=(
                "https://www.sec.gov/files/investment/data/other/"
                "information-about-registered-investment-advisers-exempt-reporting-"
                "advisers/ia06012026-exempt_0.zip"
            ),
            format="zip",
            text="Exempt Investment Advisers, June 2026",
        ),
        AdviserReportLink(
            url=(
                "https://www.sec.gov/files/investment/data/other/"
                "information-about-registered-investment-advisers-exempt-reporting-"
                "advisers/ia060126_0.zip"
            ),
            format="zip",
            text="Registered Investment Advisers, June 2026",
        ),
        AdviserReportLink(
            url="https://www.sec.gov/files/ia050126-exempt.zip",
            format="zip",
            text="Exempt Investment Advisers, May 2026",
        ),
        AdviserReportLink(
            url="https://www.sec.gov/files/ia050126.zip",
            format="zip",
            text="Registered Investment Advisers, May 2026",
        ),
    ]

    selected = select_current_adviser_report_links(links)

    assert [link.text for link in selected] == [
        "Registered Investment Advisers, June 2026",
        "Exempt Investment Advisers, June 2026",
    ]


def test_normalize_adviser_report_bytes_accepts_latin1_csv_bytes() -> None:
    """SEC adviser CSV reports can contain non-UTF-8 text bytes."""
    content = (
        b"CRD Number,SEC Number,Legal Name,Total Employees\n"
        b"123,801-123,\xc4cme Capital,19\n"
    )

    records = normalize_adviser_report_bytes(content, file_name="advisers.csv")

    assert records[0]["crd"] == "123"
    assert records[0]["legal_name"] == "\u00c4cme Capital"
    assert records[0]["employees"] == 19
    assert "source_snapshot" not in records[0]


def test_normalize_adviser_report_bytes_accepts_current_sec_roster_aliases() -> None:
    """Current SEC adviser roster identifiers use hash-suffixed columns."""
    content = (
        b"Organization CRD#,SEC#,Legal Name,Primary Business Name\n"
        b"123,801-123,Acme Capital Management LP,Acme Capital\n"
    )

    records = normalize_adviser_report_bytes(content, file_name="advisers.csv")

    assert records[0]["crd"] == "123"
    assert records[0]["sec_number"] == "801-123"
    assert records[0]["legal_name"] == "Acme Capital Management LP"


def test_load_investment_adviser_records_default_reads_registered_and_exempt(
    monkeypatch,
) -> None:
    """Current adviser report discovery and archives honor the cache flag."""
    links = [
        AdviserReportLink(
            url="https://www.sec.gov/files/registered.csv",
            format="csv",
            text="Registered Investment Advisers",
        ),
        AdviserReportLink(
            url="https://www.sec.gov/files/exempt.csv",
            format="csv",
            text="Exempt Investment Advisers",
        ),
    ]

    calls: list[tuple[str, bool]] = []

    def fake_cached_text(url: str, **kwargs: object) -> str:
        calls.append((url, bool(kwargs["use_cache"])))
        return "<html />"

    def fake_cached_bytes(url: str, **kwargs: object) -> bytes:
        calls.append((url, bool(kwargs["use_cache"])))
        if url.endswith("registered.csv"):
            return b"CRD Number,SEC Number,Legal Name\n1,801-1,Reg"
        if url.endswith("exempt.csv"):
            return b"CRD Number,SEC Number,Legal Name\n2,802-2,Exempt"
        raise AssertionError(f"Unexpected adviser archive URL: {url}")

    monkeypatch.setattr(
        "openbb_sec.models.investment_advisers.parse_adviser_report_links",
        lambda *_args, **_kwargs: links,
    )
    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_text",
        fake_cached_text,
    )
    monkeypatch.setattr(
        "openbb_sec.utils.cache.cached_bytes",
        fake_cached_bytes,
    )

    records = load_investment_adviser_records(use_cache=True)

    assert [record["legal_name"] for record in records] == ["Reg", "Exempt"]
    assert calls == [
        (investment_advisers.ADVISER_REPORTS_URL, True),
        ("https://www.sec.gov/files/registered.csv", True),
        ("https://www.sec.gov/files/exempt.csv", True),
    ]
