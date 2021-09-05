"""
from unittest import TestCase, mock

import pandas as pd

from gamestonk_terminal.cryptocurrency.due_diligence import (
    coinpaprika_view as dd_coinpaprika_view,
)
from gamestonk_terminal.cryptocurrency.discovery import (
    coinpaprika_view as disc_coinpaprika_view,
)
from gamestonk_terminal.cryptocurrency.overview import (
    coinpaprika_view as ov_coinpaprika_view,
)
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import (
    plot_chart,
    load,
    load_ta_data,
)

from tests.helpers import check_print


class TestCoinPaprikaView(TestCase):
    @check_print(assert_in="market_cap_usd")
    def test_global_markets(self):
        ov_coinpaprika_view.display_global_market(export="")

    @check_print(assert_in="Displaying data vs USD")
    def test_all_coins_market_info(self):
        ov_coinpaprika_view.display_all_coins_market_info(
            currency="USD", sortby="rank", descend=True, top=15, export=""
        )

    @check_print(assert_in="Displaying data vs USD")
    def test_all_coins_info(self):
        ov_coinpaprika_view.display_all_coins_info(
            currency="USD", sortby="rank", descend=True, top=15, export=""
        )

    @check_print(assert_in="Displaying data vs USD")
    def test_all_exchanges(self):
        ov_coinpaprika_view.display_all_exchanges(
            currency="USD", sortby="rank", descend=True, top=15, export=""
        )

    @check_print(assert_in="category")
    def test_search(self):
        disc_coinpaprika_view.display_search_results(
            query="btc", category="all", top=10, sortby="id", export="", descend=False
        )

    @check_print(assert_in="platform_id")
    def test_all_platforms(self):
        ov_coinpaprika_view.display_all_platforms(export="")

    @check_print(assert_in="active")
    def test_contracts(self):
        ov_coinpaprika_view.display_contracts(
            platform="eth-ethereum", sortby="id", descend=True, top=15, export=""
        )

    @check_print(assert_in="Couldn't find")
    @mock.patch(
        "gamestonk_terminal.cryptocurrency.due_diligence.coinpaprika_model.get_coin_twitter_timeline"
    )
    def test_twitter(self, mock_value):
        mock_value.return_value = pd.DataFrame()
        dd_coinpaprika_view.display_twitter(
            coin_id="eth-ethereum", sortby="date", descend=True, top=15, export=""
        )

    @check_print(assert_in="description")
    def test_events(self):
        dd_coinpaprika_view.display_events(
            coin_id="eth-ethereum",
            sortby="date",
            descend=True,
            top=15,
            export="",
            links=False,
        )

    @check_print(assert_in="name")
    def test_exchanges(self):
        dd_coinpaprika_view.display_exchanges(
            coin_id="eth-ethereum", sortby="id", descend=True, top=15, export=""
        )

    @check_print(assert_in="exchange")
    def test_markets(self):
        dd_coinpaprika_view.display_markets(
            coin_id="eth-ethereum",
            sortby="exchange",
            descend=True,
            top=15,
            export="",
            links=False,
            currency="USD",
        )

    @check_print(assert_in="\n")
    @mock.patch("matplotlib.pyplot.show")
    def test_chart(self, mock_matplot):
        # pylint: disable=unused-argument
        plot_chart(coin="btc-bitcoin", source="cp", currency="USD", days=30)

    @check_print(assert_in="base_currency_name")
    def test_exchange_markets(self):
        ov_coinpaprika_view.display_exchange_markets(
            exchange="binance",
            sortby="exchange_id",
            descend=True,
            top=15,
            export="",
            links=False,
        )

    @check_print(assert_in="asset_platform_id")
    def price_supply(self):
        dd_coinpaprika_view.display_price_supply(
            "eth-ethereum", currency="btc", export=""
        )

    def test_load(self):
        value = load(
            coin="BTC",
            source="cp",
        )
        self.assertEqual(value[0], "btc-bitcoin")

    def test_load_ta_data(self):
        value = load_ta_data(
            coin="eth-ethereum",
            source="cp",
            currency="USD",
            days=30,
        )
        print(value[0])
        self.assertIn("Open", value[0])

    @check_print(assert_in="Metric")
    def test_basic(self):
        dd_coinpaprika_view.display_basic(coin_id="bit-bitcoin", export="")
"""
