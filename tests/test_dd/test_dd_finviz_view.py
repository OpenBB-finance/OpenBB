""" due_diligence/finviz_api.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.due_diligence.finviz_model import get_analyst_data
from tests.helpers import check_print


class TestDdFinvizApi(unittest.TestCase):
    @check_print(assert_in="category")
    @vcr.use_cassette(
        "tests/cassettes/test_dd/test_finzin/test_analyst.yaml",
        record_mode="new_episodes",
    )
    def test_analyst(self):
        df = get_analyst_data(ticker="PLTR")
        print(df.to_string())
