"""Test the econdb_model.py"""

import pytest
from pandas import DataFrame

from openbb_terminal.fixedincome import econdb_model


@pytest.mark.record_http
@pytest.mark.parametrize(
    "frequency, start_date, end_date, kwargs",
    [
        ("monthly", "2019-01-01", "2022-01-01", dict()),
    ],
)
def test_get_treasuries(frequency, start_date, end_date, kwargs):
    df = econdb_model.get_treasuries(
        frequency=frequency, start_date=start_date, end_date=end_date, **kwargs
    )
    assert isinstance(df, DataFrame)
    assert not df.empty
