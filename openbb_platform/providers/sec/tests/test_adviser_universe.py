"""Tests for the SEC investment adviser universe."""

from __future__ import annotations

import asyncio
import csv
from datetime import date
from io import BytesIO, StringIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic import ValidationError

from openbb_sec import sec_provider
from openbb_sec.models import adviser_universe
from openbb_sec.models.adviser_universe import (
    ADVISER_DATASET_TITLE,
    AdviserReport,
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
        "Organization CRD#",
        "SEC#",
        "CIK#",
        "Total number of CIK numbers",
        "Primary Business Name",
        "Legal Name",
        "SEC Current Status",
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


def test_parse_report_returns_only_flat_universe_fields() -> None:
    archive = _report_archive(
        [
            {
                "Organization CRD#": "70",
                "SEC#": "801-56943",
                "CIK#": "9319",
                "Total number of CIK numbers": "2",
                "Primary Business Name": "BCG SECURITIES, INC.",
                "Legal Name": "BCG SECURITIES, INC.",
                "SEC Current Status": "Approved",
            },
            {
                "Organization CRD#": "148826",
                "SEC#": "801-73907",
                "CIK#": "",
                "Total number of CIK numbers": "",
                "Primary Business Name": "CITADEL ADVISORS LLC",
                "Legal Name": "CITADEL ADVISORS LLC",
                "SEC Current Status": "Approved",
            },
        ]
    )

    records = adviser_universe._parse_report(archive, _registered_report())

    assert records == [
        {
            "crd": "70",
            "sec_number": "801-56943",
            "cik": "0000009319",
            "reported_cik_count": 2,
            "name": "BCG SECURITIES, INC.",
            "legal_name": "BCG SECURITIES, INC.",
            "registration_type": "SEC Registered",
            "status": "Approved",
            "report_period": date(2026, 7, 1),
        },
        {
            "crd": "148826",
            "sec_number": "801-73907",
            "cik": None,
            "reported_cik_count": None,
            "name": "CITADEL ADVISORS LLC",
            "legal_name": "CITADEL ADVISORS LLC",
            "registration_type": "SEC Registered",
            "status": "Approved",
            "report_period": date(2026, 7, 1),
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
                "Organization CRD#": "70",
                "SEC#": "801-56943",
                "CIK#": "invalid",
                "Total number of CIK numbers": "1",
                "Primary Business Name": "BCG SECURITIES, INC.",
                "Legal Name": "BCG SECURITIES, INC.",
                "SEC Current Status": "Approved",
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
                "Organization CRD#": "342972",
                "SEC#": "802-136595",
                "CIK#": "",
                "Total number of CIK numbers": "",
                "Primary Business Name": "GALILEO GLOBAL LTD",
                "Legal Name": "GALILEO GLOBAL LTD",
                "SEC Current Status": "ERA - Active",
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
        return catalog if url == adviser_universe.SEC_DATA_CATALOG_URL else archive

    monkeypatch.setattr(adviser_universe, "cached_request", fake_cached_request)
    query = SecAdviserUniverseQueryParams(
        registration_type="exempt",
        use_cache=False,
    )

    records = asyncio.run(SecAdviserUniverseFetcher.aextract_data(query, None))
    result = SecAdviserUniverseFetcher.transform_data(query, records)

    assert calls == [
        (adviser_universe.SEC_DATA_CATALOG_URL, False),
        (report_url, False),
    ]
    assert len(result) == 1
    assert set(result[0].model_dump()) == {
        "crd",
        "sec_number",
        "cik",
        "reported_cik_count",
        "name",
        "legal_name",
        "registration_type",
        "status",
        "report_period",
    }
    assert result[0].crd == "342972"
    assert result[0].registration_type == "SEC Exempt Reporting Adviser"
