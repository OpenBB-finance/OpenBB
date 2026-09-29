"""Deribit through the REST API, against the live exchange."""

import pytest

from .cases import CHARTS, FEEDS, MODELS, TABLES, case_id, namespace

pytestmark = pytest.mark.integration


def _get(api: dict, path: str, params: dict):
    """Call one route and return its decoded body.

    Raises
    ------
    AssertionError
        If the route does not answer 200.
    """
    import requests

    written = {
        key: str(value).lower() if isinstance(value, bool) else value
        for key, value in params.items()
    }
    response = requests.get(
        f"{api['base']}{path}", params=written, headers=api["headers"], timeout=120
    )

    assert response.status_code == 200, f"{path} {params}: {response.text}"

    return response.json()


class TestModels:
    """Every model-backed route returns rows."""

    @pytest.mark.parametrize("case", MODELS, ids=case_id)
    def test_returns_rows(self, api, case):
        """The route answers with an OBBject body holding at least one row."""
        router, name, params = case
        body = _get(
            api,
            f"/{namespace(router, name)}/{router}/{name}",
            {"provider": "deribit", **params},
        )

        assert body["provider"] == "deribit"
        assert body["results"]

    def test_an_unoffered_depth_is_refused(self, api):
        """A book depth Deribit does not return is refused before the exchange."""
        import requests

        response = requests.get(
            f"{api['base']}/deribit/market/order_book",
            params={"provider": "deribit", "symbol": "BTC-PERPETUAL", "depth": "7"},
            headers=api["headers"],
            timeout=60,
        )

        assert response.status_code in (400, 422)
        assert "not 7" in response.text


class TestFeeds:
    """Every choice feed and scalar route answers."""

    @pytest.mark.parametrize("case", FEEDS, ids=case_id)
    def test_answers(self, api, case):
        """The route returns something to offer."""
        router, name, params = case
        body = _get(api, f"/deribit/{router}/{name}", params)

        assert body is not None
        assert body not in ([], {})


class TestAnalysisTables:
    """The options analysis routes return ranked or priced rows."""

    @pytest.mark.parametrize(
        "case", TABLES, ids=lambda case: case_id(("options", *case))
    )
    def test_returns_rows(self, api, case):
        """The route answers with rows."""
        name, params = case
        body = _get(api, f"/deribit/options/{name}", params)

        assert body["results"]

    def test_the_optimizer_codes_every_row(self, api):
        """Each ranked position names the Deribit combo it is."""
        body = _get(
            api, "/deribit/options/optimizer", {"symbol": "BTC", "target_price": 100000}
        )

        assert all(row["code"] for row in body["results"])


class TestCharts:
    """Every chart route draws, and hands back its rows on request."""

    @pytest.mark.parametrize(
        "case", CHARTS, ids=lambda case: case_id(("options", *case))
    )
    def test_draws_a_figure(self, api, case):
        """The route answers with a Plotly figure and its display config."""
        name, params = case
        figure = _get(api, f"/deribit/options/{name}", params)

        assert figure["data"]
        assert figure["layout"]["title"]["text"]
        assert figure["config"]["responsive"] is True

    @pytest.mark.parametrize(
        "name", sorted({name for name, _params in CHARTS}), ids=str
    )
    def test_raw_returns_rows(self, api, name):
        """With raw set, the route answers with the rows behind the chart."""
        rows = _get(api, f"/deribit/options/{name}", {"symbol": "BTC", "raw": True})

        assert isinstance(rows, list)
        assert rows

    def test_the_payoff_draws_a_ranked_position(self, api):
        """The legs the optimizer prints draw back as that position."""
        view = {"symbol": "BTC", "target_price": 100000}
        row = _get(api, "/deribit/options/optimizer", view)["results"][-1]
        figure = _get(api, "/deribit/options/payoff", {**view, "legs": row["legs"]})

        assert row["strategy"] in figure["layout"]["title"]["text"]

    def test_an_unlisted_underlying_is_a_404(self, api):
        """An underlying Deribit lists no options on answers 404."""
        import requests

        response = requests.get(
            f"{api['base']}/deribit/options/smile",
            params={"symbol": "NOPE"},
            headers=api["headers"],
            timeout=60,
        )

        assert response.status_code == 404
