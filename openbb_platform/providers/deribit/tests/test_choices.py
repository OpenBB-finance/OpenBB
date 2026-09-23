"""Tests for the Deribit choice feeds."""

import pytest

from openbb_deribit.utils import choices


class TestPairing:
    """Choices are paired as a label and a value."""

    def test_defaults_the_label_to_the_value(self):
        """A value with no label is its own label."""
        assert choices._choices(["BTC"]) == [{"label": "BTC", "value": "BTC"}]

    def test_uses_a_given_label(self):
        """A named value carries its name."""
        assert choices._choices(["BTC"], {"BTC": "Bitcoin"}) == [
            {"label": "Bitcoin", "value": "BTC"}
        ]


class TestFeeds:
    """Each feed reads what the exchange lists right now."""

    @pytest.mark.asyncio
    async def test_currencies(self, responder, load):
        """Currencies are labelled by their long name."""
        responder({"get_currencies": load("currencies")})
        feed = await choices.currency_choices()

        assert {"label": "Bitcoin", "value": "BTC"} in feed
        assert [row["value"] for row in feed] == sorted(row["value"] for row in feed)

    @pytest.mark.asyncio
    async def test_index_names(self, responder, load):
        """Index names come back sorted."""
        responder({"get_index_price_names": load("index_price_names")})
        feed = await choices.index_choices()

        assert {"label": "btc_usd", "value": "btc_usd"} in feed

    @pytest.mark.asyncio
    async def test_extended_index_names(self, responder):
        """The extended listing names each index under its ``name`` member."""
        responder({"get_index_price_names": [{"name": "btc_usd"}]})
        feed = await choices.index_choices(extended=True)

        assert feed == [{"label": "btc_usd", "value": "btc_usd"}]

    @pytest.mark.asyncio
    async def test_instruments(self, responder, load):
        """Instruments are listed by their name."""
        responder({"get_instruments": load("instruments_future")})
        feed = await choices.instrument_choices("future")

        assert {"label": "BTC-PERPETUAL", "value": "BTC-PERPETUAL"} in feed

    @pytest.mark.asyncio
    async def test_perpetuals(self, responder, load):
        """Perpetuals are listed by their full instrument name."""
        responder({"get_instruments": load("instruments_future")})
        feed = await choices.perpetual_choices()

        assert feed == [{"label": "BTC-PERPETUAL", "value": "BTC-PERPETUAL"}]

    @pytest.mark.asyncio
    async def test_options_roots(self, responder, load):
        """Only underlyings with listed options are offered."""
        responder({"get_instruments": load("instruments_option")})

        assert await choices.options_root_choices() == [
            {"label": "BTC", "value": "BTC"},
            {"label": "XRP_USDC", "value": "XRP_USDC"},
        ]

    @pytest.mark.asyncio
    async def test_futures_roots(self, responder, load):
        """Only underlyings with a curve are offered."""
        responder({"get_instruments": load("instruments_future")})

        assert await choices.futures_root_choices() == [
            {"label": "BTC", "value": "BTC"}
        ]

    @pytest.mark.asyncio
    async def test_combos(self, responder, load):
        """Combo identifiers come back sorted."""
        responder({"get_combo_ids": load("combo_ids")})
        feed = await choices.combo_choices("BTC")

        assert [row["value"] for row in feed] == sorted(row["value"] for row in feed)

    @pytest.mark.asyncio
    async def test_combos_normalize_the_wildcard(self, responder):
        """The wildcard currency reaches the exchange in lower case."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return []

        responder({"get_combo_ids": capture})
        await choices.combo_choices("all", "active")

        assert seen == {"currency": "any", "state": "active"}
