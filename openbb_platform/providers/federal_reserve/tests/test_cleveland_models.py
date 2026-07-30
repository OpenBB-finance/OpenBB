"""Tests for the Cleveland Fed regional models."""

import io
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.cleveland_inflation import (
    FederalReserveClevelandInflationData,
    FederalReserveClevelandInflationFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_inflation_nowcast import (
    FederalReserveClevelandInflationNowcastData,
    FederalReserveClevelandInflationNowcastFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_median_cpi import (
    FederalReserveClevelandMedianCpiData,
    FederalReserveClevelandMedianCpiFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_median_cpi_components import (
    FederalReserveClevelandMedianCpiComponentsData,
    FederalReserveClevelandMedianCpiComponentsFetcher,
)
from openbb_federal_reserve.models.regional.cleveland_systemic_risk import (
    FederalReserveClevelandSystemicRiskData,
    FederalReserveClevelandSystemicRiskFetcher,
)


def _inflation_workbook() -> bytes:
    """Build an inflation workbook with the expected and ten-year-chart sheets."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Expected Inflation"
    sheet.append(
        [
            "Model Output Date",
            " 1 year Expected Inflation",
            " 10 year Expected Inflation",
        ]
    )
    sheet.append([datetime(2026, 5, 1), 0.0310, 0.0250])
    sheet.append([datetime(2026, 6, 1), 0.0302, 0.0249])
    # The ten-year chart sheet is published in percent, not decimal.
    chart = workbook.create_sheet("Ten-year Expected Chart")
    chart.append(
        [
            "Model Output Date",
            "10 year Expected Inflation",
            "Real Risk Premium",
            "Inflation Risk Premium",
        ]
    )
    chart.append([datetime(2026, 6, 1), 2.49, 1.28, 0.39])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _response(content: bytes) -> MagicMock:
    """Build a make_request response with the given binary body."""
    response = MagicMock()
    response.content = content
    response.raise_for_status = MagicMock()
    return response


def _text_response(text: str) -> MagicMock:
    """Build a make_request response carrying both text and bytes bodies."""
    response = MagicMock()
    response.text = text
    response.content = text.encode("utf-8")
    response.raise_for_status = MagicMock()
    return response


class TestInflationExpectations:
    """Tests for the inflation-expectations fetcher."""

    def test_pivots_and_filters(self, monkeypatch):
        """The expected-inflation sheet pivots to wide and start_date applies."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_inflation_workbook()),
        )
        query = FederalReserveClevelandInflationFetcher.transform_query(
            {"table": "expected_inflation", "start_date": "2026-06-01"}
        )
        rows = FederalReserveClevelandInflationFetcher.extract_data(query, None)
        result = FederalReserveClevelandInflationFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveClevelandInflationData) for r in result)
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2026, 6, 1)
        assert row["1 year Expected Inflation"] == 0.0302
        assert row["10 year Expected Inflation"] == 0.0249
        assert "series" not in row
        assert "value" not in row

    def test_all_series_and_end_date(self, monkeypatch):
        """Every horizon series becomes a column and end_date applies."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_inflation_workbook()),
        )
        query = FederalReserveClevelandInflationFetcher.transform_query(
            {"end_date": "2026-05-31"}
        )
        rows = FederalReserveClevelandInflationFetcher.extract_data(query, None)
        result = FederalReserveClevelandInflationFetcher.transform_data(query, rows)
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2026, 5, 1)
        assert set(row) == {
            "date",
            "1 year Expected Inflation",
            "10 year Expected Inflation",
        }

    def test_ten_year_decomposition_scaled(self, monkeypatch):
        """The ten-year chart sheet is rescaled from percent to decimals."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_inflation_workbook()),
        )
        query = FederalReserveClevelandInflationFetcher.transform_query(
            {"table": "ten_year_decomposition"}
        )
        rows = FederalReserveClevelandInflationFetcher.extract_data(query, None)
        result = FederalReserveClevelandInflationFetcher.transform_data(query, rows)
        row = result[0].model_dump()
        assert row["10 year Expected Inflation"] == pytest.approx(0.0249)
        assert row["Real Risk Premium"] == pytest.approx(0.0128)
        assert row["Inflation Risk Premium"] == pytest.approx(0.0039)

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveClevelandInflationFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveClevelandInflationFetcher.extract_data(query, None)


class TestMedianCpi:
    """Tests for the Median CPI series fetcher."""

    _CSV = (
        "date,mediancpi,trimmedmeancpi,cpi,corecpi\n"
        "2026-04-01,2.5950000001,2.3,2.5,2.2\n"
        "2026-05-01,2.7152000003,2.4,2.8,2.3\n"
    )

    _CHANGE_CSV = (
        "date,mcpi_monthly_chg,mcpi_ann_monthly_chg\n"
        "2026-04-01,0.0019010331209758,2.3\n"
        "2026-05-01,0.0030034608406641,3.7\n"
    )

    def test_pivots_summary_and_filters(self, monkeypatch):
        """The summary CSV pivots to wide columns, rounded to two decimals."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._CSV),
        )
        query = FederalReserveClevelandMedianCpiFetcher.transform_query(
            {"table": "summary", "start_date": "2026-05-01"}
        )
        rows = FederalReserveClevelandMedianCpiFetcher.extract_data(query, None)
        result = FederalReserveClevelandMedianCpiFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveClevelandMedianCpiData) for r in result)
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2026, 5, 1)
        assert row["Median CPI"] == 2.72
        assert row["16% Trimmed-Mean CPI"] == 2.4
        assert "series" not in row
        assert "value" not in row

    def test_small_change_keeps_significant_digits(self, monkeypatch):
        """Tiny monthly-change fractions widen past two decimals, not zero."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._CHANGE_CSV),
        )
        query = FederalReserveClevelandMedianCpiFetcher.transform_query(
            {"table": "median_cpi"}
        )
        rows = FederalReserveClevelandMedianCpiFetcher.extract_data(query, None)
        result = FederalReserveClevelandMedianCpiFetcher.transform_data(query, rows)
        changes = [r.model_dump()["Median CPI, 1-Month Change"] for r in result]
        assert changes == [0.0019, 0.003]
        assert result[0].model_dump()["Median CPI, 1-Month Annualized"] == 2.3

    def test_end_date_filters(self, monkeypatch):
        """The end_date filter narrows the pivoted rows to earlier months."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._CSV),
        )
        query = FederalReserveClevelandMedianCpiFetcher.transform_query(
            {"table": "summary", "end_date": "2026-04-30"}
        )
        rows = FederalReserveClevelandMedianCpiFetcher.extract_data(query, None)
        result = FederalReserveClevelandMedianCpiFetcher.transform_data(query, rows)
        assert {r.date for r in result} == {date(2026, 4, 1)}

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(""),
        )
        query = FederalReserveClevelandMedianCpiFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveClevelandMedianCpiFetcher.extract_data(query, None)


class TestMedianCpiComponents:
    """Tests for the Median CPI components fetcher."""

    _CSV = (
        "Component,1-Month Annualized Percent Change,"
        "Relative Importance (Normalized),Cumulative Relative Importance\n"
        "Car and truck rental,-40.34,0.1,0.1\n"
        "Motor vehicle insurance,-18.48,2.7,2.8\n"
    )

    def test_parses_components(self, monkeypatch):
        """Each component row keeps its change and importance values."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._CSV),
        )
        query = FederalReserveClevelandMedianCpiComponentsFetcher.transform_query({})
        rows = FederalReserveClevelandMedianCpiComponentsFetcher.extract_data(
            query, None
        )
        result = FederalReserveClevelandMedianCpiComponentsFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveClevelandMedianCpiComponentsData)
            for r in result
        )
        first = result[0]
        assert first.component == "Car and truck rental"
        assert first.change == -40.34
        assert first.cumulative_relative_importance == 0.1

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(""),
        )
        query = FederalReserveClevelandMedianCpiComponentsFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveClevelandMedianCpiComponentsFetcher.extract_data(query, None)


class TestSystemicRisk:
    """Tests for the Systemic Risk Indicator fetcher."""

    _CSV = (
        "date,add,sri,pdd\n"
        "2025-09-30,2.1,0.2,1.9\n"
        "2025-10-01,2.2049999998,0.2533333331,1.9516666667\n"
    )

    def test_pivots_components(self, monkeypatch):
        """The indicator and its two legs pivot to wide, rounded columns."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._CSV),
        )
        query = FederalReserveClevelandSystemicRiskFetcher.transform_query(
            {"start_date": "2025-10-01"}
        )
        rows = FederalReserveClevelandSystemicRiskFetcher.extract_data(query, None)
        result = FederalReserveClevelandSystemicRiskFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveClevelandSystemicRiskData) for r in result
        )
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2025, 10, 1)
        assert row["Systemic Risk Indicator (ADD minus PDD)"] == 0.25
        assert row["Average Distance-to-Default (ADD)"] == 2.2
        assert "series" not in row
        assert "value" not in row

    def test_end_date_filters(self, monkeypatch):
        """The end_date filter narrows the pivoted rows to earlier dates."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._CSV),
        )
        query = FederalReserveClevelandSystemicRiskFetcher.transform_query(
            {"end_date": "2025-09-30"}
        )
        rows = FederalReserveClevelandSystemicRiskFetcher.extract_data(query, None)
        result = FederalReserveClevelandSystemicRiskFetcher.transform_data(query, rows)
        assert {r.date for r in result} == {date(2025, 9, 30)}

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(""),
        )
        query = FederalReserveClevelandSystemicRiskFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveClevelandSystemicRiskFetcher.extract_data(query, None)


class TestInflationNowcast:
    """Tests for the Inflation Nowcasting fetcher."""

    _JSON = (
        '[{"chart":{"subcaption":"2026-6"},"dataset":['
        '{"seriesname":"CPI Inflation","data":[{"value":""},{"value":"0.20"}]},'
        '{"seriesname":"Actual CPI Inflation","data":[{"value":""},{"value":""}]}'
        "]}]"
    )

    def test_takes_final_value_per_series(self, monkeypatch):
        """The final non-empty value per series is kept; empty actuals drop out."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._JSON),
        )
        query = FederalReserveClevelandInflationNowcastFetcher.transform_query(
            {"frequency": "month"}
        )
        rows = FederalReserveClevelandInflationNowcastFetcher.extract_data(query, None)
        result = FederalReserveClevelandInflationNowcastFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveClevelandInflationNowcastData) for r in result
        )
        # The empty actual series is excluded; only the final nowcast survives.
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2026, 6, 1)
        assert row["CPI Inflation"] == 0.20
        assert "Actual CPI Inflation" not in row
        assert "series" not in row
        assert "value" not in row

    _MULTI_JSON = (
        "["
        '{"chart":{"subcaption":"2026:Q1"},"dataset":['
        '{"seriesname":"CPI Inflation","data":[{"value":"1.10"}]}]},'
        '{"chart":{"subcaption":"2026:Q2"},"dataset":['
        '{"seriesname":"CPI Inflation","data":[{"value":"1.20"}]}]},'
        '{"chart":{"subcaption":"2025"},"dataset":['
        '{"seriesname":"CPI Inflation","data":[{"value":"2.50"}]}]},'
        '{"chart":{"subcaption":"not a period"},"dataset":['
        '{"seriesname":"CPI Inflation","data":[{"value":"9.99"}]}]}'
        "]"
    )

    def test_decodes_periods_and_filters(self, monkeypatch):
        """Quarter and year subcaptions decode; unparseable and out-of-range drop."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(self._MULTI_JSON),
        )
        query = FederalReserveClevelandInflationNowcastFetcher.transform_query(
            {
                "frequency": "quarter",
                "start_date": "2026-01-01",
                "end_date": "2026-03-31",
            }
        )
        rows = FederalReserveClevelandInflationNowcastFetcher.extract_data(query, None)
        result = FederalReserveClevelandInflationNowcastFetcher.transform_data(
            query, rows
        )
        assert {r.date for r in result} == {date(2026, 1, 1)}
        assert result[0].model_dump()["CPI Inflation"] == 1.10

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _text_response(""),
        )
        query = FederalReserveClevelandInflationNowcastFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveClevelandInflationNowcastFetcher.extract_data(query, None)
