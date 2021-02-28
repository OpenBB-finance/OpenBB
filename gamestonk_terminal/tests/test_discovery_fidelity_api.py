""" CLI tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.discovery.fidelity_api import (
    buy_sell_ratio_color_red_green,
    price_change_color_red_green,
    orders,
)


class TestDiscoveryFidelityApi(unittest.TestCase):
    def test_orders(self):
        orders([])

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
