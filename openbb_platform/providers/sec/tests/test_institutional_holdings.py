"""Tests for SEC institutional holdings."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_sec.models import institutional_holdings as holdings_module
from openbb_sec.models.institutional_holdings import (
    SecInstitutionalHoldingsFetcher,
    SecInstitutionalHoldingsQueryParams,
)


@dataclass(frozen=True)
class _DataSet:
    period_label: str
    url: str
    file_name: str
    period_date: date | None


@dataclass(frozen=True)
class _Extracted:
    filers: list[dict]
    holdings: list[dict]


@pytest.fixture(autouse=True)
def clear_extracted_period_cache() -> None:
    """Keep institutional holdings cache state isolated between tests."""
    holdings_module._EXTRACTED_PERIOD_CACHE.clear()
    holdings_module._INDEXED_PERIOD_CACHE.clear()
    holdings_module._DATA_SETS_PAGE_CACHE.clear()


def test_institutional_holdings_query_requires_selector() -> None:
    """A period-only query is rejected before fetching a full quarter."""
    with pytest.raises(ValidationError):
        SecInstitutionalHoldingsQueryParams(period=date(2024, 12, 31))


def test_institutional_holdings_fetcher_returns_flat_rows_without_source_url(
    monkeypatch,
) -> None:
    """The fetcher exposes holdings as normalized manager holding rows."""
    data_set = _DataSet(
        period_label="2024 Q4",
        url="https://www.sec.gov/files/form13fdata2024q4.zip",
        file_name="form13fdata2024q4.zip",
        period_date=date(2024, 12, 31),
    )

    class Response:
        text = "<html />"

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.sec_make_request",
        lambda *_args, **_kwargs: Response(),
    )
    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.parse_13f_data_set_page",
        lambda *_args, **_kwargs: [data_set],
    )
    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.download_13f_data_set",
        lambda *_args, **_kwargs: Path("fixture.zip"),
    )
    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.extract_13f_data_set_zip",
        lambda *_args, **_kwargs: _Extracted(
            filers=[],
            holdings=[
                {
                    "period_date": date(2024, 12, 31),
                    "accession_number": "0001",
                    "cik": "0001000275",
                    "filer_name": "Acme Capital LP",
                    "issuer": "Apple Inc",
                    "cusip": "037833100",
                    "value": 750.0,
                    "shares": 10.0,
                    "weight": 0.75,
                    "sector": "Technology",
                },
                {
                    "period_date": date(2024, 12, 31),
                    "accession_number": "0002",
                    "cik": "0002000000",
                    "filer_name": "Beta Advisors LLC",
                    "issuer": "Microsoft Corp",
                    "cusip": "594918104",
                    "value": 250.0,
                    "shares": 5.0,
                    "weight": 0.25,
                    "sector": "Technology",
                },
            ],
        ),
    )

    query = SecInstitutionalHoldingsQueryParams(
        period=date(2024, 12, 31),
        cik="1000275",
    )
    data = asyncio.run(SecInstitutionalHoldingsFetcher.aextract_data(query, None))
    result = SecInstitutionalHoldingsFetcher.transform_data(query, data)

    assert len(result) == 1
    row = result[0]
    assert row.period_end == date(2024, 12, 31)
    assert row.manager_cik == "0001000275"
    assert row.manager_name == "Acme Capital LP"
    assert row.issuer == "Apple Inc"
    assert "source_url" not in row.model_dump()


def test_institutional_holdings_reuses_extracted_period_for_selectors(
    monkeypatch,
) -> None:
    """Repeated selectors for one period reuse the parsed quarterly data."""
    data_set = _DataSet(
        period_label="2024 Q4",
        url="https://www.sec.gov/files/form13fdata2024q4.zip",
        file_name="form13fdata2024q4.zip",
        period_date=date(2024, 12, 31),
    )
    extract_calls = 0
    page_calls = 0

    class Response:
        text = "<html />"

        def raise_for_status(self) -> None:
            return None

    def fake_extract(*_args: object, **_kwargs: object) -> _Extracted:
        nonlocal extract_calls
        extract_calls += 1
        return _Extracted(
            filers=[],
            holdings=[
                {
                    "period_date": date(2024, 12, 31),
                    "accession_number": "0001",
                    "cik": "0001000275",
                    "filer_name": "Acme Capital LP",
                    "issuer": "Apple Inc",
                },
                {
                    "period_date": date(2024, 12, 31),
                    "accession_number": "0002",
                    "cik": "0002000000",
                    "filer_name": "Beta Advisors LLC",
                    "issuer": "Microsoft Corp",
                },
            ],
        )

    def fake_sec_make_request(*_args: object, **_kwargs: object) -> Response:
        nonlocal page_calls
        page_calls += 1
        return Response()

    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.sec_make_request",
        fake_sec_make_request,
    )
    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.parse_13f_data_set_page",
        lambda *_args, **_kwargs: [data_set],
    )
    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.download_13f_data_set",
        lambda *_args, **_kwargs: Path("fixture.zip"),
    )
    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.extract_13f_data_set_zip",
        fake_extract,
    )

    for cik in ("1000275", "2000000"):
        query = SecInstitutionalHoldingsQueryParams(
            period=date(2024, 12, 31),
            cik=cik,
        )
        data = asyncio.run(SecInstitutionalHoldingsFetcher.aextract_data(query, None))
        assert len(data) == 1

    query = SecInstitutionalHoldingsQueryParams(
        period=date(2024, 12, 31),
        accession_number="0001",
    )
    data = asyncio.run(SecInstitutionalHoldingsFetcher.aextract_data(query, None))
    assert data[0]["issuer"] == "Apple Inc"

    assert page_calls == 1
    assert extract_calls == 1


def test_institutional_holdings_fetcher_rejects_missing_period(monkeypatch) -> None:
    """Unknown periods fail instead of falling back to a broad download."""

    class Response:
        text = "<html />"

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.sec_make_request",
        lambda *_args, **_kwargs: Response(),
    )
    monkeypatch.setattr(
        "openbb_sec.models.institutional_holdings.parse_13f_data_set_page",
        lambda *_args, **_kwargs: [],
    )

    query = SecInstitutionalHoldingsQueryParams(
        period=date(2024, 12, 31),
        cik="1000275",
    )

    with pytest.raises(EmptyDataError):
        asyncio.run(SecInstitutionalHoldingsFetcher.aextract_data(query, None))
