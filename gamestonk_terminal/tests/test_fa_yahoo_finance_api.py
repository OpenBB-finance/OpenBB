""" fundamental_analysis/yahoo_finance_api.py tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.fundamental_analysis.yahoo_finance_api import info


class TestFaYahooFinanceApi(unittest.TestCase):
    def test_info(self):
        info([], "PLTR")
