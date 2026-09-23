"""Tests for the MDRM dictionary helpers."""

import csv
import io
import zipfile
from datetime import date
from unittest.mock import MagicMock

from openbb_federal_reserve.utils import mdrm

_ROWS = [
    ["PUBLIC"],
    [
        "Mnemonic",
        "Item Code",
        "Start Date",
        "End Date",
        "Item Name",
        "Confidentiality",
        "ItemType",
        "Reporting Form",
        "Description",
        "SeriesGlossary",
    ],
    [
        "RISK",
        "M334",
        "12/31/2012 12:00:00 AM",
        "12/31/2013 12:00:00 AM",
        "OLD SFT GROSS",
        "N",
        "F",
        "FR Y-15",
        "d",
        "g",
    ],
    [
        "RISK",
        "M334",
        "12/31/2014 12:00:00 AM",
        "12/31/9999 12:00:00 AM",
        "NEW SFT GROSS",
        "N",
        "F",
        "FR Y-15",
        "d",
        "g",
    ],
    ["RISK", "2170", "", "", "TOTAL ASSETS", "N", "F", "FR Y-15", "d", "g"],
    ["RISK", "BAD", "notadate", "notadate", "BAD DATES", "N", "P", "FR Y-15", "d", "g"],
    [
        "BHCK",
        "2170",
        "12/31/2001 12:00:00 AM",
        "12/31/9999 12:00:00 AM",
        "TOTAL ASSETS Y9C",
        "N",
        "F",
        "FR Y-9C",
        "d",
        "g",
    ],
    ["RISK", "SHORT"],
    ["", "", "", "", "", "", "", "", "", ""],
]


def _archive() -> bytes:
    """Build a synthetic MDRM zip with the canonical CSV layout."""
    buffer = io.StringIO()
    csv.writer(buffer).writerows(_ROWS)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("MDRM_CSV.csv", buffer.getvalue())
        archive.writestr("README File for MDRM.txt", "readme")
    return zip_buffer.getvalue()


def _patch(monkeypatch):
    """Point ``make_request`` at the synthetic MDRM archive."""
    response = MagicMock()
    response.content = _archive()
    response.raise_for_status = MagicMock()
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request",
        lambda *a, **k: response,
    )


class TestFetchMdrmRecords:
    """Tests for ``fetch_mdrm_records``."""

    def test_parses_skips_and_dates(self, monkeypatch):
        """Records parse, short/blank rows skip, and bad dates degrade to None."""
        _patch(monkeypatch)
        records = mdrm.fetch_mdrm_records()
        codes = [r["code"] for r in records]
        assert codes.count("RISKM334") == 2
        assert "RISK2170" in codes and "BHCK2170" in codes
        assert "RISKSHORT" not in codes
        bad = next(r for r in records if r["code"] == "RISKBAD")
        assert bad["start"] is None and bad["end"] is None
        m334 = next(r for r in records if r["code"] == "RISKM334")
        assert m334["start"] == date(2012, 12, 31)


class TestFetchMdrmItemTypes:
    """Tests for ``fetch_mdrm_item_types``."""

    def test_maps_codes_to_item_types(self, monkeypatch):
        """Each code maps to its uppercased ItemType; short rows skip."""
        _patch(monkeypatch)
        item_types = mdrm.fetch_mdrm_item_types()
        assert item_types["RISK2170"] == "F"
        assert item_types["RISKBAD"] == "P"
        assert item_types["BHCK2170"] == "F"
        assert "RISKSHORT" not in item_types


class TestFetchMdrmDictionary:
    """Tests for ``fetch_mdrm_dictionary`` resolution."""

    def test_prefix_filters_mnemonic(self, monkeypatch):
        """The prefix restricts the dictionary to one mnemonic family."""
        _patch(monkeypatch)
        dictionary = mdrm.fetch_mdrm_dictionary(prefix="RISK")
        assert "BHCK2170" not in dictionary
        assert dictionary["RISK2170"] == "TOTAL ASSETS"

    def test_as_of_selects_covering_old_revision(self, monkeypatch):
        """An as-of inside the first window selects the old label."""
        _patch(monkeypatch)
        dictionary = mdrm.fetch_mdrm_dictionary(as_of=date(2013, 6, 1), prefix="RISK")
        assert dictionary["RISKM334"] == "OLD SFT GROSS"

    def test_as_of_selects_covering_new_revision(self, monkeypatch):
        """An as-of inside the later window selects the new label."""
        _patch(monkeypatch)
        dictionary = mdrm.fetch_mdrm_dictionary(as_of=date(2024, 1, 1), prefix="RISK")
        assert dictionary["RISKM334"] == "NEW SFT GROSS"

    def test_as_of_uncovered_falls_back_to_latest(self, monkeypatch):
        """An as-of before any window falls back to the most recent revision."""
        _patch(monkeypatch)
        dictionary = mdrm.fetch_mdrm_dictionary(as_of=date(2000, 1, 1), prefix="RISK")
        assert dictionary["RISKM334"] == "NEW SFT GROSS"

    def test_no_as_of_uses_active_and_all_mnemonics(self, monkeypatch):
        """Without an as-of the active revision is used across all mnemonics."""
        _patch(monkeypatch)
        dictionary = mdrm.fetch_mdrm_dictionary()
        assert dictionary["RISKM334"] == "NEW SFT GROSS"
        assert dictionary["BHCK2170"] == "TOTAL ASSETS Y9C"


class TestFetchMdrmDefinitions:
    """Tests for ``fetch_mdrm_definitions`` resolution."""

    def test_returns_descriptions_for_codes_with_text(self, monkeypatch):
        """Each resolved code maps to its cleaned description text."""
        _patch(monkeypatch)
        definitions = mdrm.fetch_mdrm_definitions(prefix="RISK")
        assert definitions["RISK2170"] == "d"
        assert definitions["RISKM334"] == "d"


class TestFetchMonetaryCodes:
    """Tests for ``fetch_monetary_codes`` over the committed asset."""

    def test_loads_committed_classification(self):
        """The asset yields the non-monetary code set and FFIEC 101 prefixes."""
        codes, prefixes = mdrm.fetch_monetary_codes()
        assert "MRRRS300" in codes
        assert "AAABP793" not in codes
        assert prefixes == frozenset({"AABA", "AABE", "AABF"})


class TestIsMonetary:
    """Tests for the per-code monetary classifier."""

    def test_percentage_and_string_item_types_are_non_monetary(self):
        """``P`` and ``S`` ItemTypes are never dollar amounts."""
        assert mdrm.is_monetary("AAABP793", "P") is False
        assert mdrm.is_monetary("BHTX8901", "S") is False

    def test_absent_item_type_is_non_monetary(self):
        """A code with no MDRM ItemType is not scaled."""
        assert mdrm.is_monetary("UNKN0000", None) is False

    def test_financial_dollar_amount_is_monetary(self):
        """A plain ``F`` dollar amount not in the exception set is monetary."""
        assert mdrm.is_monetary("AAABA223", "F") is True

    def test_committed_non_monetary_code_is_excluded(self):
        """An ``F`` ratio or factor named in the asset is not scaled."""
        assert mdrm.is_monetary("MRRRS300", "F") is False
        assert mdrm.is_monetary("BHCA7204", "F") is False

    def test_ffiec101_column_prefix_drives_derived_units(self):
        """The FFIEC 101 grid column prefix splits monetary EAD from percents/years."""
        assert mdrm.is_monetary("AABAJ124", "D") is False
        assert mdrm.is_monetary("AABEJ124", "D") is False
        assert mdrm.is_monetary("AABBJ124", "D") is True
