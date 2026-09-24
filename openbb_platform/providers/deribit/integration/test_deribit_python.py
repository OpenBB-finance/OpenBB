"""Deribit through the Python interface, against the live exchange."""

import pytest
from openbb_core.app.model.obbject import OBBject

from .cases import CHARTS, FEEDS, MODELS, TABLES, case_id, namespace

pytestmark = pytest.mark.integration


def _command(obb, router: str, name: str):
    """Return the Python command for a route, wherever it is served."""
    return getattr(getattr(getattr(obb, namespace(router, name)), router), name)


def _field(row, name: str):
    """Read one field of a result row, whether a model or a mapping."""
    return row[name] if isinstance(row, dict) else getattr(row, name)


class TestModels:
    """Every model-backed command returns rows."""

    @pytest.mark.parametrize("case", MODELS, ids=case_id)
    def test_returns_rows(self, obb, case):
        """The command answers with an OBBject holding at least one row."""
        router, name, params = case
        result = _command(obb, router, name)(provider="deribit", **params)

        assert isinstance(result, OBBject)
        assert result.provider == "deribit"
        assert result.results

    def test_a_result_converts_to_a_frame(self, obb):
        """The rows convert to a DataFrame for Python users."""
        frame = _command(obb, "market", "ticker")(
            symbol="BTC-PERPETUAL", provider="deribit"
        ).to_df()

        assert not frame.empty

    def test_an_unoffered_depth_is_refused(self, obb):
        """A book depth Deribit does not return is refused before the exchange."""
        from openbb_core.app.model.abstract.error import OpenBBError

        with pytest.raises(OpenBBError, match="not 7"):
            obb.deribit.market.order_book(
                symbol="BTC-PERPETUAL", depth=7, provider="deribit"
            )


class TestFeeds:
    """Every choice feed and scalar answers."""

    @pytest.mark.parametrize("case", FEEDS, ids=case_id)
    def test_answers(self, obb, case):
        """The feed returns something to offer."""
        router, name, params = case
        answer = _command(obb, router, name)(**params)

        assert answer is not None
        assert answer not in ([], {})

    def test_status_reports_locked_currencies(self, obb):
        """The platform status names what is locked."""
        assert "locked" in obb.deribit.reference.status()


class TestAnalysisTables:
    """The options analysis tables return ranked or priced rows."""

    @pytest.mark.parametrize(
        "case", TABLES, ids=lambda case: case_id(("options", *case))
    )
    def test_returns_rows(self, obb, case):
        """The table answers with rows."""
        name, params = case
        result = getattr(obb.deribit.options, name)(**params)

        assert isinstance(result, OBBject)
        assert result.results

    def test_the_optimizer_codes_every_row(self, obb):
        """Each ranked position names the Deribit combo it is."""
        result = obb.deribit.options.optimizer(symbol="BTC", target_price=100000)
        codes = [_field(row, "code") for row in result.results]

        assert all(codes)
        assert len(set(codes)) > 1


class TestCharts:
    """Every chart draws, and every chart hands back its rows on request."""

    @pytest.mark.parametrize(
        "case", CHARTS, ids=lambda case: case_id(("options", *case))
    )
    def test_draws_a_figure(self, obb, case):
        """The chart answers with a Plotly figure."""
        name, params = case
        figure = getattr(obb.deribit.options, name)(**params)

        assert isinstance(figure, dict)
        assert figure["data"]
        assert figure["layout"]["title"]["text"]

    @pytest.mark.parametrize(
        "name", sorted({name for name, _params in CHARTS}), ids=str
    )
    def test_raw_returns_rows(self, obb, name):
        """With raw set, the chart answers with the rows behind it."""
        rows = getattr(obb.deribit.options, name)(symbol="BTC", raw=True)

        assert isinstance(rows, list)
        assert rows

    def test_the_smile_draws_chosen_expirations(self, obb):
        """Expirations picked from the feed are drawn as calls and puts each."""
        offered = obb.deribit.options.expiration_choices(symbol="BTC")
        chosen = [item["value"] for item in offered[2:4]]
        figure = obb.deribit.options.smile(symbol="BTC", expirations=",".join(chosen))

        assert len(figure["data"]) == 2 * len(chosen)

    def test_stats_for_one_expiration(self, obb):
        """An expiration picked from the feed is drawn by strike."""
        offered = obb.deribit.options.expiration_choices(symbol="BTC")
        figure = obb.deribit.options.stats(symbol="BTC", date=offered[1]["value"])

        assert "By Strike" in figure["layout"]["title"]["text"]

    def test_term_structure_at_a_chosen_strike(self, obb):
        """A strike picked from the feed titles the term structure."""
        offered = obb.deribit.options.strike_choices(symbol="BTC")
        strike = offered[len(offered) // 2]["value"]
        figure = obb.deribit.options.term_structure(symbol="BTC", strike=strike)

        assert f"${strike}" in figure["layout"]["title"]["text"]

    def test_the_payoff_draws_a_ranked_position(self, obb):
        """The legs the optimizer prints draw back as that position."""
        ranked = obb.deribit.options.optimizer(symbol="BTC", target_price=100000)
        row = ranked.results[-1]
        figure = obb.deribit.options.payoff(
            symbol="BTC", target_price=100000, legs=_field(row, "legs")
        )

        assert _field(row, "strategy") in figure["layout"]["title"]["text"]
