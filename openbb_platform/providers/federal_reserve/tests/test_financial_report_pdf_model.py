"""Tests for the FFIEC filed financial-report PDF viewer model."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.ffiec.financial_report_pdf import (
    FederalReserveFinancialReportPdfData,
    FederalReserveFinancialReportPdfFetcher,
    _pdf_choices,
)

_PROFILE = {
    "FRY9C": {
        "name": "Consolidated Financial Statements for Holding Companies (FR Y-9C)",
        "periods": [
            {"year": 2024, "quarter": 4, "month_day": "12/31"},
            {"year": 2025, "quarter": 1, "month_day": "3/31"},
        ],
    }
}


def _patch(monkeypatch, profile=None):
    """Patch the institution profile fetch to the fixture."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
        lambda rssd: dict(profile if profile is not None else _PROFILE),
    )


class TestPdfChoices:
    """Tests for the ``_pdf_choices`` helper."""

    def test_builds_urls_in_profile_order(self, monkeypatch):
        """Each filed period yields a ReturnFinancialReportPDF URL choice."""
        _patch(monkeypatch)
        choices = _pdf_choices("1039502", "fry9c")
        assert choices == [
            {
                "label": "2024 Q4",
                "value": "https://www.ffiec.gov/npw/FinancialReport/"
                "ReturnFinancialReportPDF?rpt=FRY9C&id=1039502&dt=20241231",
            },
            {
                "label": "2025 Q1",
                "value": "https://www.ffiec.gov/npw/FinancialReport/"
                "ReturnFinancialReportPDF?rpt=FRY9C&id=1039502&dt=20250331",
            },
        ]

    def test_blank_firm_returns_empty(self):
        """A blank firm yields no choices without a fetch."""
        assert _pdf_choices("", "FRY9C") == []

    def test_no_report_type_lists_latest_of_each(self, monkeypatch):
        """With no report type, the latest filed PDF of each report is offered."""
        _patch(
            monkeypatch,
            profile={
                "FFIEC101": {
                    "name": "FFIEC 101",
                    "periods": [
                        {"year": 2026, "quarter": 1, "month_day": "3/31"},
                        {"year": 2025, "quarter": 4, "month_day": "12/31"},
                    ],
                },
                "FFIEC102": {
                    "name": "FFIEC 102",
                    "periods": [{"year": 2026, "quarter": 1, "month_day": "3/31"}],
                },
            },
        )
        choices = _pdf_choices("852218", None)
        assert [c["label"] for c in choices] == [
            "FFIEC 101 — 2026 Q1",
            "FFIEC 102 — 2026 Q1",
        ]

    def test_non_mapping_result_returns_empty(self, monkeypatch):
        """A non-mapping profile result (e.g. a stale shape) yields no choices."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: ["FFIEC101"],
        )
        assert _pdf_choices("852218", None) == []

    def test_unknown_report_returns_empty(self, monkeypatch):
        """A report the firm does not file yields no choices."""
        _patch(monkeypatch)
        assert _pdf_choices("1039502", "FRY15") == []


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_lists_filed_pdfs(self, monkeypatch):
        """Every filed period becomes a row with its PDF URL."""
        _patch(monkeypatch)
        query = FederalReserveFinancialReportPdfFetcher.transform_query(
            {"rssd_id": "1039502", "report_type": "FRY9C"}
        )
        rows = FederalReserveFinancialReportPdfFetcher.extract_data(query, None)
        assert {(r["year"], r["quarter"]) for r in rows} == {(2024, 4), (2025, 1)}
        assert all(
            r["url"].startswith(
                "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportPDF"
            )
            for r in rows
        )

    def test_no_filed_periods_raises_empty(self, monkeypatch):
        """A firm that files no period for the report raises ``EmptyDataError``."""
        _patch(monkeypatch, profile={})
        query = FederalReserveFinancialReportPdfFetcher.transform_query(
            {"rssd_id": "1039502", "report_type": "FRY9C"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveFinancialReportPdfFetcher.extract_data(query, None)

    def test_no_report_type_lists_latest_of_each(self, monkeypatch):
        """With no report type, the latest PDF of each filed report becomes a row."""
        _patch(
            monkeypatch,
            profile={
                "FFIEC101": {
                    "name": "FFIEC 101",
                    "periods": [{"year": 2026, "quarter": 1, "month_day": "3/31"}],
                },
                "FFIEC102": {
                    "name": "FFIEC 102",
                    "periods": [{"year": 2025, "quarter": 4, "month_day": "12/31"}],
                },
            },
        )
        query = FederalReserveFinancialReportPdfFetcher.transform_query(
            {"rssd_id": "852218"}
        )
        rows = FederalReserveFinancialReportPdfFetcher.extract_data(query, None)
        assert {r["report_type"] for r in rows} == {"FFIEC101", "FFIEC102"}

    def test_non_mapping_result_raises_empty(self, monkeypatch):
        """A non-mapping profile result raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: ["FFIEC101"],
        )
        query = FederalReserveFinancialReportPdfFetcher.transform_query(
            {"rssd_id": "852218"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveFinancialReportPdfFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data`` ordering and validation."""

    def test_sorts_newest_first(self, monkeypatch):
        """Rows are validated and sorted newest-first."""
        _patch(monkeypatch)
        query = FederalReserveFinancialReportPdfFetcher.transform_query(
            {"rssd_id": "1039502", "report_type": "FRY9C"}
        )
        rows = FederalReserveFinancialReportPdfFetcher.extract_data(query, None)
        result = FederalReserveFinancialReportPdfFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveFinancialReportPdfData) for r in result)
        assert (result[0].year, result[0].quarter) == (2025, 1)
        assert result[0].label == "2025 Q1"
