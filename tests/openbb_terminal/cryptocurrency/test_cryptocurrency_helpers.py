import json

import pandas as pd
import pytest
from pycoingecko import CoinGeckoAPI

from openbb_terminal.cryptocurrency.cryptocurrency_helpers import (
    read_data_file,
    _load_coin_map,
    load,
    load_coins_list,
    _create_closest_match_df,
)

# pylint: disable=unused-import

base = "openbb_terminal.cryptocurrency."


def test_load_coin_map():
    with pytest.raises(TypeError):
        _load_coin_map("test.test")


def test_read_data_file(recorder):
    file = read_data_file("coinbase_gecko_map.json")

    recorder.capture(file)


def test_read_data_file_invalid():
    with pytest.raises(TypeError):
        read_data_file("sample.bad")


def test_load_coins_list(recorder):
    value = load_coins_list("coinbase_gecko_map.json", True)

    recorder.capture(value)


def test_load_coins_list_invalud():
    with pytest.raises(TypeError):
        load_coins_list("bad.bad")


def test_create_closet_match_df(recorder):
    df = pd.DataFrame({"id": ["btc", "eth"], "index": [1, 2]})
    value = _create_closest_match_df("btc", df, 5, 0.2)

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin, vs",
    [
        ("btc", "usd"),
    ],
)
def test_load_none(coin, vs):
    df = load(symbol=coin, to_symbol=vs)
    assert df is not None


@pytest.fixture(name="get_bitcoin")
def fixture_get_bitcoin(mocker):
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
    df = load("BTC", to_symbol="usd", source="YahooFinance")
    return df


@pytest.mark.record_stdout
@pytest.mark.vcr
def test_get_coins():
    """Test that pycoingecko retrieves the major coins"""
    coins = CoinGeckoAPI().get_coins()
    bitcoin_list = [coin["id"] for coin in coins]
    test_coins = ["bitcoin", "ethereum", "dogecoin"]
    for test in test_coins:
        assert test in bitcoin_list
