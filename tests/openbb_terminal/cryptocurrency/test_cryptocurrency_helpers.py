import json

import pytest
from pycoingecko import CoinGeckoAPI

from openbb_terminal.cryptocurrency.cryptocurrency_helpers import (
    plot_chart,
    load,
    load_ta_data,
    prepare_all_coins_df,
)

# pylint: disable=unused-import

base = "openbb_terminal.cryptocurrency."


def get_bitcoin(mocker):
    # pylint: disable=unused-argument
    mock_load = mocker.patch(
        base
        + "due_diligence.pycoingecko_model.CoinGeckoAPI.get_coin_market_chart_by_id"
    )

    with open(
        "tests/openbb_terminal/cryptocurrency/json/test_cryptocurrency_helpers/btc_usd_test_data.json",
        encoding="utf8",
    ) as f:
        sample_return = json.load(f)
    mock_load.return_value = sample_return
    coin, _, symbol, _, _, _ = load(coin="BTC", source="cp")
    return coin, symbol


# pylint: disable=R0904


def test_coin_api_load(mocker):
    """
    Mock load function through get_coin_market_chart_by_id.
    Mock returns a dict saved as .json
    """
    coin, _ = get_bitcoin(mocker)

    assert coin == "btc-bitcoin"


def test_coin_api_load_df_for_ta(mocker):
    """
    Mock load function through get_coin_market_chart_by_id.
    Mock returns a dict saved as .json
    """
    mock_load = mocker.patch(
        base
        + "due_diligence.pycoingecko_model.CoinGeckoAPI.get_coin_market_chart_by_id"
    )
    _, symbol = get_bitcoin(mocker)
    coin_map_df = prepare_all_coins_df().set_index("Symbol").loc[symbol.upper()].iloc[0]

    with open(
        "tests/openbb_terminal/cryptocurrency/json/test_cryptocurrency_helpers/btc_usd_test_data.json",
        encoding="utf8",
    ) as f:
        sample_return = json.load(f)

    mock_load.return_value = sample_return
    mock_return, vs = load_ta_data(
        coin_map_df=coin_map_df,
        source="cg",
        currency="usd",
        days=30,
    )
    assert mock_return.shape == (31, 4)
    assert vs == "usd"


@pytest.mark.record_stdout
@pytest.mark.vcr
def test_get_coins():
    """Test that pycoingecko retrieves the major coins"""
    coins = CoinGeckoAPI().get_coins()
    bitcoin_list = [coin["id"] for coin in coins]
    test_coins = ["bitcoin", "ethereum", "dogecoin"]
    for test in test_coins:
        assert test in bitcoin_list


@pytest.mark.record_stdout
def test_coin_chart(mocker):
    # pylint: disable=unused-argument
    _, symbol = get_bitcoin(mocker)
    coin_map_df = prepare_all_coins_df().set_index("Symbol").loc[symbol.upper()].iloc[0]

    plot_chart(coin_map_df=coin_map_df, source="cg", currency="usd", days=30)
