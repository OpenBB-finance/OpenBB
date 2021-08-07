""" fundamental_analysis/business_insider_api.py tests """
import unittest

from gamestonk_terminal.stocks.due_diligence.financial_modeling_prep_view import rating


class TestDdFinancialModelingPrepView(unittest.TestCase):
    def test_rating(self):
        rating([], "PLTR")
