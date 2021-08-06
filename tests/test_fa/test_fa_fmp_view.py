""" fundamental_analysis/financial_modeling_prep/fmp_view.py tests """
# Not testing these tests further. I do not have a fmp key
from contextlib import contextmanager
import unittest
import io
import sys

# pylint: disable=unused-import
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_view,
)


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


class TestFMPView(unittest.TestCase):
    def test_fmp_valinvest_score(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        fmp_view.valinvest_score([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        print(capt)
        self.assertIn("Ticker should be a NASDAQ", capt)
