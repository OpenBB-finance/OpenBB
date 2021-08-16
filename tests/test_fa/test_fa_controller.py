""" fundamental_analysis/fa_controller.py tests """
import io
import sys
import unittest
from contextlib import contextmanager
from datetime import datetime, timedelta

from gamestonk_terminal.stocks.fundamental_analysis import fa_controller
from tests.helpers import check_print


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

    @check_print(assert_in="fraud")
    def test_fa_controller_help(self):
        self.menuClass.print_help()

    @check_print(assert_in="fraud")
    def test_menu(self):
        with replace_stdin(io.StringIO("q")):
            fa_controller.menu("GME", self.start, "1440min")
