import pytest
from pandas import DataFrame

from openbb_terminal.cryptocurrency.overview import coinpaprika_model


@pytest.mark.record_http
def test_get_global_info():
    df = coinpaprika_model.get_global_info()

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbols, sortby, ascend",
    [
        ("ETH", "rank", True),
    ],
)
def test_get_coins_info(symbols, sortby, ascend):
    df = coinpaprika_model.get_coins_info(symbols=symbols, sortby=sortby, ascend=ascend)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbols, sortby, ascend",
    [
        ("ETH", "rank", True),
    ],
)
def test_get_coins_market_info(symbols, sortby, ascend):
    df = coinpaprika_model.get_coins_market_info(
        symbols=symbols, sortby=sortby, ascend=ascend
    )

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbols, sortby, ascend",
    [
        ("ETH", "rank", True),
    ],
)
def test_get_list_of_exchanges(symbols, sortby, ascend):
    df = coinpaprika_model.get_list_of_exchanges(
        symbols=symbols, sortby=sortby, ascend=ascend
    )

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "exchange_id, symbols, sortby, ascend",
    [
        ("binance", "ETH", "pair", True),
    ],
)
def test_get_exchanges_market(exchange_id, symbols, sortby, ascend):
    df = coinpaprika_model.get_exchanges_market(
        exchange_id=exchange_id,
        symbols=symbols,
        sortby=sortby,
        ascend=ascend,
    )

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
def test_get_contract_platform():
    df = coinpaprika_model.get_contract_platform()

    assert isinstance(df, DataFrame)
    assert not df.empty
