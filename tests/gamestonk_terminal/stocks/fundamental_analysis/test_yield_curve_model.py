""" fundamental_analysis/yield_curve_model.py tests """
import unittest
from datetime import datetime
from io import StringIO
from unittest import mock

import pandas as pd

from gamestonk_terminal.stocks.fundamental_analysis.yield_curve_model import (
    get_yield_curve,
    get_yield_curve_year,
)

# pylint: disable=unused-import
from gamestonk_terminal.test_helper import (  # noqa: F401
    parameterize_from_file,
    pytest_generate_tests,
)

assertions = unittest.TestCase("__init__")


class TestFaYieldCurveModel:
    @mock.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.yield_curve_model.get_yield_curve_year"
    )
    @parameterize_from_file(
        "test_get_yield_curve",
        "../tests/gamestonk_terminal/stocks/fundamental_analysis/yaml/test_yield_curve_model/curve_model.yaml",
    )
    # pylint: disable=too-many-arguments
    def test_get_yield_curve(
        self,
        mock_get_yield_curve_year,
        start,
        end,
        mock_get_yield_curve_year_rets,
        expected_result,
    ):

        rets = []
        for a_ret in mock_get_yield_curve_year_rets:
            rets.append(
                pd.read_csv(StringIO(a_ret), header=0, index_col=0, parse_dates=True)
            )

        mock_get_yield_curve_year.side_effect = rets
        df = get_yield_curve(
            datetime.strptime(start, "%m/%d/%y"),
            datetime.strptime(end, "%m/%d/%y"),
        )

        assertions.assertEqual(
            df.to_csv().replace("\r\n", "\n"), expected_result.replace("\r\n", "\n")
        )

    @mock.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.yield_curve_model.requests"
    )
    @parameterize_from_file(
        "test_get_yield_curve_year",
        "../tests/gamestonk_terminal/stocks/fundamental_analysis/yaml/test_yield_curve_model/curve_model.yaml",
    )
    def test_get_yield_curve_year(
        self, mock_request_get, year, mock_yield_curve_page, expected_result
    ):
        mock_request_get.get().text = mock_yield_curve_page

        ret = get_yield_curve_year(year)

        assertions.assertEqual(
            ret.to_csv().replace("\r\n", "\n"), expected_result.replace("\r\n", "\n")
        )
