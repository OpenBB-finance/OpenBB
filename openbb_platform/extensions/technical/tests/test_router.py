"""Tests for the top-level openbb_technical.router aggregator."""

from __future__ import annotations

from openbb_core.app.route_iter import iter_api_routes
from openbb_technical.router import router


class TestTopLevelRouter:
    def test_aggregator_exposes_indicator_routes(self):
        paths = {r.path for r in iter_api_routes(router.api_router)}
        assert "/sma" in paths
        assert "/rsi" in paths
        assert "/macd" in paths
        assert "/atr" in paths
        assert "/realized_volatility" in paths
        assert "/aroon" in paths
        assert "/obv" in paths
        assert "/fib" in paths
        assert "/relative_rotation" in paths

    def test_aggregator_exposes_signal_routes(self):
        paths = {r.path for r in iter_api_routes(router.api_router)}
        assert "/signals/crossovers" in paths
        assert "/signals/oscillator_signals" in paths
        assert "/signals/divergences" in paths
        assert "/signals/breakouts" in paths
        assert "/signals/candlestick_patterns" in paths
        assert "/signals/regime" in paths

    def test_aggregator_exposes_multi_routes(self):
        paths = {r.path for r in iter_api_routes(router.api_router)}
        assert "/multi" in paths
        assert "/screen" in paths
        assert "/correlation" in paths
        assert "/correlation_matrix" in paths
        assert "/indicators" in paths

    def test_no_duplicate_paths(self):
        paths = [r.path for r in iter_api_routes(router.api_router)]
        assert len(paths) == len(set(paths)), (
            f"Duplicate route registered. Counts: "
            f"{ {p: paths.count(p) for p in set(paths) if paths.count(p) > 1} }"
        )
