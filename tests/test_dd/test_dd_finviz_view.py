""" due_diligence/finviz_api.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.due_diligence.finviz_view import analyst

from tests.helpers import check_print


class TestDdFinvizApi(unittest.TestCase):
    @check_print(assert_in="category")
    @vcr.use_cassette("tests/cassettes/test_dd/test_finzin/test_analyst.yaml")
    def test_analyst(self):
        analyst([], "PLTR")
