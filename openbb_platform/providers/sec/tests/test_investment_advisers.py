"""Tests for SEC investment adviser records."""

from __future__ import annotations

import asyncio

from openbb_sec.models.investment_advisers import (
    AdviserReportLink,
    SecInvestmentAdvisersFetcher,
    SecInvestmentAdvisersQueryParams,
    load_investment_adviser_records,
    normalize_adviser_report_bytes,
    select_current_adviser_report_links,
)


def test_investment_advisers_fetcher_filters_by_query_and_limit(monkeypatch) -> None:
    """Adviser records can be filtered by name-like query."""
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
        "openbb_sec.models.investment_advisers.load_investment_adviser_records",
        lambda **_kwargs: records,
    )

    query = SecInvestmentAdvisersQueryParams(query="capital", limit=1)
    data = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))
    result = SecInvestmentAdvisersFetcher.transform_data(query, data)

    assert len(result) == 1
    assert result[0].crd == "123"
    assert result[0].legal_name == "Acme Capital Management LP"
    assert "source_snapshot" not in result[0].model_dump()


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
        "openbb_sec.models.investment_advisers.load_investment_adviser_records",
        lambda **_kwargs: records,
    )

    query = SecInvestmentAdvisersQueryParams(crd="456", sec_number="801-456")
    data = asyncio.run(SecInvestmentAdvisersFetcher.aextract_data(query, None))

    assert data == [records[1]]


def test_select_current_adviser_report_links_keeps_latest_registered_and_exempt() -> None:
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
    """The cache flag does not change adviser report coverage."""
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

    class Response:
        def __init__(self, *, text: str = "", content: bytes = b"") -> None:
            self.text = text
            self.content = content

        def raise_for_status(self) -> None:
            return None

    def fake_sec_make_request(url: str, **_kwargs: object) -> Response:
        if url.endswith("registered.csv"):
            return Response(content=b"CRD Number,SEC Number,Legal Name\n1,801-1,Reg")
        if url.endswith("exempt.csv"):
            return Response(content=b"CRD Number,SEC Number,Legal Name\n2,802-2,Exempt")
        return Response(text="<html />")

    monkeypatch.setattr(
        "openbb_sec.models.investment_advisers.parse_adviser_report_links",
        lambda *_args, **_kwargs: links,
    )
    monkeypatch.setattr(
        "openbb_sec.utils.ratelimit.sec_make_request",
        fake_sec_make_request,
    )

    records = load_investment_adviser_records(use_cache=True)

    assert [record["legal_name"] for record in records] == ["Reg", "Exempt"]
