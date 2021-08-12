""" fundamental_analysis/yahoo_finance_api.py tests """
import unittest
import sys
import io

import vcr

# pylint: disable=unused-import
from gamestonk_terminal.stocks.fundamental_analysis.yahoo_finance_view import (  # noqa: F401
    info,
    sustainability,
    calendar_earnings,
)


class TestFaYahooFinanceApi(unittest.TestCase):
    @vcr.use_cassette("tests/cassettes/test_fa/test_fa_yahoo/test_info.yaml")
    def test_info(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        info([], "PLTR")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Zip", capt)

    @vcr.use_cassette("tests/cassettes/test_fa/test_fa_yahoo/test_sustainability.yaml")
    def test_sustainability(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        sustainability([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("GME", capt)

    @vcr.use_cassette(
        "tests/cassettes/test_fa/test_fa_yahoo/test_calendar_earnings.yaml"
    )
    def test_calendar_earnings(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        calendar_earnings([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Earnings Date", capt)
