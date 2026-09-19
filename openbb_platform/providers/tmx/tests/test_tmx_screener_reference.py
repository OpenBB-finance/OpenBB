"""Tests for the covered call screener and symbol reference."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_tmx.models.covered_call_screener import TmxCoveredCallScreenerFetcher
from openbb_tmx.models.symbol_reference import TmxSymbolReferenceFetcher
from openbb_tmx.utils import mx

CREDS: dict = {}

SCREENER_HTML = """
<table>
<tr><th>Symbol</th><th>Serie / Strike Price</th><th>Last Price</th>
<th>Potential Total Return (%)</th><th>Premium Return (%)</th>
<th>Potential Capital Gain (%)</th><th>Bid Price</th><th>Bid Size</th>
<th>Ask Price</th><th>Ask Size</th><th>Volume</th><th>Open Int.</th></tr>
<tr><td>AC</td><td>2026-08-07 C 24.000</td><td>23.27</td><td>114</td><td>32</td>
<td>82</td><td>0.29</td><td>35</td><td>0.34</td><td>87</td><td>2</td><td>2</td></tr>
</table>
"""


class TestSeriesParsing:
    """Splitting the screener's combined series column."""

    def test_splits_expiry_and_strike(self):
        assert mx._parse_series("2026-09-18 C 310.000") == ("2026-09-18", 310.0)

    @pytest.mark.parametrize("raw", ["", None, "2026-09-18", "bad row"])
    def test_unparseable_series(self, raw):
        assert mx._parse_series(raw)[1] is None

    def test_non_numeric_strike(self):
        assert mx._parse_series("2026-09-18 C abc") == ("2026-09-18", None)

    @pytest.mark.parametrize(
        ("raw", "expected"), [(114, 1.14), (0, 0.0), (None, None), ("x", None)]
    )
    def test_percent_normalisation(self, raw, expected):
        assert mx._percent(raw) == expected


class TestCoveredCallScreener:
    """The covered call screen."""

    @pytest.fixture
    def screener(self, monkeypatch):
        """Serve the screener's posted results page."""
        seen: dict = {}

        async def fake(url, use_cache=True, accept_type="json", method="GET", **kwargs):
            seen["method"] = method
            seen["data"] = kwargs.get("data")
            return SCREENER_HTML

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)

        return seen

    async def test_rows_are_parsed(self, screener):
        rows = await TmxCoveredCallScreenerFetcher.fetch_data({}, CREDS)
        assert rows[0].symbol == "AC"
        assert rows[0].strike == 24.0
        assert rows[0].expiration.isoformat() == "2026-08-07"

    async def test_percentages_are_normalised(self, screener):
        rows = await TmxCoveredCallScreenerFetcher.fetch_data({}, CREDS)
        assert rows[0].total_return == pytest.approx(1.14)
        assert rows[0].premium_return == pytest.approx(0.32)

    async def test_the_form_is_posted(self, screener):
        await TmxCoveredCallScreenerFetcher.fetch_data(
            {"symbol": "ac", "premium_return_min": 7.5}, CREDS
        )
        assert screener["method"] == "POST"
        assert "symbol=AC" in screener["data"]
        assert "premium=7.5" in screener["data"]

    async def test_no_matches(self, monkeypatch):
        async def empty(*args, **kwargs):
            return "<html><body>no table</body></html>"

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", empty)

        with pytest.raises(EmptyDataError):
            await TmxCoveredCallScreenerFetcher.fetch_data({}, CREDS)

    async def test_unavailable_page(self, monkeypatch):
        async def empty(*args, **kwargs):
            return ""

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", empty)
        assert await mx.screen_covered_calls() == []


class TestSymbolReference:
    """Resolving symbols to their canonical form."""

    @pytest.fixture
    def reference(self, monkeypatch):
        """Serve the symbology's validation response."""

        async def fake(symbols, use_cache=True):
            return [
                {
                    "symbolstring": "AC",
                    "valid": True,
                    "symbol": "AC:CA",
                    "exchange": "TSX",
                    "exShName": "TSX",
                    "exLgName": "Toronto Stock Exchange",
                },
                {
                    "symbolstring": "ZZZZ9",
                    "valid": False,
                    "symbol": "ZZZZ9",
                    "exchange": "",
                },
            ]

        monkeypatch.setattr("openbb_tmx.utils.quotemedia.validate_symbols", fake)

    async def test_resolves_symbols(self, reference):
        rows = await TmxSymbolReferenceFetcher.fetch_data({"symbol": "AC,ZZZZ9"}, CREDS)
        assert rows[0].resolved_symbol == "AC:CA"
        assert rows[0].exchange_name == "Toronto Stock Exchange"

    async def test_marks_invalid_symbols(self, reference):
        rows = await TmxSymbolReferenceFetcher.fetch_data({"symbol": "AC,ZZZZ9"}, CREDS)
        assert rows[1].is_valid is False
        assert rows[1].exchange is None

    async def test_empty_response(self, monkeypatch):
        async def empty(symbols, use_cache=True):
            return []

        monkeypatch.setattr("openbb_tmx.utils.quotemedia.validate_symbols", empty)

        with pytest.raises(EmptyDataError):
            await TmxSymbolReferenceFetcher.fetch_data({"symbol": "AC"}, CREDS)

    async def test_single_entry_is_wrapped(self, monkeypatch):
        async def one(endpoint, tool, use_cache=True, **params):
            return {"validatesymbol": {"symbolstring": "AC", "valid": True}}

        monkeypatch.setattr("openbb_tmx.utils.quotemedia.get_datatool", one)

        from openbb_tmx.utils.quotemedia import validate_symbols

        assert len(await validate_symbols(["AC"])) == 1
