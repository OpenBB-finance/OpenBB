""" fundamental_analysis/dcf_view.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.fundamental_analysis import dcf_view
from tests.helpers import check_print


class TestDCFView(unittest.TestCase):
    @check_print(assert_in=" ")
    @vcr.use_cassette(
        "tests/cassettes/test_fa/dcf_view.yaml",
        record_mode="new_episodes",
    )
    def test_management(self):
        dcf = dcf_view.CreateExcelFA("TSLA", False)
        dcf.create_workbook()
