# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.due_diligence import glassnode_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
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


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        (
            "get_close_price",
            dict(asset="BTC", interval="24h", since=1_643_136_577, until=1_643_309_377),
        ),
        (
            "get_non_zero_addresses",
            dict(asset="BTC", interval="24h", since=1_643_136_577, until=1_643_309_377),
        ),
        (
            "get_active_addresses",
            dict(asset="BTC", interval="24h", since=1_643_136_577, until=1_643_309_377),
        ),
        (
            "get_hashrate",
            dict(asset="BTC", interval="24h", since=1_643_136_577, until=1_643_309_377),
        ),
        (
            "get_exchange_balances",
            dict(
                asset="BTC",
                exchange="binance",
                interval="24h",
                since=1_643_136_577,
                until=1_643_309_377,
            ),
        ),
        (
            "get_exchange_net_position_change",
            dict(
                asset="BTC",
                exchange="binance",
                interval="24h",
                since=1_643_136_577,
                until=1_643_309_377,
            ),
        ),
    ],
)
def test_call_func(func, kwargs, recorder):
    result = getattr(glassnode_model, func)(**kwargs)

    recorder.capture(result)
