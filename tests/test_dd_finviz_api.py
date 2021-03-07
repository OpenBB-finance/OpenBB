""" due_diligence/finviz_api.py tests """
import unittest

from gamestonk_terminal.due_diligence.finviz_api import analyst


class TestDdFinvizApi(unittest.TestCase):
    def test_analyst(self):
        analyst([], "PLTR")
