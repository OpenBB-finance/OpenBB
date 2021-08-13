from unittest import TestCase, mock

import vcr

from gamestonk_terminal.cryptocurrency.coinpaprika import coinpaprika_view
from tests.helpers import check_print


class TestCoinPaprikaView(TestCase):
    @check_print(assert_in="market_cap_usd")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_global_markets.yaml"
    )
    def test_global_markets(self):
        coinpaprika_view.global_market([])

    @check_print(assert_in="rank")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_coins.yaml"
    )
    def test_coins(self):
        coinpaprika_view.coins([])

    @check_print(assert_in="Displaying data vs USD")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_all_coins_info.yaml"
    )
    def test_all_coins_info(self):
        coinpaprika_view.all_coins_info([])

    @check_print(assert_in="Displaying data vs USD")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_all_exchanges.yaml"
    )
    def test_all_exchanges(self):
        coinpaprika_view.all_exchanges([])

    @check_print(assert_in="category")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_search.yaml"
    )
    def test_search(self):
        coinpaprika_view.search(["-q", "bt"])

    @check_print(assert_in="platform_id")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_all_platforms.yaml"
    )
    def test_all_platforms(self):
        coinpaprika_view.all_platforms([])

    @check_print(assert_in="active")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_contracts.yaml"
    )
    def test_contracts(self):
        coinpaprika_view.contracts([])

    @check_print(assert_in="index")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_find.yaml"
    )
    def test_find(self):
        coinpaprika_view.find(["-c", "BTC"])

    @check_print(assert_in="Couldn't find")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_twitter.yaml"
    )
    def test_twitter(self):
        coinpaprika_view.twitter("eth-ethereum", [])

    @check_print(assert_in="description")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_events.yaml"
    )
    def test_events(self):
        coinpaprika_view.events("eth-ethereum", [])

    @check_print(assert_in="name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_exchanges.yaml"
    )
    def test_exchanges(self):
        coinpaprika_view.exchanges("btc-bitcoin", [])

    @check_print(assert_in="exchange")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_markets.yaml"
    )
    def test_markets(self):
        coinpaprika_view.markets("eth-ethereum", [])

    @check_print(assert_in="\n")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_chart.yaml"
    )
    @mock.patch("matplotlib.pyplot.show")
    def test_chart(self, mock_matplot):
        # pylint: disable=unused-argument
        coinpaprika_view.chart("btc-bitcoin", [])

    @check_print(assert_in="base_currency_name")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_exchange_markets.yaml"
    )
    def test_exchange_markets(self):
        coinpaprika_view.exchange_markets([])

    @check_print(assert_in="asset_platform_id")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_price_supply.yaml"
    )
    def price_supply(self):
        coinpaprika_view.price_supply("btc", [])

    @check_print()
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_load.yaml"
    )
    def test_load(self):
        value = coinpaprika_view.load(["-c", "BTC"])
        self.assertEqual(value, "btc-bitcoin")

    # @check_print()
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_ta.yaml",
        record_mode="new_episodes",
    )
    def test_ta(self):
        value = coinpaprika_view.ta("eth-ethereum", [])
        self.assertIn("Open", value[0])

    @check_print(assert_in="Metric")
    @vcr.use_cassette(
        "tests/cassettes/test_cryptocurrency/test_coinpaprika/test_basic.yaml"
    )
    def test_basic(self):
        coinpaprika_view.basic("BTC", [])
