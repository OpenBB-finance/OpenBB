import pytest

from openbb_terminal.cryptocurrency.onchain import shroom_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("x-api-key", "MOCK_AUTHORIZATION"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "user_address, address_name",
    [
        ("0x0000000000000000000000000000000000000000", ""),
    ],
)
def test_get_total_value_locked(user_address, address_name, recorder):
    df = shroom_model.get_total_value_locked(
        user_address=user_address, address_name=address_name
    )
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "symbols",
    [
        ["DAI", "USDT", "BUSD", "USDC"],
    ],
)
def test_get_daily_transactions(symbols, recorder):
    df = shroom_model.get_daily_transactions(symbols=symbols)
    recorder.capture(df)


@pytest.mark.vcr
def test_get_dapp_stats(recorder):
    df = shroom_model.get_dapp_stats(platform="curve")
    recorder.capture(df)
