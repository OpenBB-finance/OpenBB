"""Tests for the FFIEC BHCPR per-institution CSV parser."""

import csv
import io
from pathlib import Path

from openbb_federal_reserve.utils.bhcpr_csv import (
    PERIOD_SUFFIXES,
    _numeric,
    parse_bhcpr_csv,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "bhcpr" / "1039502_20260331.csv"


def _csv_bytes(rows):
    """Serialise rows to BOM-prefixed CSV bytes as the FFIEC endpoint returns them."""
    buffer = io.StringIO()
    csv.writer(buffer).writerows(rows)
    return ("﻿" + buffer.getvalue()).encode("utf-8")


_ROWS = [
    ["MDRM", "Description", "Value"],
    ["Institution Name", "", "JPMORGAN CHASE & CO."],
    ["City and State", "", "NEW YORK, NY"],
    ["ID_RSSD", "", "1039502"],
    ["Regulatory District", "", "2"],
    ["Bank Count", "", "130"],
    ["PEER_GRP", "", "5"],
    ["DT", "Current Period", "20260331"],
    ["DT_4Q", "Prior Year Quarter", "20250331"],
    ["BHSR028", "NET INTEREST INCOME / AVERAGE ASSETS", "2.15"],
    ["BHSR028_4Q", "NET INTEREST INCOME / AVERAGE ASSETS", "2.22"],
    ["PHSR028", "PG RATIO: NII / AVG ASSETS", "3.08"],
    ["BHCK2170", "TOTAL ASSETS (BHC CONSOLIDATED)", "4900475"],
    ["BHCK2170_4Q", "TOTAL ASSETS (BHC CONSOLIDATED)", ""],
    ["short"],
]


class TestNumeric:
    """Tests for ``_numeric`` cell coercion."""

    def test_integer_valued_float_returns_int(self):
        """A whole-valued figure returns an int."""
        assert _numeric("4900475") == 4900475
        assert isinstance(_numeric("4900475"), int)

    def test_fractional_returns_float(self):
        """A fractional figure returns a float."""
        assert _numeric("2.15") == 2.15

    def test_blank_returns_none(self):
        """A blank or whitespace cell returns None."""
        assert _numeric("") is None
        assert _numeric("   ") is None

    def test_non_numeric_returns_none(self):
        """A non-numeric cell returns None."""
        assert _numeric("n/a") is None


class TestParseBhcprCsv:
    """Tests for ``parse_bhcpr_csv`` over a representative CSV payload."""

    def _parsed(self):
        """Parse the representative CSV payload."""
        return parse_bhcpr_csv(_csv_bytes(_ROWS))

    def test_identity_metadata_extracted(self):
        """Named metadata rows populate the identity block."""
        identity = self._parsed()["identity"]
        assert identity["institution_name"] == "JPMORGAN CHASE & CO."
        assert identity["city_state"] == "NEW YORK, NY"
        assert identity["rssd_id"] == "1039502"
        assert identity["district"] == "2"
        assert identity["bank_count"] == "130"

    def test_period_dates_keyed_by_suffix(self):
        """``DT`` and ``DT_*`` rows map period suffixes to their dates."""
        periods = self._parsed()["periods"]
        assert periods == {"": "20260331", "_4Q": "20250331"}

    def test_values_keyed_by_base_code_and_suffix(self):
        """Coded rows collapse to ``{base: {suffix: value}}``."""
        values = self._parsed()["values"]
        assert values["BHSR028"] == {"": 2.15, "_4Q": 2.22}
        assert values["PHSR028"] == {"": 3.08}
        assert values["BHCK2170"] == {"": 4900475, "_4Q": None}

    def test_descriptions_keyed_by_base_code(self):
        """The first description seen for a base code is kept."""
        descriptions = self._parsed()["descriptions"]
        assert descriptions["BHSR028"] == "NET INTEREST INCOME / AVERAGE ASSETS"
        assert descriptions["BHCK2170"] == "TOTAL ASSETS (BHC CONSOLIDATED)"

    def test_peer_group_and_short_rows_ignored(self):
        """The ``PEER_GRP`` marker and malformed short rows are not coded values."""
        values = self._parsed()["values"]
        assert "PEER_GRP" not in values
        assert all(len(base) >= 2 for base in values)

    def test_bom_is_stripped(self):
        """The UTF-8 BOM does not corrupt the first metadata key."""
        assert "institution_name" in self._parsed()["identity"]


class TestPeriodSuffixes:
    """Tests for the exported period-suffix order."""

    def test_current_quarter_first(self):
        """The published column order opens with the current quarter."""
        assert PERIOD_SUFFIXES[0] == ""
        assert PERIOD_SUFFIXES == ("", "_4Q", "_1Y", "_2Y", "_3Y")


class TestRealFixture:
    """Tests parsing the committed real JPMorgan BHCPR CSV."""

    def _parsed(self):
        """Parse the committed real BHCPR CSV fixture."""
        return parse_bhcpr_csv(_FIXTURE.read_bytes())

    def test_identity_from_real_csv(self):
        """The real CSV yields the reporting institution's identity."""
        identity = self._parsed()["identity"]
        assert identity["institution_name"] == "JPMORGAN CHASE & CO."
        assert identity["city_state"] == "NEW YORK, NY"
        assert identity["rssd_id"] == "1039502"

    def test_period_dates_from_real_csv(self):
        """The real CSV's current and year-ago quarter dates parse."""
        periods = self._parsed()["periods"]
        assert periods[""] == "20260331"
        assert periods["_4Q"] == "20250331"

    def test_values_and_descriptions_aligned(self):
        """Every coded value carries a description, and known codes resolve."""
        parsed = self._parsed()
        assert len(parsed["values"]) == len(parsed["descriptions"]) > 1000
        assert parsed["values"]["BHCK2170"][""] == 4900475000
        assert "TOTAL ASSETS" in parsed["descriptions"]["BHCK2170"].upper()
