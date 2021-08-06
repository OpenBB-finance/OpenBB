""" fundamental_analysis/business_insider_api.py tests """
import unittest

from gamestonk_terminal.stocks.fundamental_analysis.business_insider_view import (
    management,
)


class TestFaBusinessInsiderApi(unittest.TestCase):
    def test_management(self):
        management([], "PLTR")
