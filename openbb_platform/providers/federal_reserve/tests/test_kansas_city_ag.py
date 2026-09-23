"""Tests for the Kansas City Fed agricultural workbook parsing utilities."""

import io
from datetime import date

import pytest

from openbb_federal_reserve.utils.kansas_city_ag import (
    _quarter_end,
    annual_sheets,
    parse_kc_annual_table,
    parse_kc_databook,
    parse_kc_district,
    parse_kc_quarterly,
    resolve_kc_ag_url,
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


def _patch_fetch(monkeypatch, value) -> None:
    """Point the Kansas City fetch helper at a fixture value."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.kansas_city.fetch_kansas_city",
        lambda *a, **k: value,
    )


class TestResolveKcAgUrl:
    """Tests for ``resolve_kc_ag_url``."""

    def test_resolves_document_link(self, monkeypatch):
        """A document id is resolved to its quarter-versioned absolute URL."""
        html = '<a href="/documents/7230/some-survey-2025q1.xlsx">Survey</a>'
        _patch_fetch(monkeypatch, html.encode("utf-8"))
        url = resolve_kc_ag_url(7230)
        assert url == (
            "https://www.kansascityfed.org/documents/7230/some-survey-2025q1.xlsx"
        )

    def test_missing_document_raises(self, monkeypatch):
        """A document id absent from the index raises ``ValueError``."""
        _patch_fetch(monkeypatch, b"<html>no links here</html>")
        with pytest.raises(ValueError, match="Could not resolve"):
            resolve_kc_ag_url(7230)


class TestQuarterEnd:
    """Tests for the ``_quarter_end`` helper."""

    def test_non_numeric_year_returns_none(self):
        """A year that cannot be parsed to a number returns ``None``."""
        assert _quarter_end("not-a-year", 1) is None

    def test_out_of_range_quarter_returns_none(self):
        """A quarter outside 1-4 returns ``None``."""
        assert _quarter_end(2024, 5) is None

    def test_valid_quarter_end(self):
        """A valid year and quarter resolves to the quarter-end date."""
        assert _quarter_end(2024, 2) == date(2024, 6, 30)


class TestParseKcQuarterly:
    """Tests for ``parse_kc_quarterly``."""

    def test_group_super_header_breaks_label_ties(self):
        """Colliding column labels are disambiguated by the group super-header."""
        content = _save(
            {
                "Sheet1": [
                    [None, None, "North", None, "South", None, None, None],
                    ["Year", "Qtr.", "Corn", "Corn", "Wheat", "Wheat", "Soy", "Soy"],
                    [2024, 1, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                ]
            }
        )
        rows = parse_kc_quarterly(content, "Sheet1")
        series = {r["series"] for r in rows}
        assert any("North" in s for s in series)
        assert any("South" in s for s in series)

    def test_empty_block_is_skipped(self):
        """A ``Year`` header with no body rows is skipped."""
        content = _save(
            {
                "Sheet1": [
                    ["Year", "Qtr.", "Kansas"],
                ]
            }
        )
        assert parse_kc_quarterly(content, "Sheet1") == []

    def test_date_filters_and_unparseable_row(self):
        """Out-of-range and unparseable observations are dropped by the filters."""
        content = _save(
            {
                "Sheet1": [
                    ["Year", "Qtr.", "Kansas"],
                    [2020, 1, 1.0],
                    [2021, 2, 2.0],
                    [2022, 3, 3.0],
                    ["bad", "x", 4.0],
                ]
            }
        )
        rows = parse_kc_quarterly(
            content,
            "Sheet1",
            start_date=date(2021, 1, 1),
            end_date=date(2021, 12, 31),
        )
        assert {r["date"] for r in rows} == {date(2021, 6, 30)}

    def test_multi_block_skips_title_row(self):
        """A stacked multi-block sheet folds the title and skips the title row."""
        content = _save(
            {
                "Sheet1": [
                    [None, None, "Block One"],
                    ["Year", "Qtr.", "Kansas"],
                    [2024, 1, 1.0],
                    [None, None, "Block Two"],
                    ["Year", "Qtr.", "Kansas"],
                    [2024, 1, 2.0],
                ]
            }
        )
        rows = parse_kc_quarterly(content, "Sheet1")
        series = {r["series"] for r in rows}
        assert "Block One - Kansas" in series
        assert "Block Two - Kansas" in series


class TestParseKcDistrict:
    """Tests for ``parse_kc_district``."""

    def test_district_codes_and_date_filters(self):
        """District codes are named and out-of-range quarters are dropped."""
        content = _save(
            {
                "Data": [
                    ["Date", "001CHI", "002DAL"],
                    ["bad", 1.0, 2.0],
                    ["2020Q1", 3.0, 4.0],
                    ["2024Q1", 5.0, 6.0],
                    ["2025Q1", 7.0, 8.0],
                ],
                "Description": [
                    ["Statistic Identifier", "Description"],
                    ["001CHI", "Demand for Loans"],
                    ["002DAL", "Farm Income"],
                ],
            }
        )
        rows = parse_kc_district(
            content,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
        by_series = {r["series"]: r["value"] for r in rows}
        assert by_series["Chicago - Demand for Loans"] == 5.0
        assert by_series["Dallas - Farm Income"] == 6.0


class TestAnnualSheets:
    """Tests for ``annual_sheets``."""

    def test_drops_section_dividers(self):
        """Section divider sheets are excluded from the data-sheet list."""
        content = _save(
            {
                "Section A": [["divider"]],
                "afdr_a1": [["Period", "Total"], ["2017", 1.0]],
            }
        )
        assert annual_sheets(content) == ["afdr_a1"]


class TestParseKcAnnualTable:
    """Tests for ``parse_kc_annual_table``."""

    def test_no_period_header_returns_empty(self):
        """A sheet with no period/year/date header returns no records."""
        content = _save({"sheet": [["foo", "bar"], [1, 2]]})
        assert parse_kc_annual_table(content, "sheet") == []

    def test_characteristic_columns_and_sections(self):
        """Leading characteristic columns fold into the label and mark sections."""
        content = _save(
            {
                "sheet": [
                    ["Loan Characteristic", "Period", "Value"],
                    ["Feeder", "2015", 1.0],
                    ["Other", "2016", 2.0],
                    ["Feeder", "2017", 3.0],
                ]
            }
        )
        rows = parse_kc_annual_table(content, "sheet")
        sections = {r["section"] for r in rows}
        assert sections == {1, 2}
        assert any(r["series"] == "Feeder - Value" for r in rows)

    def test_quarter_and_date_filters(self):
        """Quarterly periods parse and date bounds drop out-of-range rows."""
        content = _save(
            {
                "sheet": [
                    ["Period", "Value"],
                    ["bad", 1.0],
                    ["2020:Q1", 2.0],
                    ["2024:Q2", 3.0],
                    ["2025:Q1", 4.0],
                ]
            }
        )
        rows = parse_kc_annual_table(
            content,
            "sheet",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
        assert len(rows) == 1
        assert rows[0]["date"] == date(2024, 6, 30)
        assert rows[0]["frequency"] == "quarter"


class TestParseKcDatabook:
    """Tests for ``parse_kc_databook``."""

    def test_attribute_columns_and_filters(self):
        """Attribute columns extend labels and date bounds drop rows."""
        content = _save(
            {
                "Data": [
                    ["Date", "A001"],
                    ["bad", 1.0],
                    ["2020Q1", 2.0],
                    ["2024Q1", 3.0],
                    ["2025Q1", 4.0],
                ],
                "Descriptions": [
                    ["Statistic Identifier", "Statistic", "Attribute 1"],
                    ["A001", "Total Loans", "Quarterly"],
                    [None, "skip-me", "x"],
                ],
            }
        )
        rows = parse_kc_databook(
            content,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
        assert len(rows) == 1
        assert rows[0]["series"] == "Total Loans - Quarterly"
        assert rows[0]["value"] == 3.0
