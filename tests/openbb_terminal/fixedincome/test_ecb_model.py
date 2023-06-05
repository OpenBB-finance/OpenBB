import pandas as pd
import pytest

from openbb_terminal.fixedincome import ecb_model


@pytest.mark.vcr
def test_get_series_data(recorder):
    """Test get_series_data"""
    data = ecb_model.get_series_data(
        "EST.B.EU000A2X2A25.WT", start_date="2022-01-01", end_date="2022-01-31"
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_ecb_yield_curve(recorder):
    """Test get_ecb_yield_curve"""
    data = ecb_model.get_ecb_yield_curve(
        date="2023-02-15",
        yield_type="spot_rate",
        return_date=True,
        detailed=False,
        any_rating=True,
    )
    assert isinstance(data, tuple)
    recorder.capture(data[0])
