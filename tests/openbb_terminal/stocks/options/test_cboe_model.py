# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import cboe_model


@pytest.mark.vcr
def test_symbol_directory(recorder):
    result_df = cboe_model.get_cboe_directory()
    assert isinstance(result_df, pd.DataFrame)
    recorder.capture(result_df)


@pytest.mark.vcr
def test_underlying_price(recorder):
    result_df = cboe_model.load_options("QQQ")
    recorder.capture(result_df.underlying_price)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_underlying_price_bad_symbol():
    result_df = cboe_model.load_options("BAD_SYMBOL")
    assert result_df.underlying_price.empty


@pytest.mark.vcr
def test_underlying_name(recorder):
    ticker = cboe_model.load_options("SPX")
    result_df = ticker.underlying_name
    recorder.capture(result_df)


@pytest.mark.vcr
def test_last_price(recorder):
    ticker = cboe_model.load_options("AAPL")
    result_df = ticker.last_price
    recorder.capture(result_df)


@pytest.mark.vcr
def test_chains(recorder):
    ticker = cboe_model.load_options("JPM")
    results_df = ticker.chains
    assert not results_df.empty
    recorder.capture(results_df)


@pytest.mark.vcr
def test_strikes(recorder):
    ticker = cboe_model.load_options("TSLA")
    results_df = ticker.strikes
    assert isinstance(results_df, list)
    recorder.capture(results_df)


@pytest.mark.vcr
def test_expirations(recorder):
    ticker = cboe_model.load_options("OXY")
    results_df = ticker.expirations
    assert isinstance(results_df, list)
    recorder.capture(results_df)


@pytest.mark.vcr
def test_hasGreeks_hasIV():
    ticker = cboe_model.Options()
    assert ticker.chains.empty
    ticker = cboe_model.load_options("TSLA")
    ticker.hasGreeks
    ticker.hasIV
    assert ticker.hasGreeks is True
    assert ticker.hasIV is True
