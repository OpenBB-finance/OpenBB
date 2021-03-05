""" fundamental_analysis/yahoo_finance_api.py tests """
# noqa: F401
import unittest

# pylint: disable=unused-import
import pytest

from gamestonk_terminal.fundamental_analysis.yahoo_finance_api import (
    info,
    sustainability,
    calendar_earnings,
)


class TestFaYahooFinanceApi(unittest.TestCase):
    def test_info(self):
        info([], "PLTR")

    def test_sustainability(self):
        sustainability([], "PLTR")

    def test_calendar_earnings(self):
        calendar_earnings([], "PLTR")
