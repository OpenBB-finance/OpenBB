""" fundamental_analysis/av_view.py tests """
import json
import sys
import unittest

# Not testing these tests further. I do not have a fmp key
from contextlib import contextmanager
from unittest import mock

from gamestonk_terminal import config_terminal as cfg

# pylint: disable=unused-import
from gamestonk_terminal.stocks.fundamental_analysis import av_view
from tests.helpers import check_print


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


def mocked_requests_get(*args, **kwargs):
    # pylint: disable=unused-argument
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    base = "https://www.alphavantage.co/query?function="
    if args[0] == f"{base}OVERVIEW&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}":
        with open(
            "tests/gamestonk_terminal/stocks/fundamental_analysis/json/test_av_view/fa_av_overview.json",
            encoding="utf8",
        ) as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if (
        args[0]
        == f"{base}INCOME_STATEMENT&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    ):
        with open(
            "tests/gamestonk_terminal/stocks/fundamental_analysis/json/test_av_view/fa_av_income.json",
            encoding="utf8",
        ) as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if args[0] == f"{base}BALANCE_SHEET&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}":
        with open(
            "tests/gamestonk_terminal/stocks/fundamental_analysis/json/test_av_view/fa_av_balance.json",
            encoding="utf8",
        ) as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if args[0] == f"{base}CASH_FLOW&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}":
        with open(
            "tests/gamestonk_terminal/stocks/fundamental_analysis/json/test_av_view/fa_av_cash.json",
            encoding="utf8",
        ) as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if args[0] == f"{base}EARNINGS&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}":
        with open(
            "tests/gamestonk_terminal/stocks/fundamental_analysis/json/test_av_view/fa_av_earnings.json",
            encoding="utf8",
        ) as f:
            data = json.load(f)
        return MockResponse(data, 200)

    return MockResponse(None, 404)


class TestAVView(unittest.TestCase):
    @check_print(assert_in="Price to sales ratio")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_av_overview(self, mock_get):
        # pylint: disable=unused-argument
        av_view.display_overview("GME")

    @check_print(assert_in="Market capitalization")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_av_key(self, mock_get):
        # pylint: disable=unused-argument
        av_view.display_key("GME")

    @check_print(assert_in="netIncome")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_income_statement(self, mock_get):
        # pylint: disable=unused-argument
        av_view.display_income_statement("GME", 1)

    @check_print(assert_in="commonStockSharesOutstanding")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_balance_sheet(self, mock_get):
        # pylint: disable=unused-argument
        av_view.display_balance_sheet("GME", 1)

    @check_print(assert_in="Reported EPS")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_earnings(self, mock_get):
        # pylint: disable=unused-argument
        av_view.display_earnings("GME", 1)

    @check_print(assert_in="")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_fraud(self, mock_get):
        # pylint: disable=unused-argument
        av_view.display_fraud("GME")
