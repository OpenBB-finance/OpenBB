""" dark_pool_shorts/short_interest_api.py tests """
import unittest
from unittest import mock

# from gamestonk_terminal.stocks.dark_pool_shorts.shortinterest_model import get_high_short_interest
from gamestonk_terminal.stocks.discovery.shortinterest_model import get_low_float

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

assertions = unittest.TestCase("__init__")


class TestDiscoveryShortInterestApi:
    """
    # TODO
    @mock.patch("gamestonk_terminal.stocks.discovery.shortinterest_model.requests")
    @parameterize_from_file(
        "test_get_high_short_interest",
        "../tests/data/discovery_short_interest_model.yaml",
    )
    # pylint: disable=unused-argument
    def test_get_high_short_interest(
        self, mock_request_get, mock_high_short, expected_result
    ):
        mock_request_get.get().text = mock_high_short

        df_high_short = get_high_short_interest()

        assertions.assertEqual.__self__.maxDiff = None
        assertions.assertEqual(
            df_high_short.to_csv().replace("\r\n", "\n"),
            expected_result.replace("\r\n", "\n"),
        )
    """

    @mock.patch("gamestonk_terminal.stocks.discovery.shortinterest_model.requests")
    @parameterize_from_file(
        "test_get_low_float",
        "../tests/gamestonk_terminal/stocks/discovery/yaml/test_short_interest_model/model.yaml",
    )
    # pylint: disable=unused-argument
    def test_get_low_float(self, mock_request_get, mock_low_float, expected_result):
        mock_request_get.get().text = mock_low_float

        df_low_float = get_low_float()

        assertions.assertEqual.__self__.maxDiff = None
        assertions.assertEqual(
            df_low_float.to_csv().replace("\r\n", "\n"),
            expected_result.replace("\r\n", "\n"),
        )
