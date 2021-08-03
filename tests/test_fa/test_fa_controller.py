""" fundamental_analysis/fa_controller.py tests """
from datetime import datetime, timedelta
import unittest
import io
import sys

# pylint: disable=unused-import
from gamestonk_terminal.fundamental_analysis import fa_controller


class TestFaController(unittest.TestCase):
    start = str(datetime.now() - timedelta(days=200))
    menuClass = fa_controller.FundamentalAnalysisController("GME", start, "1440min")
    choices = fa_controller.FundamentalAnalysisController.CHOICES

    def test_fa_controller_help(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        self.menuClass.print_help()
        sys.stdout = sys.__stdout__
        capt = capturedOutput.getvalue()
        for item in self.choices:
            assert item in capt

    def test_key_metrics_explained(self):
        pass

    def test_menu(self):
        # fa_controller.menu("GME", self.start, "1440min")
        pass
