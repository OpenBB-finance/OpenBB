import pytest
from pandas import DataFrame

from openbb_terminal.cryptocurrency.overview import cryptopanic_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("auth_token", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.record_http
def test_get_news():
    df = cryptopanic_model.get_news(limit=10)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "post_kind, filter_, region, symbol, kwargs",
    [
        ("news", "rising", "en", "btc", {"limit": 10}),
    ],
)
def test_make_request(post_kind, filter_, region, symbol, kwargs):
    response = cryptopanic_model.make_request(
        post_kind=post_kind,
        filter_=filter_,
        region=region,
        symbol=symbol,
        kwargs=kwargs,
    )

    assert isinstance(response, dict)
