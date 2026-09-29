"""Tests for the universes the screener runs each asset type against."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pandas import DataFrame

from openbb_tmx.models.equity_screener import (
    TmxEquityScreenerFetcher,
)

CREDS: dict = {}

INDICES = DataFrame(
    [
        {
            "symbol": "^TSX",
            "name": "S&P/TSX Composite",
            "marketCap": 0.0,
            "optionable": False,
            "exchangeShortName": "TSX",
            "symbolType": "Index",
            "countryCode": "CA",
        },
        {
            "symbol": "^DP60",
            "name": "S&P/TSX 60 Dividend Points",
            "marketCap": 0.0,
            "optionable": False,
            "exchangeShortName": "TSX",
            "symbolType": "Index",
            "countryCode": "CA",
        },
    ]
)

QUOTES = [
    {
        "symbol": "^TSX",
        "longname": "S&P/TSX Composite Index",
        "currency": "CAD",
        "exchange": "TSX",
        "price": 35908.28,
        "volume": 91358589,
        "openPrice": 35759.55,
        "priceChange": 417.01,
        "percentChange": 1.174965,
        "dayHigh": 35920.13,
        "dayLow": 35724.62,
        "prevClose": 35491.27,
        "weeks52high": 37069.11,
        "weeks52low": 29201.87,
    },
    {
        "symbol": "^DP60",
        "longname": "S&P/TSX 60 Dividend Points Index",
        "currency": "CAD",
        "exchange": "TSX",
        "price": 12.36,
        "volume": 0,
        "openPrice": 12.36,
        "priceChange": 0,
        "percentChange": 0,
        "dayHigh": 12.36,
        "dayLow": 12.36,
        "prevClose": 12.36,
        "weeks52high": 12.36,
        "weeks52low": 0.08,
    },
]

FUTURES = (
    {
        "symbol": "/CGBZ6",
        "contract": "CGBZ26",
        "root": "CGB",
        "expiration": "2026-12-01",
        "name": "Ten-Year Government of Canada Bond Futures",
        "exchange": "MOE",
        "open": 115.7,
        "high": 116.53,
        "low": 115.68,
        "price": 116.47,
        "net_change": 0.78,
        "volume": 200908,
        "open_interest": 896724,
    },
    {
        "symbol": "/SXWZ6",
        "contract": "SXWZ26",
        "root": "SXW",
        "expiration": "2026-09-01",
        "name": "S&P/TSX Composite Insurance Index Futures",
        "exchange": "MOE",
        "open": None,
        "high": None,
        "low": None,
        "price": None,
        "net_change": None,
        "volume": 0,
        "open_interest": 0,
    },
    {
        "symbol": "/FAA",
        "contract": None,
        "root": "FAA",
        "name": "Share Futures",
        "exchange": "MOE",
        "volume": 0,
        "open_interest": 3140,
        "transactions": 0,
    },
)


@pytest.fixture
def indices(monkeypatch):
    """Serve a two-row index directory and its quotes."""

    async def frame(**kwargs):
        return INDICES.copy()

    async def quotes(operation, query, variables=None, **kwargs):
        wanted = set(variables["symbols"])

        return {"getQuoteForSymbols": [q for q in QUOTES if q["symbol"] in wanted]}

    monkeypatch.setattr("openbb_tmx.utils.directory.get_directory_frame", frame)
    monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", quotes)


SETTLEMENTS = {"/CGBZ6": 116.49, "/SXWZ6": 1288.4, "/FAA": 42.75}


@pytest.fixture
def futures(monkeypatch):
    """Serve the exchange's session summary and its settlement prices."""
    swept: list = []

    async def summary(use_cache=True):
        return FUTURES

    async def settlements(roots, use_cache=True):
        swept.append(sorted(roots))

        return SETTLEMENTS

    monkeypatch.setattr("openbb_tmx.utils.mx.get_futures_summary", summary)
    monkeypatch.setattr("openbb_tmx.utils.mx.get_settlement_prices", settlements)

    return swept


def _query(**kwargs):
    """Build a screener query the way the fetcher does."""
    return TmxEquityScreenerFetcher.transform_query(kwargs)


class TestDefaultSort:
    """Neither indices nor futures carry a market capitalization."""

    def test_an_index_screen_sorts_on_volume(self):
        assert _query(symbol_type="Index").sort_by == "volume"

    def test_a_future_screen_sorts_on_open_interest(self):
        assert _query(symbol_type="Future").sort_by == "open_interest"

    def test_an_equity_screen_keeps_its_market_capitalization(self):
        assert _query(symbol_type="Equity").sort_by == "market_cap"

    def test_an_explicit_sort_is_kept(self):
        assert (
            _query(symbol_type="Future", sort_by="expiration").sort_by == "expiration"
        )

    def test_the_fundamentals_are_left_to_equities(self):
        assert _query(symbol_type="Index").fundamentals is False
        assert _query(symbol_type="Equity").fundamentals is True


class TestIndexScreen:
    """An index screen is quoted over the instrument directory."""

    async def test_the_quote_is_joined_onto_the_directory(self, indices):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index"}, CREDS
        )
        found = next(r for r in rows if r.symbol == "^TSX")

        assert found.name == "S&P/TSX Composite Index"
        assert found.exchange == "TSX"
        assert found.country == "CA"
        assert found.symbol_type == "Index"
        assert found.currency == "CAD"
        assert found.price == 35908.28
        assert found.open == 35759.55
        assert found.high == 35920.13
        assert found.low == 35724.62
        assert found.prev_close == 35491.27
        assert found.net_change == 417.01
        assert found.high_52w == 37069.11
        assert found.low_52w == 29201.87
        assert found.volume == 91358589

    async def test_the_percent_change_is_normalized(self, indices):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index"}, CREDS
        )
        found = next(r for r in rows if r.symbol == "^TSX")

        assert found.price_change == pytest.approx(0.01174965)

    async def test_no_market_capitalization_is_reported(self, indices):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index"}, CREDS
        )

        assert all(r.market_cap is None for r in rows)

    async def test_the_busiest_index_leads(self, indices):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index"}, CREDS
        )

        assert [r.symbol for r in rows] == ["^TSX", "^DP60"]

    async def test_the_order_can_be_reversed(self, indices):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index", "sort_order": "ASC"}, CREDS
        )

        assert [r.symbol for r in rows] == ["^DP60", "^TSX"]

    async def test_a_bound_narrows_the_universe(self, indices):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index", "price_min": 1000}, CREDS
        )

        assert [r.symbol for r in rows] == ["^TSX"]

    async def test_the_limit_is_applied(self, indices):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index", "limit": 1}, CREDS
        )

        assert len(rows) == 1

    async def test_an_unquoted_index_keeps_its_reference(self, monkeypatch, indices):
        async def nothing(operation, query, variables=None, **kwargs):
            return {"getQuoteForSymbols": []}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", nothing)
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Index"}, CREDS
        )
        found = next(r for r in rows if r.symbol == "^TSX")

        assert found.name == "S&P/TSX Composite"
        assert found.exchange == "TSX"
        assert found.price is None

    async def test_an_empty_screen_is_reported(self, indices):
        with pytest.raises(EmptyDataError, match="No instruments matched"):
            await TmxEquityScreenerFetcher.fetch_data(
                {"symbol_type": "Index", "price_min": 10**9}, CREDS
            )


class TestFutureScreen:
    """A future screen runs against the exchange that lists them."""

    async def test_the_listed_contracts_are_returned(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future"}, CREDS
        )

        assert [r.symbol for r in rows] == ["/CGBZ6", "/FAA", "/SXWZ6"]

    async def test_a_contract_carries_its_session(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future"}, CREDS
        )
        found = next(r for r in rows if r.symbol == "/CGBZ6")

        assert found.name == "Ten-Year Government of Canada Bond Futures"
        assert found.exchange == "MOE"
        assert found.country == "CA"
        assert found.symbol_type == "Future"
        assert found.expiration.isoformat() == "2026-12-01"
        assert found.price == 116.47
        assert found.open == 115.7
        assert found.net_change == 0.78
        assert found.volume == 200908
        assert found.open_interest == 896724

    async def test_a_product_reported_at_the_root_has_no_month(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future"}, CREDS
        )
        found = next(r for r in rows if r.symbol == "/FAA")

        assert found.expiration is None
        assert found.transactions == 0
        assert found.open_interest == 3140

    async def test_the_open_interest_floor_is_applied(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future", "open_interest_min": 4000}, CREDS
        )

        assert [r.symbol for r in rows] == ["/CGBZ6"]

    async def test_the_contracts_can_be_ordered_by_month(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future", "sort_by": "expiration", "sort_order": "ASC"},
            CREDS,
        )

        assert [r.symbol for r in rows[:2]] == ["/SXWZ6", "/CGBZ6"]

    async def test_a_contract_without_the_sorted_field_is_listed_last(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future", "sort_by": "price"}, CREDS
        )

        assert [r.symbol for r in rows] == ["/CGBZ6", "/SXWZ6", "/FAA"]

    async def test_another_venue_lists_none_of_them(self, futures):
        with pytest.raises(EmptyDataError, match="No instruments matched"):
            await TmxEquityScreenerFetcher.fetch_data(
                {"symbol_type": "Future", "exchange": "TSX"}, CREDS
            )

    async def test_another_country_lists_none_of_them(self, futures):
        with pytest.raises(EmptyDataError, match="No instruments matched"):
            await TmxEquityScreenerFetcher.fetch_data(
                {"symbol_type": "Future", "country": "US"}, CREDS
            )

    async def test_an_empty_screen_is_reported(self, futures):
        with pytest.raises(EmptyDataError, match="No instruments matched"):
            await TmxEquityScreenerFetcher.fetch_data(
                {"symbol_type": "Future", "open_interest_min": 10**9}, CREDS
            )

    async def test_a_contract_that_has_not_traded_carries_its_settlement(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future"}, CREDS
        )
        found = next(r for r in rows if r.symbol == "/SXWZ6")

        assert found.price is None
        assert found.settlement_price == 1288.4

    async def test_a_traded_contract_carries_both(self, futures):
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future"}, CREDS
        )
        found = next(r for r in rows if r.symbol == "/CGBZ6")

        assert found.price == 116.47
        assert found.settlement_price == 116.49

    async def test_only_the_returned_products_are_swept(self, futures):
        await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future", "open_interest_min": 4000}, CREDS
        )

        assert futures == [["CGB"]]

    async def test_a_contract_the_exchange_has_not_settled_carries_nothing(
        self, futures, monkeypatch
    ):
        async def nothing(roots, use_cache=True):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.mx.get_settlement_prices", nothing)
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future"}, CREDS
        )

        assert all(r.settlement_price is None for r in rows)

    async def test_a_universe_without_a_product_is_not_swept(
        self, futures, monkeypatch
    ):
        async def rootless(use_cache=True):
            return ({"symbol": "/CGBZ6", "exchange": "MOE", "open_interest": 1},)

        monkeypatch.setattr("openbb_tmx.utils.mx.get_futures_summary", rootless)
        rows = await TmxEquityScreenerFetcher.fetch_data(
            {"symbol_type": "Future"}, CREDS
        )

        assert futures == []
        assert rows[0].settlement_price is None


class TestScreenerColumns:
    """The grid renders the columns each asset type publishes."""

    def test_futures_have_their_own_columns(self):
        from openbb_tmx.utils.screener_iframe import columns_for

        fields = [c["field"] for c in columns_for("Future")]

        assert "open_interest" in fields
        assert "expiration" in fields
        assert "settlement_price" in fields
        assert "market_cap" not in fields

    def test_indices_carry_their_session(self):
        from openbb_tmx.utils.screener_iframe import columns_for

        fields = [c["field"] for c in columns_for("Index")]

        assert fields[:3] == ["symbol", "name", "exchange"]
        assert "prev_close" in fields
        assert "market_cap" not in fields

    def test_a_normalized_percent_is_scaled_for_display(self):
        from openbb_tmx.utils.screener_iframe import columns_for

        columns = {c["field"]: c for c in columns_for("Equity")}

        assert "* 100" in columns["price_change"]["valueFormatter"]
        assert "* 100" in columns["change_52w"]["valueFormatter"]
        assert "* 100" not in columns["dividend_yield"]["valueFormatter"]

    def test_the_catalog_offers_open_interest_to_futures_only(self):
        from openbb_tmx.utils.screener_catalog import build_screener_catalog

        catalog = build_screener_catalog()
        defaults = catalog["asset_defaults"]

        assert any(f["param"] == "open_interest" for f in catalog["fields"])
        assert "open_interest" in defaults["Future"]["fields"]
        assert "open_interest" not in defaults["Equity"]["fields"]
        assert "market_cap" in defaults["Equity"]["fields"]

    def test_each_asset_type_sorts_on_what_it_publishes(self):
        from openbb_tmx.utils.screener_catalog import build_screener_catalog

        defaults = build_screener_catalog()["asset_defaults"]

        assert defaults["Index"]["sort_by"] == "volume"
        assert defaults["Future"]["sort_by"] == "open_interest"
        assert [s["value"] for s in defaults["Future"]["sort_fields"]][0] == (
            "open_interest"
        )

    def test_an_open_interest_bound_reaches_the_query(self):
        from openbb_tmx.utils.screener_catalog import query_from_config

        params = query_from_config(
            {
                "asset_type": "Future",
                "conditions": [
                    {
                        "param": "open_interest",
                        "operator": "between",
                        "value": [1000, 5000],
                    }
                ],
            }
        )

        assert params["open_interest_min"] == 1000
        assert params["open_interest_max"] == 5000
