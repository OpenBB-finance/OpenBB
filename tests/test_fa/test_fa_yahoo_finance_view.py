""" fundamental_analysis/yahoo_finance_api.py tests """
import unittest

import vcr

# pylint: disable=unused-import
from gamestonk_terminal.stocks.fundamental_analysis.yahoo_finance_view import (  # noqa: F401
    info,
    sustainability,
    calendar_earnings,
)
from tests.helpers import check_print


class TestFaYahooFinanceApi(unittest.TestCase):
    @check_print(assert_in="Zip")
    @vcr.use_cassette("tests/cassettes/test_fa/test_fa_yahoo/test_info.yaml")
    def test_info(self):
        info([], "PLTR")

    @check_print(assert_in="GME")
    @vcr.use_cassette("tests/cassettes/test_fa/test_fa_yahoo/test_sustainability.yaml")
    def test_sustainability(self):
        sustainability([], "GME")

    @check_print(assert_in="Earnings Date")
    @vcr.use_cassette(
        "tests/cassettes/test_fa/test_fa_yahoo/test_calendar_earnings.yaml"
    )
    def test_calendar_earnings(self):
        calendar_earnings([], "GME")
