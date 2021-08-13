""" econ/fred_view.py tests """
import unittest
from unittest import mock
import io

import pandas as pd

from gamestonk_terminal.economy.fred_view import display_series
from tests.helpers import check_print

fred_data_mock = """
For 'gdp', series IDs found: GDP, GDPC1, M2V, GFDEGDQ188S, PAYEMS.

GDP
---
Date
2019-01-01    21001.591
2019-04-01    21289.268
2019-07-01    21505.012
2019-10-01    21694.458
2020-01-01    21481.367
2020-04-01    19477.444
2020-07-01    21138.574
2020-10-01    21477.597
2021-01-01    22038.226
2021-04-01    22722.581
"""


class TestFredFredView(unittest.TestCase):
    @check_print(assert_in="No series found for term")
    @mock.patch("gamestonk_terminal.economy.fred_model.get_series_data")
    def test_display_fred(self, mock_get_series):
        fred_data = pd.read_csv(io.StringIO(fred_data_mock), header=0, index_col=0)

        mock_get_series.return_value = fred_data
        display_series(
            series="gdp",
            start_date="2019-01-01",
            raw=True,
            export="",
        )
