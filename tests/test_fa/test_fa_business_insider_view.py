""" fundamental_analysis/business_insider_api.py tests """
import unittest
import io
import sys

import vcr

from gamestonk_terminal.stocks.fundamental_analysis.business_insider_view import (
    management,
)


class TestFaBusinessInsiderApi(unittest.TestCase):
    @vcr.use_cassette("tests/cassettes/test_fa/test_fa_business/test_management.yaml")
    def test_management(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        management([], "PLTR")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("PLTR", capt)
