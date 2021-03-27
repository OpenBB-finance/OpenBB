""" discovery/short_interest_api.py tests """
import unittest
from unittest import mock

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

from gamestonk_terminal.discovery.short_interest_api import (
    high_short_interest,
    low_float,
)

assertions = unittest.TestCase("__init__")


class TestDiscoveryShortInterestApi:
    @mock.patch("gamestonk_terminal.discovery.short_interest_api.requests")
    @parameterize_from_file(
        "test_high_short_interest",
        "../tests/data/discovery_short_interest_api.yaml",
    )
    # pylint: disable=unused-argument
    def test_high_short_interest(
        self, mock_request_get, mock_high_short, expected_result
    ):
        mock_request_get.get().text = mock_high_short
        high_short_interest(["-n", "10"])

    @mock.patch("gamestonk_terminal.discovery.short_interest_api.requests")
    @parameterize_from_file(
        "test_low_float",
        "../tests/data/discovery_short_interest_api.yaml",
    )
    # pylint: disable=unused-argument
    def test_low_float(self, mock_request_get, mock_low_float, expected_result):
        mock_request_get.get().text = mock_low_float
        low_float(["-n", "10"])
