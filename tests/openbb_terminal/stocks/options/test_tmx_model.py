# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import tmx_model


@pytest.mark.vcr
def test_get_all_symbols(recorder):
    result_df = tmx_model.get_all_ticker_symbols()
    recorder.capture(result_df)
    assert isinstance(result_df, pd.DataFrame)


@pytest.mark.vcr
def test_get_underlying_price(recorder):
    result_df = tmx_model.get_underlying_price("XIU")
    result_df2 = tmx_model.Ticker().get_quotes("XIU").underlying_price
    assert isinstance(result_df, pd.Series)
    recorder.capture(pd.concat([result_df, result_df2], axis=1))


@pytest.mark.vcr
def test_get_underlying_price_bad_symbol(recorder):
    result_df = tmx_model.get_underlying_price("BAD_SYMBOL")
    assert not result_df
    recorder.capture(result_df)


@pytest.mark.vcr
def test_get_underlying_name(recorder):
    ticker = tmx_model.Ticker().get_quotes("BAM")
    result_df = ticker.underlying_name
    recorder.capture(result_df)
    assert isinstance(result_df, str)


@pytest.mark.vcr
def test_check_symbol(recorder):
    ticker = tmx_model.Ticker()
    result_df = ticker.check_symbol("BAD_SYMBOL")
    assert isinstance(result_df, bool)
    result_df2 = ticker.check_symbol("CM")
    recorder.capture([result_df, result_df2])
    assert result_df2 is True


@pytest.mark.vcr
def test_get_last_price(recorder):
    ticker = tmx_model.Ticker().get_quotes("AC")
    result_df = ticker.last_price
    assert isinstance(result_df, float)
    ticker2 = tmx_model.Ticker().get_eodchains("AC", "2021-12-28")
    result_df2 = ticker2.last_price
    assert isinstance(result_df2, float)
    assert result_df != result_df2
    recorder.capture([result_df, result_df2])


@pytest.mark.vcr
def test_chains(recorder):
    ticker = tmx_model.Ticker().get_quotes("BMO")
    results_df = ticker.chains
    assert not results_df.empty
    recorder.capture(results_df)


@pytest.mark.vcr
def test_strikes(recorder):
    ticker = tmx_model.Ticker().get_quotes("RY")
    results_df = ticker.strikes
    assert isinstance(results_df, list)
    recorder.capture(results_df)


@pytest.mark.vcr
def test_eodchains_holiday(recorder):
    ticker = tmx_model.Ticker().get_eodchains("SU", "2018-12-25")
    results_df = ticker.chains
    assert not results_df.empty
    recorder.capture(results_df)
