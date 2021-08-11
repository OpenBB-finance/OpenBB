""" discovery/fidelity_api.py tests """
import unittest

from gamestonk_terminal.stocks.discovery.fidelity_view import (
    buy_sell_ratio_color_red_green,
    price_change_color_red_green,
    orders_view,
)


class TestDiscoveryFidelityApi(unittest.TestCase):
    def test_orders(self):
        orders_view(5, "")

    def test_buy_sell_ratio_color_red_green(self):
        res = buy_sell_ratio_color_red_green("56% Buys, 44% Sells")

        assert res == "\x1b[32m56%\x1b[0m Buys, 44% Sells"

        res = buy_sell_ratio_color_red_green("44% Buys, 56% Sells")

        assert res == "44% Buys, \x1b[31m56%\x1b[0m Sells"

    def test_price_change_color_red_green(self):
        res = price_change_color_red_green("-6.99 (-6.4288%)")

        assert res == "\x1b[31m-6.99 (-6.4288%)\x1b[0m"

        res = price_change_color_red_green("2.40 (+124.3523%)")

        assert res == "\x1b[32m2.40 (+124.3523%)\x1b[0m"
