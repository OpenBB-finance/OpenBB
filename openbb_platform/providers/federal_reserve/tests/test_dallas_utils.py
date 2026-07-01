"""Tests for the Dallas Fed workbook and survey decoding helpers."""

import io
from datetime import date, datetime

from openbb_federal_reserve.utils.dallas import (
    find_label_row,
    melt_two_level,
    parse_dgei,
    quarter_to_date,
)
from openbb_federal_reserve.utils.dallas_survey import (
    BANKING_INDICATORS,
    MANUFACTURING_INDICATORS,
    _decode,
    _decode_retail,
    decode_energy_code,
    parse_keyed_survey,
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


class TestParseDgei:
    """Tests for ``parse_dgei``."""

    def test_no_date_row_returns_empty(self):
        """A sheet without a ``Date`` label row yields no records."""
        content = _save({"S": [["Header"], ["World", 1.0], ["US", 2.0]]})
        assert parse_dgei(content, "S") == []

    def test_skips_blank_and_reserved_labels_and_filters_dates(self):
        """Blank/``unnamed``/``date`` labels skip, junk dates drop, window filters."""
        content = _save(
            {
                "S": [
                    ["Percent Change", None, None, None],
                    ["Date", "World", None, "Unnamed: 3"],
                    ["not a date", 1.0, 9.9, 9.9],
                    [datetime(2026, 1, 1), 2.5, 9.9, 9.9],
                    [datetime(2026, 2, 1), 3.0, 9.9, 9.9],
                    [datetime(2026, 3, 1), 3.5, 9.9, 9.9],
                ]
            }
        )
        rows = parse_dgei(
            content,
            "S",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 28),
        )
        assert {r["series"] for r in rows} == {"World - Percent Change"}
        assert [(r["date"], r["value"]) for r in rows] == [(date(2026, 2, 1), 3.0)]


class TestFindLabelRow:
    """Tests for ``find_label_row``."""

    def test_missing_marker_returns_zero(self):
        """A sheet lacking the marker in the first column returns row 0."""
        content = _save({"S": [["Alpha", "Beta"], [1, 2]]})
        assert find_label_row(content, "S", marker="date") == 0


class TestMeltTwoLevel:
    """Tests for ``melt_two_level``."""

    def test_no_body_rows_returns_empty(self):
        """A sheet with nothing below the label row yields no records."""
        content = _save({"S": [["group"], ["Date"]]})
        assert melt_two_level(content, "S", label_row=1) == []

    def test_bare_label_and_blank_and_reserved_columns(self):
        """A column with no group prefix keeps its bare label; junk rows/columns drop."""
        content = _save(
            {
                "S": [
                    [None, None, None, None],
                    ["Date", "Alpha", None, "Unnamed: 3"],
                    ["not a date", 1.0, 9.9, 9.9],
                    [datetime(2026, 1, 1), 5.0, 9.9, 9.9],
                ]
            }
        )
        rows = melt_two_level(content, "S", label_row=1)
        assert {r["series"] for r in rows} == {"Alpha"}
        assert [(r["date"], r["value"]) for r in rows] == [(date(2026, 1, 1), 5.0)]

    def test_yyyymm_dates_and_window_filter(self):
        """The ``yyyymm`` date kind decodes integers and the window filters."""
        content = _save(
            {
                "S": [
                    ["Group", "Group"],
                    ["Date", "Alpha"],
                    [202601, 5.0],
                    [202602, 6.0],
                    [202603, 7.0],
                ]
            }
        )
        rows = melt_two_level(
            content,
            "S",
            label_row=1,
            date_kind="yyyymm",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 28),
        )
        assert [(r["date"], r["value"]) for r in rows] == [(date(2026, 2, 1), 6.0)]


class TestQuarterToDate:
    """Tests for ``quarter_to_date``."""

    def test_non_quarter_returns_none(self):
        """A non ``YYYY:QN`` label decodes to ``None``."""
        assert quarter_to_date("not a quarter") is None


class TestDecodeEnergyCode:
    """Tests for ``decode_energy_code``."""

    def test_date_and_blank_pass_through(self):
        """The ``date`` and empty codes pass through unchanged."""
        assert decode_energy_code("date") == "date"
        assert decode_energy_code("") == ""

    def test_price_expectation_codes(self):
        """The ``f<product>`` codes decode to expected/share labels."""
        assert decode_energy_code("foprc") == "WTI Oil Price (Expected)"
        assert decode_energy_code("foprcd") == "WTI Oil Price (% Expecting Decrease)"

    def test_unknown_code_passes_through(self):
        """An unrecognised code is returned unchanged."""
        assert decode_energy_code("zzz") == "zzz"


class TestDecodeRetail:
    """Tests for ``_decode_retail``."""

    def test_response_share_suffix(self):
        """A code with a response suffix decodes to that response share."""
        assert _decode_retail("revi") == ("Retail Sales", "current", "increase")

    def test_unknown_code_returns_none(self):
        """A code matching no indicator returns ``None``."""
        assert _decode_retail("zzz") is None


class TestDecode:
    """Tests for ``_decode``."""

    def test_unknown_code_returns_none(self):
        """A code matching no indicator returns ``None``."""
        assert _decode("zzz", MANUFACTURING_INDICATORS) is None


class TestParseKeyedSurvey:
    """Tests for ``parse_keyed_survey``."""

    def test_unmapped_columns_are_skipped(self):
        """Columns absent from the mapping are skipped."""
        content = _save(
            {
                "S": [
                    ["date", "LVol", "zzz"],
                    [datetime(2026, 1, 1), 15.0, 99.0],
                ]
            }
        )
        rows = parse_keyed_survey(content, "S", BANKING_INDICATORS)
        assert {r["indicator"] for r in rows} == {"Total Loan Volume"}
        assert rows[0]["value"] == 15.0
