"""TMX Python interface integration tests."""

from datetime import date, timedelta

import pytest
from openbb_core.app.model.obbject import OBBject

TRADE_END = date.today() - timedelta(days=1)
TRADE_START = TRADE_END - timedelta(days=30)


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb

    return None


def _call(obb, path, params):
    """Call a dotted command path on the TMX namespace."""
    command = obb.tmx

    for part in path.split("."):
        command = getattr(command, part)

    return command(**params)


@pytest.mark.integration
class TestEquity:
    """The equity namespace."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("equity.search", {"query": "bank", "provider": "tmx"}),
            ("equity.search", {"limit": 50, "provider": "tmx"}),
            ("equity.quote", {"symbol": "AC", "provider": "tmx"}),
            ("equity.profile", {"symbol": "AC", "provider": "tmx"}),
            ("equity.historical", {"symbol": "AC", "provider": "tmx"}),
            ("equity.filings", {"symbol": "AC", "provider": "tmx"}),
            ("equity.gainers", {"provider": "tmx"}),
            ("equity.rankings", {"ranking": "tsx30", "provider": "tmx"}),
            ("equity.rankings", {"ranking": "venture50", "provider": "tmx"}),
            ("equity.symbol_reference", {"symbol": "AC,IBM:US", "provider": "tmx"}),
        ],
    )
    def test_the_command_returns_results(self, path, params, obb):
        result = _call(obb, path, params)

        assert isinstance(result, OBBject)
        assert len(result.results) > 0


@pytest.mark.integration
class TestScreener:
    """Each asset type screens against the universe that lists it."""

    @pytest.mark.parametrize(
        "params",
        [
            {"exchange": "TSX", "limit": 10},
            {"symbol_type": "ETF", "limit": 10},
            {"symbol_type": "Index", "limit": 10},
            {"symbol_type": "Future", "limit": 10},
        ],
    )
    def test_the_screen_returns_results(self, params, obb):
        result = obb.tmx.equity.screener(**params, provider="tmx")

        assert isinstance(result, OBBject)
        assert len(result.results) > 0

    def test_an_index_screen_is_quoted(self, obb):
        """Indices carry no market capitalization, so the quote is the point."""
        result = obb.tmx.equity.screener(
            symbol_type="Index", sort_by="volume", limit=25, provider="tmx"
        )

        assert any(r.price for r in result.results)
        assert all(r.market_cap is None for r in result.results)

    def test_a_future_screen_lists_live_contracts(self, obb):
        """The Montreal Exchange lists them, the instrument directory does not."""
        result = obb.tmx.equity.screener(
            symbol_type="Future", sort_by="open_interest", limit=25, provider="tmx"
        )

        assert all(r.exchange == "MOE" for r in result.results)
        assert any(r.open_interest for r in result.results)
        assert any(r.expiration for r in result.results)


@pytest.mark.integration
class TestFundamentals:
    """Statements, distributions, and the corporate record."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("equity.fundamental.income", {"symbol": "AC", "provider": "tmx"}),
            ("equity.fundamental.balance", {"symbol": "AC", "provider": "tmx"}),
            ("equity.fundamental.cash", {"symbol": "AC", "provider": "tmx"}),
            ("equity.fundamental.dividends", {"symbol": "BNS", "provider": "tmx"}),
            ("equity.fundamental.splits", {"symbol": "BNS", "provider": "tmx"}),
            ("equity.calendar.earnings", {"provider": "tmx"}),
            ("equity.ownership.insider_trading", {"symbol": "AC", "provider": "tmx"}),
            (
                "equity.ownership.insider_transactions",
                {"symbol": "AC", "provider": "tmx"},
            ),
            ("equity.estimates.consensus", {"symbol": "AC", "provider": "tmx"}),
        ],
    )
    def test_the_command_returns_results(self, path, params, obb):
        result = _call(obb, path, params)

        assert isinstance(result, OBBject)
        assert len(result.results) > 0


@pytest.mark.integration
class TestFundsAndIndices:
    """The fund universe and the index family."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("etf.search", {"provider": "tmx"}),
            ("etf.info", {"symbol": "XIU", "provider": "tmx"}),
            ("etf.holdings", {"symbol": "XIU", "provider": "tmx"}),
            ("etf.sectors", {"symbol": "XIU", "provider": "tmx"}),
            ("etf.countries", {"symbol": "XIU", "provider": "tmx"}),
            ("etf.historical", {"symbol": "XIU", "provider": "tmx"}),
            ("index.available", {"provider": "tmx"}),
            ("index.info", {"symbol": "^TSX", "provider": "tmx"}),
            ("index.historical", {"symbol": "^TSX", "provider": "tmx"}),
            ("index.constituents", {"symbol": "^TSX", "provider": "tmx"}),
            ("index.sectors", {"symbol": "^TSX", "provider": "tmx"}),
            ("index.snapshots", {"region": "ca", "provider": "tmx"}),
            ("index.documents", {"symbol": "^TSX", "provider": "tmx"}),
        ],
    )
    def test_the_command_returns_results(self, path, params, obb):
        result = _call(obb, path, params)

        assert isinstance(result, OBBject)
        assert len(result.results) > 0


@pytest.mark.integration
class TestMarkets:
    """Market breadth, time and sales, and short interest."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("markets.movers", {"provider": "tmx"}),
            ("markets.trades", {"symbol": "AC", "provider": "tmx"}),
            ("markets.short_interest", {"symbol": "AC", "provider": "tmx"}),
        ],
    )
    def test_the_command_returns_results(self, path, params, obb):
        result = _call(obb, path, params)

        assert isinstance(result, OBBject)
        assert len(result.results) > 0


@pytest.mark.integration
class TestDerivativesAndCurrency:
    """The Montreal Exchange universe and currency history."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("derivatives.futures.instruments", {"provider": "tmx"}),
            ("derivatives.futures.historical", {"symbol": "CGB", "provider": "tmx"}),
            ("derivatives.options.covered_calls", {"provider": "tmx"}),
            ("currency.historical", {"symbol": "USDCAD", "provider": "tmx"}),
        ],
    )
    def test_the_command_returns_results(self, path, params, obb):
        result = _call(obb, path, params)

        assert isinstance(result, OBBject)
        assert len(result.results) > 0


@pytest.mark.integration
class TestFixedIncome:
    """The CIRO bond master and reported trades."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("fixedincome.prices", {"provider": "tmx"}),
            ("fixedincome.treasury_prices", {"provider": "tmx"}),
            (
                "fixedincome.trades",
                {
                    "cusip": "135087U28",
                    "start_date": TRADE_START,
                    "end_date": TRADE_END,
                    "provider": "tmx",
                },
            ),
        ],
    )
    def test_the_command_returns_results(self, path, params, obb):
        """CIRO rate-limits, so a failing trades case means it declined."""
        result = _call(obb, path, params)

        assert isinstance(result, OBBject)
        assert len(result.results) > 0


@pytest.mark.integration
class TestNews:
    """The newsroom feeds."""

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("news.feed", {"symbol": "AC", "limit": 5, "fetch_body": False}),
            (
                "news.market",
                {"symbols": "AC,RY", "limit": 5, "fetch_body": False},
            ),
            ("news.blog", {}),
            ("news.search", {"query": "bank", "limit": 5, "fetch_body": False}),
        ],
    )
    def test_the_command_returns_articles(self, path, params, obb):
        result = _call(obb, path, params)

        assert isinstance(result, list)
        assert result
        assert result[0]["title"]

    def test_an_article_carries_its_body(self, obb):
        articles = obb.tmx.news.feed(symbol="AC", limit=3, fetch_body=True)

        assert any(article.get("body") for article in articles)


@pytest.mark.integration
class TestOptionsAnalysis:
    """Strategy pricing over the loaded chain, answered as plain rows."""

    def test_the_spreads_are_priced(self, obb):
        rows = obb.tmx.derivatives.options.spreads(symbol="AC", spread_type="both")

        assert isinstance(rows, list)
        assert rows

    @pytest.mark.parametrize(
        ("path", "params"),
        [
            ("derivatives.options.straddle", {"symbol": "AC"}),
            ("derivatives.options.strangle", {"symbol": "AC"}),
        ],
    )
    def test_a_strategy_answers_with_whatever_qualifies(self, path, params, obb):
        """A chain that prices no qualifying pair is an empty list, not an error."""
        rows = _call(obb, path, params)

        assert isinstance(rows, list)
        assert all(row["expiration"] and row["strike_1"] for row in rows)

    @pytest.mark.parametrize("expiry_list", [True, False])
    def test_the_dropdown_choices_are_offered(self, expiry_list, obb):
        choices = obb.tmx.derivatives.options.get_tickers(
            symbol="AC", expiry_list=expiry_list, strike_list=not expiry_list
        )

        assert isinstance(choices, list)
        assert choices[0]["label"]


@pytest.mark.integration
class TestOptionsChains:
    """The chain covers every expiry, with greeks."""

    @pytest.mark.parametrize("symbol", ["AC", "AAPL:US"])
    def test_the_chain_carries_its_greeks(self, symbol, obb):
        result = obb.tmx.derivatives.options.chains(symbol=symbol, provider="tmx")

        assert isinstance(result, OBBject)
        assert len(result.results.contract_symbol) > 0
        assert any(d is not None for d in result.results.delta)
        assert any(v is not None for v in result.results.implied_volatility)


@pytest.mark.integration
class TestSymbology:
    """Every prefix and suffix the quote feed addresses."""

    @pytest.mark.parametrize(
        "symbol",
        [
            "AC",
            "IBM:US",
            "AIR:PA",
            "ASML:AS",
            "SAP:DB",
            "$USDCAD",
            "^TSX",
            "/CGB",
            "~BTCUSD:US",
        ],
    )
    def test_history_resolves_across_markets(self, symbol, obb):
        result = obb.tmx.equity.historical(symbol=symbol, provider="tmx")

        assert isinstance(result, OBBject)
        assert len(result.results) > 0

    def test_an_option_contract_resolves(self, obb):
        """A contract is addressed by the symbol the chain publishes."""
        chain = obb.tmx.derivatives.options.chains(symbol="AC", provider="tmx")
        contract = chain.results.contract_symbol[0]
        result = obb.tmx.equity.quote(symbol=contract, provider="tmx")

        assert isinstance(result, OBBject)
        assert result.results[0].last_price is not None
