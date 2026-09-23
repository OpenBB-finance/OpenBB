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


class TestMarkPriceChoices:
    """Only the volatility index constituents have a mark price history.

    The exchange returns an empty series for every other instrument, so the
    feed offers the two expirations bracketing thirty days rather than the
    whole option universe.
    """

    @pytest.fixture
    def universe(self, responder):
        """List options at the given number of days out, for BTC and ETH."""
        from datetime import datetime, timedelta, timezone

        from openbb_deribit.utils.helpers import to_timestamp

        def install(day_offsets):
            now = datetime.now(timezone.utc)

            def listing(params):
                return [
                    {
                        "instrument_name": f"{params['currency']}-{offset}-C",
                        "expiration_timestamp": to_timestamp(
                            now + timedelta(days=offset)
                        ),
                        "strike": 100.0,
                    }
                    for offset in day_offsets
                ]

            responder({"get_instruments": listing})

        return install

    @pytest.mark.asyncio
    async def test_brackets_thirty_days(self, universe):
        """The expirations either side of thirty days out are the ones offered."""
        universe([1, 8, 29, 38, 90])
        feed = await choices.mark_price_choices()
        offsets = sorted({int(row["value"].split("-")[1]) for row in feed})

        assert offsets == [29, 38]
        assert {row["value"].split("-")[0] for row in feed} == {"BTC", "ETH"}

    @pytest.mark.asyncio
    async def test_handles_expirations_only_on_one_side(self, universe):
        """A listing entirely inside thirty days offers its last expiration."""
        universe([1, 8, 15])
        feed = await choices.mark_price_choices()

        assert sorted({int(row["value"].split("-")[1]) for row in feed}) == [15]

    @pytest.mark.asyncio
    async def test_an_empty_listing_offers_nothing(self, responder):
        """A currency the exchange lists no options on contributes nothing."""
        responder({"get_instruments": []})

        assert await choices.mark_price_choices() == []


class TestDefaultVolatilityOption:
    """A widget with no contract chosen still has something valid to show."""

    @pytest.fixture
    def universe(self, responder):
        """List two expirations of strikes around a known index level."""
        from datetime import datetime, timedelta, timezone

        from openbb_deribit.utils.helpers import to_timestamp

        now = datetime.now(timezone.utc)
        responder(
            {
                "get_instruments": lambda params: [
                    {
                        "instrument_name": f"BTC-{offset}-{strike}-C",
                        "expiration_timestamp": to_timestamp(
                            now + timedelta(days=offset)
                        ),
                        "strike": float(strike),
                    }
                    for offset in (29, 38)
                    for strike in (50000, 80000, 120000)
                ],
                "get_index_price": {"index_price": 81000.0},
            }
        )

    @pytest.mark.asyncio
    async def test_picks_the_nearest_strike_on_the_front_expiration(self, universe):
        """The chosen contract is the one closest to the index, nearest expiry."""
        from openbb_deribit.utils.helpers import default_volatility_option

        assert await default_volatility_option() == "BTC-29-80000-C"

    @pytest.mark.asyncio
    async def test_no_listing_is_an_error(self, responder):
        """A currency with no volatility index options says so."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_deribit.utils.helpers import default_volatility_option

        responder({"get_instruments": []})

        with pytest.raises(EmptyDataError, match="volatility index options"):
            await default_volatility_option()
