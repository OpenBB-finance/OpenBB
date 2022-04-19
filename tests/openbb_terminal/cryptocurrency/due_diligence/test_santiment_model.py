# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.due_diligence import santiment_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin,dev_activity,interval,start,end",
    [
        ("BTC", "True", "1d", "2022-01-10", "2022-03-08"),
    ],
)
def test_get_github_activity(coin, dev_activity, interval, start, end, recorder):
    df = santiment_model.get_github_activity(
        coin=coin, dev_activity=dev_activity, interval=interval, start=start, end=end
    )
    recorder.capture(df)
