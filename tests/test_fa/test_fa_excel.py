""" fundamental_analysis/dcf_model.py tests """
from unittest import TestCase

import vcr

from gamestonk_terminal.stocks.fundamental_analysis.dcf_model import CreateExcelFA
import gamestonk_terminal.stocks.fundamental_analysis.excel.variables as var


class TestExcelClass(TestCase):
    @vcr.use_cassette("tests/cassettes/test_fa/test_covers_all_tickers.yaml")
    def test_covers_all_tickers(self):
        for ticker in var.tickers:
            excel = CreateExcelFA(ticker, False, False)
            df_is = excel.get_data("IS", 1, True)
            items_is = var.non_gaap_is + var.gaap_is
            for item in df_is.index:
                self.assertIn(item, items_is)
            df_bs = excel.get_data("BS", 1, True)
            items_bs = var.non_gaap_bs + var.gaap_bs
            for item in df_bs.index:
                self.assertIn(item, items_bs)
            df_cf = excel.get_data("CF", 1, True)
            items_cf = var.non_gaap_cf + var.gaap_cf
            for item in df_cf.index:
                self.assertIn(item, items_cf)
