"""Tests for the SEC investment adviser universe."""

from __future__ import annotations

import asyncio
import csv
from datetime import date
from io import BytesIO, StringIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_sec import sec_provider
from openbb_sec.models import adviser_universe
from openbb_sec.models.adviser_universe import (
    ADVISER_DATASET_TITLE,
    AdviserReport,
    SecAdviserUniverseData,
    SecAdviserUniverseFetcher,
    SecAdviserUniverseQueryParams,
)


def _distribution(
    title: str,
    url: str,
    media_type: str = "application/zip",
) -> dict[str, str]:
    return {
        "title": title,
        "mediaType": media_type,
        "downloadURL": url,
    }


def _catalog(*distributions: dict[str, str]) -> dict[str, object]:
    return {
        "dataset": [
            {
                "title": ADVISER_DATASET_TITLE,
                "distribution": list(distributions),
            }
        ]
    }


def _report_archive(
    rows: list[dict[str, str]],
    *,
    columns: list[str] | None = None,
) -> bytes:
    fieldnames = columns or [
        "SEC Region",
        "Organization CRD#",
        "SEC#",
        "Firm Type",
        "CIK#",
        "Total number of CIK numbers",
        "Primary Business Name",
        "Legal Name",
        "SEC Current Status",
        "Latest ADV Filing Date",
        "Website Address",
        "5A",
        "5F(2)(a)",
        "5F(2)(b)",
        "5F(2)(c)",
        "5F(2)(d)",
        "5F(2)(e)",
        "5F(2)(f)",
        "6A(3)",
    ]
    text = StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("adviser-universe.csv", text.getvalue().encode("cp1252"))
    return output.getvalue()


def _registered_report() -> AdviserReport:
    return AdviserReport(
        registration_type="registered",
        report_date=date(2026, 7, 1),
        media_type="application/zip",
        url="https://www.sec.gov/files/ia07012026.zip",
    )


def test_adviser_universe_is_registered_with_sec_provider() -> None:
    assert sec_provider.fetcher_dict["SecAdviserUniverse"] is SecAdviserUniverseFetcher


def test_adviser_universe_query_requires_registration_type() -> None:
    with pytest.raises(ValidationError, match="registration_type"):
        SecAdviserUniverseQueryParams()


@pytest.mark.parametrize("crd", ["", "abc", True, 148826])
def test_adviser_universe_query_requires_numeric_crd_string(crd: object) -> None:
    with pytest.raises(ValidationError, match="crd"):
        SecAdviserUniverseQueryParams(
            registration_type="registered",
            crd=crd,
        )


def test_latest_report_selects_requested_population() -> None:
    catalog = _catalog(
        _distribution(
            "Registered Investment Advisers, June 2026",
            "https://www.sec.gov/files/ia06012026.zip",
        ),
        _distribution(
            "Exempt Investment Advisers, July 2026",
            "https://www.sec.gov/files/ia07012026-exempt.zip",
        ),
        _distribution(
            "Registered Investment Advisers, July 2026",
            "https://www.sec.gov/files/ia07012026.zip",
        ),
    )

    registered = adviser_universe._latest_report(catalog, "registered")
    exempt = adviser_universe._latest_report(catalog, "exempt")

    assert registered.report_date == date(2026, 7, 1)
    assert registered.url.endswith("ia07012026.zip")
    assert exempt.registration_type == "exempt"
    assert exempt.url.endswith("ia07012026-exempt.zip")


def test_latest_report_normalizes_catalog_whitespace() -> None:
    catalog = _catalog(
        _distribution(
            "Registered Investment Advisers, July 2026 ",
            "https://www.sec.gov/files/ia07012026.zip ",
            "application/zip ",
        )
    )

    report = adviser_universe._latest_report(catalog, "registered")

    assert report.report_date == date(2026, 7, 1)
    assert report.url == "https://www.sec.gov/files/ia07012026.zip"


def test_latest_report_reads_date_before_catalog_note() -> None:
    catalog = _catalog(
        _distribution(
            "Registered Investment Advisers, January 2019 - unavailable due to "
            "federal government shutdown",
            "https://www.sec.gov/files/ia01012019.zip",
        )
    )

    report = adviser_universe._latest_report(catalog, "registered")

    assert report.report_date == date(2019, 1, 1)


def test_latest_report_does_not_fall_back_from_unsupported_current_format() -> None:
    catalog = _catalog(
        _distribution(
            "Registered Investment Advisers, June 2026",
            "https://www.sec.gov/files/ia06012026.zip",
        ),
        _distribution(
            "Registered Investment Advisers, July 2026",
            "https://www.sec.gov/files/ia-no-data-07012026.pdf",
            "application/pdf",
        ),
    )

    with pytest.raises(OpenBBError, match="unsupported media type 'application/pdf'"):
        adviser_universe._latest_report(catalog, "registered")


def test_parse_report_preserves_all_form_adv_fields() -> None:
    archive = _report_archive(
        [
            {
                "SEC Region": "HQ",
                "Organization CRD#": "70",
                "SEC#": "801-56943",
                "Firm Type": "Registered",
                "CIK#": "9319",
                "Total number of CIK numbers": "2",
                "Primary Business Name": "BCG SECURITIES, INC.",
                "Legal Name": "BCG SECURITIES, INC.",
                "SEC Current Status": "Approved",
                "Latest ADV Filing Date": "07/01/2026",
                "Website Address": "https://example.com",
                "5A": "100",
                "5F(2)(a)": "1,250,000.00",
                "5F(2)(b)": "250,000.00",
                "5F(2)(c)": "1,500,000.00",
                "5F(2)(d)": "10",
                "5F(2)(e)": "2",
                "5F(2)(f)": "12",
                "6A(3)": "Y",
            },
            {
                "SEC Region": "HQ",
                "Organization CRD#": "148826",
                "SEC#": "801-73907",
                "Firm Type": "Registered",
                "CIK#": "",
                "Total number of CIK numbers": "",
                "Primary Business Name": "CITADEL ADVISORS LLC",
                "Legal Name": "CITADEL ADVISORS LLC",
                "SEC Current Status": "Approved",
                "Latest ADV Filing Date": "06/11/2026",
            },
        ]
    )

    records = adviser_universe._parse_report(archive, _registered_report())
    filtered_records = adviser_universe._parse_report(
        archive,
        _registered_report(),
        crd="148826",
    )

    assert SecAdviserUniverseData.model_validate(records[0]).model_dump() == records[0]
    assert filtered_records == [records[1]]
    assert records == [
        {
            "sec_region": "HQ",
            "crd": "70",
            "sec_number": "801-56943",
            "firm_type": "Registered",
            "cik": "0000009319",
            "cik_count": 2,
            "primary_business_name": "BCG SECURITIES, INC.",
            "legal_name": "BCG SECURITIES, INC.",
            "status": "Approved",
            "latest_adv_filing_date": date(2026, 7, 1),
            "website": "https://example.com",
            "employee_count": 100,
            "discretionary_aum": 1_250_000,
            "non_discretionary_aum": 250_000,
            "regulatory_assets_under_management": 1_500_000,
            "discretionary_account_count": 10,
            "non_discretionary_account_count": 2,
            "account_count": 12,
            "item_6a_3": "Y",
            "report_date": date(2026, 7, 1),
        },
        {
            "sec_region": "HQ",
            "crd": "148826",
            "sec_number": "801-73907",
            "firm_type": "Registered",
            "cik": None,
            "cik_count": None,
            "primary_business_name": "CITADEL ADVISORS LLC",
            "legal_name": "CITADEL ADVISORS LLC",
            "status": "Approved",
            "latest_adv_filing_date": date(2026, 6, 11),
            "website": None,
            "employee_count": None,
            "discretionary_aum": None,
            "non_discretionary_aum": None,
            "regulatory_assets_under_management": None,
            "discretionary_account_count": None,
            "non_discretionary_account_count": None,
            "account_count": None,
            "item_6a_3": None,
            "report_date": date(2026, 7, 1),
        },
    ]


def test_parse_report_rejects_changed_schema() -> None:
    archive = _report_archive([], columns=["Organization CRD#"])

    with pytest.raises(OpenBBError, match="missing required columns"):
        adviser_universe._parse_report(archive, _registered_report())


def test_parse_report_rejects_invalid_archive() -> None:
    with pytest.raises(OpenBBError, match="expected a ZIP archive"):
        adviser_universe._parse_report(b"not a zip", _registered_report())


def test_parse_report_rejects_multiple_csv_files() -> None:
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("first.csv", "crd\n1\n")
        archive.writestr("second.csv", "crd\n2\n")

    with pytest.raises(OpenBBError, match="expected exactly one CSV file"):
        adviser_universe._parse_report(output.getvalue(), _registered_report())


def test_parse_report_rejects_malformed_cik() -> None:
    archive = _report_archive(
        [
            {
                "SEC Region": "HQ",
                "Organization CRD#": "70",
                "SEC#": "801-56943",
                "Firm Type": "Registered",
                "CIK#": "invalid",
                "Total number of CIK numbers": "1",
                "Primary Business Name": "BCG SECURITIES, INC.",
                "Legal Name": "BCG SECURITIES, INC.",
                "SEC Current Status": "Approved",
                "Latest ADV Filing Date": "07/01/2026",
            }
        ]
    )

    with pytest.raises(OpenBBError, match="CIK must be numeric"):
        adviser_universe._parse_report(archive, _registered_report())


def test_adviser_universe_fetcher_uses_catalog_and_selected_report(
    monkeypatch,
) -> None:
    report_url = "https://www.sec.gov/files/ia07012026-exempt.zip"
    catalog = _catalog(
        _distribution(
            "Exempt Investment Advisers, July 2026",
            report_url,
        )
    )
    archive = _report_archive(
        [
            {
                "SEC Region": "HQ",
                "Organization CRD#": "342972",
                "SEC#": "802-136595",
                "Firm Type": "Exempt",
                "CIK#": "",
                "Total number of CIK numbers": "",
                "Primary Business Name": "GALILEO GLOBAL LTD",
                "Legal Name": "GALILEO GLOBAL LTD",
                "SEC Current Status": "ERA - Active",
                "Latest ADV Filing Date": "07/01/2026",
            }
        ]
    )
    calls: list[tuple[str, bool]] = []

    async def fake_cached_request(
        url: str,
        *,
        use_cache: bool,
        **kwargs: object,
    ) -> object:
        calls.append((url, use_cache))
        return catalog

    def fake_cached_bytes(
        url: str,
        *,
        use_cache: bool,
        **kwargs: object,
    ) -> bytes:
        calls.append((url, use_cache))
        return archive

    monkeypatch.setattr(adviser_universe, "cached_request", fake_cached_request)
    monkeypatch.setattr(adviser_universe, "cached_bytes", fake_cached_bytes)
    query = SecAdviserUniverseQueryParams(
        registration_type="exempt",
        crd="342972",
        use_cache=False,
    )

    records = asyncio.run(SecAdviserUniverseFetcher.aextract_data(query, None))
    result = SecAdviserUniverseFetcher.transform_data(query, records)

    assert calls == [
        (adviser_universe.SEC_DATA_CATALOG_URL, False),
        (report_url, False),
    ]
    assert len(result) == 1
    assert len(result[0].model_dump()) == 20
    assert result[0].crd == "342972"
    assert result[0].firm_type == "Exempt"
    assert result[0].latest_adv_filing_date == date(2026, 7, 1)


def test_adviser_universe_rejects_unknown_crd(monkeypatch) -> None:
    report_url = "https://www.sec.gov/files/ia07012026.zip"
    catalog = _catalog(
        _distribution(
            "Registered Investment Advisers, July 2026",
            report_url,
        )
    )
    archive = _report_archive(
        [
            {
                "SEC Region": "HQ",
                "Organization CRD#": "148826",
                "SEC#": "801-73907",
                "Firm Type": "Registered",
                "CIK#": "",
                "Total number of CIK numbers": "",
                "Primary Business Name": "CITADEL ADVISORS LLC",
                "Legal Name": "CITADEL ADVISORS LLC",
                "SEC Current Status": "Approved",
                "Latest ADV Filing Date": "06/11/2026",
            }
        ]
    )

    async def fake_cached_request(*_args: object, **_kwargs: object) -> object:
        return catalog

    def fake_cached_bytes(*_args: object, **_kwargs: object) -> bytes:
        return archive

    monkeypatch.setattr(adviser_universe, "cached_request", fake_cached_request)
    monkeypatch.setattr(adviser_universe, "cached_bytes", fake_cached_bytes)
    query = SecAdviserUniverseQueryParams(
        registration_type="registered",
        crd="999999",
    )

    with pytest.raises(
        EmptyDataError,
        match="No registered investment adviser with CRD 999999",
    ):
        asyncio.run(SecAdviserUniverseFetcher.aextract_data(query, None))
