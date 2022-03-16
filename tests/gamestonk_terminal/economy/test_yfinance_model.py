# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import yfinance_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "index, interval, start_date, end_date, column",
    [
        ["sp500", "1d", "2022-01-01", "2022-02-02", "Adj Close"],
        ["nasdaq", "1wk", "2020-06-06", "2020-07-07", "Close"],
        ["dowjones", "1mo", "2015-01-01", "2015-02-02", "Volume"],
        ["cac40", "3mo", "2010-01-01", "2016-02-06", "High"],
    ],
)
def test_get_index(index, interval, start_date, end_date, column):
    result_df = yfinance_model.get_index(index, interval, start_date, end_date, column)

    assert isinstance(result_df, pd.Series)
