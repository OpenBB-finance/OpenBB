""" discovery/ark_view.py tests """
import unittest
from unittest import mock
from io import StringIO
import pandas as pd

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

from gamestonk_terminal.stocks.discovery.ark_view import ark_orders_view

assertions = unittest.TestCase("__init__")


class TestDiscoveryArkView:
    @mock.patch("gamestonk_terminal.stocks.discovery.ark_view.ark_model.get_ark_orders")
    @mock.patch(
        "gamestonk_terminal.stocks.discovery.ark_view.ark_model.add_order_total"
    )
    @parameterize_from_file(
        "test_ark_orders_view",
        "../tests/data/discovery_ark_view.yaml",
    )
    def test_ark_orders_view(
        self,
        mock_add_order_total,
        mock_get_ark_orders,
        return_get_ark_orders,
        return_add_order_total,
    ):
        mock_get_ark_orders.return_value = pd.read_csv(
            StringIO(return_get_ark_orders), header=0, index_col=0, parse_dates=["date"]
        )
        mock_add_order_total.return_value = pd.read_csv(
            StringIO(return_add_order_total),
            header=0,
            index_col=0,
            parse_dates=["date"],
        )

        ark_orders_view(["-n", "10"])
