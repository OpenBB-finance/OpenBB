""" discovery/fidelity_model.py tests """
import unittest
from unittest import mock

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

from gamestonk_terminal.discovery.fidelity_model import get_orders

assertions = unittest.TestCase("__init__")


class TestDiscoveryFidelityModel:
    @mock.patch("gamestonk_terminal.discovery.fidelity_model.requests")
    @parameterize_from_file(
        "test_get_orders",
        "../tests/data/discovery_fidelity_model.yaml",
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

        print("")
        print(ret.to_csv())
        print("")
        print(header)

        assertions.assertEqual.__self__.maxDiff = None
        assertions.assertEqual(
            header.replace("\r\n", "\n"), expected_header.replace("\r\n", "\n")
        )
        assertions.assertEqual(
            ret.to_csv().replace("\r\n", "\n"), expected_orders.replace("\r\n", "\n")
        )
