import sys
import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import vcr

from gamestonk_terminal.stocks import stocks_helper
from tests.helpers import check_print


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


class TestMainHelper(unittest.TestCase):
    start = datetime.now() - timedelta(days=200)

    # @vcr.use_cassette(
    #     "tests/gamestonk_terminal/stocks/cassettes/test_stocks_helper/general1.yaml",
    #     record_mode="new_episodes",
    # )
    # @check_print(assert_in="Loading Daily GME")
    # def test_load(self):
    #     values = stocks_helper.load(
    #         ["GME"], "GME", self.start, "1440min", pd.DataFrame()
    #     )
    #     self.assertEqual(values[0], "GME")
    #     self.assertNotEqual(values[1], None)
    #     self.assertEqual(values[2], "1440min")

    @check_print()
    def test_load_clear(self):
        stocks_helper.load(["GME"], "GME", self.start, "1440min", pd.DataFrame())
        values = stocks_helper.clear([], "GME", self.start, "1440min", pd.DataFrame())
        self.assertEqual(values[0], "")
        self.assertEqual(values[1], "")
        self.assertEqual(values[2], "")

    # @check_print()
    # @vcr.use_cassette(
    #     "tests/gamestonk_terminal/stocks/cassettes/test_stocks_helper/general1.yaml",
    #     record_mode="new_episodes",
    # )
    # @patch("matplotlib.pyplot.show")
    # def test_candle(self, mock):
    #     # pylint: disable=unused-argument
    #     stocks_helper.candle("GME", [])

    @check_print(assert_in="Price")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/stocks/cassettes/test_stocks_helper/test_quote.yaml",
        record_mode="new_episodes",
    )
    def test_quote(self):
        stocks_helper.quote(["GME"], "GME")

    @check_print()
    @patch("matplotlib.pyplot.show")
    def test_view(self, mock):
        # pylint: disable=unused-argument
        stocks_helper.view(["GME"], "GME", "1440min", pd.DataFrame())
