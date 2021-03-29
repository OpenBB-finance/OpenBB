""" discovery/short_interest_api.py tests """
import unittest
from unittest import mock

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

from gamestonk_terminal.discovery.short_interest_model import (
    get_high_short_interest,
    get_low_float,
)

assertions = unittest.TestCase("__init__")


class TestDiscoveryShortInterestApi:
    @mock.patch("gamestonk_terminal.discovery.short_interest_model.requests")
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

    @mock.patch("gamestonk_terminal.discovery.short_interest_model.requests")
    @parameterize_from_file(
        "test_get_low_float",
        "../tests/data/discovery_short_interest_model.yaml",
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