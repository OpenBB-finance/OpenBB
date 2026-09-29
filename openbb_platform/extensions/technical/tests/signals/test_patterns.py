"""Tests for openbb_technical.signals.patterns."""

from __future__ import annotations

import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.signals.patterns import (
    SUPPORTED_PATTERNS,
    CandlestickPatternsQueryParams,
    PatternEvent,
    candlestick_patterns,
)


def _bar(o: float, h: float, l: float, c: float) -> dict:
    return {"open": o, "high": h, "low": l, "close": c, "volume": 1000.0}


def _frame(rows: list[dict]) -> list:
    df = pd.DataFrame(
        rows,
        index=pd.date_range("2022-01-01", periods=len(rows), freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


@pytest.fixture
def doji_records():
    """A tiny-body bar with long shadows on both sides."""
    return _frame(
        [
            _bar(100.0, 105.0, 95.0, 100.05),
            _bar(100.0, 100.6, 99.4, 100.5),
        ]
    )


@pytest.fixture
def hammer_records():
    """Small body with a long lower shadow and tiny upper shadow."""
    return _frame(
        [
            _bar(100.0, 100.2, 90.0, 100.2),
            _bar(101.0, 101.5, 100.5, 101.2),
        ]
    )


@pytest.fixture
def marubozu_records():
    """Full-body up bar with negligible shadows."""
    return _frame(
        [
            _bar(100.0, 110.0, 100.0, 110.0),
            _bar(110.0, 110.0, 100.0, 100.0),
        ]
    )


@pytest.fixture
def spinning_top_records():
    """Small body centred between roughly equal shadows."""
    return _frame(
        [
            _bar(100.0, 105.0, 95.0, 100.5),
        ]
    )


@pytest.fixture
def engulfing_records():
    """Small red bar followed by a much larger green bar that engulfs it."""
    return _frame(
        [
            _bar(100.0, 100.2, 99.8, 99.9),
            _bar(99.5, 102.0, 99.4, 101.5),
        ]
    )


@pytest.fixture
def neutral_records():
    """Medium-body bars that don't match any of the five native patterns."""
    return _frame(
        [
            _bar(100.0, 100.25, 99.25, 100.5),
            _bar(100.5, 101.0, 99.75, 101.0),
        ]
    )


class TestCandlestickEndpoint:
    def test_doji_detected(self, doji_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=doji_records, patterns=["doji"])
        )
        names = [e.pattern for e in result.results]
        assert "doji" in names
        doji_events = [e for e in result.results if e.pattern == "doji"]
        assert doji_events[0].direction == "neutral"
        assert 0.0 < doji_events[0].confidence <= 1.0

    def test_hammer_detected(self, hammer_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=hammer_records, patterns=["hammer"])
        )
        hammers = [e for e in result.results if e.pattern == "hammer"]
        assert len(hammers) == 1
        assert hammers[0].direction == "bullish"

    def test_marubozu_directions(self, marubozu_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=marubozu_records, patterns=["marubozu"])
        )
        marubozus = [e for e in result.results if e.pattern == "marubozu"]
        assert len(marubozus) == 2
        directions = {m.direction for m in marubozus}
        assert directions == {"bullish", "bearish"}

    def test_spinning_top_detected(self, spinning_top_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(
                data=spinning_top_records, patterns=["spinning_top"]
            )
        )
        tops = [e for e in result.results if e.pattern == "spinning_top"]
        assert len(tops) == 1
        assert tops[0].direction == "neutral"

    def test_engulfing_detected(self, engulfing_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(
                data=engulfing_records, patterns=["engulfing"]
            )
        )
        engulfings = [e for e in result.results if e.pattern == "engulfing"]
        assert len(engulfings) == 1
        assert engulfings[0].direction == "bullish"

    def test_neutral_bars_produce_no_events(self, neutral_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=neutral_records)
        )
        assert result.results == []

    def test_default_patterns_runs_all(self, doji_records):
        result = candlestick_patterns(CandlestickPatternsQueryParams(data=doji_records))
        assert any(e.pattern == "doji" for e in result.results)

    def test_unsupported_pattern_silently_dropped(self, doji_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(
                data=doji_records, patterns=["three_white_soldiers"]
            )
        )
        assert result.results == []

    def test_mixed_supported_and_unsupported(self, doji_records):
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(
                data=doji_records, patterns=["doji", "three_white_soldiers"]
            )
        )
        assert any(e.pattern == "doji" for e in result.results)

    def test_all_results_are_pattern_events(self, doji_records):
        result = candlestick_patterns(CandlestickPatternsQueryParams(data=doji_records))
        assert all(isinstance(e, PatternEvent) for e in result.results)


class TestDetectorRejection:
    def test_zero_range_bar_rejected(self):
        records = _frame([_bar(100.0, 100.0, 100.0, 100.0)])
        result = candlestick_patterns(CandlestickPatternsQueryParams(data=records))
        assert result.results == []

    def test_doji_with_large_body_rejected(self):
        records = _frame([_bar(100.0, 105.0, 100.0, 105.0)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["doji"])
        )
        assert not any(e.pattern == "doji" for e in result.results)

    def test_hammer_with_long_upper_shadow_rejected(self):
        records = _frame([_bar(100.0, 110.0, 99.5, 100.2)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["hammer"])
        )
        assert not any(e.pattern == "hammer" for e in result.results)

    def test_hammer_short_lower_shadow_rejected(self):
        records = _frame([_bar(100.0, 100.5, 99.5, 100.2)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["hammer"])
        )
        assert not any(e.pattern == "hammer" for e in result.results)

    def test_hammer_body_not_in_upper_third(self):
        records = _frame([_bar(4.0, 5.0, 1.0, 3.0)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["hammer"])
        )
        assert not any(e.pattern == "hammer" for e in result.results)

    def test_marubozu_with_shadows_rejected(self):
        records = _frame([_bar(100.0, 110.0, 99.0, 109.0)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["marubozu"])
        )
        assert not any(e.pattern == "marubozu" for e in result.results)

    def test_marubozu_doji_body_rejected(self):
        records = _frame([_bar(100.0, 105.0, 95.0, 100.05)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["marubozu"])
        )
        assert not any(e.pattern == "marubozu" for e in result.results)

    def test_spinning_top_lopsided_rejected(self):
        records = _frame([_bar(100.0, 105.0, 99.9, 100.5)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["spinning_top"])
        )
        assert not any(e.pattern == "spinning_top" for e in result.results)

    def test_spinning_top_too_large_body_rejected(self):
        records = _frame([_bar(100.0, 105.0, 100.0, 104.0)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["spinning_top"])
        )
        assert not any(e.pattern == "spinning_top" for e in result.results)

    def test_spinning_top_tiny_body_rejected(self):
        records = _frame([_bar(100.0, 110.0, 90.0, 100.01)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["spinning_top"])
        )
        assert not any(e.pattern == "spinning_top" for e in result.results)

    def test_spinning_top_zero_upper_shadow_rejected(self):
        records = _frame([_bar(100.0, 100.1, 99.0, 100.1)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["spinning_top"])
        )
        assert not any(e.pattern == "spinning_top" for e in result.results)

    def test_spinning_top_zero_lower_shadow_rejected(self):
        records = _frame([_bar(100.1, 101.0, 100.0, 100.0)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["spinning_top"])
        )
        assert not any(e.pattern == "spinning_top" for e in result.results)

    def test_engulfing_first_bar_has_no_prev(self):
        records = _frame([_bar(99.5, 102.0, 99.4, 101.5)])
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["engulfing"])
        )
        assert not any(e.pattern == "engulfing" for e in result.results)

    def test_engulfing_same_direction_rejected(self):
        records = _frame(
            [
                _bar(100.0, 100.5, 99.9, 100.3),
                _bar(99.5, 102.0, 99.4, 101.5),
            ]
        )
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["engulfing"])
        )
        assert not any(e.pattern == "engulfing" for e in result.results)

    def test_engulfing_zero_body_rejected(self):
        records = _frame(
            [
                _bar(100.0, 100.5, 99.5, 100.0),
                _bar(99.5, 102.0, 99.4, 101.5),
            ]
        )
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["engulfing"])
        )
        assert not any(e.pattern == "engulfing" for e in result.results)

    def test_engulfing_current_zero_body_rejected(self):
        records = _frame(
            [
                _bar(100.0, 100.5, 99.0, 99.5),
                _bar(99.7, 100.6, 99.4, 99.7),
            ]
        )
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["engulfing"])
        )
        assert not any(e.pattern == "engulfing" for e in result.results)

    def test_engulfing_not_full_overlap_rejected(self):
        records = _frame(
            [
                _bar(100.0, 101.0, 99.0, 99.5),
                _bar(99.6, 100.5, 99.4, 100.4),
            ]
        )
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["engulfing"])
        )
        assert not any(e.pattern == "engulfing" for e in result.results)

    def test_engulfing_bearish(self):
        records = _frame(
            [
                _bar(100.0, 101.0, 99.8, 100.8),
                _bar(101.0, 101.2, 98.5, 99.0),
            ]
        )
        result = candlestick_patterns(
            CandlestickPatternsQueryParams(data=records, patterns=["engulfing"])
        )
        bears = [e for e in result.results if e.direction == "bearish"]
        assert len(bears) == 1


class TestQueryParamModel:
    def test_defaults(self, doji_records):
        params = CandlestickPatternsQueryParams(data=doji_records)
        assert params.patterns is None
        assert params.index == "date"

    def test_supported_patterns_constant(self):
        assert isinstance(SUPPORTED_PATTERNS, tuple)
        assert len(SUPPORTED_PATTERNS) == 5
