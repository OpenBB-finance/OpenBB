from datetime import datetime
import pytest
from bots.load_candle import dt_utcnow_local_tz, stock_data


@pytest.mark.bots
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }


@pytest.mark.bots
def test_dt_utcnow_local_tz():
    value = dt_utcnow_local_tz()
    assert isinstance(value, datetime)


@pytest.mark.bots
@pytest.mark.vcr
def test_stock_data(recorder):
    value = stock_data("TSLA")
    df = value[0]
    df.index = df.index.strftime("%Y-%m-%d")
    recorder.capture(df)
