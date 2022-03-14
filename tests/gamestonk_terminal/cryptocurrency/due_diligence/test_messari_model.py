# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.due_diligence import messari_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("x-messari-api-key", "mock_x-messari-api-key")],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin,interval,start,end",
    [
        ("BTC", "1d", "2022-01-10", "2022-03-08"),
    ],
)
def test_get_marketcap_dominance(coin, interval, start, end, recorder):
    df = messari_model.get_marketcap_dominance(
        coin=coin, interval=interval, start=start, end=end
    )
    recorder.capture(df)
