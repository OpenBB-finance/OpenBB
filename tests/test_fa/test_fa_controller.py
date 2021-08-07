""" fundamental_analysis/fa_controller.py tests """
from datetime import datetime, timedelta
from contextlib import contextmanager
import unittest
import io
import sys

# pylint: disable=unused-import
from gamestonk_terminal.stocks.fundamental_analysis import fa_controller


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


class TestFaController(unittest.TestCase):
    start = datetime.now() - timedelta(days=200)
    menuClass = fa_controller.FundamentalAnalysisController("GME", start, "1440min")  # type: ignore
    choices = fa_controller.FundamentalAnalysisController.CHOICES

    def test_fa_controller_help(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        self.menuClass.print_help()
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        for item in self.choices:
            self.assertIn(item, capt)

    def key_metrics_explained(self):
        # Is this base function ever even used?
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        fa_controller.key_metrics_explained([""])
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        self.assertIn("RETURN ON EQUITY", capt)

    def test_menu(self):
        with replace_stdin(io.StringIO("q")):
            capturedOutput = io.StringIO()
            sys.stdout = capturedOutput
            fa_controller.menu("GME", self.start, "1440min")
            sys.stdout = sys.__stdout__
            capt = capturedOutput.getvalue()
            self.assertIn("fraud", capt)
