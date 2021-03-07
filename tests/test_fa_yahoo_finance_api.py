""" fundamental_analysis/yahoo_finance_api.py tests """
import unittest

# pylint: disable=unused-import
from gamestonk_terminal.fundamental_analysis.yahoo_finance_api import (  # noqa: F401
    info,
    sustainability,
    calendar_earnings,
)


class TestFaYahooFinanceApi(unittest.TestCase):
    def test_info(self):
        info([], "PLTR")

    def test_sustainability(self):
        # Fix: Yahoo sustainability API is flaky
        # sustainability([], "GME")
        return

    def test_calendar_earnings(self):
        calendar_earnings([], "GME")
