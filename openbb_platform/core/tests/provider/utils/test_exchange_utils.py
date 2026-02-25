"""Tests for exchange_utils module."""

import pytest
from openbb_core.provider.utils.exchange_utils import Exchange


class TestExchange:
    """Tests for the Exchange type."""

    def test_from_mic(self):
        """Test creating Exchange from MIC code."""
        e = Exchange("XNAS")
        assert str(e) == "XNAS"
        assert e.mic == "XNAS"
        assert e.acronym == "NASDAQ"
        assert e.name == "NASDAQ - ALL MARKETS"

    def test_from_mic_lowercase(self):
        """Test creating Exchange from lowercase MIC."""
        e = Exchange("xnys")
        assert str(e) == "XNYS"
        assert e.mic == "XNYS"

    def test_from_acronym(self):
        """Test creating Exchange from acronym."""
        e = Exchange("NASDAQ")
        assert str(e) == "XNAS"
        assert e.mic == "XNAS"
        assert e.acronym == "NASDAQ"

    def test_from_acronym_lowercase(self):
        """Test creating Exchange from lowercase acronym."""
        e = Exchange("nyse")
        assert str(e) == "XNYS"
        assert e.acronym == "NYSE"
        assert e.name == "NEW YORK STOCK EXCHANGE, INC."

    def test_from_name(self):
        """Test creating Exchange from full name."""
        e = Exchange("LONDON STOCK EXCHANGE")
        assert str(e) == "XLON"
        assert e.mic == "XLON"
        assert e.acronym == "LSE"

    def test_from_partial_name(self):
        """Test creating Exchange from acronym lookup."""
        e = Exchange("HKEX")
        assert str(e) == "XHKG"
        assert e.mic == "XHKG"
        assert e.acronym == "HKEX"

    def test_properties(self):
        """Test all Exchange properties."""
        e = Exchange("TSX")
        assert e.mic == "XTSE"
        assert e.acronym == "TSX"
        assert e.name == "TORONTO STOCK EXCHANGE"

    def test_invalid_exchange(self):
        """Test that invalid exchanges raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            Exchange("INVALID_EXCHANGE")
        assert "Invalid exchange" in str(exc_info.value)
        assert "XNAS" in str(exc_info.value)

    def test_str_inheritance(self):
        """Test that Exchange behaves as str."""
        e = Exchange("NASDAQ")
        assert isinstance(e, str)
        assert e == "XNAS"
        assert e.upper() == "XNAS"

    def test_from_existing_exchange(self):
        """Test creating Exchange from another Exchange instance."""
        e1 = Exchange("NYSE")
        e2 = Exchange(e1)
        assert str(e2) == "XNYS"
        assert e2.acronym == "NYSE"

    def test_various_exchanges(self):
        """Test various international exchanges."""
        test_cases = [
            ("XETRA", "XETR"),
            ("XSWX", "XSWX"),
            ("ASX", "XASX"),
            ("JPX", "XJPX"),
            ("XNSE", "XNSE"),
            ("B3", "BVMF"),
        ]
        for input_val, expected_mic in test_cases:
            e = Exchange(input_val)
            assert e.mic == expected_mic, f"Failed for {input_val}"

    def test_whitespace_handling(self):
        """Test that whitespace is stripped from input."""
        e = Exchange("  NASDAQ  ")
        assert str(e) == "XNAS"

    def test_case_insensitivity(self):
        """Test case insensitivity for all input types."""
        assert Exchange("XNAS").mic == Exchange("xnas").mic
        assert Exchange("NASDAQ").mic == Exchange("nasdaq").mic
        assert Exchange("Nasdaq").mic == Exchange("NASDAQ").mic
