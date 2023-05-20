# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
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
