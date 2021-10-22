""" fundamental_analysis/financial_modeling_prep/fmp_view.py tests """
import unittest

from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_view,
)


class TestFMPView(unittest.TestCase):
    def test_fmp_valinvest_score(self):
        self.assertRaises(ValueError, fmp_view.valinvest_score, "GME")
