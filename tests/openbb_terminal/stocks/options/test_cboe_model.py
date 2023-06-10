# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import cboe_model


@pytest.mark.vcr
def test_symbol_directory():
    result_df = cboe_model.get_cboe_directory()
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty


@pytest.mark.vcr
def test_underlying_price():
    result_df = cboe_model.load_options("QQQ")
    hasattr(result_df, "underlying_price")
    assert isinstance(result_df.underlying_price, pd.Series)
    assert isinstance(result_df.underlying_price["price"], float)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_underlying_price_bad_symbol():
    data = cboe_model.load_options("BAD_SYMBOL")
    assert hasattr(data, "underlying_name") is False


@pytest.mark.vcr
def test_underlying_name():
    ticker = cboe_model.load_options("SPX")
    assert hasattr(ticker, "underlying_name")
    assert isinstance(ticker.underlying_name, str)
    assert ticker.underlying_name == "SPX"


@pytest.mark.vcr
def test_last_price():
    ticker = cboe_model.load_options("AAPL")
    assert hasattr(ticker, "last_price")
    assert isinstance(ticker.last_price, float)
    assert ticker.last_price == ticker.underlying_price["price"]


@pytest.mark.vcr
def test_chains():
    ticker = cboe_model.load_options("JPM")
    assert hasattr(ticker, "chains")
    assert ticker.symbol == "JPM"
    assert isinstance(ticker.chains, pd.DataFrame)
    assert ticker.expirations[0] == ticker.chains["expiration"][0]


@pytest.mark.vcr
def test_strikes():
    ticker = cboe_model.load_options("TSLA")
    results_df = ticker
    assert hasattr(results_df, "strikes")
    assert isinstance(results_df.strikes, list)
    assert isinstance(results_df.strikes[0], float)
    assert len(results_df.strikes) > 1


@pytest.mark.vcr
def test_expirations():
    ticker = cboe_model.load_options("OXY")
    assert hasattr(ticker, "expirations")
    assert isinstance(ticker.expirations, list)
    assert isinstance(ticker.expirations[0], str)
    assert ticker.expirations[0] == ticker.chains["expiration"].iloc[0]


@pytest.mark.vcr
def test_hasGreeks_hasIV():
    ticker = cboe_model.load_options("TSLA")
    assert ticker.underlying_name != "TSLA"
    assert ticker.hasGreeks is True
    assert ticker.hasIV is True
