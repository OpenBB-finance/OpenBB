""" fundamental_analysis/business_insider_api.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.due_diligence.financial_modeling_prep_view import rating


class TestDdFinancialModelingPrepView(unittest.TestCase):
    @vcr.use_cassette("tests/cassettes/test_dd/test_financial_model/test_rating.yaml")
    def test_rating(self):
        rating([], "PLTR")
