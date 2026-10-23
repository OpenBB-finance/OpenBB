"""TMX API interface integration tests."""

import base64
from datetime import date, timedelta

import pytest
import requests
from openbb_core.env import Env

ROOT = "http://0.0.0.0:8000/api/v1/tmx"

TRADE_END = date.today() - timedelta(days=1)
TRADE_START = TRADE_END - timedelta(days=30)


@pytest.fixture(scope="session")
def headers():
    """Fixture to setup the request headers."""
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    token = base64.b64encode(userpass.encode("utf-8")).decode("ascii")

    return {"Authorization": f"Basic {token}"}


def _get(path, params, headers, timeout=180):
    """Call one TMX endpoint."""
    response = requests.get(
        f"{ROOT}/{path}", params=params, headers=headers, timeout=timeout
    )

    assert response.status_code == 200, f"{path} answered {response.status_code}"

    return response


@pytest.mark.integration
class TestModelCommands:
    """Every model-backed command answers with a populated envelope."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("equity/search", {"query": "bank"}),
            ("equity/search", {"country": "CA", "limit": 50}),
            ("equity/screener", {"exchange": "TSX", "limit": 10}),
            ("equity/screener", {"symbol_type": "Index", "limit": 10}),
            ("equity/screener", {"symbol_type": "Future", "limit": 10}),
            ("equity/quote", {"symbol": "AC"}),
            ("equity/profile", {"symbol": "AC"}),
            ("equity/historical", {"symbol": "AC"}),
            ("equity/filings", {"symbol": "AC"}),
            ("equity/gainers", {}),
            ("equity/rankings", {"ranking": "tsx30"}),
            ("equity/rankings", {"ranking": "venture50"}),
            ("equity/symbol_reference", {"symbol": "AC,IBM:US"}),
            ("equity/fundamental/income", {"symbol": "AC"}),
            ("equity/fundamental/balance", {"symbol": "AC"}),
            ("equity/fundamental/cash", {"symbol": "AC"}),
            ("equity/fundamental/dividends", {"symbol": "BNS"}),
            ("equity/fundamental/splits", {"symbol": "BNS"}),
            ("equity/calendar/earnings", {}),
            ("equity/ownership/insider_trading", {"symbol": "AC"}),
            ("equity/ownership/insider_transactions", {"symbol": "AC"}),
            ("equity/estimates/consensus", {"symbol": "AC"}),
            ("etf/search", {}),
            ("etf/info", {"symbol": "XIU"}),
            ("etf/holdings", {"symbol": "XIU"}),
            ("etf/sectors", {"symbol": "XIU"}),
            ("etf/countries", {"symbol": "XIU"}),
            ("etf/historical", {"symbol": "XIU"}),
            ("index/available", {}),
            ("index/info", {"symbol": "^TSX"}),
            ("index/historical", {"symbol": "^TSX"}),
            ("index/constituents", {"symbol": "^TSX"}),
            ("index/sectors", {"symbol": "^TSX"}),
            ("index/snapshots", {"region": "ca"}),
            ("index/documents", {"symbol": "^TSX"}),
            ("derivatives/options/chains", {"symbol": "AC"}),
            ("derivatives/options/covered_calls", {}),
            ("derivatives/futures/instruments", {}),
            ("derivatives/futures/historical", {"symbol": "CGB"}),
            ("currency/historical", {"symbol": "USDCAD"}),
            ("fixedincome/prices", {}),
            ("fixedincome/treasury_prices", {}),
            (
                "fixedincome/trades",
                {
                    "cusip": "135087U28",
                    "start_date": str(TRADE_START),
                    "end_date": str(TRADE_END),
                },
            ),
            ("markets/movers", {}),
            ("markets/trades", {"symbol": "AC"}),
            ("markets/short_interest", {"symbol": "AC"}),
        ],
    )
    def test_the_command_returns_results(self, path, params, headers):
        """CIRO rate-limits, so a failing bond trade case means it declined."""
        payload = _get(path, {**params, "provider": "tmx"}, headers).json()

        assert payload["results"]


@pytest.mark.integration
class TestListCommands:
    """The commands that answer with a bare list rather than an envelope."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("news/feed", {"symbol": "AC", "limit": 5, "fetch_body": False}),
            ("news/market", {"symbols": "AC,RY", "limit": 5, "fetch_body": False}),
            ("news/blog", {}),
            ("news/search", {"query": "bank", "limit": 5, "fetch_body": False}),
            ("derivatives/options/spreads", {"symbol": "AC", "spread_type": "both"}),
            ("derivatives/options/get_tickers", {"symbol": "AC", "expiry_list": True}),
            ("derivatives/options/get_tickers", {"symbol": "AC", "strike_list": True}),
        ],
    )
    def test_the_command_returns_a_populated_list(self, path, params, headers):
        payload = _get(path, params, headers).json()

        assert isinstance(payload, list)
        assert payload

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("derivatives/options/straddle", {"symbol": "AC"}),
            ("derivatives/options/strangle", {"symbol": "AC"}),
        ],
    )
    def test_a_strategy_answers_with_whatever_qualifies(self, path, params, headers):
        """A chain that prices no qualifying pair is an empty list, not an error."""
        payload = _get(path, params, headers).json()

        assert isinstance(payload, list)
        assert all(row["expiration"] and row["strike_1"] for row in payload)


@pytest.mark.integration
class TestChartRoutes:
    """The Plotly routes registered when openbb-charting is installed."""

    @pytest.mark.parametrize(
        "path",
        [
            "derivatives/options/smile",
            "derivatives/options/surface",
            "derivatives/options/stats",
            "derivatives/options/term_structure",
        ],
    )
    def test_the_figure_is_served(self, path, headers):
        payload = _get(path, {"symbol": "AC"}, headers).json()

        assert payload["data"]
        assert payload["layout"]
        assert payload["config"]

    def test_the_rows_are_served_instead_when_asked(self, headers):
        payload = _get(
            "derivatives/options/stats", {"symbol": "AC", "raw": True}, headers
        ).json()

        assert isinstance(payload, list)
        assert payload


@pytest.mark.integration
class TestViewRoutes:
    """The pages and file viewers the Workspace embeds."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("equity/screener_builder/view", {"theme": "dark"}),
            ("equity/asset_info/view", {"symbol": "AC"}),
            ("etf/fund_info/view", {"symbol": "XIU"}),
        ],
    )
    def test_the_page_is_rendered(self, path, params, headers):
        response = _get(path, params, headers)

        assert response.text.lstrip().startswith("<")

    def test_a_filing_is_handed_to_the_viewer(self, headers):
        filings = _get("equity/filings", {"symbol": "AC", "provider": "tmx"}, headers)
        url = next(
            f["report_url"] for f in filings.json()["results"] if f.get("report_url")
        )
        response = requests.post(
            f"{ROOT}/equity/filings_view",
            json={"url": url},
            headers=headers,
            timeout=60,
        )

        assert response.status_code == 200
        assert response.json()[0]["data_format"]["data_type"] == "pdf"

    def test_an_index_document_is_handed_to_the_viewer(self, headers):
        documents = _get(
            "index/documents", {"symbol": "^TSX", "provider": "tmx"}, headers
        )
        url = next(d["url"] for d in documents.json()["results"] if d.get("url"))
        response = requests.post(
            f"{ROOT}/index/document_view",
            json={"url": url},
            headers=headers,
            timeout=60,
        )

        assert response.status_code == 200
        assert response.json()[0]["url"]


@pytest.mark.integration
class TestUdfProtocol:
    """The UDF feed answers every endpoint TradingView calls."""

    def test_the_configuration_is_served(self, headers):
        payload = _get("udf/config", {}, headers).json()

        assert payload["supports_search"] is True
        assert payload["supported_resolutions"]

    def test_the_search_is_served(self, headers):
        payload = _get("udf/search", {"query": "bank", "limit": 5}, headers).json()

        assert isinstance(payload, list)
        assert payload[0]["ticker"]

    def test_a_symbol_resolves(self, headers):
        payload = _get("udf/symbols", {"symbol": "AC"}, headers).json()

        assert payload["ticker"] == "AC"
        assert payload["supported_resolutions"]

    def test_the_history_is_served(self, headers):
        payload = _get(
            "udf/history",
            {"symbol": "AC", "resolution": "D", "from": 0, "to": 2000000000},
            headers,
        ).json()

        assert payload["s"] == "ok"
        assert payload["t"]

    def test_the_server_time_is_served(self, headers):
        assert _get("udf/time", {}, headers).json() > 0


@pytest.mark.integration
class TestWorkspaceApp:
    """The bundled dashboard."""

    def test_the_app_is_served(self, headers):
        payload = _get("apps.json", {}, headers).json()

        assert payload[0]["tabs"]
