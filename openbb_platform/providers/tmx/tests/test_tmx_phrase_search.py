"""Tests for multi-word symbol lookup."""

import pytest

from openbb_tmx.utils import directory

UNIVERSE = [
    {"symbol": "^COMPX:US", "name": "NASDAQ Composite", "exchangeShortName": "NSD"},
    {
        "symbol": "ONEQ:US",
        "name": "Fidelity Nasdaq Composite Tracker",
        "exchangeShortName": "ARCA",
    },
    {"symbol": "^TSX", "name": "S&P/TSX Composite Index", "exchangeShortName": "TSX"},
    {"symbol": "AC", "name": "Air Canada", "exchangeShortName": "TSX"},
]


@pytest.fixture
def vendor(monkeypatch):
    """Answer single tokens and refuse phrases, as the symbology does."""
    calls: list = []

    async def request(url, use_cache=True, **kwargs):
        from urllib.parse import parse_qs, urlparse

        query = parse_qs(urlparse(url).query)["q"][0]
        calls.append(query)

        if " " in query:
            return []

        needle = query.casefold()

        return [
            row
            for row in UNIVERSE
            if needle in f"{row['name']} {row['symbol']}".casefold()
        ]

    async def token(_tool):
        return "t"

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
    monkeypatch.setattr("openbb_tmx.utils.quotemedia.get_token", token)

    return calls


class TestPhraseLookup:
    """A phrase the symbology cannot answer is resolved from its words."""

    async def test_a_phrase_matches_on_every_word(self, vendor):
        rows = await directory.lookup_symbols("NASDAQ Composite", limit=5)

        assert [r["symbol"] for r in rows] == ["^COMPX:US", "ONEQ:US"]

    async def test_each_word_is_searched(self, vendor):
        await directory.lookup_symbols("NASDAQ Composite", limit=5)

        assert vendor[0] == "NASDAQ Composite"
        assert set(vendor[1:]) == {"NASDAQ", "Composite"}

    async def test_a_word_that_matches_nothing_excludes_every_row(self, vendor):
        rows = await directory.lookup_symbols("NASDAQ Airlines", limit=5)

        assert rows == []

    async def test_the_limit_is_respected(self, vendor):
        rows = await directory.lookup_symbols("NASDAQ Composite", limit=1)

        assert len(rows) == 1

    async def test_a_single_word_is_answered_directly(self, vendor):
        rows = await directory.lookup_symbols("Composite", limit=5)

        assert vendor == ["Composite"]
        assert len(rows) == 3

    async def test_a_phrase_that_the_vendor_answers_is_left_alone(self, monkeypatch):
        async def request(url, use_cache=True, **kwargs):
            return [UNIVERSE[3]]

        async def token(_tool):
            return "t"

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
        monkeypatch.setattr("openbb_tmx.utils.quotemedia.get_token", token)
        rows = await directory.lookup_symbols("Air Canada", limit=5)

        assert [r["symbol"] for r in rows] == ["AC"]

    async def test_a_blank_phrase_returns_nothing(self, vendor):
        assert await directory._lookup_phrase("   ", 5, None, False, True) == []
