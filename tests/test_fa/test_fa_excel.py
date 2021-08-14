""" fundamental_analysis/dcf_view.py tests """
from unittest import TestCase

import vcr

from gamestonk_terminal.stocks.fundamental_analysis.dcf_view import CreateExcelFA
import gamestonk_terminal.stocks.fundamental_analysis.dcf_model as md


class TestExcelClass(TestCase):
    @vcr.use_cassette(
        "tests/cassettes/test_fa/test_fa_excel/test_covers_all_tickers.yaml"
    )
    def test_covers_all_tickers(self):
        for ticker in md.tickers:
            excel = CreateExcelFA(ticker, False)
            df_is = excel.get_data("IS", 1, True)
            items_is = md.non_gaap_is + md.gaap_is
            for item in df_is.index:
                self.assertIn(item, items_is)
            df_bs = excel.get_data("BS", 1, True)
            items_bs = md.non_gaap_bs + md.gaap_bs
            for item in df_bs.index:
                self.assertIn(item, items_bs)
            df_cf = excel.get_data("CF", 1, True)
            items_cf = md.non_gaap_cf + md.gaap_cf
            for item in df_cf.index:
                self.assertIn(item, items_cf)
