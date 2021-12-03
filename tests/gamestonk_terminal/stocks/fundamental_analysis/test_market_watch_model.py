""" fundamental_analysis/market_watch_api.py tests """
import unittest
from unittest import mock

from gamestonk_terminal.stocks.fundamental_analysis.market_watch_model import (
    prepare_df_financials,
)

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

assertions = unittest.TestCase("__init__")


class TestFaMarketWatchApiUnit:
    @mock.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.market_watch_model.requests"
    )
    @parameterize_from_file(
        "test_prepare_df_financials",
        "../tests/gamestonk_terminal/stocks/fundamental_analysis/yaml/test_market_watch_model/watch_model.yaml",
    )
    # pylint: disable=too-many-arguments
    def test_prepare_df_financials(
        self, mock_request_get, ticker, statement, mock_market_watch, expected_result
    ):
        mock_request_get.get().text = mock_market_watch
        ret = prepare_df_financials(ticker, statement)

        assertions.assertEqual.__self__.maxDiff = None
        assertions.assertEqual(
            ret.to_csv().replace("\r\n", "\n"),
            expected_result.replace("\r\n", "\n"),
        )
