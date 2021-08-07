""" discovery/seeking_alpha_model.py tests """
import unittest
from unittest import mock

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

from gamestonk_terminal.stocks.discovery.seeking_alpha_model import get_next_earnings

assertions = unittest.TestCase("__init__")


class TestDiscoverySeekingAlphaModel:
    @mock.patch(
        "gamestonk_terminal.stocks.discovery.seeking_alpha_model.get_earnings_html"
    )
    @parameterize_from_file(
        "test_get_next_earnings",
        "../tests/data/discovery_seeking_alpha_model.yaml",
    )
    # pylint: disable=unused-argument
    def test_get_next_earnings(
        self, mock_get_earnings_html, pages, mock_next_earnings_rets, expected_result
    ):
        mock_get_earnings_html.side_effect = mock_next_earnings_rets
        ret = get_next_earnings(pages)

        assertions.assertEqual(
            ret.to_csv().replace("\r\n", "\n"), expected_result.replace("\r\n", "\n")
        )
