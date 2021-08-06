""" fundamental_analysis/market_watch_api.py tests """
import unittest

from gamestonk_terminal.stocks.fundamental_analysis.market_watch_view import income


class TestFaMarketWatchApi(unittest.TestCase):
    def test_income(self):
        income([], "GME")
