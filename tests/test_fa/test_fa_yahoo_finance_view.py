""" fundamental_analysis/yahoo_finance_api.py tests """
import unittest

import vcr

# pylint: disable=unused-import
from gamestonk_terminal.stocks.fundamental_analysis.yahoo_finance_view import (  # noqa: F401
    calendar_earnings,
    info,
    sustainability,
)
from tests.helpers import check_print


class TestFaYahooFinanceApi(unittest.TestCase):
    @check_print(assert_in="Zip")
    @vcr.use_cassette(
        "tests/cassettes/test_fa/test_fa_yahoo/test_info.yaml",
        record_mode="new_episodes",
    )
    def test_info(self):
        info([], "PLTR")

    @check_print(assert_in="GME")
    @vcr.use_cassette(
        "tests/cassettes/test_fa/test_fa_yahoo/test_sustainability.yaml",
        record_mode="new_episodes",
    )
    def test_sustainability(self):
        sustainability([], "GME")

    @check_print(assert_in="Earnings Date")
    @vcr.use_cassette(
        "tests/cassettes/test_fa/test_fa_yahoo/test_calendar_earnings.yaml",
        record_mode="new_episodes",
    )
    def test_calendar_earnings(self):
        calendar_earnings([], "GME")
