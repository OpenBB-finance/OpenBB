""" due_diligence/finviz_api.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.due_diligence.finviz_view import analyst


class TestDdFinvizApi(unittest.TestCase):
    @vcr.use_cassette("tests/cassettes/test_dd/test_finzin/test_analyst.yaml")
    def test_analyst(self):
        analyst([], "PLTR")
