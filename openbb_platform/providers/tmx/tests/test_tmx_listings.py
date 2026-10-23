"""Tests for the Montreal Exchange listing metadata."""

import pytest

from openbb_tmx.utils import mx

LIST_HTML = """
<table><tr><th>Name of Underlying Instrument</th><th>Option Symbol</th><th>Underlying Symbol</th></tr>
<tr><td>Air Canada</td><td>AC</td><td>AC</td></tr>
<tr><td>National Bank of Canada</td><td>NA</td><td>NA</td></tr>
<tr><td>ATCO Ltd.</td><td>ACO</td><td>ACO.X</td></tr></table>
<table><tr><th>Name of Underlying Instrument</th><th>Option Symbol</th><th>Underlying Symbol</th></tr>
<tr><td>Apple CDR</td><td>AAPL</td><td>AAPL</td></tr></table>
<table><tr><th>Name of Underlying Instrument</th><th>Option Symbol</th><th>Underlying Symbol</th></tr>
<tr><td>Sprott Physical Gold</td><td>PHYS</td><td>PHYS</td></tr></table>
<table><tr><th>Name of Underlying Instrument</th><th>Option Symbol</th><th>Underlying Symbol</th></tr>
<tr><td>iShares S&amp;P/TSX 60</td><td>XIU</td><td>XIU</td></tr></table>
<table><tr><th>Name of Underlying Instrument</th><th>Option Symbol</th><th>Underlying Symbol</th></tr>
<tr><td>US Dollar</td><td>USX</td><td>USX</td></tr></table>
<table><tr><th>Name of Underlying Instrument</th><th>Option Symbol</th><th>Underlying Symbol</th></tr>
<tr><td>S&amp;P/TSX 60 Index</td><td>SXO</td><td>TX60</td></tr></table>
<table><tr><th>Name of Underlying Instrument</th><th>Option Symbol</th><th>Underlying Symbol</th></tr>
<tr><td>Air Canada</td><td>AC</td><td>AC</td></tr>
<tr><td>iShares S&amp;P/TSX 60</td><td>XIU</td><td>XIU</td></tr></table>
"""


@pytest.fixture
def listings(monkeypatch):
    """Serve the published options list."""

    async def fake(url, use_cache=True, accept_type="json", **kwargs):
        return LIST_HTML

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
    mx.get_options_listings.cache_clear()


class TestOptionsListings:
    """Reading the per-class listing tables."""

    async def test_class_comes_from_the_table(self, listings):
        rows = await mx.get_options_listings()
        assert rows["AC"]["asset_class"] == "equity_option"
        assert rows["AAPL"]["asset_class"] == "cdr_option"
        assert rows["PHYS"]["asset_class"] == "cef_option"
        assert rows["XIU"]["asset_class"] == "etf_option"
        assert rows["USX"]["asset_class"] == "currency_option"
        assert rows["SXO"]["asset_class"] == "index_option"

    async def test_underlying_symbol_differs_from_the_option_symbol(self, listings):
        rows = await mx.get_options_listings()
        assert rows["ACO"]["underlying_symbol"] == "ACO.X"
        assert rows["SXO"]["underlying_symbol"] == "TX60"

    async def test_weekly_tab_marks_the_classes_it_lists(self, listings):
        rows = await mx.get_options_listings()
        assert rows["AC"]["has_weeklies"] is True
        assert rows["XIU"]["has_weeklies"] is True
        assert rows["ACO"]["has_weeklies"] is False

    async def test_names_are_carried(self, listings):
        rows = await mx.get_options_listings()
        assert rows["AC"]["name"] == "Air Canada"

    async def test_unavailable_list_is_not_fatal(self, monkeypatch):
        async def boom(*args, **kwargs):
            raise RuntimeError("offline")

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", boom)
        mx.get_options_listings.cache_clear()
        assert await mx.get_options_listings() == {}


class TestExpiryCycles:
    """Reading the published expiry cycle document."""

    def test_cycle_names(self):
        assert mx.CYCLE_NAMES["S"] == "standard"
        assert mx.CYCLE_NAMES["SC"] == "short"

    async def test_unavailable_document_is_not_fatal(self, monkeypatch):
        async def boom(*args, **kwargs):
            raise RuntimeError("offline")

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", boom)
        mx.get_expiry_cycles.cache_clear()
        assert await mx.get_expiry_cycles() == {}

    def test_rows_are_read_from_the_document(self, monkeypatch):
        class Page:
            @staticmethod
            def extract_tables():
                return [
                    [
                        [
                            "Name of Underlying",
                            "Symbol",
                            "Cycle",
                            "",
                            "Long",
                            "",
                            "Weeklies",
                        ],
                        ["Air Canada", "AC", "S", "", "X", "", "X"],
                        ["Aurora Cannabis Inc.", "ACB", "SC", "", "", "", ""],
                        [None, None, None],
                        ["short", "row"],
                    ]
                ]

        class Document:
            pages = [Page()]

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        monkeypatch.setattr("pdfplumber.open", lambda _: Document())
        rows = mx._parse_cycles(b"%PDF-")

        assert rows["AC"] == {
            "name": "Air Canada",
            "expiry_cycle": "standard",
            "has_long_term": True,
            "has_weeklies": True,
        }
        assert rows["ACB"]["expiry_cycle"] == "short"
        assert rows["ACB"]["has_weeklies"] is False
        assert "Symbol" not in rows


SCREENER_HTML = """
<table><tr><th>Symbol</th><th>Serie / Strike Price</th><th>Last Price</th>
<th>Potential Total Return (%)</th><th>Premium Return (%)</th>
<th>Potential Capital Gain (%)</th><th>Bid Price</th><th>Bid Size</th>
<th>Ask Price</th><th>Ask Size</th><th>Volume</th><th>Open Int.</th></tr>
<tr><td>NA</td><td>2026-09-18 C 235.000</td><td>227.4</td><td>36</td><td>14</td>
<td>22</td><td>4.750</td><td>20</td><td>5.000</td><td>20</td><td>0</td>
<td>146</td></tr>
<tr><td>RY</td><td>2026-09-18 C 310.000</td><td>295.01</td><td>39</td><td>6</td>
<td>33</td><td>2.940</td><td>20</td><td>3.150</td><td>35</td><td>0</td>
<td>1132</td></tr></table>
"""


class TestNationalBankSymbol:
    """The literal symbol 'NA' survives the table parsers."""

    async def test_the_options_list_keeps_it(self, listings):
        rows = await mx.get_options_listings()

        assert rows["NA"]["name"] == "National Bank of Canada"
        assert rows["NA"]["underlying_symbol"] == "NA"

    async def test_the_covered_call_screener_keeps_it(self, monkeypatch):
        async def fake(url, use_cache=True, accept_type="json", **kwargs):
            return SCREENER_HTML

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        rows = await mx.screen_covered_calls()

        assert [r["symbol"] for r in rows] == ["NA", "RY"]
        assert rows[0]["open_interest"] == 146


class TestUnderlyingPrices:
    """The screener's own last price column is filled from the quote feed."""

    SCREEN = """
<table><tr><th>Symbol</th><th>Serie / Strike Price</th><th>Last Price</th>
<th>Potential Total Return (%)</th><th>Premium Return (%)</th>
<th>Potential Capital Gain (%)</th><th>Bid Price</th><th>Bid Size</th>
<th>Ask Price</th><th>Ask Size</th><th>Volume</th><th>Open Int.</th></tr>
<tr><td>RCI</td><td>2027-07-16 C 55.000</td><td>0</td><td>22</td><td>8</td>
<td>14</td><td>1.00</td><td>1</td><td>0</td><td>0</td><td>0</td><td>10</td></tr>
</table>
"""

    @pytest.fixture
    def screen(self, monkeypatch):
        """Serve one contract whose last price is published as zero."""

        async def request(url, use_cache=True, accept_type="json", **kwargs):
            return self.SCREEN

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
        mx.get_options_listings.cache_clear()

    async def test_an_option_root_resolves_to_its_listing(self, screen, monkeypatch):
        async def listings(use_cache=True):
            return {"RCI": {"underlying_symbol": "RCI.B", "name": "Rogers"}}

        async def quote(operation, query, variables, **kwargs):
            assert variables["symbols"] == ["RCI.B"]
            return {"getQuoteForSymbols": [{"symbol": "RCI.B", "price": 46.2}]}

        monkeypatch.setattr(mx, "get_options_listings", listings)
        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", quote)
        rows = await mx.screen_covered_calls()

        assert rows[0]["underlying_price"] == 46.2

    async def test_a_zero_quote_is_not_published_as_a_price(self, screen, monkeypatch):
        async def listings(use_cache=True):
            return {}

        async def quote(operation, query, variables, **kwargs):
            return {"getQuoteForSymbols": []}

        monkeypatch.setattr(mx, "get_options_listings", listings)
        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", quote)
        rows = await mx.screen_covered_calls()

        assert rows[0]["underlying_price"] is None
        assert rows[0]["ask"] is None
        assert rows[0]["ask_size"] is None

    async def test_a_failing_quote_leaves_the_price_unset(self, screen, monkeypatch):
        async def listings(use_cache=True):
            return {}

        async def boom(*args, **kwargs):
            raise RuntimeError("down")

        monkeypatch.setattr(mx, "get_options_listings", listings)
        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", boom)
        rows = await mx.screen_covered_calls()

        assert rows[0]["underlying_price"] is None

    async def test_no_rows_asks_for_no_quotes(self, monkeypatch):
        async def request(url, use_cache=True, accept_type="json", **kwargs):
            return "<table><tr><th>Other</th></tr></table>"

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)

        assert await mx.screen_covered_calls() == []
