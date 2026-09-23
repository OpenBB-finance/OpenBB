"""Tests for the Deribit models."""

from datetime import date, datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_deribit.models.announcements import DeribitAnnouncementsFetcher
from openbb_deribit.models.apr_history import DeribitAprHistoryFetcher
from openbb_deribit.models.block_rfq_trades import DeribitBlockRfqTradesFetcher
from openbb_deribit.models.book_summary import DeribitBookSummaryFetcher
from openbb_deribit.models.combos import DeribitCombosFetcher
from openbb_deribit.models.currencies import DeribitCurrenciesFetcher
from openbb_deribit.models.delivery_prices import DeribitDeliveryPricesFetcher
from openbb_deribit.models.expirations import DeribitExpirationsFetcher
from openbb_deribit.models.funding_chart import DeribitFundingChartFetcher
from openbb_deribit.models.funding_rate_history import (
    DeribitFundingRateHistoryFetcher,
)
from openbb_deribit.models.futures_curve import DeribitFuturesCurveFetcher
from openbb_deribit.models.futures_historical import DeribitFuturesHistoricalFetcher
from openbb_deribit.models.futures_info import DeribitFuturesInfoFetcher
from openbb_deribit.models.futures_instruments import (
    DeribitFuturesInstrumentsFetcher,
)
from openbb_deribit.models.historical_volatility import (
    DeribitHistoricalVolatilityFetcher,
)
from openbb_deribit.models.index_historical import DeribitIndexHistoricalFetcher
from openbb_deribit.models.index_price import DeribitIndexPriceFetcher
from openbb_deribit.models.instruments import DeribitInstrumentsFetcher
from openbb_deribit.models.order_book import DeribitOrderBookFetcher
from openbb_deribit.models.settlements import DeribitSettlementsFetcher
from openbb_deribit.models.ticker import DeribitTickerFetcher
from openbb_deribit.models.trade_volumes import DeribitTradeVolumesFetcher
from openbb_deribit.models.trades import DeribitTradesFetcher
from openbb_deribit.models.volatility_index import DeribitVolatilityIndexFetcher


async def run(fetcher, params, responder, mapping):
    """Run one fetcher against canned payloads."""
    responder(mapping)

    return await fetcher.fetch_data(params, {})


class TestCurrencies:
    """Currencies are returned sorted and typed."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Every currency is returned, in alphabetical order."""
        rows = await run(
            DeribitCurrenciesFetcher,
            {},
            responder,
            {"get_currencies": load("currencies")},
        )

        assert [row.currency for row in rows] == sorted(row.currency for row in rows)
        assert rows[0].currency_long
        assert rows[0].decimals is not None

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """An empty listing is an error, not an empty table."""
        with pytest.raises(EmptyDataError):
            await run(DeribitCurrenciesFetcher, {}, responder, {"get_currencies": []})


class TestInstruments:
    """Instruments are returned with the perpetual sentinel dropped."""

    @pytest.mark.asyncio
    async def test_by_currency(self, responder, load):
        """A currency and kind reads the whole listing."""
        rows = await run(
            DeribitInstrumentsFetcher,
            {"currency": "BTC", "kind": "future"},
            responder,
            {"get_instruments": load("instruments_future")},
        )

        assert len(rows) == 13
        assert all(row.kind == "future" for row in rows)

    @pytest.mark.asyncio
    async def test_perpetual_has_no_expiration(self, responder, load):
        """The year-3000 sentinel reads as no expiration at all."""
        rows = await run(
            DeribitInstrumentsFetcher,
            {"symbol": "BTC-PERPETUAL"},
            responder,
            {"get_instrument": load("instrument")},
        )

        assert rows[0].symbol == "BTC-PERPETUAL"
        assert rows[0].expiration_timestamp is None
        assert isinstance(rows[0].creation_timestamp, datetime)

    @pytest.mark.asyncio
    async def test_options_carry_strikes(self, responder, load):
        """An option listing carries its strike and type."""
        rows = await run(
            DeribitInstrumentsFetcher,
            {"currency": "BTC", "kind": "option"},
            responder,
            {"get_instruments": load("instruments_option")},
        )

        assert all(row.strike for row in rows)
        assert {row.option_type for row in rows} == {"call", "put"}

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No matching instrument is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitInstrumentsFetcher,
                {"currency": "BTC"},
                responder,
                {"get_instruments": []},
            )


class TestExpirations:
    """Expirations are flattened to one row per currency, kind, and date."""

    @pytest.mark.asyncio
    async def test_grouped_shape(self, responder, load):
        """The grouped response yields one row per listed expiration."""
        rows = await run(
            DeribitExpirationsFetcher,
            {"currency": "grouped", "kind": "any"},
            responder,
            {"get_expirations": load("expirations_grouped")},
        )

        assert rows
        assert {row.currency for row in rows} == {"BTC", "ETH", "USDC"}
        assert {row.kind for row in rows} == {"future", "option"}

    @pytest.mark.asyncio
    async def test_flat_shape(self, responder, load):
        """The pooled response is read under the queried currency."""
        rows = await run(
            DeribitExpirationsFetcher,
            {"currency": "any", "kind": "any"},
            responder,
            {"get_expirations": load("expirations_flat")},
        )

        assert {row.currency for row in rows} == {"ANY"}

    @pytest.mark.asyncio
    async def test_perpetual_has_no_date(self, responder):
        """A perpetual code carries a code but no expiration date."""
        rows = await run(
            DeribitExpirationsFetcher,
            {"currency": "BTC", "kind": "future"},
            responder,
            {"get_expirations": {"btc": {"future": ["PERPETUAL", "25DEC26"]}}},
        )

        perpetual = next(row for row in rows if row.code == "PERPETUAL")

        assert perpetual.expiration is None
        assert rows[0].expiration == date(2026, 12, 25)

    @pytest.mark.asyncio
    async def test_empty_response(self, responder):
        """An empty response is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitExpirationsFetcher,
                {"currency": "BTC", "kind": "future"},
                responder,
                {"get_expirations": {}},
            )

    @pytest.mark.asyncio
    async def test_all_currencies_empty(self, responder):
        """A response whose currencies list nothing is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitExpirationsFetcher,
                {"currency": "BTC", "kind": "future"},
                responder,
                {"get_expirations": {"btc": {"future": []}}},
            )


class TestCombos:
    """Combos are flattened to one row per leg."""

    @pytest.mark.asyncio
    async def test_by_currency(self, responder, load):
        """Every leg of every combo is a row."""
        payload = load("combos")
        rows = await run(
            DeribitCombosFetcher,
            {"currency": "BTC"},
            responder,
            {"get_combos": payload},
        )

        assert len(rows) == sum(len(combo["legs"]) for combo in payload)
        assert rows[0].leg
        assert isinstance(rows[0].creation_timestamp, datetime)

    @pytest.mark.asyncio
    async def test_by_id(self, responder, load):
        """A named combo reads its own legs."""
        rows = await run(
            DeribitCombosFetcher,
            {"combo_id": "BTC-STRG-30OCT26-66000_90000"},
            responder,
            {"get_combo_details": load("combo_details")},
        )

        assert {row.combo_id for row in rows} == {"BTC-STRG-30OCT26-66000_90000"}

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No matching combo is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitCombosFetcher,
                {"currency": "BTC"},
                responder,
                {"get_combos": []},
            )


class TestAnnouncements:
    """Announcements are returned newest first."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each announcement carries a publication date and a title."""
        rows = await run(
            DeribitAnnouncementsFetcher,
            {"limit": 3},
            responder,
            {"get_announcements": load("announcements")},
        )

        assert [row.date for row in rows] == sorted(
            (row.date for row in rows), reverse=True
        )
        assert all(row.title for row in rows)

    @pytest.mark.asyncio
    async def test_start_date_is_sent(self, responder, load):
        """A start date reaches the exchange as a timestamp."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return load("announcements")

        await run(
            DeribitAnnouncementsFetcher,
            {"start_date": "2026-01-01", "limit": 3},
            responder,
            {"get_announcements": capture},
        )

        assert seen["start_timestamp"] == 1767225600000

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No announcements over the span is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitAnnouncementsFetcher,
                {},
                responder,
                {"get_announcements": []},
            )


class TestBookSummary:
    """Book summaries normalize the percent the exchange publishes."""

    @pytest.mark.asyncio
    async def test_by_currency(self, responder, load):
        """A currency reads every instrument's summary."""
        rows = await run(
            DeribitBookSummaryFetcher,
            {"currency": "BTC", "kind": "future"},
            responder,
            {"get_book_summary_by_currency": load("book_summary_future")},
        )

        assert len(rows) == 13
        assert [row.symbol for row in rows] == sorted(row.symbol for row in rows)

    @pytest.mark.asyncio
    async def test_by_instrument(self, responder, load):
        """A named instrument reads only its own summary."""
        rows = await run(
            DeribitBookSummaryFetcher,
            {"symbol": "BTC-PERPETUAL"},
            responder,
            {
                "get_book_summary_by_instrument": load("book_summary_instrument"),
                "get_instruments": load("instruments_future"),
            },
        )

        assert len(rows) == 1
        assert rows[0].symbol == "BTC-PERPETUAL"

    @pytest.mark.asyncio
    async def test_percent_is_left_in_percent_units(self, responder, load):
        """A price change is kept as the exchange publishes it."""
        payload = load("book_summary_future")
        payload[0]["price_change"] = 1.25
        rows = await run(
            DeribitBookSummaryFetcher,
            {"currency": "BTC"},
            responder,
            {"get_book_summary_by_currency": payload},
        )
        changed = next(
            row for row in rows if row.symbol == payload[0]["instrument_name"]
        )

        assert changed.change_percent == 1.25

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No summary is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitBookSummaryFetcher,
                {"currency": "BTC"},
                responder,
                {"get_book_summary_by_currency": []},
            )


class TestOrderBook:
    """The book is returned one row per resting level."""

    @pytest.mark.asyncio
    async def test_levels(self, responder, load):
        """Both sides are flattened, numbered from the top of the book."""
        payload = load("order_book")
        rows = await run(
            DeribitOrderBookFetcher,
            {"symbol": "BTC-PERPETUAL", "depth": 5},
            responder,
            {
                "get_order_book": payload,
                "get_instruments": load("instruments_future"),
            },
        )

        assert len(rows) == len(payload["bids"]) + len(payload["asks"])
        assert {row.side for row in rows} == {"bid", "ask"}
        assert [row.level for row in rows if row.side == "bid"] == list(
            range(1, len(payload["bids"]) + 1)
        )

    @pytest.mark.asyncio
    async def test_by_instrument_id(self, responder, load):
        """A numeric identifier reads the same book."""
        rows = await run(
            DeribitOrderBookFetcher,
            {"instrument_id": 210838, "depth": 5},
            responder,
            {"get_order_book_by_instrument_id": load("order_book")},
        )

        assert rows[0].symbol == "BTC-PERPETUAL"

    @pytest.mark.asyncio
    async def test_needs_a_selector(self):
        """A query naming neither a symbol nor an identifier is rejected."""
        with pytest.raises(OpenBBError, match="symbol or an instrument ID"):
            DeribitOrderBookFetcher.transform_query({})

    @pytest.mark.asyncio
    async def test_no_book(self, responder):
        """No book at all is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitOrderBookFetcher,
                {"instrument_id": 1},
                responder,
                {"get_order_book_by_instrument_id": {}},
            )

    @pytest.mark.asyncio
    async def test_empty_book(self, responder):
        """A book with no resting orders is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitOrderBookFetcher,
                {"instrument_id": 1},
                responder,
                {
                    "get_order_book_by_instrument_id": {
                        "instrument_name": "X",
                        "bids": [],
                        "asks": [],
                    }
                },
            )


class TestTicker:
    """The ticker is flattened and its percents normalized."""

    @pytest.mark.asyncio
    async def test_row(self, responder, load):
        """The quote, statistics, and greeks land on one row."""
        rows = await run(
            DeribitTickerFetcher,
            {"symbol": "BTC-PERPETUAL"},
            responder,
            {
                "ticker": load("ticker_future"),
                "get_instruments": load("instruments_future"),
            },
        )

        assert rows[0].symbol == "BTC-PERPETUAL"
        assert rows[0].volume is not None
        assert isinstance(rows[0].timestamp, datetime)

    @pytest.mark.asyncio
    async def test_short_root_resolves(self, responder, load):
        """A shortened perpetual root reaches the exchange in full."""
        seen: list = []

        def capture(params):
            seen.append(params["instrument_name"])

            return load("ticker_future")

        await run(
            DeribitTickerFetcher,
            {"symbol": "btc"},
            responder,
            {"ticker": capture, "get_instruments": load("instruments_future")},
        )

        assert seen == ["BTC-PERPETUAL"]

    @pytest.mark.asyncio
    async def test_empty(self, responder, load):
        """No quote at all is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitTickerFetcher,
                {"symbol": "BTC-PERPETUAL"},
                responder,
                {"ticker": {}, "get_instruments": load("instruments_future")},
            )


class TestTrades:
    """Trades are returned newest first, with the option volatility decimalized."""

    @pytest.mark.asyncio
    async def test_by_instrument(self, responder, load):
        """A named instrument reads its own prints."""
        rows = await run(
            DeribitTradesFetcher,
            {"symbol": "BTC-PERPETUAL", "limit": 5},
            responder,
            {
                "get_last_trades_by_instrument": load("trades_instrument"),
                "get_instruments": load("instruments_future"),
            },
        )

        assert rows
        assert [row.timestamp for row in rows] == sorted(
            (row.timestamp for row in rows), reverse=True
        )

    @pytest.mark.asyncio
    async def test_by_currency_needs_a_kind(self, responder, load):
        """A currency query sends the kind the exchange insists on."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return load("trades_currency")

        await run(
            DeribitTradesFetcher,
            {"currency": "BTC", "kind": "option", "limit": 5},
            responder,
            {"get_last_trades_by_currency": capture},
        )

        assert seen["kind"] == "option"

    @pytest.mark.asyncio
    async def test_timed_variant(self, responder, load):
        """Naming both ends of a span switches to the timed endpoint."""
        rows = await run(
            DeribitTradesFetcher,
            {
                "currency": "BTC",
                "kind": "option",
                "start_date": "2026-09-01",
                "end_date": "2026-09-02",
            },
            responder,
            {"get_last_trades_by_currency_and_time": load("trades_currency")},
        )

        assert rows

    @pytest.mark.asyncio
    async def test_timed_variant_by_instrument(self, responder, load):
        """A named instrument over a span uses the timed endpoint too."""
        rows = await run(
            DeribitTradesFetcher,
            {
                "symbol": "BTC-PERPETUAL",
                "start_date": "2026-09-01",
                "end_date": "2026-09-02",
            },
            responder,
            {
                "get_last_trades_by_instrument_and_time": load("trades_instrument"),
                "get_instruments": load("instruments_future"),
            },
        )

        assert rows

    @pytest.mark.asyncio
    async def test_ascending(self, responder, load):
        """Asking for ascending order returns the oldest print first."""
        rows = await run(
            DeribitTradesFetcher,
            {"currency": "BTC", "kind": "option", "sorting": "asc"},
            responder,
            {"get_last_trades_by_currency": load("trades_currency")},
        )

        assert [row.timestamp for row in rows] == sorted(row.timestamp for row in rows)

    @pytest.mark.asyncio
    async def test_option_volatility_is_left_in_percent_units(self, responder, load):
        """An option print's volatility is kept as the exchange publishes it."""
        payload = load("trades_currency")
        payload["trades"][0]["iv"] = 42.0
        rows = await run(
            DeribitTradesFetcher,
            {"currency": "BTC", "kind": "option"},
            responder,
            {"get_last_trades_by_currency": payload},
        )

        assert 42.0 in {row.iv for row in rows}

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No prints is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitTradesFetcher,
                {"currency": "BTC"},
                responder,
                {"get_last_trades_by_currency": {"trades": []}},
            )

    @pytest.mark.asyncio
    async def test_routed_spot_by_currency_is_explained(self, responder):
        """The exchange's routed-spot refusal is rewritten as an explanation."""

        def refuse(params):
            raise OpenBBError(
                "Deribit returned an error for public/get_last_trades_by_currency"
                " -> not_supported_for_coinbase_routed_spot"
            )

        with pytest.raises(OpenBBError, match="routes to Coinbase"):
            await run(
                DeribitTradesFetcher,
                {"currency": "BTC"},
                responder,
                {"get_last_trades_by_currency": refuse},
            )

    @pytest.mark.asyncio
    async def test_other_errors_by_currency_are_not_rewritten(self, responder):
        """Any other failure is passed through untouched."""

        def refuse(params):
            raise OpenBBError("some other problem entirely")

        with pytest.raises(OpenBBError, match="some other problem"):
            await run(
                DeribitTradesFetcher,
                {"currency": "BTC"},
                responder,
                {"get_last_trades_by_currency": refuse},
            )

    @pytest.mark.asyncio
    async def test_routed_spot_by_symbol_is_explained(
        self, monkeypatch, responder, load
    ):
        """A routed spot pair named by symbol is explained, not left as a code."""
        responder({"get_instruments": load("instruments_future")})

        async def _gather(calls, use_cache=True):
            return [
                OpenBBError(
                    "Deribit returned an error for"
                    " public/get_last_trades_by_instrument ->"
                    " not_supported_for_coinbase_routed_spot"
                )
            ]

        monkeypatch.setattr("openbb_deribit.utils.client.gather", _gather)

        with pytest.raises(OpenBBError, match="routes to Coinbase"):
            await DeribitTradesFetcher.fetch_data({"symbol": "BTC_USDC"}, {})

    @pytest.mark.asyncio
    async def test_other_symbol_failures_fall_through_to_empty(
        self, monkeypatch, responder, load
    ):
        """A failure that is not the routed-spot refusal reports no data."""
        responder({"get_instruments": load("instruments_future")})

        async def _gather(calls, use_cache=True):
            return [OpenBBError("something else")]

        monkeypatch.setattr("openbb_deribit.utils.client.gather", _gather)

        with pytest.raises(EmptyDataError):
            await DeribitTradesFetcher.fetch_data({"symbol": "BTC-PERPETUAL"}, {})


class TestTradeVolumes:
    """Traded volume is returned per currency."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each currency carries its one, seven, and thirty day volumes."""
        rows = await run(
            DeribitTradeVolumesFetcher,
            {},
            responder,
            {"get_trade_volumes": load("trade_volumes")},
        )

        assert rows
        assert rows[0].futures_volume_30d is not None

    @pytest.mark.asyncio
    async def test_the_busiest_currencies_come_first(self, responder, load):
        """Currencies are ranked by what traded, not by name."""
        rows = await run(
            DeribitTradeVolumesFetcher,
            {},
            responder,
            {"get_trade_volumes": load("trade_volumes")},
        )
        traded = [
            (row.futures_volume or 0)
            + (row.calls_volume or 0)
            + (row.puts_volume or 0)
            + (row.spot_volume or 0)
            for row in rows
        ]

        assert traded == sorted(traded, reverse=True)

    @pytest.mark.asyncio
    async def test_currencies_that_traded_nothing_sort_by_name(self, responder):
        """A tie is broken by name, so the order never wanders between calls."""
        rows = await run(
            DeribitTradeVolumesFetcher,
            {},
            responder,
            {
                "get_trade_volumes": [
                    {"currency": "ZZZ", "futures_volume": 0.0},
                    {"currency": "AAA", "futures_volume": 0.0},
                    {"currency": "MMM", "spot_volume": 5.0},
                ]
            },
        )

        assert [row.currency for row in rows] == ["MMM", "AAA", "ZZZ"]

    @pytest.mark.asyncio
    async def test_every_product_counts_towards_the_ranking(self, responder):
        """A currency that trades only options outranks one that trades nothing."""
        rows = await run(
            DeribitTradeVolumesFetcher,
            {},
            responder,
            {
                "get_trade_volumes": [
                    {"currency": "AAA", "futures_volume": 1.0},
                    {"currency": "BBB", "calls_volume": 2.0, "puts_volume": 3.0},
                ]
            },
        )

        assert [row.currency for row in rows] == ["BBB", "AAA"]

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No volumes is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitTradeVolumesFetcher, {}, responder, {"get_trade_volumes": []}
            )


class TestBlockRfqTrades:
    """Block requests are flattened to one row per leg."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Every leg of every request is a row, newest first."""
        payload = load("block_rfq_trades")
        rows = await run(
            DeribitBlockRfqTradesFetcher,
            {"limit": 10},
            responder,
            {"get_block_rfq_trades": payload},
        )

        assert len(rows) == sum(len(rfq["legs"]) for rfq in payload["block_rfqs"])
        assert [row.timestamp for row in rows] == sorted(
            (row.timestamp for row in rows), reverse=True
        )

    @pytest.mark.asyncio
    async def test_legless_request(self, responder):
        """A request carrying no legs still produces one row."""
        rows = await run(
            DeribitBlockRfqTradesFetcher,
            {"limit": 10},
            responder,
            {
                "get_block_rfq_trades": {
                    "block_rfqs": [{"id": 1, "timestamp": 1789938000000}]
                }
            },
        )

        assert len(rows) == 1
        assert rows[0].leg is None

    @pytest.mark.asyncio
    async def test_limit_is_bounded(self):
        """A count outside the range the exchange accepts is rejected."""
        with pytest.raises(ValueError):
            DeribitBlockRfqTradesFetcher.transform_query({"limit": 1})

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No traded request is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitBlockRfqTradesFetcher,
                {},
                responder,
                {"get_block_rfq_trades": {"block_rfqs": []}},
            )


class TestSettlements:
    """Settlements are returned newest first."""

    @pytest.mark.asyncio
    async def test_by_currency(self, responder, load):
        """A currency reads every settlement it processed."""
        rows = await run(
            DeribitSettlementsFetcher,
            {"currency": "BTC", "limit": 5},
            responder,
            {"get_last_settlements_by_currency": load("settlements_currency")},
        )

        assert rows
        assert rows[0].settlement_type

    @pytest.mark.asyncio
    async def test_by_instrument(self, responder, load):
        """A named instrument reads only its own settlements."""
        rows = await run(
            DeribitSettlementsFetcher,
            {"symbol": "BTC-PERPETUAL", "limit": 5},
            responder,
            {
                "get_last_settlements_by_instrument": load("settlements_instrument"),
                "get_instruments": load("instruments_future"),
            },
        )

        assert {row.symbol for row in rows} == {"BTC-PERPETUAL"}

    @pytest.mark.asyncio
    async def test_start_date_is_sent(self, responder, load):
        """A start date reaches the exchange as a search bound."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return load("settlements_currency")

        await run(
            DeribitSettlementsFetcher,
            {"currency": "BTC", "start_date": "2026-01-01"},
            responder,
            {"get_last_settlements_by_currency": capture},
        )

        assert seen["search_start_timestamp"] == 1767225600000

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """Nothing settled is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitSettlementsFetcher,
                {"currency": "BTC"},
                responder,
                {"get_last_settlements_by_currency": {"settlements": []}},
            )


class TestDeliveryPrices:
    """Delivery prices are returned oldest first."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each session the index delivered on is a row."""
        rows = await run(
            DeribitDeliveryPricesFetcher,
            {"index_name": "btc_usd", "limit": 5},
            responder,
            {"get_delivery_prices": load("delivery_prices")},
        )

        assert [row.date for row in rows] == sorted(row.date for row in rows)
        assert {row.index_name for row in rows} == {"btc_usd"}

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """An index that has not delivered is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitDeliveryPricesFetcher,
                {"index_name": "btc_usd"},
                responder,
                {"get_delivery_prices": {"data": []}},
            )


class TestIndexPrice:
    """Index levels are returned one row per index."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each named index carries its level."""
        rows = await run(
            DeribitIndexPriceFetcher,
            {"index_name": "btc_usd,eth_usd"},
            responder,
            {"get_index_price": load("index_price")},
        )

        assert [row.index_name for row in rows] == ["btc_usd", "eth_usd"]
        assert all(row.index_price for row in rows)

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No level at all is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitIndexPriceFetcher,
                {"index_name": "btc_usd"},
                responder,
                {"get_index_price": {}},
            )


class TestIndexHistorical:
    """An index series is returned oldest first."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each published level is a row."""
        payload = load("index_chart_data")
        rows = await run(
            DeribitIndexHistoricalFetcher,
            {"index_name": "btc_usd", "span": "1h"},
            responder,
            {"get_index_chart_data": payload},
        )

        assert len(rows) == len(payload)
        assert [row.date for row in rows] == sorted(row.date for row in rows)

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No series is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitIndexHistoricalFetcher,
                {"index_name": "btc_usd"},
                responder,
                {"get_index_chart_data": []},
            )


class TestFundingRateHistory:
    """Funding history is returned oldest first."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each hour of funding is a row, with no raw timestamp left over."""
        payload = load("funding_rate_history")
        rows = await run(
            DeribitFundingRateHistoryFetcher,
            {"symbol": "BTC-PERPETUAL"},
            responder,
            {
                "get_funding_rate_history": payload,
                "get_instruments": load("instruments_future"),
            },
        )

        assert len(rows) == len(payload)
        assert "timestamp" not in rows[0].model_dump()
        assert [row.date for row in rows] == sorted(row.date for row in rows)

    @pytest.mark.asyncio
    async def test_empty(self, responder, load):
        """No funding over the span is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitFundingRateHistoryFetcher,
                {"symbol": "BTC-PERPETUAL"},
                responder,
                {
                    "get_funding_rate_history": [],
                    "get_instruments": load("instruments_future"),
                },
            )


class TestFundingChart:
    """The funding chart carries the running interest alongside each point."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each point is a row and the running interest is repeated."""
        payload = load("funding_chart")
        rows = await run(
            DeribitFundingChartFetcher,
            {"symbol": "BTC-PERPETUAL", "length": "8h"},
            responder,
            {
                "get_funding_chart_data": payload,
                "get_instruments": load("instruments_future"),
            },
        )

        assert len(rows) == len(payload["data"])
        assert "timestamp" not in rows[0].model_dump()

    @pytest.mark.asyncio
    async def test_empty(self, responder, load):
        """No funding over the span is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitFundingChartFetcher,
                {"symbol": "BTC-PERPETUAL"},
                responder,
                {
                    "get_funding_chart_data": {"data": []},
                    "get_instruments": load("instruments_future"),
                },
            )


class TestAprHistory:
    """Yield history reads the day number as a date."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each day is a row, with the rate as a decimal."""
        payload = load("apr_history")
        rows = await run(
            DeribitAprHistoryFetcher,
            {"currency": "usde", "limit": 5},
            responder,
            {"get_apr_history": payload},
        )

        assert len(rows) == len(payload["data"])
        assert isinstance(rows[0].date, date)
        assert "day" not in rows[0].model_dump()
        assert rows[0].apr > 1

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No yield history is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitAprHistoryFetcher,
                {"currency": "usde"},
                responder,
                {"get_apr_history": {"data": []}},
            )


class TestHistoricalVolatility:
    """Realized volatility is returned oldest first, as a decimal."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each reading is a row."""
        payload = load("historical_volatility")
        rows = await run(
            DeribitHistoricalVolatilityFetcher,
            {"currency": "BTC"},
            responder,
            {"get_historical_volatility": payload},
        )

        assert len(rows) == len(payload)
        assert rows[0].volatility > 5
        assert [row.date for row in rows] == sorted(row.date for row in rows)

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No readings is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitHistoricalVolatilityFetcher,
                {"currency": "BTC"},
                responder,
                {"get_historical_volatility": []},
            )


class TestVolatilityIndex:
    """The volatility index is returned as candles, oldest first."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Each candle carries four decimal levels."""
        payload = load("volatility_index")
        rows = await run(
            DeribitVolatilityIndexFetcher,
            {"currency": "BTC", "interval": "12h"},
            responder,
            {"get_volatility_index_data": payload},
        )

        assert len(rows) == len(payload["data"])
        assert rows[0].high >= rows[0].low
        assert rows[0].close > 5

    @pytest.mark.asyncio
    async def test_resolution_is_mapped(self, responder, load):
        """The interval reaches the exchange as the resolution it names."""
        seen: dict = {}

        def capture(params):
            seen.update(params)

            return load("volatility_index")

        await run(
            DeribitVolatilityIndexFetcher,
            {"currency": "BTC", "interval": "1d"},
            responder,
            {"get_volatility_index_data": capture},
        )

        assert seen["resolution"] == "1D"

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No candles over the span is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitVolatilityIndexFetcher,
                {"currency": "BTC"},
                responder,
                {"get_volatility_index_data": {"data": []}},
            )


class TestFuturesInstruments:
    """The standard futures listing keeps the extended Deribit fields."""

    @pytest.mark.asyncio
    async def test_rows(self, responder, load):
        """Every future is a row, carrying the live-only fields."""
        rows = await run(
            DeribitFuturesInstrumentsFetcher,
            {},
            responder,
            {"get_instruments": load("instruments_future")},
        )

        assert len(rows) == 13
        assert rows[0].index_id
        assert rows[0].product_group
        assert rows[0].underlying_type

    @pytest.mark.asyncio
    async def test_perpetual_has_no_expiration(self, responder, load):
        """The year-3000 sentinel reads as no expiration."""
        rows = await run(
            DeribitFuturesInstrumentsFetcher,
            {},
            responder,
            {"get_instruments": load("instruments_future")},
        )
        perpetual = next(row for row in rows if row.symbol == "BTC-PERPETUAL")

        assert perpetual.expiration_timestamp is None

    @pytest.mark.asyncio
    async def test_empty(self, responder):
        """No futures is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitFuturesInstrumentsFetcher,
                {},
                responder,
                {"get_instruments": []},
            )


class TestFuturesInfo:
    """The standard futures quote is the flattened ticker."""

    @pytest.mark.asyncio
    async def test_row(self, responder, load):
        """The quote carries the statistics the ticker nests."""
        rows = await run(
            DeribitFuturesInfoFetcher,
            {"symbol": "BTC-PERPETUAL"},
            responder,
            {
                "ticker": load("ticker_future"),
                "get_instruments": load("instruments_future"),
            },
        )

        assert rows[0].symbol == "BTC-PERPETUAL"
        assert rows[0].volume is not None

    @pytest.mark.asyncio
    async def test_empty(self, responder, load):
        """No quote is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitFuturesInfoFetcher,
                {"symbol": "BTC-PERPETUAL"},
                responder,
                {"ticker": {}, "get_instruments": load("instruments_future")},
            )


class TestFuturesCurve:
    """The current curve is priced off the mark."""

    @pytest.mark.asyncio
    async def test_prefers_the_mark(self, responder, load):
        """A stale last trade does not set the level of the curve."""
        payload = dict(load("ticker_future"))
        payload["last_price"] = 1.0
        payload["mark_price"] = 2.0
        payload["instrument_name"] = "BTC-25DEC26"
        rows = await run(
            DeribitFuturesCurveFetcher,
            {"symbol": "BTC"},
            responder,
            {
                "ticker": payload,
                "get_instruments": load("instruments_future"),
            },
        )

        assert rows[0].price == 2.0
        assert rows[0].last_price == 1.0

    @pytest.mark.asyncio
    async def test_hours_ago_is_appended(self, monkeypatch, responder, load):
        """A past curve is added alongside the current one."""

        async def _past(symbol, hours):
            return [
                {
                    "instrument_name": "BTC-25DEC26",
                    "hours_ago": hours,
                    "last_price": 3.0,
                }
            ]

        monkeypatch.setattr(
            "openbb_deribit.utils.helpers.get_futures_curve_by_hours_ago", _past
        )
        payload = dict(load("ticker_future"))
        payload["instrument_name"] = "BTC-25DEC26"
        rows = await run(
            DeribitFuturesCurveFetcher,
            {"symbol": "BTC", "hours_ago": 24},
            responder,
            {
                "ticker": payload,
                "get_instruments": load("instruments_future"),
            },
        )

        assert 24 in {row.hours_ago for row in rows}

    def test_rejects_a_date(self):
        """A date is rejected, because the exchange serves no curve for one."""
        with pytest.raises(ValueError, match="hours_ago"):
            DeribitFuturesCurveFetcher.transform_query(
                {"symbol": "BTC", "date": "2026-01-01"}
            )

    def test_hours_ago_accepts_a_list(self):
        """Several hour counts are carried as a comma-separated string."""
        query = DeribitFuturesCurveFetcher.transform_query(
            {"symbol": "BTC", "hours_ago": [1, 24]}
        )

        assert query.hours_ago == "1,24"

    def test_hours_ago_defaults_to_nothing(self):
        """No hour count is carried as nothing at all."""
        assert (
            DeribitFuturesCurveFetcher.transform_query(
                {"symbol": "BTC", "hours_ago": None}
            ).hours_ago
            is None
        )

    def test_a_non_mapping_query_passes_through(self):
        """A query the validator cannot read is left to pydantic."""
        from openbb_deribit.models.futures_curve import (
            DeribitFuturesCurveQueryParams,
        )

        assert DeribitFuturesCurveQueryParams.validate_model("BTC") == "BTC"

    def test_hours_ago_accepts_an_integer(self):
        """One hour count is carried as its own string."""
        query = DeribitFuturesCurveFetcher.transform_query(
            {"symbol": "BTC", "hours_ago": 24}
        )

        assert query.hours_ago == "24"

    @pytest.mark.asyncio
    async def test_no_quotes(self, responder, load):
        """A curve with no quote at all is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitFuturesCurveFetcher,
                {"symbol": "BTC"},
                responder,
                {"ticker": {}, "get_instruments": load("instruments_future")},
            )

    @pytest.mark.asyncio
    async def test_no_prices(self, responder, load):
        """A curve whose contracts are all unpriced is an error."""
        with pytest.raises(EmptyDataError):
            await run(
                DeribitFuturesCurveFetcher,
                {"symbol": "BTC"},
                responder,
                {
                    "ticker": {"instrument_name": "BTC-25DEC26"},
                    "get_instruments": load("instruments_future"),
                },
            )


class TestFuturesHistorical:
    """Candles are returned oldest first."""

    @pytest.mark.asyncio
    async def test_single_symbol_drops_the_column(self, monkeypatch, responder, load):
        """One symbol needs no symbol column."""

        async def _ohlc(symbol, start_date, end_date, interval):
            return [
                {
                    "date": date(2026, 9, 19),
                    "symbol": symbol,
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                    "volume": 10.0,
                    "volume_notional": 15.0,
                }
            ]

        monkeypatch.setattr("openbb_deribit.utils.helpers.get_ohlc_data", _ohlc)
        responder({"get_instruments": load("instruments_future")})
        rows = await DeribitFuturesHistoricalFetcher.fetch_data(
            {"symbol": "BTC-PERPETUAL"}, {}
        )

        assert rows[0].symbol is None
        assert rows[0].volume_notional == 15.0

    @pytest.mark.asyncio
    async def test_several_symbols_keep_the_column(self, monkeypatch, responder, load):
        """Several symbols are told apart by the symbol column."""

        async def _ohlc(symbol, start_date, end_date, interval):
            return [
                {
                    "date": date(2026, 9, 19),
                    "symbol": symbol,
                    "open": 1.0,
                    "high": 2.0,
                    "low": 0.5,
                    "close": 1.5,
                    "volume": 10.0,
                    "volume_notional": 15.0,
                }
            ]

        monkeypatch.setattr("openbb_deribit.utils.helpers.get_ohlc_data", _ohlc)
        responder({"get_instruments": load("instruments_future")})
        rows = await DeribitFuturesHistoricalFetcher.fetch_data(
            {"symbol": "BTC-PERPETUAL,BTC-25DEC26"}, {}
        )

        assert {row.symbol for row in rows} == {"BTC-PERPETUAL", "BTC-25DEC26"}

    def test_span_defaults_narrow_with_the_interval(self):
        """A one-minute interval defaults to a much shorter span than a daily."""
        minute = DeribitFuturesHistoricalFetcher.transform_query(
            {"symbol": "BTC-PERPETUAL", "interval": "1m"}
        )
        daily = DeribitFuturesHistoricalFetcher.transform_query(
            {"symbol": "BTC-PERPETUAL", "interval": "1d"}
        )

        assert minute.start_date > daily.start_date
        assert minute.end_date == daily.end_date

    def test_a_non_mapping_query_passes_through(self):
        """A query the validator cannot read is left to pydantic."""
        from openbb_deribit.models.futures_historical import (
            DeribitFuturesHistoricalQueryParams,
        )

        assert DeribitFuturesHistoricalQueryParams.validate_model("BTC") == "BTC"

    def test_given_span_is_kept(self):
        """A span the caller named is not overridden."""
        query = DeribitFuturesHistoricalFetcher.transform_query(
            {
                "symbol": "BTC-PERPETUAL",
                "start_date": "2026-01-01",
                "end_date": "2026-02-01",
            }
        )

        assert query.start_date == date(2026, 1, 1)
        assert query.end_date == date(2026, 2, 1)

    @pytest.mark.asyncio
    async def test_empty(self, monkeypatch, responder, load):
        """No candles at all is an error."""

        async def _ohlc(symbol, start_date, end_date, interval):
            return []

        monkeypatch.setattr("openbb_deribit.utils.helpers.get_ohlc_data", _ohlc)
        responder({"get_instruments": load("instruments_future")})

        with pytest.raises(EmptyDataError):
            await DeribitFuturesHistoricalFetcher.fetch_data(
                {"symbol": "BTC-PERPETUAL"}, {}
            )
