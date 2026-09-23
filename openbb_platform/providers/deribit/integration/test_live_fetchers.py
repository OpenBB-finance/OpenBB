"""Run every Deribit fetcher against the live exchange.

These reach the public API and are excluded from the default run. Invoke them
with ``pytest integration -m integration``.
"""

import pytest
import pytest_asyncio

from openbb_deribit import deribit_provider

pytestmark = pytest.mark.integration

PARAMS = {
    "DeribitAnnouncements": {"limit": 3},
    "DeribitAprHistory": {"currency": "usde", "limit": 5},
    "DeribitBlockRfqTrades": {"limit": 10},
    "DeribitBookSummary": {"currency": "BTC", "kind": "future"},
    "DeribitCombos": {"currency": "BTC"},
    "DeribitCurrencies": {},
    "DeribitDeliveryPrices": {"index_name": "btc_usd", "limit": 5},
    "DeribitExpirations": {"currency": "BTC", "kind": "any"},
    "DeribitFundingChart": {"symbol": "BTC-PERPETUAL"},
    "DeribitFundingRateHistory": {"symbol": "BTC-PERPETUAL"},
    "DeribitFuturesCurve": {"symbol": "BTC"},
    "DeribitFuturesHistorical": {
        "symbol": "BTC-PERPETUAL",
        "start_date": "2026-01-01",
        "end_date": "2026-02-01",
    },
    "DeribitFuturesInfo": {"symbol": "BTC-PERPETUAL"},
    "DeribitFuturesInstruments": {},
    "DeribitHistoricalVolatility": {"currency": "BTC"},
    "DeribitIndexHistorical": {"index_name": "btc_usd", "span": "1h"},
    "DeribitIndexPrice": {"index_name": "btc_usd,eth_usd"},
    "DeribitInstruments": {"currency": "BTC", "kind": "future"},
    "DeribitOptionsChains": {"symbol": "BTC"},
    "DeribitOrderBook": {"symbol": "BTC-PERPETUAL", "depth": 5},
    "DeribitSettlements": {"currency": "BTC", "limit": 5},
    "DeribitTicker": {"symbol": "BTC-PERPETUAL"},
    "DeribitTradeVolumes": {},
    "DeribitTrades": {"symbol": "BTC-PERPETUAL", "limit": 5},
    "DeribitVolatilityIndex": {"currency": "BTC", "interval": "1d"},
}


@pytest_asyncio.fixture(autouse=True)
async def _close_sessions():
    """Leave no pooled session open behind a test."""
    yield

    from openbb_deribit.utils.session import close_sessions

    await close_sessions()


class TestLiveFetchers:
    """Every fetcher returns rows from the live exchange."""

    @pytest.mark.parametrize("name", sorted(PARAMS))
    @pytest.mark.asyncio
    async def test_returns_rows(self, name):
        """The fetcher answers with at least one row."""
        result = await deribit_provider.fetcher_dict[name].fetch_data(PARAMS[name], {})
        rows = result if isinstance(result, list) else result.model_dump()

        assert rows

    @pytest.mark.asyncio
    async def test_mark_price_history_names_a_dvol_option(self):
        """The mark price history reads one of the volatility index options."""
        from openbb_deribit.models.mark_price_history import (
            DeribitMarkPriceHistoryFetcher,
        )
        from openbb_deribit.utils.helpers import get_instruments

        options = await get_instruments("BTC", "option")
        expirations = sorted({d["expiration_timestamp"] for d in options})
        near = [
            d["instrument_name"]
            for d in options
            if d["expiration_timestamp"] in expirations[6:8]
        ]
        result = await DeribitMarkPriceHistoryFetcher.fetch_data(
            {"symbol": ",".join(near[:4])}, {}
        )

        assert result


class TestLiveRoutes:
    """The routes that answer without a model reach the live exchange."""

    @pytest.mark.asyncio
    async def test_scalars(self):
        """The small scalar endpoints answer."""
        from openbb_deribit.routers.reference import (
            contract_size,
            server_time,
            status,
        )

        assert await contract_size("BTC-PERPETUAL") > 0
        assert await server_time() > 0
        assert "locked" in await status()

    @pytest.mark.asyncio
    async def test_choice_feeds(self):
        """Every choice feed answers with entries."""
        from openbb_deribit.routers.futures import (
            curve_choices,
            perpetual_choices,
        )
        from openbb_deribit.routers.options import underlying_choices
        from openbb_deribit.routers.reference import (
            combo_choices,
            currency_choices,
            index_choices,
            instrument_choices,
        )

        for feed in (
            currency_choices(),
            index_choices(),
            index_choices(supported=True),
            instrument_choices("future"),
            combo_choices("BTC"),
            curve_choices(),
            perpetual_choices(),
            underlying_choices(),
        ):
            assert await feed

    @pytest.mark.asyncio
    async def test_funding_value(self):
        """The single funding figure answers."""
        from openbb_deribit.routers.rates import funding_value

        assert await funding_value("BTC-PERPETUAL") is not None
