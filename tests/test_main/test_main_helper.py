from datetime import datetime, timedelta
from contextlib import contextmanager
import unittest
from unittest.mock import patch
import sys
import io

import pandas as pd

from gamestonk_terminal import terminal_helper
from gamestonk_terminal.stocks import stocks_helper


def return_val(x, shell, check):
    # pylint: disable=unused-argument
    # pylint: disable=R0903
    class ReturnVal:
        def __init__(self, code):
            self.returncode = code

    return ReturnVal(2)


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


class TestMainHelper(unittest.TestCase):
    start = datetime.now() - timedelta(days=200)

    def test_load(self):
        values = stocks_helper.load(
            ["GME"], "GME", self.start, "1440min", pd.DataFrame()
        )
        self.assertEqual(values[0], "GME")
        self.assertNotEqual(values[1], None)
        self.assertEqual(values[2], "1440min")

    def test_load_clear(self):
        stocks_helper.load(["GME"], "GME", self.start, "1440min", pd.DataFrame())
        values = stocks_helper.clear([], "GME", self.start, "1440min", pd.DataFrame())
        self.assertEqual(values[0], "")
        self.assertEqual(values[1], "")
        self.assertEqual(values[2], "")

    @patch("matplotlib.pyplot.show")
    def test_candle(self, mock):
        # pylint: disable=unused-argument
        stocks_helper.candle("GME", ["GME"])

    def test_quote(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        stocks_helper.quote(["GME"], "GME")
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Price", capt)

    @patch("matplotlib.pyplot.show")
    def test_view(self, mock):
        # pylint: disable=unused-argument
        stocks_helper.view(["GME"], "GME", "1440min", pd.DataFrame())

    def test_check_api_keys(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        terminal_helper.check_api_keys()
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("ALPHA", capt)

    def test_print_goodbye(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        terminal_helper.print_goodbye()
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertTrue(len(capt) > 0)

    @patch("subprocess.run", side_effect=return_val)
    def test_update_terminal(self, mock):
        # pylint: disable=unused-argument
        value = terminal_helper.update_terminal()
        print(f"Fail value: {value}")
        self.assertEqual(value, 2)

    def test_about_us(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        terminal_helper.about_us()
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Thanks for using Gamestonk Terminal.", capt)

    def test_bootup(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        terminal_helper.bootup()
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Welcome to Gamestonk Terminal Beta", capt)

    @patch("subprocess.run", side_effect=return_val)
    def test_reset(self, mock):
        # pylint: disable=unused-argument
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        terminal_helper.reset()
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("Unfortunately, resetting wasn't", capt)
