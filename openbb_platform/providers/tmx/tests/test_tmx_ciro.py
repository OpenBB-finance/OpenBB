"""Tests for the CIRO fixed income access."""

from datetime import date

import pytest

from openbb_tmx.models.bond_trades import _as_float, _parse_file_date
from openbb_tmx.utils.ciro import ACCOUNT_TYPE_LABELS, MAX_WINDOW_DAYS, _windows


class TestWindows:
    """Date bracketing against the API limit."""

    def test_short_range_is_one_window(self):
        spans = _windows(date(2026, 1, 1), date(2026, 1, 31))
        assert spans == [(date(2026, 1, 1), date(2026, 1, 31))]

    def test_single_day(self):
        spans = _windows(date(2026, 1, 1), date(2026, 1, 1))
        assert spans == [(date(2026, 1, 1), date(2026, 1, 1))]

    def test_long_range_is_split(self):
        spans = _windows(date(2020, 1, 1), date(2026, 1, 1))
        assert len(spans) > 1

    def test_no_window_exceeds_the_limit(self):
        for start, stop in _windows(date(2015, 1, 1), date(2026, 7, 26)):
            assert (stop - start).days < MAX_WINDOW_DAYS

    def test_windows_are_contiguous_and_cover_the_range(self):
        spans = _windows(date(2024, 1, 1), date(2025, 6, 30))
        assert spans[0][0] == date(2024, 1, 1)
        assert spans[-1][1] == date(2025, 6, 30)
        for earlier, later in zip(spans, spans[1:]):
            assert (later[0] - earlier[1]).days == 1


class TestFieldParsing:
    """Trade field coercion."""

    @pytest.mark.parametrize("raw", ["N/A", "-", "", None, "abc"])
    def test_placeholders_become_none(self, raw):
        assert _as_float(raw) is None

    @pytest.mark.parametrize(("raw", "expected"), [("96.63", 96.63), (1, 1.0)])
    def test_numbers_parse(self, raw, expected):
        assert _as_float(raw) == expected

    def test_submission_date_key(self):
        assert _parse_file_date("20260723") == "2026-07-23"

    @pytest.mark.parametrize("raw", ["2026", "", None, "bad"])
    def test_bad_submission_date_key(self, raw):
        assert _parse_file_date(raw) is None

    def test_account_type_labels(self):
        assert ACCOUNT_TYPE_LABELS == {"R": "retail", "I": "institutional"}
