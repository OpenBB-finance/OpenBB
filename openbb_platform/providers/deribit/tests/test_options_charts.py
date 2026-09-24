"""Tests for the Deribit options chart builders and the chain they draw from."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_deribit.utils.options import data_handler
from openbb_deribit.utils.options.create_smile import (
    _first_priced_expiration,
    create_smile,
)
from openbb_deribit.utils.options.create_stats import create_stats
from openbb_deribit.utils.options.create_surface import create_surface
from openbb_deribit.utils.options.create_term_structure import create_term_structure


class TestDataHandler:
    """The REST chain becomes the core model the charts are drawn from."""

    def test_volatility_is_a_decimal(self, chain_frame, options_chain):
        """Deribit quotes volatility in percent; the model carries a decimal."""
        frame = chain_frame()

        assert options_chain.implied_volatility == pytest.approx(
            list(
                frame.sort_values(["expiration", "strike", "option_type"])[
                    "implied_volatility"
                ]
                / 100
            )
        )

    def test_every_contract_names_its_underlying(self, options_chain):
        """The underlying is the root the chain was loaded for."""
        assert set(options_chain.underlying_symbol) == {"BTC"}

    def test_the_forward_is_the_underlying_price(self, chain_frame):
        """Each contract is priced against the forward of its expiration."""
        frame = chain_frame()
        frame["underlying_price"] = 101.0

        assert set(data_handler.to_chain(frame, "BTC").underlying_price) == {101.0}

    def test_a_missing_forward_falls_back_to_spot(self, chain_frame):
        """A contract with no forward is priced against the index."""
        frame = chain_frame().drop(columns=["underlying_price"])

        assert set(data_handler.to_chain(frame, "BTC").underlying_price) == {100.0}

    def test_an_untraded_contract_has_no_last_price(self, chain_frame):
        """A contract that never traded carries no last price."""
        frame = chain_frame()
        frame["last"] = None
        chain = data_handler.to_chain(frame, "BTC")

        assert set(chain.last_trade_price) == {None}

    @pytest.mark.asyncio
    async def test_load_symbol_reads_the_chain(self, loaded_chain):
        """The chain is read through the shared REST loader."""
        loaded_chain()
        chain = await data_handler.load_symbol("btc")

        assert set(chain.underlying_symbol) == {"BTC"}
        assert len(chain.expirations) == 2

    @pytest.mark.asyncio
    async def test_load_symbol_wraps_fetch_errors(self, monkeypatch):
        """An empty chain surfaces as a symbol-specific OpenBBError."""
        from openbb_core.provider.utils.errors import EmptyDataError

        async def _empty(symbol, use_cache=True):
            raise EmptyDataError("nothing listed")

        monkeypatch.setattr("openbb_deribit.utils.options.chain.load_chain", _empty)

        with pytest.raises(OpenBBError, match="No options available for NOPE"):
            await data_handler.load_symbol("nope")

    def test_strike_choices(self, options_chain):
        """Strikes are offered after the nearest out-of-the-money default."""
        strikes = data_handler.get_strikes(options_chain)

        assert strikes[0] == {"label": "Nearest OTM", "value": None}
        assert [choice["value"] for choice in strikes[1:]] == options_chain.strikes
        assert strikes[1]["label"] == "$92"
        assert "Underlying" in strikes[1]["extraInfo"]["rightOfDescription"]

    def test_a_fractional_strike_is_labelled_intact(self, chain_frame):
        """A strike below one keeps its decimals in the label."""
        chain = data_handler.to_chain(chain_frame(spot=1.05), "XRP_USDC")
        labels = [choice["label"] for choice in data_handler.get_strikes(chain)]

        assert "$1.05" in labels

    def test_no_underlying_price_describes_nothing(self):
        """Without an underlying price a strike carries no description."""
        stub = type("Stub", (), {"underlying_price": [], "strikes": [100.0]})()

        assert data_handler.get_strikes(stub)[1]["extraInfo"] == {}


class TestChainExpirations:
    """Expirations offered must be expirations that resolve to rows."""

    def test_the_frame_names_the_expirations(self, options_chain):
        """Every expiration offered has contracts in the frame."""
        offered = data_handler.chain_expirations(options_chain)

        assert offered == sorted(
            {str(v) for v in options_chain.dataframe["expiration"]}
        )

    def test_falls_back_when_there_is_no_frame(self):
        """A chain whose frame cannot be built still reports its own expirations."""

        class _NoFrame:
            expirations = ["2030-01-18"]

            @property
            def dataframe(self):
                raise ValueError("no validated data")

        assert data_handler.chain_expirations(_NoFrame()) == ["2030-01-18"]

    def test_falls_back_when_the_frame_has_no_expirations(self):
        """A frame without an expiration column defers to the model's list."""
        from pandas import DataFrame

        stub = type(
            "Stub",
            (),
            {"expirations": ["2030-01-18"], "dataframe": DataFrame({"strike": [1.0]})},
        )()

        assert data_handler.chain_expirations(stub) == ["2030-01-18"]


class TestSmile:
    """Implied-volatility smile builder."""

    def test_default_expiration_skips_zero_iv(self, options_chain):
        """The default expiration is the front one that still carries IV."""
        assert _first_priced_expiration(options_chain) in options_chain.expirations

    def test_no_priced_expiration_falls_back(self, options_chain):
        """With no priced contracts the front expiration is used."""
        stub = type(
            "Stub",
            (),
            {
                "dataframe": options_chain.dataframe.assign(implied_volatility=0.0),
                "expirations": options_chain.expirations,
            },
        )()

        assert (
            _first_priced_expiration(stub)
            == data_handler.chain_expirations(options_chain)[0]
        )

    def test_builds_chart(self, options_chain):
        """The default smile renders two traces and returns the plotted rows."""
        output = create_smile(options_chain)

        assert output.chart.format == "plotly"
        assert [trace["name"] for trace in output.chart.content["data"]] == [
            "Calls",
            "Puts",
        ]
        assert output.results

    def test_otm_and_skew(self, options_chain):
        """The OTM and skew variants both render."""
        output = create_smile(options_chain, otm=True, skew=True, theme="light")

        assert len(output.chart.content["data"]) == 2
        assert "OTM IV Skew" in output.chart.content["layout"]["title"]["text"]

    def test_comma_separated_expirations(self, options_chain):
        """A comma-separated list plots one pair of traces per date."""
        output = create_smile(
            options_chain, expirations=",".join(options_chain.expirations)
        )

        assert len(output.chart.content["data"]) == 2 * len(options_chain.expirations)

    def test_list_of_expirations(self, options_chain):
        """A list of expirations plots one pair of traces per date."""
        output = create_smile(options_chain, expirations=options_chain.expirations)

        assert len(output.chart.content["data"]) == 2 * len(options_chain.expirations)

    def test_too_many_expirations(self, options_chain):
        """More than five expirations is rejected."""
        with pytest.raises(OpenBBError, match="Too many dates"):
            create_smile(options_chain, expirations=options_chain.expirations * 3)

    def test_requires_iv(self):
        """A chain without implied volatility is rejected."""
        stub = type("Stub", (), {"has_iv": False})()

        with pytest.raises(OpenBBError, match="Implied Volatility"):
            create_smile(stub)


class TestStats:
    """Open interest and volume statistics builder."""

    @pytest.mark.parametrize(
        "unit,traces",
        [
            ("value", ["Calls", "Puts"]),
            ("percent", ["% of Total"]),
            ("pcr", ["Put/Call Ratio"]),
        ],
    )
    def test_units(self, options_chain, unit, traces):
        """Every unit mode renders its own bars."""
        output = create_stats(options_chain, unit=unit)

        assert [trace["name"] for trace in output.chart.content["data"]] == traces

    def test_puts_are_drawn_below_the_axis(self, options_chain):
        """Puts hang below zero while the returned rows stay positive."""
        output = create_stats(options_chain)
        puts = output.chart.fig.data[1]

        assert all(value <= 0 for value in puts.y)
        assert all(row.Puts >= 0 for row in output.results)

    def test_by_strike_for_one_expiration(self, options_chain):
        """Passing a date switches the axis to strikes."""
        output = create_stats(
            options_chain,
            by="strike",
            metric="volume",
            date=options_chain.expirations[1],
            theme="light",
        )

        assert output.chart.content["layout"]["title"]["text"] == (
            "BTC Volume By Strike"
        )
        assert output.chart.content["layout"]["xaxis"]["tickprefix"] == "$"


class TestSurface:
    """3-D surface builder."""

    @pytest.mark.parametrize("option_type", ["otm", "itm", "calls", "puts"])
    def test_option_types(self, options_chain, option_type):
        """Every side of the chain renders a surface."""
        output = create_surface(options_chain, option_type=option_type)

        assert output.chart.content["data"]

    @pytest.mark.parametrize("metric", ["delta", "gamma", "theta", "vega", "rho"])
    def test_greeks(self, options_chain, metric):
        """The modelled greeks are plottable as the Z axis."""
        output = create_surface(options_chain, metric=metric)

        assert output.chart.content["data"]

    @pytest.mark.parametrize("metric", ["dex", "gex"])
    def test_exposures(self, options_chain, metric):
        """The upper-cased DEX/GEX columns resolve from lowercase metric names."""
        output = create_surface(options_chain, metric=metric, theme="light")

        assert output.chart.content["data"]

    def test_filters(self, options_chain):
        """DTE, moneyness, open-interest, and volume filters all apply."""
        output = create_surface(
            options_chain,
            dte_range=[0, 400],
            moneyness=25,
            oi=True,
            volume=True,
        )
        title = output.chart.content["layout"]["title"]["text"]

        assert "With Open Interest" in title
        assert "Excluding Untraded Contracts" in title

    def test_unknown_metric(self, options_chain):
        """An absent metric is rejected."""
        with pytest.raises(OpenBBError, match="No nope data"):
            create_surface(options_chain, metric="nope")


class TestTermStructure:
    """Term-structure builder."""

    def test_default(self, options_chain):
        """The default plots calls and puts at the nearest OTM strikes."""
        output = create_term_structure(options_chain)

        assert [trace["name"] for trace in output.chart.content["data"]] == [
            "Calls",
            "Puts",
        ]

    def test_by_strike(self, options_chain):
        """A fixed strike is honored."""
        strike = options_chain.strikes[len(options_chain.strikes) // 2]
        output = create_term_structure(
            options_chain, strike=strike, metric="price", option_type="calls"
        )

        assert len(output.chart.content["data"]) == 1
        assert f"${strike}" in output.chart.content["layout"]["title"]["text"]

    def test_by_moneyness(self, options_chain):
        """A moneyness target is honored."""
        output = create_term_structure(
            options_chain, moneyness=4, option_type="puts", theme="light"
        )

        assert len(output.chart.content["data"]) == 1

    def test_untraded_contracts_are_not_drawn(self, chain_frame):
        """Only contracts with a last trade are read, as on Cboe."""
        frame = chain_frame()
        frame["last"] = None
        output = create_term_structure(data_handler.to_chain(frame, "BTC"))

        assert output.chart.content["data"] == []

    def test_requires_iv(self):
        """Requesting IV on a chain without it is rejected."""
        stub = type("Stub", (), {"has_iv": False})()

        with pytest.raises(OpenBBError, match="No implied volatility"):
            create_term_structure(stub, metric="iv")


class TestOptionalCharting:
    """Without the charting extension a view returns the rows it would draw."""

    @pytest.fixture
    def unplotted(self, monkeypatch):
        """Run as though openbb-charting were not installed."""
        import openbb_deribit

        monkeypatch.setattr(openbb_deribit, "CHARTING_INSTALLED", False)

    @pytest.mark.parametrize(
        "builder",
        [create_smile, create_stats, create_surface, create_term_structure],
        ids=lambda builder: builder.__name__,
    )
    def test_every_view_returns_its_rows(self, unplotted, options_chain, builder):
        """Each chart still answers with the rows behind it."""
        output = builder(options_chain, theme="dark")

        assert output.chart is None
        assert output.results


class TestSupportedLayout:
    """The chart template is trimmed to what the installed Plotly accepts."""

    def test_unknown_keys_are_dropped(self):
        """A key Plotly no longer knows is removed rather than raising."""
        from openbb_deribit.utils.options.theme import supported_layout

        assert supported_layout({"title": "x", "no_such_key": 1}) == {"title": "x"}

    def test_a_plotly_without_a_key_list_keeps_everything(self, monkeypatch):
        """Where Plotly publishes no key list the layout passes through."""
        from plotly.graph_objects import Layout

        from openbb_deribit.utils.options.theme import supported_layout

        monkeypatch.setattr(Layout, "_valid_props", set())
        layout = {"title": "x", "no_such_key": 1}

        assert supported_layout(layout) is layout
