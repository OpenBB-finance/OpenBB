from datetime import datetime

import pytest
from pandas import DataFrame

from openbb_terminal.fixedincome import oecd_model


@pytest.mark.vcr
@pytest.mark.parametrize("data", ["short", "short_forecast", "long", "long_forecast"])
def test_get_interest_rates(recorder, data):
    """Test get_interest_rates"""
    data = oecd_model.get_interest_rate_data(
        data=data,
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2022-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, DataFrame)
    recorder.capture(data)
