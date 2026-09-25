"""Unit tests for ``openbb_sec.models.form_13FHR``."""

import asyncio
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.form_13FHR import SecForm13FHRFetcher, SecForm13FHRQueryParams


def test_form_13fhr_aextract_date_branch():
    """form_13FHR.py:71-73 -> the date branch resolves a quarter-end URL."""
    from datetime import date

    from pandas import Series

    filings = Series(
        ["https://example.com/q1.xml"],
        index=["2023-03-31"],
    )

    async def _candidates(symbol=None, cik=None):  # noqa: ARG001
        return filings

    async def _parse(url):  # noqa: ARG001
        return [{"period_ending": "2023-03-31", "weight": 0.5}]

    query = SecForm13FHRQueryParams(symbol="0001067983", date=date(2023, 2, 15))
    with (
        patch("openbb_sec.utils.parse_13f.get_13f_candidates", _candidates),
        patch("openbb_sec.utils.parse_13f.parse_13f_hr", _parse),
        patch("openbb_sec.utils.parse_13f.date_to_quarter_end", lambda d: "2023-03-31"),
    ):
        result = asyncio.run(SecForm13FHRFetcher.aextract_data(query, None))
    assert result == [{"period_ending": "2023-03-31", "weight": 0.5}]


def test_form_13fhr_aextract_empty_data_error():
    """form_13FHR.py:87 -> EmptyDataError when parsing returns nothing."""
    from pandas import Series

    filings = Series(["https://example.com/q1.xml"], index=["2023-03-31"])

    async def _candidates(symbol=None, cik=None):  # noqa: ARG001
        return filings

    async def _parse(url):  # noqa: ARG001
        return []

    query = SecForm13FHRQueryParams(symbol="BRK-A", limit=1)
    with (
        patch("openbb_sec.utils.parse_13f.get_13f_candidates", _candidates),
        patch("openbb_sec.utils.parse_13f.parse_13f_hr", _parse),
    ):
        with pytest.raises(EmptyDataError) as exc:
            asyncio.run(SecForm13FHRFetcher.aextract_data(query, None))
    assert "No data was returned" in str(exc.value)


def test_form_13fhr_aextract_reraises_openbb_error():
    """form_13FHR.py:90-91 -> an OpenBBError from candidates is re-raised."""

    async def _candidates(symbol=None, cik=None):  # noqa: ARG001
        raise OpenBBError("candidate lookup failed")

    query = SecForm13FHRQueryParams(symbol="AAPL", limit=1)
    with patch("openbb_sec.utils.parse_13f.get_13f_candidates", _candidates):
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(SecForm13FHRFetcher.aextract_data(query, None))
    assert "candidate lookup failed" in str(exc.value)
