"""Tests for the pure helpers in ``openbb_government_ca.utils.helpers``.

These functions are pure (no I/O) so they get full unit coverage
without VCR cassettes.
"""

from __future__ import annotations

from datetime import date

import pytest

from openbb_government_ca.utils.helpers import (
    normalize_fx_symbol,
    parse_observation_date,
    safe_float,
)


class TestSafeFloat:
    """``safe_float`` coerces upstream string values to ``float | None``."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (None, None),
            ("", None),
            ("   ", None),
            ("..", None),  # StatsCan missing marker
            ("...", None),
            ("NaN", None),
            ("N/A", None),
            ("n/a", None),
            ("0", 0.0),
            ("1.5", 1.5),
            ("-3.14", -3.14),
            ("1e3", 1000.0),
            (0, 0.0),
            (42, 42.0),
            (3.14, 3.14),
            ("not-a-number", None),
        ],
    )
    def test_safe_float_handles_edge_cases(self, value, expected):
        """All upstream shapes are normalized correctly."""
        assert safe_float(value) == expected


class TestParseObservationDate:
    """``parse_observation_date`` handles BoC + StatsCan date shapes."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            # Daily ISO (BoC Valet)
            ("2024-01-15", date(2024, 1, 15)),
            # Monthly (BoC Valet + StatsCan)
            ("2024-01", date(2024, 1, 1)),
            # Quarterly (StatsCan SDMX)
            ("2024-Q1", date(2024, 1, 1)),
            ("2024-Q2", date(2024, 4, 1)),
            ("2024-Q3", date(2024, 7, 1)),
            ("2024-Q4", date(2024, 10, 1)),
            # Annual (StatsCan SDMX)
            ("2024", date(2024, 1, 1)),
            # Empty / garbage
            ("", None),
            ("   ", None),
            (None, None),
            ("not-a-date", None),
            ("2024-13", None),  # invalid month
            ("2024-Q5", None),  # invalid quarter
        ],
    )
    def test_parse_observation_date_handles_all_shapes(self, value, expected):
        """All four date shapes parse correctly; garbage returns ``None``."""
        assert parse_observation_date(value) == expected


class TestNormalizeFxSymbol:
    """``normalize_fx_symbol`` accepts the common user spellings."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("USDCAD", "FXUSDCAD"),
            ("usdcad", "FXUSDCAD"),
            ("USD/CAD", "FXUSDCAD"),
            ("USD-CAD", "FXUSDCAD"),
            ("USD CAD", "FXUSDCAD"),
            ("usd_cad", "FXUSDCAD"),
            ("FXUSDCAD", "FXUSDCAD"),
            ("fxusdcad", "FXUSDCAD"),
        ],
    )
    def test_normalize_fx_symbol_accepts_common_spellings(self, raw, expected):
        """All common spellings normalize to the BoC canonical form."""
        assert normalize_fx_symbol(raw) == expected

    @pytest.mark.parametrize(
        "bad",
        [
            "",
            "USD",  # too short
            "USDEURCAD",  # too long
            "US",  # too short
        ],
    )
    def test_normalize_fx_symbol_rejects_invalid(self, bad):
        """Invalid shapes raise ``ValueError`` with a helpful message."""
        with pytest.raises(ValueError, match="FX symbol"):
            normalize_fx_symbol(bad)

    def test_normalize_fx_symbol_rejects_non_string(self):
        """Non-string input raises ``TypeError`` (defensive)."""
        with pytest.raises(TypeError, match="symbol must be str"):
            normalize_fx_symbol(123)  # type: ignore[arg-type]
