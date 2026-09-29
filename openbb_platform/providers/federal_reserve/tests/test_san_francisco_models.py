"""Tests for the San Francisco Fed regional dataset models."""

import io
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_federal_reserve.models.regional.san_francisco_cyclical_pce import (
    FederalReserveSanFranciscoCyclicalPceData,
    FederalReserveSanFranciscoCyclicalPceFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_news_sentiment import (
    FederalReserveSanFranciscoNewsSentimentData,
    FederalReserveSanFranciscoNewsSentimentFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_proxy_funds_rate import (
    FederalReserveSanFranciscoProxyFundsRateData,
    FederalReserveSanFranciscoProxyFundsRateFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_short_rate_path import (
    FederalReserveSanFranciscoShortRatePathData,
    FederalReserveSanFranciscoShortRatePathFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_supply_demand_pce import (
    FederalReserveSanFranciscoSupplyDemandPceData,
    FederalReserveSanFranciscoSupplyDemandPceFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_term_premium import (
    FederalReserveSanFranciscoTermPremiumData,
    FederalReserveSanFranciscoTermPremiumFetcher,
)
from openbb_federal_reserve.models.regional.san_francisco_tfp import (
    FederalReserveSanFranciscoTfpData,
    FederalReserveSanFranciscoTfpFetcher,
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


def _response(content: bytes) -> MagicMock:
    """Build a make_request response with the given binary body."""
    response = MagicMock()
    response.content = content
    response.raise_for_status = MagicMock()
    return response


def _news_sentiment_workbook() -> bytes:
    """Build a News Sentiment workbook with the Data sheet."""
    return _save(
        {
            "Methodology": [["note"]],
            "Data": [
                ["date", "News Sentiment"],
                [datetime(2026, 6, 20), 0.0277],
                [datetime(2026, 6, 21), 0.0342],
            ],
        }
    )


def _proxy_workbook() -> bytes:
    """Build a Proxy Funds Rate workbook with Weekly and Monthly sheets."""
    return _save(
        {
            "Description": [["note"]],
            "Weekly": [
                ["Date", "Effective funds rate", "Proxy funds rate"],
                ["2026-06-12", 3.63, 4.50],
                ["2026-06-19", 3.63, 4.524],
            ],
            "Monthly": [
                ["Date", "Effective funds rate", "Proxy funds rate"],
                ["2026-04-30", 3.63, 4.40],
                ["2026-05-31", 3.63, 4.232],
            ],
        }
    )


def _cyclical_workbook() -> bytes:
    """Build a Cyclical & Acyclical PCE workbook with leading-space dates."""
    header = [
        "time_month",
        "Cyclical core PCE inflation (y/y)",
        "Acyclical core PCE inflation (y/y)",
        "Cyclical core PCE contribution (y/y)",
        "Ayclical core PCE contribution (y/y)",
        "Health-care services portion of acyclical contribution (y/y)",
        "Non-health-care portion of acyclical contribution (y/y)",
        "Cyclical core PCE inflation (m/m, ar)",
        "Acyclical core PCE inflation (m/m, ar)",
        "Cyclical core PCE contribution (m/m, ar)",
        "Ayclical core PCE contribution (m/m, ar)",
        "Health-care services portion of acyclical contribution (m/m, ar)",
        "Non-health-care portion of acyclical contribution (m/m, ar)",
    ]
    return _save(
        {
            "Data": [
                header,
                [" 2026m3", *[1.0] * 12],
                [" 2026m4", 3.31, 3.33, 1.28, 2.04, 0.51, 1.53, *[2.0] * 6],
            ]
        }
    )


def _supply_demand_workbook() -> bytes:
    """Build a Supply & Demand PCE workbook with mixed-space dates."""
    header = [
        "time_month",
        "Demand-driven Inflation (core, y/y)",
        "Ambiguous (core, y/y)",
        "Supply-driven Inflation (core, y/y)",
        "Demand-driven Inflation (core, m/m)",
        "Ambiguous (core, m/m)",
        "Supply-driven Inflation (core, m/m)",
        "Demand-driven Inflation (headline, y/y)",
        "Ambiguous (headline, y/y)",
        "Supply-driven Inflation (headline, y/y)",
        "Demand-driven Inflation (headline, m/m)",
        "Ambiguous (headline, m/m)",
        "Supply-driven Inflation (headline, m/m)",
    ]
    return _save(
        {
            "Data": [
                header,
                ["2026m3", *[0.5] * 12],
                [" 2026m4", 1.13, 0.86, 1.29, *[0.9] * 9],
            ]
        }
    )


def _tfp_workbook() -> bytes:
    """Build a Quarterly TFP workbook with the one-row note offset."""
    header = [
        "date",
        "dY_prod",
        "dY_inc",
        "dY",
        "dhours",
        "dLP",
        "dk",
        "dLQ_BLS_interpolated",
        "dLQ_Aaronson_Sullivan",
        "dLQ",
        "alpha",
        "dtfp",
        "dutil",
        "dtfp_util",
        "relativePrice",
        "invShare",
        "dtfp_I",
        "dtfp_C",
        "du_invest",
        "du_consumption",
        "dtfp_I_util",
        "dtfp_C_util",
    ]

    def _row(label, dY, dtfp):
        """Build a TFP row with sentinel values in mapped columns."""
        values = [None] * (len(header) - 1)
        values[2] = dY
        values[3] = 0.8
        values[4] = -0.3
        values[5] = 2.8
        values[8] = -1.4
        values[10] = dtfp
        values[11] = 2.4
        values[12] = -2.7
        values[15] = 1.0
        values[16] = -0.7
        return [label, *values]

    return _save(
        {
            "quarterly": [
                ["Note: growth-accounting series."],
                header,
                _row("2025:Q4", 0.4, 0.1),
                _row("2026:Q1", 0.49, -0.33),
                ["2026:Q2", *[None] * (len(header) - 1)],
                ["Past 8 qtrs", *[None] * (len(header) - 1)],
                ["nan", *[None] * (len(header) - 1)],
            ],
            "Capital-input-details": [
                ["Note: capital input composition."],
                ["date", "Capital Input:", "dk", "dk_software", "Weights:", "wgt_soft"],
                ["2026:Q1", None, 3.1, 1.2, None, 0.4],
            ],
        }
    )


def _tfp_annual_workbook() -> bytes:
    """Build an annual TFP workbook whose ``annual`` sheet has a four-digit-year index."""
    return _save(
        {
            "annual": [
                ["date", "dY", "dtfp"],
                [2024, 1.2, 0.4],
                [2025.0, 1.5, 0.5],
                ["Average", None, None],
            ],
        }
    )


def _term_premium_workbook() -> bytes:
    """Build a Term Premium web-chart workbook with both decompositions."""
    return _save(
        {
            "Contents": [["note"]],
            "Two_year_decomposition": [
                ["date", "ZCYLD02YR", "AVGEXP02YR", "ZCTERM02YR"],
                [datetime(2026, 6, 22), 4.10, 3.94, 0.16],
                [datetime(2026, 6, 23), 4.1164, 3.945234, 0.171166],
            ],
            "Ten_year_decomposition": [
                ["date", "ZCYLD10YR", "AVGEXP10YR", "ZCTERM10YR"],
                [datetime(2026, 6, 22), 4.55, 3.39, 1.16],
                [datetime(2026, 6, 23), 4.5601, 3.395567, 1.164533],
            ],
            "Estimated_Short_Rate_Path": [
                ["MATURITY", "MOSTRECENT", "FOMC"],
                [0.25, 4.10, 3.93],
                [1.0, 3.80, 3.50],
                [2.0, 3.601, None],
            ],
        }
    )


class TestNewsSentiment:
    """Tests for the Daily News Sentiment fetcher."""

    def test_parses_and_filters(self, monkeypatch):
        """The Data sheet parses and dates filter."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_news_sentiment_workbook()),
        )
        query = FederalReserveSanFranciscoNewsSentimentFetcher.transform_query(
            {"start_date": "2026-06-21", "end_date": "2026-06-21"}
        )
        rows = FederalReserveSanFranciscoNewsSentimentFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoNewsSentimentFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveSanFranciscoNewsSentimentData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 21)
        assert result[0].news_sentiment == 0.0342

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveSanFranciscoNewsSentimentFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoNewsSentimentFetcher.extract_data(query, None)


class TestProxyFundsRate:
    """Tests for the Proxy Funds Rate fetcher."""

    def test_weekly_sheet(self, monkeypatch):
        """The weekly sheet parses and string dates coerce."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_proxy_workbook()),
        )
        query = FederalReserveSanFranciscoProxyFundsRateFetcher.transform_query(
            {"frequency": "weekly", "start_date": "2026-06-15"}
        )
        rows = FederalReserveSanFranciscoProxyFundsRateFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoProxyFundsRateFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveSanFranciscoProxyFundsRateData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 19)
        assert result[0].proxy_funds_rate == 4.524

    def test_monthly_sheet_and_end_date(self, monkeypatch):
        """The monthly sheet parses and the end_date filter applies."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_proxy_workbook()),
        )
        query = FederalReserveSanFranciscoProxyFundsRateFetcher.transform_query(
            {"frequency": "monthly", "end_date": "2026-04-30"}
        )
        rows = FederalReserveSanFranciscoProxyFundsRateFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoProxyFundsRateFetcher.transform_data(
            query, rows
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 4, 30)
        assert result[0].proxy_funds_rate == 4.40

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveSanFranciscoProxyFundsRateFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoProxyFundsRateFetcher.extract_data(query, None)


class TestCyclicalPce:
    """Tests for the Cyclical & Acyclical Core PCE fetcher."""

    def test_strips_leading_space_dates_and_filters(self, monkeypatch):
        """Leading-space YYYYmM dates strip and parse, and dates filter."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_cyclical_workbook()),
        )
        query = FederalReserveSanFranciscoCyclicalPceFetcher.transform_query(
            {"start_date": "2026-04-01", "end_date": "2026-04-30"}
        )
        rows = FederalReserveSanFranciscoCyclicalPceFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoCyclicalPceFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveSanFranciscoCyclicalPceData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 4, 1)
        assert result[0].cyclical_inflation_yoy == 3.31
        assert result[0].acyclical_non_healthcare_contribution_yoy == 1.53

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveSanFranciscoCyclicalPceFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoCyclicalPceFetcher.extract_data(query, None)


class TestSupplyDemandPce:
    """Tests for the Supply & Demand-Driven PCE fetcher."""

    def test_mixed_space_dates_and_end_date(self, monkeypatch):
        """Both spaced and unspaced YYYYmM dates parse and end_date filters."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_supply_demand_workbook()),
        )
        query = FederalReserveSanFranciscoSupplyDemandPceFetcher.transform_query(
            {"start_date": "2026-04-01", "end_date": "2026-04-30"}
        )
        rows = FederalReserveSanFranciscoSupplyDemandPceFetcher.extract_data(
            query, None
        )
        result = FederalReserveSanFranciscoSupplyDemandPceFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveSanFranciscoSupplyDemandPceData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 4, 1)
        assert result[0].demand_core_yoy == 1.13
        assert result[0].supply_core_yoy == 1.29

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveSanFranciscoSupplyDemandPceFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoSupplyDemandPceFetcher.extract_data(query, None)


class TestTotalFactorProductivity:
    """Tests for the Quarterly TFP (Fernald) fetcher."""

    def test_decodes_series_and_filters(self, monkeypatch):
        """The YYYY:QN rows pivot to one wide row per quarter-end date.

        The all-None ``2026:Q2`` quarter passes the date filter yet carries no
        value, so it is dropped from the wide output.
        """
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_tfp_workbook()),
        )
        query = FederalReserveSanFranciscoTfpFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-06-30"}
        )
        rows = FederalReserveSanFranciscoTfpFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoTfpFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveSanFranciscoTfpData) for r in result)
        assert len(result) == 1
        assert all(r.date != date(2026, 6, 30) for r in result)
        row = result[0].model_dump()
        assert result[0].date == date(2026, 3, 31)
        assert row["Output"] == 0.49
        assert row["TFP"] == -0.33

    def test_capital_input_details(self, monkeypatch):
        """The capital-input sheet pivots every value column wide; markers drop out."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_tfp_workbook()),
        )
        query = FederalReserveSanFranciscoTfpFetcher.transform_query(
            {"table": "capital_input_details"}
        )
        rows = FederalReserveSanFranciscoTfpFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoTfpFetcher.transform_data(query, rows)
        assert len(result) == 1
        row = result[0].model_dump()
        # "dk" carries its readme label; section-marker columns are dropped.
        assert row["Capital Input"] == 3.1
        assert row["dk_software"] == 1.2
        assert row["wgt_soft"] == 0.4
        assert "Capital Input:" not in row
        assert result[0].date == date(2026, 3, 31)

    def test_annual_table_dates_year_end(self, monkeypatch):
        """The annual table keeps four-digit-year rows and dates them at year-end."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_tfp_annual_workbook()),
        )
        query = FederalReserveSanFranciscoTfpFetcher.transform_query(
            {"table": "annual", "start_date": "2025-01-01"}
        )
        rows = FederalReserveSanFranciscoTfpFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoTfpFetcher.transform_data(query, rows)
        assert all(r.date == date(2025, 12, 31) for r in result)
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["Output"] == 1.5
        assert row["TFP"] == 0.5

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveSanFranciscoTfpFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoTfpFetcher.extract_data(query, None)


class TestShortRatePath:
    """Tests for the Estimated Short-Rate Path fetcher."""

    def test_pivots_scenarios_wide_by_horizon(self, monkeypatch):
        """Both scenarios pivot to one wide row per horizon, with raw values."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_term_premium_workbook()),
        )
        query = FederalReserveSanFranciscoShortRatePathFetcher.transform_query({})
        rows = FederalReserveSanFranciscoShortRatePathFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoShortRatePathFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveSanFranciscoShortRatePathData) for r in result
        )
        assert len(result) == 3
        by_maturity = {r.maturity: r.model_dump() for r in result}
        assert by_maturity[0.25]["Most Recent"] == 4.10
        assert by_maturity[1.0]["FOMC Summary of Economic Projections"] == 3.50
        assert by_maturity[0.25]["FOMC Summary of Economic Projections"] == 3.93
        assert by_maturity[2.0]["Most Recent"] == 3.601
        assert by_maturity[2.0]["FOMC Summary of Economic Projections"] is None

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveSanFranciscoShortRatePathFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoShortRatePathFetcher.extract_data(query, None)


class TestTermPremium:
    """Tests for the Treasury Term Premium fetcher."""

    def test_two_year_decomposition(self, monkeypatch):
        """The two-year sheet maps its suffixed columns."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_term_premium_workbook()),
        )
        query = FederalReserveSanFranciscoTermPremiumFetcher.transform_query(
            {"maturity": 2, "start_date": "2026-06-23"}
        )
        rows = FederalReserveSanFranciscoTermPremiumFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoTermPremiumFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveSanFranciscoTermPremiumData) for r in result
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 23)
        assert result[0].yield_zero_coupon == 4.1164
        assert result[0].term_premium == 0.171166

    def test_ten_year_decomposition_and_end_date(self, monkeypatch):
        """The ten-year sheet maps its columns and end_date filters."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(_term_premium_workbook()),
        )
        query = FederalReserveSanFranciscoTermPremiumFetcher.transform_query(
            {"maturity": 10, "end_date": "2026-06-22"}
        )
        rows = FederalReserveSanFranciscoTermPremiumFetcher.extract_data(query, None)
        result = FederalReserveSanFranciscoTermPremiumFetcher.transform_data(
            query, rows
        )
        assert len(result) == 1
        assert result[0].date == date(2026, 6, 22)
        assert result[0].yield_zero_coupon == 4.55

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(b""),
        )
        query = FederalReserveSanFranciscoTermPremiumFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveSanFranciscoTermPremiumFetcher.extract_data(query, None)

    def test_unsupported_maturity_rejected(self):
        """A maturity other than 2 or 10 is rejected during query validation."""
        with pytest.raises(ValidationError):
            FederalReserveSanFranciscoTermPremiumFetcher.transform_query(
                {"maturity": 5}
            )
