""" discovery/ark_view.py tests """
import unittest
from unittest import mock

import vcr

from gamestonk_terminal.stocks.discovery.ark_view import ark_orders_view
from tests.helpers import check_print


def mock_add_order_total_noop(value):
    return value


class TestDiscoveryArkView(unittest.TestCase):
    @mock.patch("gamestonk_terminal.stocks.discovery.ark_model.add_order_total")
    @check_print(assert_in="direction")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/stocks/discovery/cassettes/test_ark_view/test_ark_order_view.yaml",
        record_mode="none",
    )
    def test_ark_orders_view(self, mock_add_order_total):
        mock_add_order_total.side_effect = mock_add_order_total_noop
        ark_orders_view(10, "")
