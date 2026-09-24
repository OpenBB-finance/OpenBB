"""Tests for the additional Kansas City Fed agricultural dataset models."""

import io
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.kansas_city_ag_databook_archived import (
    FederalReserveKansasCityAgDatabookArchivedData,
    FederalReserveKansasCityAgDatabookArchivedFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_district_surveys import (
    FederalReserveKansasCityAgDistrictSurveysData,
    FederalReserveKansasCityAgDistrictSurveysFetcher,
)
from openbb_federal_reserve.models.regional.kansas_city_ag_terms_of_lending import (
    FederalReserveKansasCityAgTermsOfLendingData,
    FederalReserveKansasCityAgTermsOfLendingFetcher,
)


def _save(sheets: dict[str, list[list]]) -> bytes:
    """Build an xlsx workbook from a mapping of sheet name to rows."""
    from openpyxl import Workbook

    workbook = Workbook()
    workbook.remove(workbook.active)
    for title, rows in sheets.items():
        sheet = workbook.create_sheet(title=title)
        for row in rows:
            sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _patch_resolved(monkeypatch, content: bytes) -> None:
    """Bypass URL resolution and serve fixture bytes from the fetch helper."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.kansas_city_ag.resolve_kc_ag_url",
        lambda document_id: "https://example.test/file.xlsx",
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
        lambda *a, **k: content,
    )


def _patch_direct(monkeypatch, content: bytes) -> None:
    """Serve fixture bytes from the fetch helper."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
        lambda *a, **k: content,
    )


class TestAgTermsOfLending:
    """Tests for the National Survey of Terms of Lending fetcher."""

    def test_codes_resolve_and_missing(self, monkeypatch):
        """Codes resolve to descriptions and ``---`` maps to missing."""
        _patch_resolved(
            monkeypatch,
            _save(
                {
                    "Data": [
                        ["Date", "010A", "010B"],
                        ["2025Q1", 100.0, "---"],
                    ],
                    "Descriptions": [
                        ["Statistic Identifier", "Statistic"],
                        ["010A", "Number of Loans"],
                        ["010B", "Average Size"],
                    ],
                }
            ),
        )
        query = FederalReserveKansasCityAgTermsOfLendingFetcher.transform_query({})
        rows = FederalReserveKansasCityAgTermsOfLendingFetcher.extract_data(query, None)
        result = FederalReserveKansasCityAgTermsOfLendingFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveKansasCityAgTermsOfLendingData) for r in result
        )
        row = result[0].model_dump()
        assert row["Number of Loans"] == 100.0
        assert row["Average Size"] is None

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_resolved(monkeypatch, b"")
        query = FederalReserveKansasCityAgTermsOfLendingFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityAgTermsOfLendingFetcher.extract_data(query, None)


class TestAgDistrictSurveys:
    """Tests for the combined District Ag Credit Surveys fetcher."""

    _CONTENT = {
        "Data": [
            ["Date", "001CHI", "002DAL"],
            ["2025Q1", 14.0, 30.0],
        ],
        "Description": [
            ["Statistic Identifier", "Description"],
            ["001CHI", "Demand for Loans"],
            ["002DAL", "Farm Income"],
        ],
    }

    def test_districts_named_from_codes(self, monkeypatch):
        """Each code's trailing district abbreviation becomes a name prefix."""
        _patch_resolved(monkeypatch, _save(self._CONTENT))
        query = FederalReserveKansasCityAgDistrictSurveysFetcher.transform_query({})
        rows = FederalReserveKansasCityAgDistrictSurveysFetcher.extract_data(
            query, None
        )
        result = FederalReserveKansasCityAgDistrictSurveysFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveKansasCityAgDistrictSurveysData) for r in result
        )
        row = result[0].model_dump()
        assert row["Chicago - Demand for Loans"] == 14.0
        assert row["Dallas - Farm Income"] == 30.0

    def test_district_filter(self, monkeypatch):
        """The district filter narrows to one district's series."""
        _patch_resolved(monkeypatch, _save(self._CONTENT))
        query = FederalReserveKansasCityAgDistrictSurveysFetcher.transform_query(
            {"district": "Chicago"}
        )
        rows = FederalReserveKansasCityAgDistrictSurveysFetcher.extract_data(
            query, None
        )
        result = FederalReserveKansasCityAgDistrictSurveysFetcher.transform_data(
            query, rows
        )
        assert result
        columns = {key for r in result for key in r.model_dump() if key != "date"}
        assert columns
        assert all("Chicago" in column for column in columns)

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_resolved(monkeypatch, b"")
        query = FederalReserveKansasCityAgDistrictSurveysFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityAgDistrictSurveysFetcher.extract_data(query, None)


class TestAgDatabookArchived:
    """Tests for the archived Ag Finance Databook fetcher."""

    def test_annual_table(self, monkeypatch):
        """A year-indexed section A table melts to annual records."""
        _patch_direct(
            monkeypatch,
            _save(
                {
                    "afdr_a1": [
                        ["Period", "Total", "Feeder livestock"],
                        ["2017", 3.4, 0.4],
                        ["2018", 3.5, 0.5],
                    ]
                }
            ),
        )
        query = FederalReserveKansasCityAgDatabookArchivedFetcher.transform_query(
            {"table": "afdr_a1"}
        )
        rows = FederalReserveKansasCityAgDatabookArchivedFetcher.extract_data(
            query, None
        )
        result = FederalReserveKansasCityAgDatabookArchivedFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveKansasCityAgDatabookArchivedData)
            for r in result
        )
        by_date = {r.date: r.model_dump() for r in result}
        assert by_date[date(2017, 12, 31)]["frequency"] == "annual"
        assert by_date[date(2017, 12, 31)]["Total"] == 3.4

    def test_quarterly_table(self, monkeypatch):
        """A quarter-indexed section B table melts to quarter-end records."""
        _patch_direct(
            monkeypatch,
            _save({"afdr_b1": [["Period", "Loan Volume"], ["2020Q1", 22.6]]}),
        )
        query = FederalReserveKansasCityAgDatabookArchivedFetcher.transform_query(
            {"table": "afdr_b1"}
        )
        rows = FederalReserveKansasCityAgDatabookArchivedFetcher.extract_data(
            query, None
        )
        result = FederalReserveKansasCityAgDatabookArchivedFetcher.transform_data(
            query, rows
        )
        by_date = {r.date: r.model_dump() for r in result}
        assert by_date[date(2020, 3, 31)]["frequency"] == "quarter"
        assert by_date[date(2020, 3, 31)]["Loan Volume"] == 22.6

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_direct(monkeypatch, b"")
        query = FederalReserveKansasCityAgDatabookArchivedFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveKansasCityAgDatabookArchivedFetcher.extract_data(query, None)
