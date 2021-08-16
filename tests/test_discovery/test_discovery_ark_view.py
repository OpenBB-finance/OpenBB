""" discovery/ark_view.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.discovery.ark_view import ark_orders_view
from tests.helpers import check_print


class TestDiscoveryArkView(unittest.TestCase):
    @check_print(assert_in="direction")
    @vcr.use_cassette(
        "tests/cassettes/test_discovery/test_discovery_ark_view/test_ark_order_view.yaml",
        record_mode="new_episodes",
    )
    def test_ark_orders_view(self):
        ark_orders_view(10, "")
