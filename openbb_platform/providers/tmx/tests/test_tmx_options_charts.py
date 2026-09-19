"""Tests for the options charts built over a loaded chain."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.utils.options.create_smile import (
    MAX_EXPIRATIONS,
    _first_priced_expiration,
    create_smile,
)
from openbb_tmx.utils.options.create_stats import create_stats
from openbb_tmx.utils.options.create_surface import create_surface
from openbb_tmx.utils.options.create_term_structure import create_term_structure
from openbb_tmx.utils.options.theme import CHART_CONFIG, new_figure

from .conftest import build_options_chain


def _plotted(output) -> set:
    """Return the names of the traces a chart drew."""
    return {trace.name for trace in output.chart.fig.data}


class TestChartTheme:
    """The shared figure styling."""

    def test_a_dark_figure_draws_light_text(self):
        _, text_color, background = new_figure("dark")

        assert text_color == "white"
        assert background == "rgba(0,0,0,0)"

    def test_a_light_figure_draws_dark_text(self):
        _, text_color, background = new_figure("light")

        assert text_color == "black"
        assert background == "rgba(255,255,255,0)"

    def test_the_chart_config_is_shared(self):
        assert CHART_CONFIG["displayModeBar"] is False
        assert CHART_CONFIG["scrollZoom"] is True

    @pytest.mark.parametrize("theme", ["dark", "light"])
    def test_the_figure_is_attached_to_the_output(self, options_chain, theme):
        output = create_stats(options_chain, theme=theme)

        assert output.chart.format == "plotly"
        assert output.chart.fig is not None
        assert output.chart.content


class TestSmileChart:
    """The implied-volatility smile across strikes."""

    def test_the_front_expiration_is_plotted(self, options_chain):
        output = create_smile(options_chain, theme="dark")

        assert _plotted(output) == {"Calls", "Puts"}
        assert output.results

    def test_each_expiration_is_named(self, options_chain):
        dates = ",".join(str(e) for e in options_chain.expirations[:2])
        output = create_smile(options_chain, expirations=dates, theme="dark")

        assert len(_plotted(output)) == 4
        assert all(" at " in name for name in _plotted(output))

    def test_a_list_of_expirations_is_accepted(self, options_chain):
        dates = [str(e) for e in options_chain.expirations[:2]]
        output = create_smile(options_chain, expirations=dates, theme="dark")

        assert len(_plotted(output)) == 4

    def test_the_skew_can_be_plotted_out_of_the_money(self, options_chain):
        output = create_smile(options_chain, otm=True, skew=True, theme="light")

        assert output.results
        assert output.chart.fig is not None

    def test_too_many_expirations_are_refused(self, options_chain):
        dates = ",".join(str(e) for e in options_chain.expirations) + ",2030-01-18" * 3

        with pytest.raises(OpenBBError, match="Up to five"):
            create_smile(options_chain, expirations=dates, theme="dark")

    def test_a_chain_without_implied_volatility_is_refused(self):
        with pytest.raises(OpenBBError, match="Implied Volatility was not found"):
            create_smile(build_options_chain(greeks=False), theme="dark")

    def test_the_first_priced_expiration_is_chosen(self, options_chain):
        assert _first_priced_expiration(options_chain) == str(
            options_chain.expirations[0]
        )

    def test_an_unpriced_chain_falls_back_to_the_front_expiration(self):
        chain = build_options_chain(priced=False)

        assert _first_priced_expiration(chain) == chain.expirations[0]

    def test_five_expirations_are_the_limit(self):
        assert MAX_EXPIRATIONS == 5


class TestStatsChart:
    """Open interest and volume by strike or expiration."""

    def test_open_interest_is_plotted_by_expiration(self, options_chain):
        output = create_stats(options_chain, theme="dark")

        assert _plotted(output) == {"Calls", "Puts"}
        assert len(output.results) == len(options_chain.expirations)

    def test_an_expiration_switches_the_axis_to_strike(self, options_chain):
        output = create_stats(
            options_chain,
            by="strike",
            date=str(options_chain.expirations[0]),
            theme="light",
        )

        assert len(output.results) == len(options_chain.strikes)

    def test_volume_is_plotted_as_a_share_of_the_total(self, options_chain):
        output = create_stats(
            options_chain, metric="volume", unit="percent", theme="dark"
        )

        assert _plotted(output) == {"% of Total"}

    def test_the_put_call_ratio_is_plotted(self, options_chain):
        output = create_stats(options_chain, unit="pcr", theme="dark")

        assert _plotted(output) == {"Put/Call Ratio"}

    def test_the_put_side_is_restored_after_plotting(self, options_chain):
        """The puts are negated to draw below the axis, not in the results."""
        output = create_stats(options_chain, theme="dark")

        assert all(row.Puts >= 0 for row in output.results)


class TestSurfaceChart:
    """The metric surface over days to expiry and strike."""

    @pytest.mark.parametrize("option_type", ["otm", "itm", "calls", "puts"])
    def test_every_side_of_the_chain_is_plotted(self, options_chain, option_type):
        output = create_surface(options_chain, option_type=option_type, theme="dark")

        assert output.results
        assert output.chart.fig is not None

    def test_a_greek_can_be_plotted(self, options_chain):
        output = create_surface(options_chain, metric="delta", theme="light")

        assert output.results
        assert "Delta" in output.chart.fig.layout.title.text

    def test_the_traded_contracts_can_be_isolated(self, options_chain):
        output = create_surface(
            options_chain, oi=True, volume=True, option_type="calls", theme="dark"
        )
        title = output.chart.fig.layout.title.text

        assert "With Open Interest" in title
        assert "Excluding Untraded Contracts" in title

    def test_the_expiries_can_be_bounded(self, options_chain):
        output = create_surface(
            options_chain, option_type="calls", dte_range=[0, 40], theme="dark"
        )

        assert output.results
        assert all(row.dte <= 40 for row in output.results)

    def test_the_strikes_can_be_bounded_by_moneyness(self, options_chain):
        output = create_surface(
            options_chain, option_type="calls", moneyness=10, theme="dark"
        )

        assert all(20.7 <= row.strike <= 25.3 for row in output.results)

    def test_an_absent_metric_is_reported(self, options_chain):
        with pytest.raises(OpenBBError, match="No nope data available"):
            create_surface(options_chain, metric="nope", theme="dark")


class TestTermStructureChart:
    """Price or implied volatility across expirations."""

    def test_both_sides_are_plotted_at_the_nearest_otm_strike(self, options_chain):
        output = create_term_structure(options_chain, theme="dark")

        assert _plotted(output) == {"Calls", "Puts"}
        assert "Nearest OTM Strikes" in output.chart.fig.layout.title.text

    def test_a_target_strike_is_named_in_the_title(self, options_chain):
        output = create_term_structure(
            options_chain, strike=23.0, option_type="calls", metric="price"
        )

        assert _plotted(output) == {"Calls"}
        assert "Strike Nearest To $23.0" in output.chart.fig.layout.title.text

    def test_moneyness_is_named_in_the_title(self, options_chain):
        output = create_term_structure(
            options_chain, moneyness=10, option_type="puts", theme="light"
        )

        assert _plotted(output) == {"Puts"}
        assert "10% Moneyness" in output.chart.fig.layout.title.text

    def test_a_chain_without_implied_volatility_is_refused(self):
        with pytest.raises(OpenBBError, match="No implied volatility"):
            create_term_structure(build_options_chain(greeks=False), theme="dark")

    def test_a_price_chart_needs_no_implied_volatility(self):
        output = create_term_structure(
            build_options_chain(greeks=False), metric="price", theme="dark"
        )

        assert output.results

    def test_an_expired_contract_is_left_out(self):
        """The chain lists a contract expiring today, its frame drops it."""
        chain = build_options_chain(expired=True)
        output = create_term_structure(chain, theme="dark")
        plotted = {str(row.expiration) for row in output.results}

        assert chain.expirations[0] not in plotted
        assert len(plotted) == len(chain.expirations) - 1
