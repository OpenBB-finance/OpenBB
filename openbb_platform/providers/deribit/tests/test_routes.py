"""Tests for the Deribit routes that answer without a model."""

import pytest

from openbb_deribit.routers import futures, market, options, rates, reference


class TestReference:
    """The reference routes answer the small scalar endpoints."""

    @pytest.mark.asyncio
    async def test_contract_size(self, responder, load):
        """The contract size is unwrapped from its envelope."""
        responder({"get_contract_size": load("contract_size")})

        assert await reference.contract_size("BTC-PERPETUAL") == 10.0

    @pytest.mark.asyncio
    async def test_contract_size_of_an_unlisted_instrument(self, responder):
        """An instrument the exchange answered nothing for reads as nothing."""
        responder({"get_contract_size": None})

        assert await reference.contract_size("NOPE") is None

    @pytest.mark.asyncio
    async def test_status(self, responder, load):
        """The platform status is returned as the exchange sends it."""
        responder({"status": load("status")})

        assert await reference.status() == {"locked": "false"}

    @pytest.mark.asyncio
    async def test_server_time(self, responder, load):
        """The server time is returned as milliseconds."""
        responder({"get_time": load("server_time")})

        assert await reference.server_time() > 0

    @pytest.mark.asyncio
    async def test_currency_choices(self, responder, load):
        """Currency choices come from the live listing."""
        responder({"get_currencies": load("currencies")})

        assert {"label": "Bitcoin", "value": "BTC"} in (
            await reference.currency_choices()
        )

    @pytest.mark.asyncio
    async def test_index_choices(self, responder, load):
        """Index choices come from the published names."""
        responder({"get_index_price_names": load("index_price_names")})
        feed = await reference.index_choices()

        assert {"label": "btc_usd", "value": "btc_usd"} in feed

    @pytest.mark.asyncio
    async def test_supported_index_choices(self, responder, load):
        """Asking for the supported names reads the other endpoint."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return load("supported_index_names")

        responder({"get_supported_index_names": capture})
        feed = await reference.index_choices(supported=True, kind="spot")

        assert seen == {"type": "spot"}
        assert feed

    @pytest.mark.asyncio
    async def test_instrument_choices(self, responder, load):
        """Instrument choices come from the live listing."""
        responder({"get_instruments": load("instruments_future")})
        feed = await reference.instrument_choices("future")

        assert {"label": "BTC-PERPETUAL", "value": "BTC-PERPETUAL"} in feed

    @pytest.mark.asyncio
    async def test_combo_choices(self, responder, load):
        """Combo choices come from the live listing."""
        responder({"get_combo_ids": load("combo_ids")})

        assert await reference.combo_choices("BTC")


class TestRates:
    """The rates router serves the single funding figure."""

    @pytest.mark.asyncio
    async def test_funding_value_defaults_to_a_week(self, responder, load):
        """With no span, the last week's funding is read."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return 0.00098

        responder(
            {
                "get_funding_rate_value": capture,
                "get_instruments": load("instruments_future"),
            }
        )
        value = await rates.funding_value("BTC-PERPETUAL")

        assert value == 0.00098
        assert seen["end_timestamp"] - seen["start_timestamp"] == 7 * 86400000

    @pytest.mark.asyncio
    async def test_funding_value_resolves_a_short_root(self, responder, load):
        """A shortened perpetual root reaches the exchange in full."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return 0.0

        responder(
            {
                "get_funding_rate_value": capture,
                "get_instruments": load("instruments_future"),
            }
        )
        await rates.funding_value("btc", "2026-01-01", "2026-01-08")

        assert seen["instrument_name"] == "BTC-PERPETUAL"
        assert seen["start_timestamp"] == 1767225600000


class TestDerivativeChoices:
    """The futures and options routers offer what the exchange lists."""

    @pytest.mark.asyncio
    async def test_curve_choices(self, responder, load):
        """Only underlyings with a curve are offered."""
        responder({"get_instruments": load("instruments_future")})

        assert await futures.curve_choices() == [{"label": "BTC", "value": "BTC"}]

    @pytest.mark.asyncio
    async def test_perpetual_choices(self, responder, load):
        """Every perpetual is offered by its full name."""
        responder({"get_instruments": load("instruments_future")})

        assert await futures.perpetual_choices() == [
            {"label": "BTC-PERPETUAL", "value": "BTC-PERPETUAL"}
        ]

    @pytest.mark.asyncio
    async def test_mark_price_choices(self, responder):
        """The mark price feed offers the volatility index constituents."""
        from datetime import datetime, timedelta, timezone

        from openbb_deribit.utils.helpers import to_timestamp

        now = datetime.now(timezone.utc)
        responder(
            {
                "get_instruments": lambda params: [
                    {
                        "instrument_name": f"{params['currency']}-{offset}-C",
                        "expiration_timestamp": to_timestamp(
                            now + timedelta(days=offset)
                        ),
                        "strike": 100.0,
                    }
                    for offset in (1, 29, 38)
                ]
            }
        )
        feed = await market.mark_price_choices()

        assert sorted({int(row["value"].split("-")[1]) for row in feed}) == [29, 38]

    @pytest.mark.asyncio
    async def test_underlying_choices(self, responder, load):
        """Only underlyings with listed options are offered."""
        responder({"get_instruments": load("instruments_option")})
        feed = await options.underlying_choices()

        assert {"label": "XRP_USDC", "value": "XRP_USDC"} in feed
