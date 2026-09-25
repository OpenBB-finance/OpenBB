"""Tests for symbol normalization."""

import pytest

from openbb_tmx.utils.helpers import normalize_symbol


class TestNormalizeSymbol:
    """Stripping listing suffixes without mangling addressed symbols."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("ac", "AC"),
            ("AC.TO", "AC"),
            ("AC.TSX", "AC"),
            ("BRK-B", "BRK.B"),
        ],
    )
    def test_canadian_listings_are_stripped(self, raw, expected):
        assert normalize_symbol(raw) == expected

    @pytest.mark.parametrize(
        "symbol",
        [
            "^TSX",
            "/CGB",
            "/CL:NMX",
            "$USDCAD",
            "IBM:US",
            "AIR:PA",
            "ASML:AS",
            "~BTCUSD:US",
        ],
    )
    def test_addressed_symbols_pass_through(self, symbol):
        assert normalize_symbol(symbol) == symbol

    def test_whitespace_is_trimmed(self):
        assert normalize_symbol("  ac  ") == "AC"

    def test_compound_symbol_keeps_its_hyphen(self):
        assert normalize_symbol("NOVO-B:CO") == "NOVO-B:CO"
