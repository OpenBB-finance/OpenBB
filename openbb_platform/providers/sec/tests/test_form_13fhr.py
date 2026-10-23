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


def test_form_13fhr_transform_data_none_weight_and_order():
    """A ``None`` weight validates as 0.0; rows sort by period, then weight."""
    from datetime import date

    def _row(period, cusip, value, weight):
        return {
            "period_ending": period,
            "nameOfIssuer": "X CORP",
            "cusip": cusip,
            "titleOfClass": "COM",
            "principal_amount": 0,
            "value": value,
            "weight": weight,
        }

    data = [
        _row(date(2025, 12, 31), "000000000", 0, None),
        _row(date(2025, 12, 31), "000000001", 0, None),
        _row(date(2026, 3, 31), "111111111", 25, 0.25),
        _row(date(2026, 3, 31), "222222222", 75, 0.75),
    ]
    query = SecForm13FHRQueryParams(symbol="1562087")
    result = SecForm13FHRFetcher.transform_data(query, data)
    assert [(r.period_ending, r.weight) for r in result] == [
        (date(2026, 3, 31), 0.75),
        (date(2026, 3, 31), 0.25),
        (date(2025, 12, 31), 0.0),
        (date(2025, 12, 31), 0.0),
    ]


def test_form_13fhr_aextract_reraises_openbb_error():
    """form_13FHR.py:90-91 -> an OpenBBError from candidates is re-raised."""

    async def _candidates(symbol=None, cik=None):  # noqa: ARG001
        raise OpenBBError("candidate lookup failed")

    query = SecForm13FHRQueryParams(symbol="AAPL", limit=1)
    with patch("openbb_sec.utils.parse_13f.get_13f_candidates", _candidates):
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(SecForm13FHRFetcher.aextract_data(query, None))
    assert "candidate lookup failed" in str(exc.value)
