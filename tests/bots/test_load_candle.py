from datetime import datetime
import pytest
from bots.load_candle import dt_utcnow_local_tz, stock_data


def test_dt_utcnow_local_tz():
    value = dt_utcnow_local_tz()
    assert isinstance(value, datetime)


@pytest.mark.skip
@pytest.mark.vcr
def test_stock_data(recorder):
    value = stock_data("TSLA")
    df = value[0]
    df.index = df.index.strftime("%Y-%m-%d")
    recorder.capture(df)
