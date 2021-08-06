""" fundamental_analysis/av_view.py tests """
# Not testing these tests further. I do not have a fmp key
from contextlib import contextmanager
import unittest
from unittest import mock
import io
import sys
import json

# pylint: disable=unused-import
from gamestonk_terminal.stocks.fundamental_analysis import av_view

from gamestonk_terminal import config_terminal as cfg


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
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_av_overview(self, mock_get):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        av_view.overview([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Price to sales ratio", capt)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_av_key(self, mock_get):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        av_view.key([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Market capitalization", capt)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_income_statement(self, mock_get):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        av_view.income_statement([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Gross profit", capt)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_balance_sheet(self, mock_get):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        av_view.balance_sheet([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Total assets", capt)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_cash_flow(self, mock_get):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        av_view.cash_flow([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Operating cashflow", capt)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_earnings(self, mock_get):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        av_view.earnings([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Reported EPS", capt)

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_fraud(self, mock_get):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        av_view.fraud([], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Mscore Sub Stats", capt)
