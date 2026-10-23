"""Tests for the Philadelphia Fed regional models."""

import io
from datetime import date
from unittest.mock import MagicMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.philadelphia_ads import (
    FederalReservePhiladelphiaAdsData,
    FederalReservePhiladelphiaAdsFetcher,
)


def _ads_workbook() -> bytes:
    """Build a small ADS workbook with the expected layout."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Date", "ADS_Index", "RECBARS"])
    sheet.append(["2026:06:11", 0.0012, 0])
    sheet.append(["2026:06:12", 0.0015, 1])
    sheet.append(["2026:06:13", 0.0011, 0])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _response(content: bytes) -> MagicMock:
    """Build a make_request response with the given binary body."""
    response = MagicMock()
    response.content = content
    response.raise_for_status = MagicMock()
    return response


class TestBusinessConditions:
    """Tests for the ADS Business Conditions fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The workbook parses to a daily date/value series and dates filter."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_ads_workbook()),
        )
        query = FederalReservePhiladelphiaAdsFetcher.transform_query(
            {"start_date": "2026-06-12", "end_date": "2026-06-12"}
        )
        rows = FederalReservePhiladelphiaAdsFetcher.extract_data(query, None)
        result = FederalReservePhiladelphiaAdsFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReservePhiladelphiaAdsData) for r in result)
        assert result[0].date == date(2026, 6, 12)
        assert result[0].ads_index == 0.0015
        assert result[0].recession == 1
        assert len(result) == 1

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReservePhiladelphiaAdsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReservePhiladelphiaAdsFetcher.extract_data(query, None)
