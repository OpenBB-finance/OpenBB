""" discovery/fidelity_api.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.discovery.fidelity_view import (
    buy_sell_ratio_color_red_green,
    orders_view,
    price_change_color_red_green,
)
from tests.helpers import check_print


class TestDiscoveryFidelityApi(unittest.TestCase):
    @check_print(assert_in="Symbol")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/stocks/discovery/cassettes/test_fidelity/test_orders.yaml",
        record_mode="new_episodes",
    )
    def test_orders(self):
        orders_view(5, "")

    @vcr.use_cassette(
        "tests/gamestonk_terminal/stocks/discovery/cassettes/test_fidelity/test_buy_sell.yaml",
        record_mode="new_episodes",
    )
    def test_buy_sell_ratio_color_red_green(self):

        res = buy_sell_ratio_color_red_green("56% Buys, 44% Sells")

        assert res == "\x1b[32m56%\x1b[0m Buys, 44% Sells"

        res = buy_sell_ratio_color_red_green("44% Buys, 56% Sells")

        assert res == "44% Buys, \x1b[31m56%\x1b[0m Sells"

    @vcr.use_cassette(
        "tests/cassettes/test_discovery/test_discovery_fidelity/test_price_change_color.yaml",
        record_mode="new_episodes",
    )
    def test_price_change_color_red_green(self):
        res = price_change_color_red_green("-6.99 (-6.4288%)")

        assert res == "\x1b[31m-6.99 (-6.4288%)\x1b[0m"

        res = price_change_color_red_green("2.40 (+124.3523%)")

        assert res == "\x1b[32m2.40 (+124.3523%)\x1b[0m"
