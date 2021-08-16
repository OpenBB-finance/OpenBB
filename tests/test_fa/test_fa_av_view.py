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
        with open("tests/data/json/fa_av_overview.json") as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if (
        args[0]
        == f"{base}INCOME_STATEMENT&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    ):
        with open("tests/data/json/fa_av_income.json") as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if args[0] == f"{base}BALANCE_SHEET&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}":
        with open("tests/data/json/fa_av_balance.json") as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if args[0] == f"{base}CASH_FLOW&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}":
        with open("tests/data/json/fa_av_cash.json") as f:
            data = json.load(f)
        return MockResponse(data, 200)

    if args[0] == f"{base}EARNINGS&symbol=GME&apikey={cfg.API_KEY_ALPHAVANTAGE}":
        with open("tests/data/json/fa_av_earnings.json") as f:
            data = json.load(f)
        return MockResponse(data, 200)

    return MockResponse(None, 404)


class TestAVView(unittest.TestCase):
    @check_print(assert_in="Price to sales ratio")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_av_overview(self, mock_get):
        # pylint: disable=unused-argument
        av_view.overview([], "GME")

    @check_print(assert_in="Market capitalization")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_av_key(self, mock_get):
        # pylint: disable=unused-argument
        av_view.key([], "GME")

    @check_print(assert_in="Gross profit")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_income_statement(self, mock_get):
        # pylint: disable=unused-argument
        av_view.income_statement([], "GME")

    @check_print(assert_in="Total assets")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_balance_sheet(self, mock_get):
        # pylint: disable=unused-argument
        av_view.balance_sheet([], "GME")

    @check_print(assert_in="Operating cashflow")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_cash_flow(self, mock_get):
        # pylint: disable=unused-argument
        av_view.cash_flow([], "GME")

    @check_print(assert_in="Reported EPS")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_earnings(self, mock_get):
        # pylint: disable=unused-argument
        av_view.earnings([], "GME")

    @check_print(assert_in="Mscore Sub Stats")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_fraud(self, mock_get):
        # pylint: disable=unused-argument
        av_view.fraud([], "GME")
