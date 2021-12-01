""" discovery/ark_model.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.discovery.ark_model import get_ark_orders
from tests.helpers import check_print


class TestDiscoveryArkModel(unittest.TestCase):
    @check_print(assert_in="direction")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/stocks/discovery/cassettes/test_ark_model/test_get_ark_order.yaml",
        record_mode="none",
    )
    def test_get_ark_orders(self):
        ret = get_ark_orders()
        print(ret)

    @check_print(assert_in="weight")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/stocks/discovery/cassettes/test_ark_model/test_get_add_order.yaml",
        record_mode="none",
    )
    def test_add_order_total(self):
        orders = get_ark_orders()
        # ret = add_order_total(orders)
        ret = orders
        print(ret)
