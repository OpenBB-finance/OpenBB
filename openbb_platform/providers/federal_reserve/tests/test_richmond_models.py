"""Tests for the Richmond Fed regional data models."""

import io
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.richmond_cfo import (
    FederalReserveRichmondCFOData,
    FederalReserveRichmondCFOFetcher,
)
from openbb_federal_reserve.models.regional.richmond_manufacturing import (
    FederalReserveRichmondManufacturingData,
    FederalReserveRichmondManufacturingFetcher,
)
from openbb_federal_reserve.models.regional.richmond_nei import (
    FederalReserveRichmondNonEmploymentData,
    FederalReserveRichmondNonEmploymentFetcher,
)
from openbb_federal_reserve.models.regional.richmond_service_sector import (
    FederalReserveRichmondServiceSectorData,
    FederalReserveRichmondServiceSectorFetcher,
)
from openbb_federal_reserve.models.regional.richmond_sos import (
    FederalReserveRichmondRecessionIndicatorData,
    FederalReserveRichmondRecessionIndicatorFetcher,
)
from openbb_federal_reserve.models.regional.richmond_state_survey import (
    FederalReserveRichmondStateSurveyData,
    FederalReserveRichmondStateSurveyFetcher,
)


def _workbook(sheet: str, header: list, rows: list) -> bytes:
    """Build a single-sheet workbook with one header row and data rows."""
    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet
    worksheet.append(header)
    for row in rows:
        worksheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _response(content: bytes) -> MagicMock:
    """Build a make_request response with the given binary body."""
    response = MagicMock()
    response.content = content
    response.raise_for_status = MagicMock()
    return response


def _patch_request(monkeypatch, content: bytes) -> None:
    """Point ``request_bytes`` (via make_request) at the given workbook bytes."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request",
        lambda *a, **k: _response(content),
    )


def _survey_workbook(sheet: str) -> bytes:
    """Build a Fifth District survey workbook with a missing cell to clean."""
    return _workbook(
        sheet,
        ["date", "sa_mfg_composite", "nsa_mfg_ship_c", "nsa_mfg_workwk_c"],
        [
            [datetime(2026, 5, 1), 13, 13, "#N/A"],
            [datetime(2026, 6, 1), 4, 3, "#N/A"],
        ],
    )


def _state_workbook(sheet: str) -> bytes:
    """Build a state-survey workbook keyed on ``nsa_gen_bus_cond_c``."""
    return _workbook(
        sheet,
        ["date", "nsa_gen_bus_cond_c", "nsa_sales_c"],
        [
            [datetime(2026, 4, 1), 5, 22],
            [datetime(2026, 5, 1), 2, 17],
        ],
    )


class TestFetchSurveyWorkbook:
    """Tests for the shared survey-workbook downloader."""

    def test_unknown_survey_raises(self):
        """An unknown survey key raises ``OpenBBError``."""
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_federal_reserve.utils.richmond_surveys import fetch_survey_workbook

        with pytest.raises(OpenBBError):
            fetch_survey_workbook("widgets")


class TestSurveyColumnDecoding:
    """Tests for the survey-column decoder and its raw-label fallback."""

    def test_undecodable_columns_keep_raw_labels(self):
        """Columns that fail to decode keep the raw label with null parts."""
        from openbb_federal_reserve.utils.richmond_surveys import parse_survey_long

        content = _workbook(
            "Sheet",
            ["date", "random_col", "sa_c"],
            [[datetime(2026, 6, 1), 11, 22]],
        )
        rows = parse_survey_long(content, "Sheet")
        by_indicator = {r["indicator"]: r for r in rows}
        # A bad adjustment prefix and an adjustment+horizon-only column both fail
        # to decode, falling back to the raw label with null adjustment/horizon.
        assert by_indicator["random_col"]["adjustment"] is None
        assert by_indicator["random_col"]["horizon"] is None
        assert by_indicator["random_col"]["value"] == 11
        assert by_indicator["sa_c"]["adjustment"] is None
        assert by_indicator["sa_c"]["value"] == 22


class TestManufacturing:
    """Tests for the manufacturing survey fetcher."""

    def test_parses_cleans_and_filters(self, monkeypatch):
        """The survey sheet parses, ``#N/A`` becomes None, and dates filter."""
        _patch_request(monkeypatch, _survey_workbook("Mfg Historical Series"))
        query = FederalReserveRichmondManufacturingFetcher.transform_query(
            {"start_date": "2026-06-01", "end_date": "2026-06-30"}
        )
        rows = FederalReserveRichmondManufacturingFetcher.extract_data(query, None)
        result = FederalReserveRichmondManufacturingFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveRichmondManufacturingData) for r in result
        )
        assert all(r.date == date(2026, 6, 1) for r in result)
        # Indicators are pivoted to dynamic columns keyed by (adjustment, horizon).
        by_cut = {(r.adjustment, r.horizon): r.model_dump() for r in result}
        sa_current = by_cut[("Seasonally Adjusted", "Current")]
        nsa_current = by_cut[("Not Seasonally Adjusted", "Current")]
        assert sa_current["Composite Index"] == 4
        assert nsa_current["Shipments"] == 3
        assert nsa_current["Average Workweek"] is None

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveRichmondManufacturingFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveRichmondManufacturingFetcher.extract_data(query, None)


class TestServiceSector:
    """Tests for the service-sector survey fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The non-mfg sheet parses and dates filter."""
        content = _workbook(
            "Non-Mfg Historical Series",
            ["date", "sa_svc_revs_sales_c", "nsa_svc_demand_c"],
            [
                [datetime(2026, 5, 1), 14, 15],
                [datetime(2026, 6, 1), -1, 6],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondServiceSectorFetcher.transform_query(
            {"start_date": "2026-06-01"}
        )
        rows = FederalReserveRichmondServiceSectorFetcher.extract_data(query, None)
        result = FederalReserveRichmondServiceSectorFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveRichmondServiceSectorData) for r in result
        )
        assert all(r.date == date(2026, 6, 1) for r in result)
        # Revenues is a dynamic column; find the seasonally adjusted current row.
        revenues = next(
            r.model_dump()["Revenues"]
            for r in result
            if r.adjustment == "Seasonally Adjusted" and r.horizon == "Current"
        )
        assert revenues == -1

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveRichmondServiceSectorFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveRichmondServiceSectorFetcher.extract_data(query, None)


class TestStateSurvey:
    """Tests for the state survey fetcher."""

    def test_default_state_is_virginia(self, monkeypatch):
        """The default state reads the Virginia sheet."""
        _patch_request(monkeypatch, _state_workbook("VA Historical Series"))
        query = FederalReserveRichmondStateSurveyFetcher.transform_query({})
        assert query.state == "virginia"
        rows = FederalReserveRichmondStateSurveyFetcher.extract_data(query, None)
        result = FederalReserveRichmondStateSurveyFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveRichmondStateSurveyData) for r in result)
        assert {r.date for r in result} == {date(2026, 4, 1), date(2026, 5, 1)}

    def test_carolinas_state_and_filter(self, monkeypatch):
        """A requested state reads its sheet and dates filter."""
        _patch_request(monkeypatch, _state_workbook("CAR Historical Series"))
        query = FederalReserveRichmondStateSurveyFetcher.transform_query(
            {"state": "carolinas", "end_date": "2026-04-30"}
        )
        rows = FederalReserveRichmondStateSurveyFetcher.extract_data(query, None)
        result = FederalReserveRichmondStateSurveyFetcher.transform_data(query, rows)
        assert all(r.date == date(2026, 4, 1) for r in result)
        conditions = next(
            r.model_dump()["General Business Conditions"]
            for r in result
            if r.horizon == "Current"
        )
        assert conditions == 5

    def test_carolinas_specific_indicator_labels(self, monkeypatch):
        """Carolinas-only columns decode to readable indicator labels."""
        content = _workbook(
            "CAR Historical Series",
            ["date", "nsa_bus_cond_nation_c", "nsa_bus_cond_region_c", "nsa_sales_c"],
            [[datetime(2026, 5, 1), 11, 7, 22]],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondStateSurveyFetcher.transform_query(
            {"state": "carolinas"}
        )
        rows = FederalReserveRichmondStateSurveyFetcher.extract_data(query, None)
        result = FederalReserveRichmondStateSurveyFetcher.transform_data(query, rows)
        # The decoded indicators are pivoted to dynamic columns on each row.
        labels = {key for r in result for key in r.model_dump()}
        assert "Business Conditions (Nation)" in labels
        assert "Business Conditions (Region)" in labels
        assert "Sales" in labels

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveRichmondStateSurveyFetcher.transform_query(
            {"state": "maryland"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveRichmondStateSurveyFetcher.extract_data(query, None)

    def test_float_values_pass_through_raw(self, monkeypatch):
        """Diffusion indices pass through unrounded from the workbook."""
        content = _workbook(
            "VA Historical Series",
            ["date", "nsa_sales_c"],
            [[datetime(2026, 5, 1), 2.123456789]],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondStateSurveyFetcher.transform_query({})
        rows = FederalReserveRichmondStateSurveyFetcher.extract_data(query, None)
        result = FederalReserveRichmondStateSurveyFetcher.transform_data(query, rows)
        assert result[0].model_dump()["Sales"] == 2.123456789


class TestCFO:
    """Tests for the CFO survey fetcher."""

    def test_builds_quarter_dates_and_filters(self, monkeypatch):
        """The optimism sheet builds quarter-start dates and filters."""
        content = _workbook(
            "CFO_optimism_all",
            [
                "year",
                "quarter",
                "economy_N",
                "economy_mean",
                "economy_median",
                "ownfirm_N",
                "ownfirm_mean",
                "ownfirm_median",
            ],
            [
                [2025, 4, 602, 60.27, 60.0, 603, 69.63, 75],
                [2026, 1, 471, 61.67, 65.0, 473, 70.15, 75],
                [2026, 2, 528, 60.57, 62.5, 530, 70.72, 75],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondCFOFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-06-30"}
        )
        rows = FederalReserveRichmondCFOFetcher.extract_data(query, None)
        result = FederalReserveRichmondCFOFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveRichmondCFOData) for r in result)
        assert {r.date for r in result} == {date(2026, 1, 1), date(2026, 4, 1)}
        # Measures are pivoted to dynamic columns; one row per (date, category).
        q2 = next(r.model_dump() for r in result if r.date == date(2026, 4, 1))
        assert q2["economy_median"] == 62.5

    def test_legacy_table_reads_through_q1_2020_sheet(self, monkeypatch):
        """The legacy table reads the ``through_Q1_2020`` sheet and melts it."""
        content = _workbook(
            "through_Q1_2020",
            ["year", "quarter", "opt_rating_econ", "opt_rating_own", "revenue_g"],
            [
                [2019, 4, 66.6, 75.0, 5.5],
                [2020, 1, 50.9, 59.7, 1.6],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondCFOFetcher.transform_query(
            {"table": "legacy_through_q1_2020"}
        )
        rows = FederalReserveRichmondCFOFetcher.extract_data(query, None)
        result = FederalReserveRichmondCFOFetcher.transform_data(query, rows)
        assert {r.date for r in result} == {date(2019, 10, 1), date(2020, 1, 1)}
        revenue = next(
            r.model_dump()["revenue_g"] for r in result if r.date == date(2020, 1, 1)
        )
        assert revenue == 1.6

    def test_text_breakdown_column_becomes_category(self, monkeypatch):
        """A non-numeric breakdown column is carried as the row's category."""
        content = _workbook(
            "CFO_optimism_bysector",
            ["year", "quarter", "sector", "economy_mean"],
            [
                [2026, 1, "Manufacturing", 61.5],
                [2026, 1, "Services", 59.2],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondCFOFetcher.transform_query(
            {"table": "optimism_by_sector"}
        )
        rows = FederalReserveRichmondCFOFetcher.extract_data(query, None)
        result = FederalReserveRichmondCFOFetcher.transform_data(query, rows)
        # The sector breakdown stays as the row-group ``category``; the measure is
        # a dynamic column on each row.
        by_category = {r.category: r.model_dump()["economy_mean"] for r in result}
        assert by_category["Manufacturing"] == 61.5
        assert by_category["Services"] == 59.2

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveRichmondCFOFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveRichmondCFOFetcher.extract_data(query, None)

    def test_float_values_pass_through_raw(self, monkeypatch):
        """Long-decimal measures pass through unrounded; NaN cells become None."""
        content = _workbook(
            "CFO_optimism_all",
            ["year", "quarter", "economy_mean", "ownfirm_mean"],
            [
                [2026, 1, 59.7491638795986, 70.1],
                [2026, 2, "#N/A", 71.2],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondCFOFetcher.transform_query({})
        rows = FederalReserveRichmondCFOFetcher.extract_data(query, None)
        result = FederalReserveRichmondCFOFetcher.transform_data(query, rows)
        by_date = {r.date: r.model_dump() for r in result}
        assert by_date[date(2026, 1, 1)]["economy_mean"] == 59.7491638795986
        assert by_date[date(2026, 4, 1)]["economy_mean"] is None


class TestNonEmploymentIndex:
    """Tests for the Non-Employment Index fetcher."""

    def test_builds_month_dates_and_filters(self, monkeypatch):
        """The Data sheet builds month dates from YEAR/MONTH and filters."""
        content = _workbook(
            "Data",
            ["YEAR", "MONTH", "NEI_26_SA", "NEI_26_pter_SA", "u5", "u6", "urate"],
            [
                [2026, 4, 7.52, 8.36, 5.3, 8.2, 4.3],
                [2026, 5, 7.80, 8.66, 5.3, 8.1, 4.3],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondNonEmploymentFetcher.transform_query(
            {"start_date": "2026-05-01", "end_date": "2026-05-31"}
        )
        rows = FederalReserveRichmondNonEmploymentFetcher.extract_data(query, None)
        result = FederalReserveRichmondNonEmploymentFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveRichmondNonEmploymentData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 5, 1)
        assert result[0].nei == 7.80
        assert result[0].unemployment_rate == 4.3

    def test_drops_all_none_value_rows_keeps_partial(self, monkeypatch):
        """An all-None value row is dropped; a partially-populated row is kept."""
        content = _workbook(
            "Data",
            ["YEAR", "MONTH", "NEI_26_SA", "NEI_26_pter_SA", "u5", "u6", "urate"],
            [
                [2026, 4, None, None, None, None, None],
                [2026, 5, 7.80, None, None, None, None],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondNonEmploymentFetcher.transform_query({})
        rows = FederalReserveRichmondNonEmploymentFetcher.extract_data(query, None)
        result = FederalReserveRichmondNonEmploymentFetcher.transform_data(query, rows)
        assert len(result) == 1
        assert result[0].date == date(2026, 5, 1)
        assert result[0].nei == 7.80
        assert result[0].nei_plus is None

    def test_all_rows_empty_raises(self, monkeypatch):
        """A sheet whose value columns are all None raises ``EmptyDataError``."""
        content = _workbook(
            "Data",
            ["YEAR", "MONTH", "NEI_26_SA", "NEI_26_pter_SA", "u5", "u6", "urate"],
            [
                [2026, 4, None, None, None, None, None],
                [2026, 5, None, None, None, None, None],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondNonEmploymentFetcher.transform_query({})
        rows = FederalReserveRichmondNonEmploymentFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveRichmondNonEmploymentFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveRichmondNonEmploymentFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveRichmondNonEmploymentFetcher.extract_data(query, None)


class TestRecessionIndicator:
    """Tests for the SOS recession indicator fetcher."""

    def test_parses_weekly_and_filters(self, monkeypatch):
        """The Data sheet parses the weekly date column and filters."""
        content = _workbook(
            "Data",
            ["Date", "SOS indicator", "Recession Threshold"],
            [
                [datetime(2026, 5, 30), 0.0, 0.2],
                [datetime(2026, 6, 6), 0.0, 0.2],
            ],
        )
        _patch_request(monkeypatch, content)
        query = FederalReserveRichmondRecessionIndicatorFetcher.transform_query(
            {"start_date": "2026-06-01", "end_date": "2026-06-30"}
        )
        rows = FederalReserveRichmondRecessionIndicatorFetcher.extract_data(query, None)
        result = FederalReserveRichmondRecessionIndicatorFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveRichmondRecessionIndicatorData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 6)
        assert result[0].sos == 0.0
        assert result[0].recession_threshold == 0.2

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveRichmondRecessionIndicatorFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveRichmondRecessionIndicatorFetcher.extract_data(query, None)
