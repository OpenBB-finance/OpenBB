# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import options_chains_model


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_load_options_chains_bad_source():
    options_chains_model.load_options_chains("AAPL", source="BAD_SOURCE")


@pytest.mark.vcr
def test_load_options_chains_compare_sources(recorder):
    df1 = options_chains_model.load_options_chains("AAPL")
    assert df1.hasGreeks is True
    recorder.capture(df1.chains)
    df2 = options_chains_model.load_options_chains("AAPL", source="YahooFinance")
    assert not df2.hasGreeks
    assert df1 != df2
    recorder.capture(df2.chains)
    df3 = options_chains_model.load_options_chains("AAPL", source="Nasdaq")
    assert df2.underlying_name != df3.underlying_name
    recorder.capture(df3.chains)


@pytest.mark.vrc
def test_load_options_pydantic(recorder):
    df = options_chains_model.load_options_chains("SPY", pydantic=True)
    df1 = options_chains_model.load_options_chains("SPY")
    assert df.underlying_name == df1.underlying_name
    recorder.capture(df1.underlying_price)
    recorder.capture(df.underlying_price)


@pytest.mark.vcr
def test_calculate_stats(recorder):
    df = options_chains_model.load_options_chains("SPY")
    stats = options_chains_model.calculate_stats(df)
    assert isinstance(stats, pd.DataFrame)
    recorder.capture(stats)
    stats1 = options_chains_model.calculate_stats(df, "strike")
    assert isinstance(stats1, pd.DataFrame)
    recorder.capture(stats1)
    stats2 = options_chains_model.calculate_stats(df.expirations, "strike")
    assert stats2.empty


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_calculate_stats_bad_input():
    df = options_chains_model.load_options_chains("SPY", source="TMX")
    options_chains_model.calculate_stats(df)
    options_chains_model.calculate_stats(df.SYMBOLS)
    df = options_chains_model.load_options_chains("SPY", source="Nasdaq")
    options_chains_model.calculate_stats(df.underlying_price)
    options_chains_model.calculate_stats(df.last_price)
    options_chains_model.calculate_stats(df.underlying_name)
