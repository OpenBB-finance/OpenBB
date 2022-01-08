import pytest

from gamestonk_terminal.cryptocurrency.due_diligence import glassnode_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "asset,interval,since,until",
    [
        ("BTC", "24h", 1_601_596_800, 1_641_573_787),
    ],
)
def test_get_close_price(asset, interval, since, until, recorder):
    df = glassnode_model.get_close_price(asset, interval, since, until)
    recorder.capture(df)
