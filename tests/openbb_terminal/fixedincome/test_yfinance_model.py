"""Test the yfinance_model.py"""

import pytest
from pandas import Series

from openbb_terminal.fixedincome import yfinance_model


@pytest.mark.record_http
@pytest.mark.parametrize(
    "series_id, interval, start_date, end_date, column",
    [
        ("^GSPC", "1d", "2021-01-01", "2022-01-01", "Adj Close"),
    ],
)
def test_get_series(series_id, interval, start_date, end_date, column):
    series = yfinance_model.get_series(
        series_id=series_id,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        column=column,
    )
    assert isinstance(series, Series)
    assert not series.empty
