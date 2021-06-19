""" econ/fred_view.py tests """
import unittest
from unittest import mock
from io import StringIO
import pandas as pd

# pylint: disable=unused-import
from gamestonk_terminal.economy.fred_view import display_fred  # noqa: F401

fred_data_mock = """
,GDP
2019-01-01,21115.309
2019-04-01,21329.877
2019-07-01,21540.325
2019-10-01,21747.394
2020-01-01,21561.139
2020-04-01,19520.114
2020-07-01,21170.252
2020-10-01,21494.731
2021-01-01,22048.894
"""


class TestFredFredView(unittest.TestCase):
    @mock.patch("gamestonk_terminal.economy.fred_view.Fred.get_series")
    def test_display_fred(self, mock_get_series):
        fred_data = pd.read_csv(StringIO(fred_data_mock), header=0, index_col=0)

        mock_get_series.return_value = fred_data

        display_fred(["-t"], "gdp")
