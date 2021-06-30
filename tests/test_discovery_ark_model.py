""" discovery/ark_model.py tests """
import unittest
from unittest import mock
from io import StringIO
import pandas as pd

# pylint: disable=unused-import,no-member

from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

from gamestonk_terminal.discovery.ark_model import get_ark_orders, add_order_total

assertions = unittest.TestCase("__init__")


class TestDiscoveryArkModel:
    @mock.patch("gamestonk_terminal.discovery.ark_model.requests")
    @parameterize_from_file(
        "test_get_ark_orders",
        "../tests/data/discovery_ark_model.yaml",
    )
    # pylint: disable=unused-argument
    def test_get_ark_orders(
        self,
        mock_requests_get,
        mock_ark_orders_html,
        expected_orders,
    ):
        mock_requests_get.get().text = mock_ark_orders_html
        ret = get_ark_orders()

        assertions.assertEqual.__self__.maxDiff = None
        assertions.assertEqual(
            ret.to_csv().replace("\r\n", "\n"), expected_orders.replace("\r\n", "\n")
        )

    @mock.patch("gamestonk_terminal.discovery.ark_model.yf.download")
    @parameterize_from_file(
        "test_add_order_total",
        "../tests/data/discovery_ark_model.yaml",
    )
    # pylint: disable=unused-argument
    def test_add_order_total(
        self, mock_yf_download, mock_df_orders, mock_yf_result, expected_orders
    ):
        df_orders = pd.read_csv(
            StringIO(mock_df_orders), header=0, index_col=0, parse_dates=["date"]
        )
        mock_yf_download.return_value = pd.read_csv(
            StringIO(mock_yf_result), header=[0, 1], index_col=0, parse_dates=True
        )

        ret = add_order_total(df_orders)

        assertions.assertEqual.__self__.maxDiff = None
        assertions.assertEqual(
            ret.to_csv().replace("\r\n", "\n"), expected_orders.replace("\r\n", "\n")
        )
