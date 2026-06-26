"""Tests for SEC investment adviser related people."""

from __future__ import annotations

import asyncio
import csv
from datetime import date
from io import BytesIO, StringIO
from zipfile import ZipFile

import pytest
from pydantic import ValidationError

from openbb_sec.models.investment_adviser_people import (
    SecInvestmentAdviserPeopleFetcher,
    SecInvestmentAdviserPeopleQueryParams,
    load_investment_adviser_people_records,
    normalize_adv_part1_people_zip,
)


def _csv_bytes(rows: list[dict[str, object]]) -> bytes:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def test_investment_adviser_people_requires_selector() -> None:
    """The route is selector-based and does not expose the whole archive."""
    with pytest.raises(ValidationError):
        SecInvestmentAdviserPeopleQueryParams()


def test_investment_adviser_people_accepts_date_range_selector() -> None:
    """A filing-date range is a selector for public ADV archive rows."""
    query = SecInvestmentAdviserPeopleQueryParams(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
    )

    assert query.start_date == date(2026, 5, 1)


def test_normalize_adv_part1_people_zip_returns_flat_rows() -> None:
    """ADV Schedule A/B and 1J/1K rows normalize to flat person rows."""
    content = _zip_bytes(
        {
            "IA_FIRM_SEC_Feed_20111105_20241231.csv": _csv_bytes(
                [
                    {
                        "FilingID": "1001",
                        "1A": "Acme Capital Management LP",
                        "1J1 SEC Number": "801-123",
                        "1J2 CRD Number": "123",
                    }
                ]
            ),
            "IA_Schedule_A_B_20111105_20241231.csv": _csv_bytes(
                [
                    {
                        "FilingID": "1001",
                        "Schedule": "A",
                        "Full Legal Name": "Grace Hopper",
                        "Title or Status": "Managing Member",
                        "Ownership Code": "C",
                        "Control Person": "Y",
                        "OwnerID": "owner-1",
                    }
                ]
            ),
            "IA_ADV_1J_1K_20111105_20241231.csv": _csv_bytes(
                [
                    {
                        "FilingID": "1001",
                        "1J1 Name": "Ada Lovelace",
                        "1J2 Name": "",
                        "1K Name": "Alan Turing",
                    }
                ]
            ),
        }
    )

    rows = normalize_adv_part1_people_zip(content)

    assert rows == [
        {
            "crd": "123",
            "sec_number": "801-123",
            "adviser_name": "Acme Capital Management LP",
            "filing_id": "1001",
            "person_name": "Grace Hopper",
            "role": "Control Person",
            "schedule": "A",
            "title_or_status": "Managing Member",
            "ownership_code": "C",
            "control_person": True,
            "owner_id": "owner-1",
            "source_table": "IA_Schedule_A_B",
        },
        {
            "crd": "123",
            "sec_number": "801-123",
            "adviser_name": "Acme Capital Management LP",
            "filing_id": "1001",
            "person_name": "Ada Lovelace",
            "role": "Chief Compliance Officer",
            "schedule": None,
            "title_or_status": None,
            "ownership_code": None,
            "control_person": None,
            "owner_id": None,
            "source_table": "IA_ADV_1J_1K",
        },
        {
            "crd": "123",
            "sec_number": "801-123",
            "adviser_name": "Acme Capital Management LP",
            "filing_id": "1001",
            "person_name": "Alan Turing",
            "role": "Control Person Contact",
            "schedule": None,
            "title_or_status": None,
            "ownership_code": None,
            "control_person": None,
            "owner_id": None,
            "source_table": "IA_ADV_1J_1K",
        },
    ]


def test_normalize_adv_part1_people_zip_accepts_current_monthly_base_files() -> None:
    """The public 2025+ adviserinfo files use ADV_Base metadata tables."""
    content = _zip_bytes(
        {
            "IA_ADV_Base_A_20260501_20260531.csv": _csv_bytes(
                [
                    {
                        "FilingID": "2001",
                        "DateSubmitted": "2026-05-15",
                        "1A": "Acme Capital Management LP",
                        "1E1": "123",
                        "1D": "801-123",
                    }
                ]
            ),
            "IA_ADV_1J_1K_20260501_20260531.csv": _csv_bytes(
                [
                    {
                        "FilingID": "2001",
                        "1J1 Name": "Ada Lovelace",
                        "1J2 Name": "",
                        "1K Name": "",
                    }
                ]
            ),
        }
    )

    rows = normalize_adv_part1_people_zip(content)

    assert rows == [
        {
            "crd": "123",
            "sec_number": "801-123",
            "adviser_name": "Acme Capital Management LP",
            "filing_date": date(2026, 5, 15),
            "filing_id": "2001",
            "person_name": "Ada Lovelace",
            "role": "Chief Compliance Officer",
            "schedule": None,
            "title_or_status": None,
            "ownership_code": None,
            "control_person": None,
            "owner_id": None,
            "source_table": "IA_ADV_1J_1K",
        }
    ]


def test_load_investment_adviser_people_records_reads_monthly_public_files(
    monkeypatch,
) -> None:
    """A current date range loads public monthly adviserinfo ADV ZIP files."""
    urls: list[str] = []

    class Response:
        def __init__(self, content: bytes) -> None:
            self.content = content

        def raise_for_status(self) -> None:
            return None

    def fake_sec_make_request(url: str, **_kwargs: object) -> Response:
        urls.append(url)
        return Response(
            _zip_bytes(
                {
                    "IA_ADV_Base_A_20260501_20260531.csv": _csv_bytes(
                        [
                            {
                                "FilingID": "2001",
                                "DateSubmitted": "2026-05-15",
                                "1A": "Acme Capital Management LP",
                                "1E1": "123",
                                "1D": "801-123",
                            }
                        ]
                    ),
                    "IA_ADV_1J_1K_20260501_20260531.csv": _csv_bytes(
                        [
                            {
                                "FilingID": "2001",
                                "1J1 Name": "Ada Lovelace",
                                "1J2 Name": "",
                                "1K Name": "",
                            }
                        ]
                    ),
                }
            )
        )

    monkeypatch.setattr(
        "openbb_sec.utils.ratelimit.sec_make_request",
        fake_sec_make_request,
    )

    rows = load_investment_adviser_people_records(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
    )

    assert urls == [
        "https://reports.adviserinfo.sec.gov/reports/foia/advFilingData/2026/"
        "ADV_Filing_Data_20260501_20260531.zip"
    ]
    assert rows[0]["person_name"] == "Ada Lovelace"
    assert rows[0]["filing_date"] == date(2026, 5, 15)


def test_load_investment_adviser_people_records_skips_unpublished_current_month(
    monkeypatch,
) -> None:
    """Current-month ADV monthly files are not requested before publication."""
    urls: list[str] = []

    class Response:
        def __init__(self, content: bytes) -> None:
            self.content = content

        def raise_for_status(self) -> None:
            return None

    def fake_sec_make_request(url: str, **_kwargs: object) -> Response:
        urls.append(url)
        return Response(
            _zip_bytes(
                {
                    "IA_ADV_Base_A_20260501_20260531.csv": _csv_bytes(
                        [
                            {
                                "FilingID": "2001",
                                "DateSubmitted": "2026-05-15",
                                "1A": "Acme Capital Management LP",
                                "1E1": "123",
                                "1D": "801-123",
                            }
                        ]
                    ),
                    "IA_ADV_1J_1K_20260501_20260531.csv": _csv_bytes(
                        [
                            {
                                "FilingID": "2001",
                                "1J1 Name": "Ada Lovelace",
                                "1J2 Name": "",
                                "1K Name": "",
                            }
                        ]
                    ),
                }
            )
        )

    monkeypatch.setattr(
        "openbb_sec.utils.ratelimit.sec_make_request",
        fake_sec_make_request,
    )

    load_investment_adviser_people_records(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 6, 26),
        today=date(2026, 6, 26),
    )

    assert urls == [
        "https://reports.adviserinfo.sec.gov/reports/foia/advFilingData/2026/"
        "ADV_Filing_Data_20260501_20260531.zip"
    ]


def test_load_investment_adviser_people_records_reads_historical_and_monthly_files(
    monkeypatch,
) -> None:
    """A date range crossing 2024 and 2025 reads both public archive families."""
    urls: list[str] = []

    class Response:
        def __init__(self, content: bytes) -> None:
            self.content = content

        def raise_for_status(self) -> None:
            return None

    def fake_sec_make_request(url: str, **_kwargs: object) -> Response:
        urls.append(url)
        return Response(
            _zip_bytes(
                {
                    "IA_FIRM_SEC_Feed_20111105_20241231.csv": _csv_bytes(
                        [
                            {
                                "FilingID": "1001",
                                "1A": "Acme Capital Management LP",
                                "1J1 SEC Number": "801-123",
                                "1J2 CRD Number": "123",
                            }
                        ]
                    ),
                    "IA_ADV_1J_1K_20111105_20241231.csv": _csv_bytes(
                        [
                            {
                                "FilingID": "1001",
                                "1J1 Name": "Ada Lovelace",
                                "1J2 Name": "",
                                "1K Name": "",
                            }
                        ]
                    ),
                }
            )
        )

    monkeypatch.setattr(
        "openbb_sec.utils.ratelimit.sec_make_request",
        fake_sec_make_request,
    )

    load_investment_adviser_people_records(
        start_date=date(2024, 12, 1),
        end_date=date(2025, 1, 31),
    )

    assert urls == [
        "https://www.sec.gov/files/adv-filing-data-20111105-20241231-part1.zip",
        "https://reports.adviserinfo.sec.gov/reports/foia/advFilingData/2025/"
        "ADV_Filing_Data_20250101_20250131.zip",
    ]


def test_investment_adviser_people_fetcher_filters_by_selector(monkeypatch) -> None:
    """CRD, SEC number, and query selectors filter normalized people rows."""
    monkeypatch.setattr(
        "openbb_sec.models.investment_adviser_people.load_investment_adviser_people_records",
        lambda **_kwargs: [
            {
                "crd": "123",
                "sec_number": "801-123",
                "adviser_name": "Acme Capital Management LP",
                "filing_id": "1001",
                "person_name": "Ada Lovelace",
                "role": "Chief Compliance Officer",
                "source_table": "IA_ADV_1J_1K",
            },
            {
                "crd": "456",
                "sec_number": "801-456",
                "adviser_name": "Beta Advisors LLC",
                "filing_id": "1002",
                "person_name": "Grace Hopper",
                "role": "Control Person",
                "source_table": "IA_Schedule_A_B",
            },
        ],
    )

    query = SecInvestmentAdviserPeopleQueryParams(
        crd="123",
        sec_number="801-123",
        query="acme",
    )
    data = asyncio.run(SecInvestmentAdviserPeopleFetcher.aextract_data(query, None))
    result = SecInvestmentAdviserPeopleFetcher.transform_data(query, data)

    assert len(result) == 1
    assert result[0].person_name == "Ada Lovelace"
    assert result[0].source_table == "IA_ADV_1J_1K"
