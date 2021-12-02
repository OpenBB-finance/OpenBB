""" fundamental_analysis/dcf_view.py tests """
from unittest import TestCase

# import vcr
# from gamestonk_terminal.stocks.fundamental_analysis import dcf_model
# from gamestonk_terminal.stocks.fundamental_analysis.dcf_view import CreateExcelFA


class TestExcelClass(TestCase):
    pass
    # @vcr.use_cassette(
    #     "tests/gamestonk_terminal/stocks/fundamental_analysis/cassettes/test_dcf_view/test_covers_all_tickers.yaml",
    #     record_mode="new_episodes",
    # )
    # def test_covers_all_tickers(self):
    #     for ticker in dcf_model.tickers:
    #         excel = CreateExcelFA(ticker, False)
    #         df_is = excel.get_data("IS", 1, True)
    #         items_is = dcf_model.non_gaap_is + dcf_model.gaap_is
    #         for item in df_is.index:
    #             self.assertIn(item, items_is)
    #         df_bs = excel.get_data("BS", 1, True)
    #         items_bs = dcf_model.non_gaap_bs + dcf_model.gaap_bs
    #         for item in df_bs.index:
    #             self.assertIn(item, items_bs)
    #         df_cf = excel.get_data("CF", 1, True)
    #         items_cf = dcf_model.non_gaap_cf + dcf_model.gaap_cf
    #         for item in df_cf.index:
    #             self.assertIn(item, items_cf)
