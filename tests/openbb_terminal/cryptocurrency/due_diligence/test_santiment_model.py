# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.due_diligence import santiment_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "MOCK_API_KEY")],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "symbol,dev_activity,interval,start,end",
    [
        ("BTC", "True", "1d", "2022-01-10", "2022-03-08"),
    ],
)
def test_get_github_activity(symbol, dev_activity, interval, start, end, recorder):
    start = start + "T00:00:00Z"
    end = end + "T00:00:00Z"
    df = santiment_model.get_github_activity(
        symbol=symbol,
        dev_activity=dev_activity,
        interval=interval,
        start_date=start,
        end_date=end,
    )
    recorder.capture(df)
