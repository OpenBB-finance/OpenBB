""" fundamental_analysis/market_watch_api.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.fundamental_analysis.market_watch_view import income
from tests.helpers import check_print


class TestFaMarketWatchApi(unittest.TestCase):
    @check_print(assert_in="Sales/Revenue")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/stocks/fundamental_analysis/cassettes/test_market_watch_view/test_income.yaml",
        record_mode="new_episodes",
    )
    def test_income(self):
        income([], "GME")
