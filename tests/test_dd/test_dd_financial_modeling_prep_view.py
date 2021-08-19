""" fundamental_analysis/business_insider_api.py tests """
import unittest

import vcr

from gamestonk_terminal.stocks.due_diligence.fmp_view import rating
from tests.helpers import check_print


class TestDdFinancialModelingPrepView(unittest.TestCase):
    @check_print(assert_in="Rating")
    @vcr.use_cassette(
        "tests/cassettes/test_dd/test_financial_model/test_rating.yaml",
        record_mode="new_episodes",
    )
    def test_rating(self):
        rating(ticker="PLTR", num=10)
