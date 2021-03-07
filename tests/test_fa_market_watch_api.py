""" fundamental_analysis/market_watch_api.py tests """
import unittest

from gamestonk_terminal.fundamental_analysis.market_watch_api import income


class TestFaMarketWatchApi(unittest.TestCase):
    def test_income(self):
        income([], "PLTR")
