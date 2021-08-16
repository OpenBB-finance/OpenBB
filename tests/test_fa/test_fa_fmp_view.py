""" fundamental_analysis/financial_modeling_prep/fmp_view.py tests """
import sys
import unittest

# Not testing these tests further. I do not have a fmp key
from contextlib import contextmanager

import vcr

from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_view,
)
from tests.helpers import check_print


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


class TestFMPView(unittest.TestCase):
    @check_print(assert_in="Ticker should be a NASDAQ")
    @vcr.use_cassette("tests/cassettes/test_fa/test_fa_fmp/test_fmp_valinvest.yaml")
    def test_fmp_valinvest_score(self):
        fmp_view.valinvest_score([], "GME")
