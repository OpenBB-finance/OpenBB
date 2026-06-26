"""Tests for SEC filing index routes."""

from __future__ import annotations

import asyncio
from datetime import date

from openbb_sec.models.filing_index import (
    SecFilingIndexFetcher,
    SecFilingIndexQueryParams,
    parse_master_index,
)

MASTER_INDEX = """Description: Master Index of EDGAR Dissemination Feed
Last Data Received: March 31, 2025
Comments: webmaster@sec.gov

CIK|Company Name|Form Type|Date Filed|Filename
--------------------------------------------------------------------------------
1841359|ACME FUND LP|D|2025-03-12|edgar/data/1841359/0001841359-25-000001.txt
1841359|ACME FUND LP|D/A|2025-03-15|edgar/data/1841359/0001841359-25-000002.txt
1841359|ACME FUND LP|SC 13D|2025-03-16|edgar/data/1841359/0001841359-25-000003.txt
"""


def test_parse_master_index_returns_flat_rows() -> None:
    rows = parse_master_index(MASTER_INDEX)

    assert rows[0] == {
        "cik": "0001841359",
        "company_name": "ACME FUND LP",
        "form_type": "D",
        "filing_date": date(2025, 3, 12),
        "accession_number": "0001841359-25-000001",
        "archive_path": "edgar/data/1841359/0001841359-25-000001.txt",
        "complete_submission_url": (
            "https://www.sec.gov/Archives/"
            "edgar/data/1841359/0001841359-25-000001.txt"
        ),
        "filing_detail_url": (
            "https://www.sec.gov/Archives/edgar/data/1841359/"
            "000184135925000001/0001841359-25-000001-index.htm"
        ),
    }


def test_filing_index_form_filter_is_exact(monkeypatch) -> None:
    class Response:
        text = MASTER_INDEX

        def raise_for_status(self) -> None:
            return None

    def fake_request(url: str, **kwargs: object) -> Response:
        assert url.endswith("/2025/QTR1/master.idx")
        assert "headers" in kwargs
        assert "use_cache" not in kwargs
        return Response()

    monkeypatch.setattr(
        "openbb_sec.models.filing_index.sec_make_request",
        fake_request,
    )

    query = SecFilingIndexQueryParams(
        form_type="D",
        start_date=date(2025, 3, 1),
        end_date=date(2025, 3, 31),
        include_amendments=True,
    )
    data = asyncio.run(SecFilingIndexFetcher.aextract_data(query, None))

    assert [row["form_type"] for row in data] == ["D/A", "D"]


def test_filing_index_can_exclude_amendments(monkeypatch) -> None:
    class Response:
        text = MASTER_INDEX

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "openbb_sec.models.filing_index.sec_make_request",
        lambda *_args, **_kwargs: Response(),
    )

    query = SecFilingIndexQueryParams(
        form_type="D",
        start_date=date(2025, 3, 1),
        end_date=date(2025, 3, 31),
        include_amendments=False,
    )
    data = asyncio.run(SecFilingIndexFetcher.aextract_data(query, None))

    assert [row["form_type"] for row in data] == ["D"]
