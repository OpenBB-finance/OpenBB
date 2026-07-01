"""Tests for the Atlanta Fed regional dataset models."""

import io
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.regional.atlanta_bie import (
    FederalReserveAtlantaBusinessInflationData,
    FederalReserveAtlantaBusinessInflationFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_gdpnow import (
    FederalReserveAtlantaGdpNowData,
    FederalReserveAtlantaGdpNowFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_market_probability import (
    FederalReserveAtlantaMarketProbabilityData,
    FederalReserveAtlantaMarketProbabilityFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_sbu import (
    FederalReserveAtlantaBusinessUncertaintyData,
    FederalReserveAtlantaBusinessUncertaintyFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_sticky_cpi import (
    FederalReserveAtlantaStickyCpiData,
    FederalReserveAtlantaStickyCpiFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_taylor_rule import (
    FederalReserveAtlantaTaylorRuleData,
    FederalReserveAtlantaTaylorRuleFetcher,
    FederalReserveAtlantaTaylorRuleHeatmapData,
    FederalReserveAtlantaTaylorRuleHeatmapFetcher,
    FederalReserveAtlantaTaylorRuleMeasuresData,
    FederalReserveAtlantaTaylorRuleMeasuresFetcher,
)
from openbb_federal_reserve.models.regional.atlanta_wage_growth import (
    FederalReserveAtlantaWageGrowthData,
    FederalReserveAtlantaWageGrowthFetcher,
)


def _response(content: bytes) -> MagicMock:
    """Build a make_request response with the given binary body."""
    response = MagicMock()
    response.content = content
    response.raise_for_status = MagicMock()
    return response


def _save(workbook) -> bytes:
    """Serialize an openpyxl workbook to bytes."""
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _gdpnow_workbook() -> bytes:
    """Build a GDPNow TrackRecord workbook with a trailing summary row."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "TrackRecord"
    sheet.append(
        [
            "Quarter being forecasted",
            "Model Forecast Right Before BEA's Advance Estimate",
            "BEA's Advance Estimate",
            "Release Date",
            None,
            "Error",
            "Absolute Error",
            "Squared Error",
        ]
    )
    sheet.append(
        [
            datetime(2026, 3, 31),
            1.239,
            1.990,
            datetime(2026, 4, 27),
            None,
            0.751,
            0.751,
            0.564,
        ]
    )
    sheet.append(
        [
            datetime(2025, 12, 31),
            2.500,
            2.300,
            datetime(2026, 1, 27),
            None,
            0.200,
            0.200,
            0.040,
        ]
    )
    sheet.append([None, "Average", None, None, None, None, "Average abs", "RMS"])
    sheet.append([None, 2.363, None, None, None, None, 0.785, 1.164])

    evolution = workbook.create_sheet("CurrentQtrEvolution")
    evolution.append(
        ["Date", "Major Releases", "GDP*", "Date", "Major Releases", "GDP*"]
    )
    evolution.append(
        [
            datetime(2026, 4, 30),
            "Initial GDPNow",
            3.7,
            datetime(2026, 5, 28),
            "GDP 2nd est.",
            3.82,
        ]
    )
    evolution.append(
        [datetime(2026, 5, 1), "ISM Manufacturing", 3.52, None, None, None]
    )

    table_cont = workbook.create_sheet("TableCont")
    table_cont.append(["Date", "Major Releases", "GDP", "PCE", "CIPI"])
    table_cont.append([datetime(2026, 4, 30), "Initial GDPNow", 3.700, 1.871, 0.690])
    table_cont.append([datetime(2026, 5, 28), "GDP 2nd est.", 3.823, 1.745, 0.871])

    change = workbook.create_sheet("ChangeInContributions")
    change.append(["", "", "PCE", "Govt", "Total", "", "", "", "", "", "", ""])
    change.append(
        [
            "Date",
            "Forecast Quarter",
            "Consumer spending (PCE)",
            "Government spending",
            "Change in GDP forecast",
            None,
            None,
            None,
            None,
            "GDP forecast",
            "Previous GDP forecast",
            "Data Releases",
        ]
    )
    change.append(
        [
            datetime(2026, 5, 1),
            datetime(2026, 6, 30),
            -0.140,
            -0.000,
            -0.182,
            None,
            None,
            None,
            None,
            3.518,
            3.700,
            "ISM Manufacturing",
        ]
    )
    return _save(workbook)


def _wage_growth_workbook() -> bytes:
    """Build a Wage Growth Tracker workbook with the one-row offset and a dot gap."""
    from openpyxl import Workbook

    columns = [
        "Overall",
        "Services",
        "Full-time",
        "College degree",
        "Age 25-54",
        "Female",
        "Male",
        "Job Stayer",
        "Job Switcher",
        "Paid Hourly",
    ]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "data_overall"
    sheet.append(["Sources: junk header row"])
    sheet.append([None, *columns])
    sheet.append(
        [datetime(2026, 4, 1), ".", 3.6, 3.6, 3.6, 3.7, 3.7, 3.8, 3.6, 3.8, 3.3]
    )
    sheet.append(
        [datetime(2026, 5, 1), 3.5, 3.5, 3.8, 3.4, 3.5, 3.4, 3.6, 3.3, 3.7, 3.3]
    )

    chart = workbook.create_sheet("data_chart1")
    chart.append(["Sources: junk header row"])
    chart.append([None, "Recession", "Overall", "Overall: Non-smoothed"])
    chart.append([datetime(2026, 4, 1), 0, 3.6, 4.3])
    chart.append([datetime(2026, 5, 1), 0, 3.5, 4.1])
    return _save(workbook)


def _sticky_cpi_workbook() -> bytes:
    """Build a Sticky-Price CPI workbook mixing ISO and US dates with na markers.

    Four measure blocks of four transforms each; the block-leading column names
    the measure and holds the monthly level, the next three the 1-month, 3-month,
    and 12-month transforms (header strings repeat across blocks, as in the live
    workbook). A ``na`` marker in the 12-month transform must resolve to ``None``.
    """
    from openpyxl import Workbook

    columns = [
        "Date",
        "Flexible CPI (monthly)",
        "1-mo annualized percent change",
        "3-mo a.r.",
        "12mo",
        "Core Flexible CPI (monthly)",
        "1-mo annualized percent change",
        "3-mo a.r.",
        "12mo",
        "Sticky CPI (monthly)",
        "1-mo annualized percent change",
        "3-mo a.r.",
        "12mo",
        "Core Sticky CPI (monthly)",
        "1-mo annualized percent change",
        "3-mo a.r.",
        "12mo",
    ]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Data"
    sheet.append(columns)
    sheet.append(
        [
            datetime(2026, 4, 1),
            0.0136,
            17.6,
            19.3,
            5.616,
            0.0036,
            4.4,
            3.9,
            1.162,
            0.0038,
            4.6,
            3.2,
            3.069,
            0.0039,
            4.8,
            3.2,
            3.039,
        ]
    )
    sheet.append(
        [
            "  5/1/2026",
            0.0111,
            14.1,
            22.4,
            6.992,
            0.0001,
            0.1,
            3.9,
            "na",
            0.0024,
            2.9,
            3.3,
            3.118,
            0.0024,
            4.0,
            3.3,
            3.091,
        ]
    )
    return _save(workbook)


def _bie_workbook() -> bytes:
    """Build a BIE survey workbook with the four side-by-side question blocks.

    Row 2 carries a "Question N:" marker at each block's first value column, row 3
    the per-bucket labels, and the data begins at row 4. Column 0 is the date and
    column 1 the shared respondent count (N). The Costs block carries a stray,
    unlabelled column to confirm only header-labelled buckets are kept.
    """
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "BIE Survey results"
    sheet.append(["Source: junk row 0"])
    markers = [None] * 33
    markers[2] = "Question 1: How do your SALES LEVELS compare with normal"
    markers[9] = "Question 2: How do your PROFIT MARGINS compare with normal"
    markers[16] = "Question 3: How do your UNIT COSTS compare with last year"
    markers[24] = "Question 4: Projecting ahead, unit costs over the next 12 months"
    sheet.append(markers)
    labels = [None] * 33
    labels[1] = "N"
    sales = [
        "Much less than normal",
        "Somewhat less than normal",
        "About normal",
        "Somewhat greater than normal",
        "Much greater than normal",
        "Diffusion Index",
    ]
    for offset, label in enumerate(sales):
        labels[2 + offset] = label
        labels[9 + offset] = label
    costs = [
        "Down (<-1%)",
        "Unchanged (-1% to 1%)",
        "Up Somewhat (1.1% to 3%)",
        "Up Significantly (3.1% to 5%)",
        "Up Very Significantly (>5%)",
        "Mean",
        "Variance",
    ]
    for offset, label in enumerate(costs):
        labels[16 + offset] = label
    projections = [
        "Unit costs down (<-1%)",
        "Unit costs about unchanged (-1% to 1%)",
        "Unit costs up somewhat (1.1% to 3%)",
        "Unit costs up significantly (3.1% to 5%)",
        "Unit costs up very significantly (>5%)",
        "Mean",
        "Median",
        "Mode",
        "Variance",
    ]
    for offset, label in enumerate(projections):
        labels[24 + offset] = label
    sheet.append(labels)

    def _data_row(date, n) -> list:
        """Build one survey data row across all four question blocks."""
        row = [None] * 33
        row[0] = date
        row[1] = n
        for offset in range(6):
            row[2 + offset] = round(0.1 + offset / 20, 3)
            row[9 + offset] = round(0.2 + offset / 20, 3)
        for offset in range(7):
            row[16 + offset] = round(0.05 + offset / 25, 3)
        row[23] = 99.0  # stray unlabelled column, must be excluded
        for offset in range(9):
            row[24 + offset] = round(0.03 + offset / 30, 3)
        return row

    sheet.append(_data_row(datetime(2026, 5, 15), 430))
    sheet.append(_data_row(datetime(2026, 6, 12), 395))

    factors = workbook.create_sheet("Quarterly-Price Fact (Disc)")
    factors.append(["Quarterly Question: junk row 0"])
    factors.append(["Note: discontinued junk row 1"])
    factors.append([None, "Labor Costs", None, None, "Sales Levels", None, None])
    factors.append(
        [
            None,
            "Little/no influence",
            "Strong upward influence",
            "Diffusion Index",
            "Little/no influence",
            "Strong upward influence",
            "Diffusion Index",
        ]
    )
    factors.append([datetime(2026, 2, 15), 0.41, 0.05, 29.0, 0.47, 0.31, 39.0])
    factors.append([datetime(2026, 5, 15), 0.39, 0.06, 30.0, 0.46, 0.30, 38.0])
    return _save(workbook)


def _sbu_workbook() -> bytes:
    """Build an SBU smoothed-index workbook with the three-row header offset."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Index Values (smoothed)"
    for _ in range(3):
        sheet.append(["junk"])
    sheet.append(
        [
            "date",
            "SalesRevGrowth_percent",
            "SalesRevGrowthUnc_percent",
            "EmpGrowth_percent",
            "EmpGrowthUnc_percent",
            None,
            "Last updated: 6/24/2026",
        ]
    )
    sheet.append([datetime(2026, 5, 1), 5.074, 3.619, 1.479, 4.272, None, None])
    sheet.append([datetime(2026, 6, 1), 5.338, 3.661, 1.258, 4.193, None, None])

    research = workbook.create_sheet("Historical Data for Research")
    research.append(["Source: junk"])
    research.append(["Attribution: junk"])
    research.append([None, "Smoothed series"])
    research.append(
        [
            "date",
            "SalesRevGrowth_percent",
            "SalesRevGrowthUnc_percent",
            "EmpGrowth_percent",
            "EmpGrowthUnc_percent",
        ]
    )
    research.append([datetime(2026, 5, 1), 0.019, 0.047, 0.009, 0.058])
    research.append([datetime(2026, 6, 1), 0.020, 0.048, 0.010, 0.057])

    discontinued = workbook.create_sheet("Dicontinued Series")
    discontinued.append(["Source: junk"])
    discontinued.append(["Attribution: junk"])
    discontinued.append(
        [
            None,
            "Note: standardized index banner",
            None,
            "Natural Units - Smoothed",
            None,
        ]
    )
    discontinued.append(
        [
            "date",
            "SalesRevGrowth_Index",
            "BusUncertaintyIndex",
            "InvestmentRate_percent",
            "InvestmentRateUnc_percent",
        ]
    )
    discontinued.append([datetime(2026, 5, 1), 87.06, 125.99, 0.092, 0.035])
    discontinued.append([datetime(2026, 6, 1), 92.84, 121.28, 0.088, 0.032])
    return _save(workbook)


def _mpt_workbook() -> bytes:
    """Build a Market Probability Tracker tidy-long workbook with bins and summaries.

    Two observation dates, each with two reference meetings carrying two
    distribution bins plus a summary metric that must be dropped. The latest date
    additionally carries a missing-value bin for one meeting.
    """
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "DATA"
    sheet.append(["date", "reference_start", "target_range", "field", "value"])
    rows = [
        # latest date, meeting A
        (datetime(2026, 6, 23), datetime(2026, 7, 29), "Prob: 475bps - 500bps", 12.5),
        (datetime(2026, 6, 23), datetime(2026, 7, 29), "Prob: 450bps - 475bps", 60.0),
        (datetime(2026, 6, 23), datetime(2026, 7, 29), "Rate: mean", 462.0),
        (datetime(2026, 6, 23), datetime(2026, 7, 29), "Prob: cut", 25.0),
        # latest date, meeting B (one bin missing for this meeting)
        (datetime(2026, 6, 23), datetime(2026, 9, 16), "Prob: 475bps - 500bps", 40.0),
        (datetime(2026, 6, 23), datetime(2026, 9, 16), "Prob: 450bps - 475bps", None),
        # earlier date that must be dropped by the latest-date selection
        (datetime(2026, 6, 22), datetime(2026, 7, 29), "Prob: 450bps - 475bps", 55.0),
    ]
    for observation, reference, field, value in rows:
        sheet.append([observation, reference, "", field, value])
    return _save(workbook)


def _taylor_rule_sheet(workbook, name, r_star, gap, may_prescribed, title) -> None:
    """Append a Taylor Rule prescription sheet with the one-row header offset."""
    sheet = workbook.create_sheet(name)
    sheet.append(["human description row"])
    sheet.append(
        [
            None,
            "FedFundsRateLag1",
            "RstarFOMCMedian",
            "TwoPercent",
            "U3gapFOMC",
            "CorePCEInflation",
            None,
            f"{name}:  {title}",
            "Actual Fed Funds Rate",
        ]
    )
    sheet.append(
        [
            datetime(2026, 2, 15),
            3.897,
            r_star,
            2,
            gap,
            3.118,
            None,
            may_prescribed - 0.3,
            3.640,
        ]
    )
    sheet.append(
        [
            datetime(2026, 5, 15),
            3.640,
            r_star,
            2,
            gap,
            3.297,
            None,
            may_prescribed,
            "#N/A",
        ]
    )


def _taylor_rule_workbook() -> bytes:
    """Build a Taylor Rule workbook with all three rule, a measure, and a heat-map sheet."""
    from openpyxl import Workbook

    workbook = Workbook()
    workbook.remove(workbook.active)
    _taylor_rule_sheet(
        workbook, "FOMCTaylor93UR", 1.125, -0.368, 4.886, "Gap weight=0.5"
    )
    _taylor_rule_sheet(
        workbook, "FOMCTaylor99UR", 1.125, -0.368, 4.702, "Gap weight=1.0"
    )
    _taylor_rule_sheet(workbook, "Taylor93GDP", 1.696, 1.157, 6.220, "Gap=CBO GDP gap")

    measures = workbook.create_sheet("NaturalRateMeasures")
    measures.append(["human description row"])
    measures.append([None, "RstarFOMCMedian", "LWRstar1side"])
    measures.append([datetime(2026, 2, 15), 1.083, 1.66])
    measures.append([datetime(2026, 5, 15), 1.125, 1.696])

    heatmap = workbook.create_sheet("HeatMapLatestQuarter")
    heatmap.append(["Taylor Rule Fed Funds Rate Prescriptions"])
    heatmap.append([None, "Prescriptions using latest values"])
    heatmap.append([None, None, "Fed SEP-LR", "Measure of Gap (CBO)"])
    heatmap.append([None, None, "U-3 Gap", "U-3", "GDP"])
    heatmap.append(["Measure of r*", 0.02, 5.761, 6.006, 6.524])
    heatmap.append([None, "FOMC Longer-run", 4.886, 5.131, 5.649])
    heatmap.append([None, "HLW 2017 model", 4.823, 5.068, 5.586])
    return _save(workbook)


def _taylor_rule_chart_workbook() -> bytes:
    """Build a Taylor Rule chart workbook with an undated row and a future row."""
    from openpyxl import Workbook

    workbook = Workbook()
    workbook.remove(workbook.active)
    for sheet_name in ("FOMCTaylor93UR", "FOMCTaylor99UR", "Taylor93GDP"):
        sheet = workbook.create_sheet(sheet_name)
        sheet.append(["human description row"])
        sheet.append(
            [None, None, None, None, None, None, sheet_name, "Actual Fed Funds Rate"]
        )
        sheet.append(["projection", None, None, None, None, None, 9.9, 1.0])
        sheet.append([datetime(2026, 2, 15), None, None, None, None, None, 4.886, 3.6])
        sheet.append([datetime(2026, 5, 15), None, None, None, None, None, 4.702, 3.7])
    return _save(workbook)


def _patch_request(monkeypatch, content: bytes) -> None:
    """Point make_request at a fixed binary response."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request",
        lambda *a, **k: _response(content),
    )


class TestGdpNow:
    """Tests for the GDPNow fetcher."""

    def test_track_record_is_flat_and_drops_summary(self, monkeypatch):
        """The TrackRecord sheet stays wide, keeping date cells, dropping summaries."""
        _patch_request(monkeypatch, _gdpnow_workbook())
        query = FederalReserveAtlantaGdpNowFetcher.transform_query(
            {
                "table": "track_record",
                "start_date": "2026-01-01",
                "end_date": "2026-06-30",
            }
        )
        rows = FederalReserveAtlantaGdpNowFetcher.extract_data(query, None)
        result = FederalReserveAtlantaGdpNowFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveAtlantaGdpNowData) for r in result)
        assert {r.date for r in result} == {date(2026, 3, 31)}
        row = next(r for r in result if r.date == date(2026, 3, 31)).model_dump()
        assert row["Model Forecast Right Before BEA's Advance Estimate"] == 1.239
        assert row["BEA's Advance Estimate"] == 1.990
        assert row["Release Date"] == date(2026, 4, 27)
        assert row["Error"] == 0.751
        assert "major_release" not in row
        assert "label" not in row

    def test_evolution_pivots_quarter_blocks(self, monkeypatch):
        """The evolution sheet pivots all side-by-side quarter blocks to wide."""
        _patch_request(monkeypatch, _gdpnow_workbook())
        query = FederalReserveAtlantaGdpNowFetcher.transform_query(
            {"table": "evolution"}
        )
        rows = FederalReserveAtlantaGdpNowFetcher.extract_data(query, None)
        result = FederalReserveAtlantaGdpNowFetcher.transform_data(query, rows)
        by_date = {r.date: r.model_dump()["GDP nowcast"] for r in result}
        assert by_date[date(2026, 4, 30)] == 3.7
        assert by_date[date(2026, 5, 1)] == 3.52
        assert by_date[date(2026, 5, 28)] == 3.82

    def test_table_contributions_pivots_components(self, monkeypatch):
        """The TableCont sheet pivots each component to a column, carrying the label."""
        _patch_request(monkeypatch, _gdpnow_workbook())
        query = FederalReserveAtlantaGdpNowFetcher.transform_query(
            {"table": "table_contributions"}
        )
        rows = FederalReserveAtlantaGdpNowFetcher.extract_data(query, None)
        result = FederalReserveAtlantaGdpNowFetcher.transform_data(query, rows)
        row = next(r for r in result if r.date == date(2026, 4, 30))
        dumped = row.model_dump()
        assert {"GDP", "PCE", "CIPI"} <= set(dumped)
        assert dumped["PCE"] == 1.871
        assert dumped["major_release"] == "Initial GDPNow"

    def test_change_in_contributions_pivots(self, monkeypatch):
        """The ChangeInContributions sheet pivots using the grouped header layout."""
        _patch_request(monkeypatch, _gdpnow_workbook())
        query = FederalReserveAtlantaGdpNowFetcher.transform_query(
            {"table": "change_in_contributions"}
        )
        rows = FederalReserveAtlantaGdpNowFetcher.extract_data(query, None)
        result = FederalReserveAtlantaGdpNowFetcher.transform_data(query, rows)
        assert all(
            r.model_dump()["major_release"] == "ISM Manufacturing" for r in result
        )
        row = result[0].model_dump()
        assert row["Consumer spending (PCE)"] == -0.140
        assert row["GDP forecast"] == 3.518

    def test_boolean_cell_coerces_to_none(self, monkeypatch):
        """A boolean value cell is treated as a blank and dropped from the pivot."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "TableCont"
        sheet.append(["Date", "Major Releases", "GDP", "PCE"])
        sheet.append([datetime(2026, 4, 30), "Initial GDPNow", True, 1.871])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaGdpNowFetcher.transform_query(
            {"table": "table_contributions"}
        )
        rows = FederalReserveAtlantaGdpNowFetcher.extract_data(query, None)
        result = FederalReserveAtlantaGdpNowFetcher.transform_data(query, rows)
        assert set(result[0].model_dump()) - {"date", "major_release"} == {"PCE"}

    def test_date_filter_emptied_raises(self, monkeypatch):
        """A date filter that removes every row raises ``EmptyDataError``."""
        _patch_request(monkeypatch, _gdpnow_workbook())
        query = FederalReserveAtlantaGdpNowFetcher.transform_query(
            {"table": "track_record", "start_date": "2099-01-01"}
        )
        rows = FederalReserveAtlantaGdpNowFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaGdpNowFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaGdpNowFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaGdpNowFetcher.extract_data(query, None)

    def test_label_coerces_nan_and_blank_to_none(self):
        """A float NaN or blank label cell yields None, not the string 'nan'."""
        from openbb_federal_reserve.models.regional.atlanta_gdpnow import _label

        assert _label(float("nan")) is None
        assert _label(None) is None
        assert _label("") is None
        assert _label("  Initial GDPNow  ") == "Initial GDPNow"

    def test_flat_table_keeps_plain_date_cells(self):
        """A bare ``date`` cell (not ``datetime``) is preserved as-is."""
        from openbb_federal_reserve.models.regional.atlanta_gdpnow import _flat_table

        grid = [
            ["Quarter being forecasted", "Release Date"],
            [date(2026, 3, 31), date(2026, 4, 27)],
        ]
        records = _flat_table(grid, header_row=0)
        assert records == [
            {"date": date(2026, 3, 31), "Release Date": date(2026, 4, 27)}
        ]

    def test_melt_table_skips_non_date_rows(self):
        """A row whose leading cell is not a date is skipped by the melt helper."""
        from openbb_federal_reserve.models.regional.atlanta_gdpnow import _melt_table

        grid = [
            ["Date", "Release", "GDP"],
            ["Average", "x", 2.0],
            [date(2026, 4, 30), "Initial GDPNow", 3.7],
        ]
        records = _melt_table(grid, header_row=0, value_start=2, label_column=1)
        assert records == [
            {
                "date": date(2026, 4, 30),
                "series": "GDP",
                "value": 3.7,
                "major_release": "Initial GDPNow",
            }
        ]


class TestWageGrowth:
    """Tests for the Wage Growth Tracker fetcher."""

    def test_pivots_cut_to_wide(self, monkeypatch):
        """The selected cut pivots to wide one row per date, categories as columns."""
        _patch_request(monkeypatch, _wage_growth_workbook())
        query = FederalReserveAtlantaWageGrowthFetcher.transform_query(
            {"cut": "overall", "start_date": "2026-04-01", "end_date": "2026-05-31"}
        )
        rows = FederalReserveAtlantaWageGrowthFetcher.extract_data(query, None)
        result = FederalReserveAtlantaWageGrowthFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveAtlantaWageGrowthData) for r in result)
        by_date = {r.date: r.model_dump() for r in result}
        assert "Overall" in (set(by_date[date(2026, 5, 1)]) - {"date"})
        assert by_date[date(2026, 4, 1)]["Overall"] is None
        assert by_date[date(2026, 5, 1)]["Overall"] == 3.5

    def test_chart_cut_drops_recession_flag(self, monkeypatch):
        """An overall-chart cut exposes its series while dropping the Recession flag."""
        _patch_request(monkeypatch, _wage_growth_workbook())
        query = FederalReserveAtlantaWageGrowthFetcher.transform_query(
            {"cut": "non_smoothed"}
        )
        rows = FederalReserveAtlantaWageGrowthFetcher.extract_data(query, None)
        result = FederalReserveAtlantaWageGrowthFetcher.transform_data(query, rows)
        by_date = {r.date: r.model_dump() for r in result}
        categories = set(by_date[date(2026, 5, 1)]) - {"date"}
        assert categories == {"Overall", "Overall: Non-smoothed"}
        assert "Recession" not in categories
        assert by_date[date(2026, 5, 1)]["Overall: Non-smoothed"] == 4.1

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaWageGrowthFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaWageGrowthFetcher.extract_data(query, None)


class TestStickyCpi:
    """Tests for the Sticky-Price CPI fetcher."""

    def test_default_transform_pivots_measures_wide(self, monkeypatch):
        """The default 1-month transform yields one column per measure, na->None."""
        _patch_request(monkeypatch, _sticky_cpi_workbook())
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query({})
        rows = FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)
        result = FederalReserveAtlantaStickyCpiFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveAtlantaStickyCpiData) for r in result)
        by_date = {r.date: r.model_dump() for r in result}
        may = by_date[date(2026, 5, 1)]
        assert set(may) - {"date"} == {
            "Flexible CPI",
            "Core Flexible CPI",
            "Sticky CPI",
            "Core Sticky CPI",
        }
        # the default transform is the 1-month annualized percent change
        assert may["Sticky CPI"] == 2.9
        assert may["Flexible CPI"] == 14.1

    def test_transform_selects_twelve_month_and_na(self, monkeypatch):
        """The 12-month transform selects the right column per measure; na->None."""
        _patch_request(monkeypatch, _sticky_cpi_workbook())
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query(
            {"transform": "12-month"}
        )
        rows = FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)
        result = FederalReserveAtlantaStickyCpiFetcher.transform_data(query, rows)
        may = next(r for r in result if r.date == date(2026, 5, 1)).model_dump()
        assert may["Sticky CPI"] == 3.118
        assert may["Core Flexible CPI"] is None

    def test_monthly_transform_takes_block_leader(self, monkeypatch):
        """The monthly transform takes each measure block's leading column."""
        _patch_request(monkeypatch, _sticky_cpi_workbook())
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query(
            {"transform": "monthly"}
        )
        rows = FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)
        result = FederalReserveAtlantaStickyCpiFetcher.transform_data(query, rows)
        apr = next(r for r in result if r.date == date(2026, 4, 1)).model_dump()
        assert apr["Flexible CPI"] == 0.0136
        assert apr["Core Sticky CPI"] == 0.0039

    def test_end_date_filters(self, monkeypatch):
        """The end_date filter narrows the series."""
        _patch_request(monkeypatch, _sticky_cpi_workbook())
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query(
            {"start_date": "2026-01-01", "end_date": "2026-04-30"}
        )
        rows = FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)
        result = FederalReserveAtlantaStickyCpiFetcher.transform_data(query, rows)
        assert {r.date for r in result} == {date(2026, 4, 1)}

    def test_leading_all_na_row_dropped(self, monkeypatch):
        """A row with no value for the selected transform is dropped, not blank."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Data"
        sheet.append(["Date", "Flexible CPI (monthly)", "1-mo", "3-mo", "12mo"])
        sheet.append([datetime(2026, 1, 1), 0.01, "na", "na", "na"])
        sheet.append([datetime(2026, 2, 1), 0.02, 5.0, 4.0, 3.0])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query(
            {"transform": "1-month annualized"}
        )
        rows = FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)
        result = FederalReserveAtlantaStickyCpiFetcher.transform_data(query, rows)
        assert {r.date for r in result} == {date(2026, 2, 1)}

    def test_all_na_transform_raises(self, monkeypatch):
        """A transform with no value on any row raises ``EmptyDataError``."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Data"
        sheet.append(["Date", "Flexible CPI (monthly)", "1-mo", "3-mo", "12mo"])
        sheet.append([datetime(2026, 1, 1), 0.01, "na", "na", "na"])
        sheet.append([datetime(2026, 2, 1), 0.02, "na", "na", "na"])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query(
            {"transform": "1-month annualized"}
        )
        rows = FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaStickyCpiFetcher.transform_data(query, rows)

    def test_no_date_rows_raises(self, monkeypatch):
        """A Data sheet whose first column holds no dates raises ``EmptyDataError``."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Data"
        sheet.append(["Date", "Flexible CPI (monthly)"])
        sheet.append(["not a date", 0.01])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query({})
        rows = FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaStickyCpiFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaStickyCpiFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaStickyCpiFetcher.extract_data(query, None)


class TestBusinessInflation:
    """Tests for the Business Inflation Expectations fetcher."""

    def test_sales_question_pivots_block_wide(self, monkeypatch):
        """The Sales question pivots its bucket block wide with the respondent count."""
        _patch_request(monkeypatch, _bie_workbook())
        query = FederalReserveAtlantaBusinessInflationFetcher.transform_query(
            {"question": "sales", "start_date": "2026-06-01", "end_date": "2026-06-30"}
        )
        rows = FederalReserveAtlantaBusinessInflationFetcher.extract_data(query, None)
        result = FederalReserveAtlantaBusinessInflationFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveAtlantaBusinessInflationData) for r in result
        )
        assert len(result) == 1
        row = result[0].model_dump()
        assert row["date"] == date(2026, 6, 12)
        # N is renamed to a readable respondent-count column
        assert row["Number of Respondents"] == 395
        assert "N" not in row
        assert set(row) - {"date", "Number of Respondents"} == {
            "Much less than normal",
            "Somewhat less than normal",
            "About normal",
            "Somewhat greater than normal",
            "Much greater than normal",
            "Diffusion Index",
        }
        assert row["Much less than normal"] == 0.1

    def test_costs_default_excludes_stray_column(self, monkeypatch):
        """The default Costs question keeps Mean/Variance but drops the stray column."""
        _patch_request(monkeypatch, _bie_workbook())
        query = FederalReserveAtlantaBusinessInflationFetcher.transform_query({})
        rows = FederalReserveAtlantaBusinessInflationFetcher.extract_data(query, None)
        result = FederalReserveAtlantaBusinessInflationFetcher.transform_data(
            query, rows
        )
        row = result[-1].model_dump()
        assert set(row) - {"date", "Number of Respondents"} == {
            "Down (<-1%)",
            "Unchanged (-1% to 1%)",
            "Up Somewhat (1.1% to 3%)",
            "Up Significantly (3.1% to 5%)",
            "Up Very Significantly (>5%)",
            "Mean",
            "Variance",
        }
        # the stray unlabelled column value (99.0) is never carried
        assert 99.0 not in row.values()

    def test_projections_question_has_median_and_mode(self, monkeypatch):
        """The Projections question's block carries Mean, Median, Mode, and Variance."""
        _patch_request(monkeypatch, _bie_workbook())
        query = FederalReserveAtlantaBusinessInflationFetcher.transform_query(
            {"question": "projections"}
        )
        rows = FederalReserveAtlantaBusinessInflationFetcher.extract_data(query, None)
        result = FederalReserveAtlantaBusinessInflationFetcher.transform_data(
            query, rows
        )
        columns = set(result[-1].model_dump())
        assert {"Mean", "Median", "Mode", "Variance"} <= columns
        assert "Unit costs down (<-1%)" in columns

    def test_quarterly_price_factors_uses_melt_path(self, monkeypatch):
        """A quarterly question still pivots via the grouped melt + pivot path."""
        _patch_request(monkeypatch, _bie_workbook())
        query = FederalReserveAtlantaBusinessInflationFetcher.transform_query(
            {"question": "price_factors", "start_date": "2026-05-01"}
        )
        rows = FederalReserveAtlantaBusinessInflationFetcher.extract_data(query, None)
        result = FederalReserveAtlantaBusinessInflationFetcher.transform_data(
            query, rows
        )
        row = result[0].model_dump()
        assert row["Labor Costs - Diffusion Index"] == 30.0
        assert row["Sales Levels - Little/no influence"] == 0.46

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaBusinessInflationFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaBusinessInflationFetcher.extract_data(query, None)


class TestBusinessUncertainty:
    """Tests for the Survey of Business Uncertainty fetcher."""

    def test_pivots_table_to_wide(self, monkeypatch):
        """The selected table pivots to one wide row per date, measures as columns."""
        _patch_request(monkeypatch, _sbu_workbook())
        query = FederalReserveAtlantaBusinessUncertaintyFetcher.transform_query(
            {
                "table": "index_smoothed",
                "start_date": "2026-06-01",
                "end_date": "2026-06-30",
            }
        )
        rows = FederalReserveAtlantaBusinessUncertaintyFetcher.extract_data(query, None)
        result = FederalReserveAtlantaBusinessUncertaintyFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveAtlantaBusinessUncertaintyData) for r in result
        )
        assert len(result) == 1
        row = result[0].model_dump()
        assert set(row) - {"date"} == {
            "SalesRevGrowth_percent",
            "SalesRevGrowthUnc_percent",
            "EmpGrowth_percent",
            "EmpGrowthUnc_percent",
        }
        assert row["SalesRevGrowth_percent"] == 5.338
        assert row["EmpGrowth_percent"] == 1.258

    def test_historical_research_table(self, monkeypatch):
        """The historical-research table pivots its four percent series to columns."""
        _patch_request(monkeypatch, _sbu_workbook())
        query = FederalReserveAtlantaBusinessUncertaintyFetcher.transform_query(
            {"table": "historical_research", "start_date": "2026-06-01"}
        )
        rows = FederalReserveAtlantaBusinessUncertaintyFetcher.extract_data(query, None)
        result = FederalReserveAtlantaBusinessUncertaintyFetcher.transform_data(
            query, rows
        )
        row = result[0].model_dump()
        assert set(row) - {"date"} == {
            "SalesRevGrowth_percent",
            "SalesRevGrowthUnc_percent",
            "EmpGrowth_percent",
            "EmpGrowthUnc_percent",
        }
        assert row["SalesRevGrowth_percent"] == 0.020

    def test_discontinued_disambiguates_duplicate_columns(self, monkeypatch):
        """The discontinued table prefixes only the duplicated percent columns."""
        _patch_request(monkeypatch, _sbu_workbook())
        query = FederalReserveAtlantaBusinessUncertaintyFetcher.transform_query(
            {"table": "discontinued", "start_date": "2026-05-01"}
        )
        rows = FederalReserveAtlantaBusinessUncertaintyFetcher.extract_data(query, None)
        result = FederalReserveAtlantaBusinessUncertaintyFetcher.transform_data(
            query, rows
        )
        columns = set().union(*(r.model_dump() for r in result))
        assert "SalesRevGrowth_Index" in columns
        assert "BusUncertaintyIndex" in columns
        assert "Natural Units - Smoothed - InvestmentRate_percent" in columns
        assert "Natural Units - Smoothed - InvestmentRateUnc_percent" in columns

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaBusinessUncertaintyFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaBusinessUncertaintyFetcher.extract_data(query, None)


class TestMarketProbability:
    """Tests for the Market Probability Tracker fetcher."""

    def test_default_meeting_is_nearest_upcoming(self, monkeypatch):
        """The default selection is the nearest upcoming meeting on the latest date."""
        _patch_request(monkeypatch, _mpt_workbook())
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query({})
        result = FederalReserveAtlantaMarketProbabilityFetcher.transform_data(
            query,
            FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None),
        )
        assert all(
            isinstance(r, FederalReserveAtlantaMarketProbabilityData) for r in result
        )
        # one row per distribution bin, sorted ascending by rate; summaries dropped
        labels = [r.target_range for r in result]
        assert labels == ["4.50–4.75%", "4.75–5.00%"]
        rows = {r.target_range: r.model_dump() for r in result}
        # each row carries a single probability column for the nearest meeting (7/29)
        assert set(rows["4.75–5.00%"]) == {"target_range", "probability"}
        assert rows["4.75–5.00%"]["probability"] == 12.5
        assert rows["4.50–4.75%"]["probability"] == 60.0
        # the Rate:/cut/hike summaries never appear as rows
        assert all("Rate:" not in label and "Prob:" not in label for label in labels)

    def test_selected_meeting_returns_its_distribution(self, monkeypatch):
        """Selecting a later meeting returns that meeting's bins, na->None."""
        _patch_request(monkeypatch, _mpt_workbook())
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query(
            {"meeting": "2026-09-16"}
        )
        result = FederalReserveAtlantaMarketProbabilityFetcher.transform_data(
            query,
            FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None),
        )
        rows = {r.target_range: r.model_dump() for r in result}
        assert rows["4.75–5.00%"]["probability"] == 40.0
        # the 4.50–4.75% bin is missing for this meeting, carried as None
        assert rows["4.50–4.75%"]["probability"] is None

    def test_unknown_meeting_falls_back_to_nearest(self, monkeypatch):
        """A meeting absent from the latest date falls back to the nearest upcoming."""
        _patch_request(monkeypatch, _mpt_workbook())
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query(
            {"meeting": "2099-01-01"}
        )
        result = FederalReserveAtlantaMarketProbabilityFetcher.transform_data(
            query,
            FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None),
        )
        rows = {r.target_range: r.model_dump() for r in result}
        assert rows["4.75–5.00%"]["probability"] == 12.5

    def test_no_distribution_meetings_raises(self, monkeypatch):
        """Data whose meetings carry only rate stats (no bins) raises everywhere."""
        from openpyxl import Workbook

        from openbb_federal_reserve.models.regional.atlanta_market_probability import (
            _load_meetings,
        )

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "DATA"
        sheet.append(["date", "reference_start", "target_range", "field", "value"])
        sheet.append(
            [datetime(2026, 6, 23), datetime(2029, 3, 21), "", "Rate: mean", 350.0]
        )
        content = _save(workbook)
        with pytest.raises(EmptyDataError):
            _load_meetings(content)
        _patch_request(monkeypatch, content)
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query({})
        rows = FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaMarketProbabilityFetcher.transform_data(query, rows)

    def test_date_filter_selects_earlier_latest(self, monkeypatch):
        """An end_date filter shifts the 'latest' selection to the earlier date."""
        _patch_request(monkeypatch, _mpt_workbook())
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query(
            {"start_date": "2026-06-22", "end_date": "2026-06-22"}
        )
        result = FederalReserveAtlantaMarketProbabilityFetcher.transform_data(
            query,
            FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None),
        )
        assert [r.target_range for r in result] == ["4.50–4.75%"]
        assert result[0].model_dump()["probability"] == 55.0

    def test_load_meetings_returns_latest_and_ascending(self, monkeypatch):
        """The choices helper returns the latest date's ascending reference meetings."""
        from openbb_federal_reserve.models.regional.atlanta_market_probability import (
            _load_meetings,
        )

        latest, meetings = _load_meetings(_mpt_workbook())
        assert latest == date(2026, 6, 23)
        assert meetings == [date(2026, 7, 29), date(2026, 9, 16)]

    def test_load_meetings_empty_raises(self):
        """The choices helper raises ``EmptyDataError`` when no dated rows remain."""
        from openpyxl import Workbook

        from openbb_federal_reserve.models.regional.atlanta_market_probability import (
            _load_meetings,
        )

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "DATA"
        sheet.append(["date", "reference_start", "target_range", "field", "value"])
        with pytest.raises(EmptyDataError):
            _load_meetings(_save(workbook))

    def test_nearest_meeting_falls_back_to_earliest_when_all_past(self):
        """When every meeting is in the past, the earliest is the fallback default."""
        from openbb_federal_reserve.models.regional.atlanta_market_probability import (
            _nearest_meeting,
        )

        past = [date(2000, 1, 1), date(2001, 1, 1)]
        assert _nearest_meeting(past) == date(2000, 1, 1)

    def test_date_filter_emptied_raises(self, monkeypatch):
        """A date filter that removes every row raises ``EmptyDataError``."""
        _patch_request(monkeypatch, _mpt_workbook())
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query(
            {"start_date": "2099-01-01"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaMarketProbabilityFetcher.transform_data(
                query,
                FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None),
            )

    def test_no_distribution_bins_raises(self, monkeypatch):
        """A latest date carrying only summary metrics raises ``EmptyDataError``."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "DATA"
        sheet.append(["date", "reference_start", "target_range", "field", "value"])
        sheet.append(
            [datetime(2026, 6, 23), datetime(2026, 7, 29), "", "Rate: mean", 4.0]
        )
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaMarketProbabilityFetcher.transform_data(
                query,
                FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None),
            )

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaMarketProbabilityFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaMarketProbabilityFetcher.extract_data(query, None)


class TestTaylorRule:
    """Tests for the Taylor Rule prescription (chart) fetcher."""

    def test_overlays_three_prescriptions_with_actual(self, monkeypatch):
        """Each rule's prescription merges by date alongside the actual rate."""
        _patch_request(monkeypatch, _taylor_rule_workbook())
        query = FederalReserveAtlantaTaylorRuleFetcher.transform_query(
            {"start_date": "2026-05-01", "end_date": "2026-05-31"}
        )
        rows = FederalReserveAtlantaTaylorRuleFetcher.extract_data(query, None)
        result = FederalReserveAtlantaTaylorRuleFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveAtlantaTaylorRuleData) for r in result)
        assert len(result) == 1
        assert result[0].date == date(2026, 5, 15)
        assert result[0].taylor_93_unemployment == 4.886
        assert result[0].taylor_99_unemployment == 4.702
        assert result[0].taylor_93_gdp == 6.220
        assert result[0].actual_fed_funds_rate is None

    def test_skips_undated_row_and_applies_end_date(self, monkeypatch):
        """A row with an unparseable date is skipped and end_date drops later rows."""
        _patch_request(monkeypatch, _taylor_rule_chart_workbook())
        query = FederalReserveAtlantaTaylorRuleFetcher.transform_query(
            {"end_date": "2026-02-28"}
        )
        rows = FederalReserveAtlantaTaylorRuleFetcher.extract_data(query, None)
        result = FederalReserveAtlantaTaylorRuleFetcher.transform_data(query, rows)
        assert {r.date for r in result} == {date(2026, 2, 15)}
        assert result[0].taylor_93_unemployment == 4.886

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaTaylorRuleFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaTaylorRuleFetcher.extract_data(query, None)


class TestTaylorRuleMeasures:
    """Tests for the Taylor Rule input-measures fetcher."""

    def test_pivots_measure_menu_to_wide(self, monkeypatch):
        """The selected measure sheet pivots to wide date + per-measure columns."""
        _patch_request(monkeypatch, _taylor_rule_workbook())
        query = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_query(
            {"measure": "natural_rate", "start_date": "2026-05-01"}
        )
        rows = FederalReserveAtlantaTaylorRuleMeasuresFetcher.extract_data(query, None)
        result = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveAtlantaTaylorRuleMeasuresData) for r in result
        )
        assert len(result) == 1
        row = result[0].model_dump()
        assert set(row) - {"date"} == {"RstarFOMCMedian", "LWRstar1side"}
        assert row["date"] == date(2026, 5, 15)
        assert row["RstarFOMCMedian"] == 1.125
        assert row["LWRstar1side"] == 1.696

    def test_end_date_filters_measures(self, monkeypatch):
        """The end_date filter narrows the measure menu to earlier quarters."""
        _patch_request(monkeypatch, _taylor_rule_workbook())
        query = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_query(
            {"measure": "natural_rate", "end_date": "2026-02-28"}
        )
        rows = FederalReserveAtlantaTaylorRuleMeasuresFetcher.extract_data(query, None)
        result = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_data(
            query, rows
        )
        assert {r.date for r in result} == {date(2026, 2, 15)}

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaTaylorRuleMeasuresFetcher.extract_data(query, None)

    def test_drops_all_none_row_keeps_partial(self, monkeypatch):
        """A row with every measure ``None`` is dropped; a partial row is kept."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "NaturalRateMeasures"
        sheet.append(["human description row"])
        sheet.append([None, "RstarFOMCMedian", "LWRstar1side"])
        sheet.append([datetime(2026, 2, 15), None, None])
        sheet.append([datetime(2026, 5, 15), 1.125, None])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_query(
            {"measure": "natural_rate"}
        )
        rows = FederalReserveAtlantaTaylorRuleMeasuresFetcher.extract_data(query, None)
        result = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_data(
            query, rows
        )
        assert {r.date for r in result} == {date(2026, 5, 15)}
        kept = result[0].model_dump()
        assert kept["RstarFOMCMedian"] == 1.125
        assert kept["LWRstar1side"] is None

    def test_all_none_rows_raise(self, monkeypatch):
        """A sheet whose dated rows are all ``None`` raises ``EmptyDataError``."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "NaturalRateMeasures"
        sheet.append(["human description row"])
        sheet.append([None, "RstarFOMCMedian", "LWRstar1side"])
        sheet.append([datetime(2026, 2, 15), None, None])
        sheet.append([datetime(2026, 5, 15), None, None])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_query(
            {"measure": "natural_rate"}
        )
        rows = FederalReserveAtlantaTaylorRuleMeasuresFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaTaylorRuleMeasuresFetcher.transform_data(query, rows)


class TestTaylorRuleHeatmap:
    """Tests for the Taylor Rule heat-map fetcher."""

    def test_parses_r_star_by_gap_grid_to_wide(self, monkeypatch):
        """The grid pivots to one row per r* measure, gap measures as columns."""
        _patch_request(monkeypatch, _taylor_rule_workbook())
        query = FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_query(
            {"quarter": "latest"}
        )
        rows = FederalReserveAtlantaTaylorRuleHeatmapFetcher.extract_data(query, None)
        result = FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_data(
            query, rows
        )
        assert all(
            isinstance(r, FederalReserveAtlantaTaylorRuleHeatmapData) for r in result
        )
        assert {r.r_star_measure for r in result} == {
            "FOMC Longer-run",
            "HLW 2017 model",
        }
        fomc = next(
            r for r in result if r.r_star_measure == "FOMC Longer-run"
        ).model_dump()
        assert set(fomc) - {"r_star_measure"} == {"U-3 Gap", "U-3", "GDP"}
        assert fomc["U-3 Gap"] == 4.886
        assert fomc["GDP"] == 5.649

    def test_missing_gap_banner_raises(self, monkeypatch):
        """A sheet with no 'Measure of Gap' banner raises ``EmptyDataError``."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "HeatMapLatestQuarter"
        sheet.append(["Taylor Rule Prescriptions"])
        sheet.append([None, "FOMC Longer-run", 4.886])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_query({})
        rows = FederalReserveAtlantaTaylorRuleHeatmapFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_data(query, rows)

    def test_breaks_at_gap_gap_and_skips_blank_r_star(self, monkeypatch):
        """A blank gap column ends the block and a blank r* label row is skipped."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "HeatMapLatestQuarter"
        sheet.append([None, None, "Fed SEP-LR", "Measure of Gap (CBO)"])
        sheet.append([None, None, "U-3 Gap", "U-3", None, "variable values"])
        sheet.append([None, None, None, None, None, 99.0])
        sheet.append([None, "FOMC Longer-run", 4.886, 5.131, None, 12.0])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_query({})
        rows = FederalReserveAtlantaTaylorRuleHeatmapFetcher.extract_data(query, None)
        result = FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_data(
            query, rows
        )
        assert {r.r_star_measure for r in result} == {"FOMC Longer-run"}
        row = result[0].model_dump()
        assert set(row) - {"r_star_measure"} == {"U-3 Gap", "U-3"}
        assert row["U-3 Gap"] == 4.886
        assert 99.0 not in row.values()

    def test_no_matrix_rows_raises(self, monkeypatch):
        """A banner with no numeric matrix rows raises ``EmptyDataError``."""
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "HeatMapLatestQuarter"
        sheet.append([None, None, "Fed SEP-LR", "Measure of Gap (CBO)"])
        sheet.append([None, None, "U-3 Gap", "U-3"])
        _patch_request(monkeypatch, _save(workbook))
        query = FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_query({})
        rows = FederalReserveAtlantaTaylorRuleHeatmapFetcher.extract_data(query, None)
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_data(query, rows)

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        _patch_request(monkeypatch, b"")
        query = FederalReserveAtlantaTaylorRuleHeatmapFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveAtlantaTaylorRuleHeatmapFetcher.extract_data(query, None)

    def test_heatmap_columns_carry_color_rules(self):
        """Each gap column fills its cells via the columnColor render function."""
        from openbb_federal_reserve.regional.atlanta import (
            _HEATMAP_COLOR_RULES,
            _HEATMAP_COLUMNS,
            _HEATMAP_GAP_MEASURES,
        )

        by_field = {column["field"]: column for column in _HEATMAP_COLUMNS}
        assert by_field["r_star_measure"]["pinned"] == "left"
        for gap in _HEATMAP_GAP_MEASURES:
            assert by_field[gap]["renderFn"] == "columnColor"
            assert by_field[gap]["renderFnParams"] == {
                "colorRules": _HEATMAP_COLOR_RULES
            }
        assert _HEATMAP_COLOR_RULES and all(
            rule["fill"] is True for rule in _HEATMAP_COLOR_RULES
        )
        assert {rule["condition"] for rule in _HEATMAP_COLOR_RULES} >= {
            "lt",
            "between",
            "gte",
        }
