"""Tests for SEC institutional manager records."""

from __future__ import annotations

import asyncio
from datetime import date

from openbb_sec.models.institutional_managers import (
    SecInstitutionalManagersFetcher,
    SecInstitutionalManagersQueryParams,
)


def test_institutional_managers_fetcher_filters_by_period_and_query(
    monkeypatch,
) -> None:
    """Institutional manager records can be selected by period and name."""
    records = [
        {
            "cik": "0001000275",
            "manager_name": "Acme Capital LP",
            "period": date(2024, 12, 31),
            "accession_number": "0001",
            "reported_value": 1000.0,
        },
        {
            "cik": "0002000000",
            "manager_name": "Beta Advisors LLC",
            "period": date(2024, 12, 31),
            "accession_number": "0002",
            "reported_value": 2000.0,
        },
    ]

    monkeypatch.setattr(
        "openbb_sec.models.institutional_managers.load_institutional_manager_records",
        lambda **_kwargs: records,
    )

    query = SecInstitutionalManagersQueryParams(
        query="capital",
        period=date(2024, 12, 31),
    )
    data = asyncio.run(SecInstitutionalManagersFetcher.aextract_data(query, None))
    result = SecInstitutionalManagersFetcher.transform_data(query, data)

    assert len(result) == 1
    assert result[0].cik == "0001000275"
    assert result[0].manager_name == "Acme Capital LP"
    assert "source_url" not in result[0].model_dump()


def test_institutional_managers_fetcher_filters_by_cik(monkeypatch) -> None:
    """CIK filtering preserves leading zero semantics."""
    records = [
        {"cik": "0001000275", "manager_name": "Acme Capital LP"},
        {"cik": "0002000000", "manager_name": "Beta Advisors LLC"},
    ]

    monkeypatch.setattr(
        "openbb_sec.models.institutional_managers.load_institutional_manager_records",
        lambda **_kwargs: records,
    )

    query = SecInstitutionalManagersQueryParams(cik="1000275")
    data = asyncio.run(SecInstitutionalManagersFetcher.aextract_data(query, None))

    assert data == [records[0]]
