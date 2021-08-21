from unittest import TestCase, mock

from gamestonk_terminal.cryptocurrency.due_diligence import (
    coinpaprika_view as dd_coinpaprika_view,
)
from gamestonk_terminal.cryptocurrency.discovery import (
    coinpaprika_view as disc_coinpaprika_view,
)
from gamestonk_terminal.cryptocurrency.overview import (
    coinpaprika_view as ov_coinpaprika_view,
)

from tests.helpers import check_print


class TestCoinPaprikaView(TestCase):
    @check_print(assert_in="market_cap_usd")
    def test_global_markets(self):
        ov_coinpaprika_view.global_market([])

    @check_print(assert_in="rank")
    def test_coins(self):
        disc_coinpaprika_view.coins([])

    @check_print(assert_in="Displaying data vs USD")
    def test_all_coins_market_info(self):
        ov_coinpaprika_view.all_coins_market_info([])

    @check_print(assert_in="Displaying data vs USD")
    def test_all_coins_info(self):
        ov_coinpaprika_view.all_coins_info([])

    @check_print(assert_in="Displaying data vs USD")
    def test_all_exchanges(self):
        ov_coinpaprika_view.all_exchanges([])

    @check_print(assert_in="category")
    def test_search(self):
        disc_coinpaprika_view.search(["-q", "bt"])

    @check_print(assert_in="platform_id")
    def test_all_platforms(self):
        ov_coinpaprika_view.all_platforms([])

    @check_print(assert_in="active")
    def test_contracts(self):
        ov_coinpaprika_view.contracts([])

    @check_print(assert_in="index")
    def test_find(self):
        disc_coinpaprika_view.find(["-c", "BTC"])

    @check_print(assert_in="Couldn't find")
    def test_twitter(self):
        dd_coinpaprika_view.twitter("eth-ethereum", [])

    @check_print(assert_in="description")
    def test_events(self):
        dd_coinpaprika_view.events("eth-ethereum", [])

    @check_print(assert_in="name")
    def test_exchanges(self):
        dd_coinpaprika_view.exchanges("btc-bitcoin", [])

    @check_print(assert_in="exchange")
    def test_markets(self):
        dd_coinpaprika_view.markets("eth-ethereum", [])

    @check_print(assert_in="\n")
    @mock.patch("matplotlib.pyplot.show")
    def test_chart(self, mock_matplot):
        # pylint: disable=unused-argument
        dd_coinpaprika_view.chart("btc-bitcoin", [])

    @check_print(assert_in="base_currency_name")
    def test_exchange_markets(self):
        ov_coinpaprika_view.exchange_markets([])

    @check_print(assert_in="asset_platform_id")
    def price_supply(self):
        dd_coinpaprika_view.price_supply("btc", [])

    def test_load(self):
        value = dd_coinpaprika_view.load(["-c", "BTC"])
        self.assertEqual(value, "btc-bitcoin")

    def test_load_ta_data(self):
        value = dd_coinpaprika_view.load_ta_data("eth-ethereum", [])
        print(value[0])
        self.assertIn("Open", value[0])

    @check_print(assert_in="Metric")
    def test_basic(self):
        dd_coinpaprika_view.basic("BTC", [])
