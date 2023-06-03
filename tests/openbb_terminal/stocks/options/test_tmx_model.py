# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import tmx_model

# pylint: disable=no-member


@pytest.fixture(scope="module")
@pytest.mark.vcr
def test_get_all_symbols(recorder):
    result_df = tmx_model.get_all_ticker_symbols()
    recorder.capture(result_df)
    assert isinstance(result_df, pd.DataFrame)


@pytest.mark.vcr
def test_underlying_price(recorder):
    result_df = tmx_model.get_underlying_price("XIU")
    result_df2 = tmx_model.Chains().get_chains("XIU").underlying_price
    assert isinstance(result_df, pd.Series)
    recorder.capture(pd.concat([result_df, result_df2], axis=1))


@pytest.mark.record_stdout
def test_underlying_price_bad_symbol():
    result_df = tmx_model.get_underlying_price("BAD_SYMBOL")
    assert result_df.empty


@pytest.mark.vcr
def test_underlying_name(recorder):
    ticker = tmx_model.Chains().get_chains("BAM")
    result_df = ticker.underlying_name
    recorder.capture(result_df)
    assert isinstance(result_df, str)


@pytest.mark.vcr
def test_check_symbol(recorder):
    ticker = tmx_model.Chains()
    result_df = ticker.check_symbol("BAD_SYMBOL")
    assert isinstance(result_df, bool)
    result_df2 = ticker.check_symbol("CM")
    recorder.capture([result_df, result_df2])
    assert result_df2 is True


@pytest.mark.vcr
def test_last_price(recorder):
    ticker = tmx_model.load_options("AC")
    result_df = ticker.last_price
    assert isinstance(result_df, float)
    ticker2 = tmx_model.load_options("AC", "2021-12-28")
    result_df2 = ticker2.last_price
    assert isinstance(result_df2, float)
    assert result_df != result_df2
    recorder.capture([result_df, result_df2])


@pytest.mark.vcr
def test_chains(recorder):
    ticker = tmx_model.Chains().get_chains("BMO")
    results_df = ticker.chains
    assert not results_df.empty
    recorder.capture(results_df)


@pytest.mark.vcr
def test_strikes(recorder):
    ticker = tmx_model.Chains().get_chains("RY")
    results_df = ticker.strikes
    assert isinstance(results_df, list)
    recorder.capture(results_df)


@pytest.mark.vcr
def test_eodchains_holiday(recorder):
    ticker = tmx_model.Chains().get_eodchains("SU", "2018-12-25")
    results_df = ticker.chains
    assert not results_df.empty
    recorder.capture(results_df)


@pytest.mark.vcr
def test_expirations(recorder):
    ticker = tmx_model.Chains().get_chains("VFV")
    results_df = ticker.expirations
    assert isinstance(results_df, list)
    ticker.get_eodchains("VFV", "2021-12-28")
    results_df2 = ticker.expirations
    assert isinstance(results_df2, list)
    assert results_df != results_df2
    recorder.capture([results_df, results_df2])


@pytest.mark.vcr
def test_SYMBOLS(recorder):
    ticker = tmx_model.Chains()
    results_df = ticker.SYMBOLS
    assert not results_df.empty
    recorder.capture(results_df)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_hasGreeks_hasIV():
    ticker = tmx_model.Chains()
    assert ticker.chains.empty
    ac = tmx_model.load_options("AC")
    assert ac.hasGreeks is False
    assert ac.hasIV is False
