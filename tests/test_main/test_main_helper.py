from datetime import datetime, timedelta
import unittest
from unittest.mock import patch

import pandas as pd

from gamestonk_terminal import main_helper


class TestMainHelper(unittest.TestCase):
    start = datetime.now() - timedelta(days=200)

    def test_load(self):
        values = main_helper.load(["GME"], "GME", self.start, "1440min", pd.DataFrame())
        self.assertEqual(values[0], "GME")
        self.assertNotEqual(values[1], None)
        self.assertEqual(values[2], "1440min")

    def test_load_clear(self):
        main_helper.load(["GME"], "GME", self.start, "1440min", pd.DataFrame())
        values = main_helper.clear([], "GME", self.start, "1440min", pd.DataFrame())
        self.assertEqual(values[0], "")
        self.assertEqual(values[1], "")
        self.assertEqual(values[2], "")

    @patch("matplotlib.pyplot.show")
    def test_candle(self, mock):
        # pylint: disable=unused-argument
        main_helper.candle("GME", ["GME"])
