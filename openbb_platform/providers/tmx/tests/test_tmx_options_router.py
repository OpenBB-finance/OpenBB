"""Tests for the derivatives.options analysis commands."""

import pytest

from openbb_tmx.routers import options as options_router


class Chain:
    """A stand-in for a validated options chain."""

    def __init__(self, iv=True, greeks=True, price=23.27):
        self.has_iv = iv
        self.has_greeks = greeks
        self.last_price = price
        self.underlying_price = [price]
        self.expirations = ["2026-07-31", "2026-08-21"]
        self.strikes = [20.0, 23.0]
        self.underlying_symbol = ["AC"]
        self.total_oi = {"expiration": [{"Expiration": "2026-07-31", "Calls": 10}]}
        self.total_volume = {"expiration": [{"Expiration": "2026-07-31", "Calls": 5}]}
        self.total_dex = {"expiration": [{"Expiration": "2026-07-31", "Calls": 1.0}]}
        self.total_gex = {"expiration": [{"Expiration": "2026-07-31", "Calls": 2.0}]}

    @property
    def dataframe(self):
        from pandas import DataFrame

        return DataFrame(
            {
                "expiration": ["2026-07-31", "2026-07-31", "2026-08-21"],
                "strike": [20.0, 23.0, 23.0],
                "implied_volatility": [0.5, 0.35, 0.4],
                "dte": [6, 6, 27],
            }
        )

    def skew(self, date=None):
        from pandas import DataFrame

        return DataFrame({"Expiration": ["2026-07-31"], "Call Skew": [0.1]})

    def straddle(self, days=30, strike=None):
        from pandas import DataFrame

        return DataFrame({"Long Straddle": [1.2]})

    def strangle(self, days=30, moneyness=20):
        from pandas import DataFrame

        return DataFrame({"Long Strangle": [0.8]})

    def vertical_call_spread(self, days=30):
        from pandas import DataFrame

        return DataFrame({"Bull Call Spread": [0.4]})

    def vertical_put_spread(self, days=30):
        from pandas import DataFrame

        return DataFrame({"Bear Put Spread": [0.3]})


@pytest.fixture
def chain(monkeypatch):
    """Serve a stub chain to every analysis command."""

    async def fake(symbol, use_cache=True):
        return Chain()

    monkeypatch.setattr(options_router, "_load_chain", fake)


class TestStrategies:
    """The strategy builders, priced from the loaded chain."""

    @pytest.fixture
    def strategies(self, monkeypatch):
        """Serve a stub chain and a stub strategy frame."""
        from pandas import DataFrame

        from openbb_tmx.utils.options import data_handler

        class Strategized(Chain):
            def strategies(self, **kwargs):
                return DataFrame(
                    {
                        "Expiration": ["2026-07-31"],
                        "DTE": [4],
                        "Strike 1": [24.0],
                        "Strike 2": [25.0],
                        "Strike 1 Premium": [0.5],
                        "Strike 2 Premium": [0.4],
                        "Cost": [0.9],
                        "Cost Percent": [0.04],
                        "Max Profit": [1.0],
                        "Max Loss": [-0.9],
                        "Breakeven Upper": [25.9],
                        "Breakeven Upper Percent": [0.06],
                        "Breakeven Lower": [23.1],
                        "Breakeven Lower Percent": [-0.05],
                        "Underlying Price": [24.25],
                        "Strategy": ["Long Straddle"],
                    }
                )

        async def fake(symbol, update=False):
            return Strategized()

        monkeypatch.setattr(data_handler, "load_symbol", fake)

    async def test_straddle(self, strategies):
        rows = await options_router.straddle(symbol="AC")

        assert rows[0]["strike_1"] == 24.0
        assert rows[0]["cost"] == 0.9

    async def test_strangle(self, strategies):
        rows = await options_router.strangle(symbol="AC")

        assert rows[0]["dte"] == 4

    @pytest.mark.parametrize("kind", ["call", "put", "both"])
    async def test_spreads(self, strategies, kind):
        rows = await options_router.spreads(symbol="AC", spread_type=kind)

        assert rows[0]["strategy"]
        assert rows[0]["sold_strike"] is not None


class TestStrategiesWithoutAQualifyingPair:
    """A chain that prices nothing is an empty answer, not a failure."""

    @pytest.fixture(params=["openbb", "pandas"])
    def refusing(self, monkeypatch, request):
        """Serve a chain whose strategy properties refuse to answer."""
        from openbb_core.app.model.abstract.error import OpenBBError
        from pandas.errors import UndefinedVariableError

        from openbb_tmx.utils.options import data_handler

        raised = (
            OpenBBError("No strategies found for the given parameters.")
            if request.param == "openbb"
            else UndefinedVariableError("BACKTICK_QUOTED_STRING_Strike_1")
        )

        class Refusing(Chain):
            def strategies(self, **kwargs):
                raise raised

        async def fake(symbol, update=False):
            return Refusing()

        monkeypatch.setattr(data_handler, "load_symbol", fake)

    async def test_the_straddle_is_empty(self, refusing):
        assert await options_router.straddle(symbol="AC") == []

    async def test_the_strangle_is_empty(self, refusing):
        assert await options_router.strangle(symbol="AC") == []

    async def test_the_spreads_are_empty(self, refusing):
        assert await options_router.spreads(symbol="AC", spread_type="both") == []


class TestChartRoutes:
    """The Plotly chart views the Workspace renders."""

    @pytest.fixture
    def loaded(self, monkeypatch):
        """Serve a stub chain to the chart builders and the dropdowns."""
        from openbb_tmx.utils.options import data_handler

        async def fake(symbol, update=False):
            return data_handler.LOADED_SYMBOLS[symbol.upper()]

        monkeypatch.setattr(data_handler, "LOADED_SYMBOLS", {"AC": Chain()})
        monkeypatch.setattr(data_handler, "load_symbol", fake)

    def test_every_chart_route_is_registered(self):
        from openbb_core.app.route_iter import iter_api_routes

        paths = {r.path for r in iter_api_routes(options_router.router.api_router)}

        for path, _, _ in options_router.CHART_ROUTES:
            assert f"/options{path}" in paths

    def test_each_route_carries_a_chart_widget(self):
        for _, _, name in options_router.CHART_ROUTES:
            config = options_router._chart_widget(name)["widget_config"]
            assert config["type"] == "chart"
            assert config["raw"] is True
            assert config["name"] == name

    async def test_tickers_serve_expiry_and_strike_choices(self, loaded):
        expiries = await options_router.get_tickers(symbol="AC", expiry_list=True)
        strikes = await options_router.get_tickers(symbol="AC", strike_list=True)

        assert [e["value"] for e in expiries] == ["2026-07-31", "2026-08-21"]
        assert strikes[0]["label"] == "Nearest OTM"

    async def test_tickers_without_a_symbol_serve_nothing(self):
        assert await options_router.get_tickers(symbol="") == []
