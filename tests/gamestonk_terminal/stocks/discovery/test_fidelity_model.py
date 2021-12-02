""" discovery/fidelity_model.py tests """
import unittest
from unittest import mock

from gamestonk_terminal.stocks.discovery.fidelity_model import get_orders

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

assertions = unittest.TestCase("__init__")


class TestDiscoveryFidelityModel:
    @mock.patch("gamestonk_terminal.stocks.discovery.fidelity_model.requests")
    @parameterize_from_file(
        "test_get_orders",
        "../tests/gamestonk_terminal/stocks/discovery/yaml/test_fidelity_model/fidelity_model.yaml",
    )
    # pylint: disable=unused-argument
    def test_get_orders(
        self,
        mock_requests_get,
        mock_fidelity_orders_html,
        expected_header,
        expected_orders,
    ):
        mock_requests_get.get().text = mock_fidelity_orders_html
        header, ret = get_orders()

        assertions.assertEqual.__self__.maxDiff = None
        assertions.assertEqual(
            header.replace("\r\n", "\n"), expected_header.replace("\r\n", "\n")
        )
        assertions.assertEqual(
            ret.to_csv().replace("\r\n", "\n"), expected_orders.replace("\r\n", "\n")
        )
