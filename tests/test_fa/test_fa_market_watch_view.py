""" fundamental_analysis/market_watch_api.py tests """
import unittest
import sys
import io

import vcr

from gamestonk_terminal.stocks.fundamental_analysis.market_watch_view import income


class TestFaMarketWatchApi(unittest.TestCase):
    @vcr.use_cassette("tests/cassettes/test_fa/test_fa_market/test_income.yaml")
    def test_income(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        income([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Sales/Revenue", capt)
