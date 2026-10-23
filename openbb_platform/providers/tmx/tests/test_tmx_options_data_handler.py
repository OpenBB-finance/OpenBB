"""Tests for the options-chain loader the chart views share."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_tmx.utils.options import data_handler

from .conftest import UNDERLYING_PRICE, build_options_chain


@pytest.fixture(autouse=True)
def _empty_cache():
    """Keep each test from reading the previous one's chain."""
    data_handler.LOADED_SYMBOLS.clear()

    yield

    data_handler.LOADED_SYMBOLS.clear()


@pytest.fixture
def chains(monkeypatch, options_chain):
    """Serve one chain, counting how often it is fetched."""
    calls: list = []

    async def fetch(params, credentials):
        calls.append(params["symbol"])

        return options_chain

    monkeypatch.setattr(
        "openbb_tmx.models.options_chains.TmxOptionsChainsFetcher.fetch_data", fetch
    )

    return calls


class TestLoadSymbol:
    """Loading a chain once and holding it."""

    async def test_the_chain_is_returned(self, chains, options_chain):
        assert await data_handler.load_symbol("AC") is options_chain

    async def test_the_symbol_is_upper_cased(self, chains):
        await data_handler.load_symbol("ac")

        assert chains == ["AC"]
        assert "AC" in data_handler.LOADED_SYMBOLS

    async def test_a_loaded_chain_is_not_fetched_again(self, chains):
        await data_handler.load_symbol("AC")
        await data_handler.load_symbol("AC")

        assert chains == ["AC"]

    async def test_an_update_refetches(self, chains):
        await data_handler.load_symbol("AC")
        await data_handler.load_symbol("AC", update=True)

        assert chains == ["AC", "AC"]

    async def test_a_wrapped_result_is_unwrapped(self, monkeypatch, options_chain):
        """A fetcher that answers with an OBBject carries the chain in result."""
        from types import SimpleNamespace

        async def wrapped(params, credentials):
            return SimpleNamespace(result=options_chain)

        monkeypatch.setattr(
            "openbb_tmx.models.options_chains.TmxOptionsChainsFetcher.fetch_data",
            wrapped,
        )

        assert await data_handler.load_symbol("AC") is options_chain

    @pytest.mark.parametrize("error", [OpenBBError("no"), EmptyDataError("none")])
    async def test_an_unavailable_chain_is_reported(self, monkeypatch, error):
        async def failing(params, credentials):
            raise error

        monkeypatch.setattr(
            "openbb_tmx.models.options_chains.TmxOptionsChainsFetcher.fetch_data",
            failing,
        )

        with pytest.raises(OpenBBError, match="No options available for NOPE"):
            await data_handler.load_symbol("NOPE")

    async def test_a_chain_without_expirations_is_reported(self, monkeypatch):
        async def nothing(params, credentials):
            return None

        monkeypatch.setattr(
            "openbb_tmx.models.options_chains.TmxOptionsChainsFetcher.fetch_data",
            nothing,
        )

        with pytest.raises(OpenBBError, match="No options available for AC"):
            await data_handler.load_symbol("AC")


class TestExpirationChoices:
    """The expiration dropdown."""

    async def test_every_expiration_is_offered(self, chains, options_chain):
        await data_handler.load_symbol("AC")
        choices = data_handler.get_expirations("ac")

        assert [c["value"] for c in choices] == [
            str(e) for e in options_chain.expirations
        ]

    def test_an_unloaded_symbol_offers_nothing(self):
        assert data_handler.get_expirations("NOPE") == []


class TestStrikeChoices:
    """The strike dropdown."""

    async def test_the_nearest_otm_strike_leads(self, chains):
        await data_handler.load_symbol("AC")
        choices = data_handler.get_strikes("ac")

        assert choices[0] == {"label": "Nearest OTM", "value": None}

    async def test_every_strike_is_offered_with_the_underlying(self, chains):
        await data_handler.load_symbol("AC")
        choices = data_handler.get_strikes("AC")

        assert [c["value"] for c in choices[1:]] == list(build_options_chain().strikes)
        assert choices[1]["extraInfo"] == {
            "rightOfDescription": f"Underlying: ${UNDERLYING_PRICE}"
        }

    async def test_a_chain_without_a_price_offers_no_extra(self, monkeypatch):
        chain = build_options_chain()
        chain.underlying_price = []

        async def fetch(params, credentials):
            return chain

        monkeypatch.setattr(
            "openbb_tmx.models.options_chains.TmxOptionsChainsFetcher.fetch_data", fetch
        )
        await data_handler.load_symbol("AC")

        assert data_handler.get_strikes("AC")[1]["extraInfo"] == {}

    def test_an_unloaded_symbol_offers_nothing(self):
        assert data_handler.get_strikes("NOPE") == []
