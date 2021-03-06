""" fundamental_analysis/business_insider_api.py tests """
import unittest

from gamestonk_terminal.due_diligence.financial_modeling_prep_api import rating


class TestDdFinancialModelingPrepApi(unittest.TestCase):
    def test_rating(self):
        rating([], "PLTR")
