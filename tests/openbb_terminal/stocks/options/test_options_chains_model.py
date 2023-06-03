# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.sdk import openbb
from openbb_terminal.stocks.options import options_chains_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


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


@pytest.mark.vcr
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


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_validate_object():
    df = options_chains_model.load_options_chains("SPY")
    assert options_chains_model.validate_object(df, scope="object")
    assert options_chains_model.validate_object(df, scope="strategies")
    assert isinstance(
        options_chains_model.validate_object(df, scope="chains"), pd.DataFrame
    )
    assert isinstance(
        options_chains_model.validate_object(df.chains, scope="chains"), pd.DataFrame
    )
    df = options_chains_model.load_options_chains("NDX", source="Nasdaq")
    assert isinstance(
        options_chains_model.validate_object(df, scope="chains"), pd.DataFrame
    )
    options_chains_model.validate_object(df, scope="strategies")
    options_chains_model.validate_object(df, scope="object")
    options_chains_model.validate_object(df.expirations, scope="chains")
    df = openbb.stocks.load("AAPL")
    options_chains_model.validate_object(df)
    options_chains_model.validate_object(df, scope="strategies")
    df = options_chains_model.load_options_chains("BAD_SYMBOL")
    options_chains_model.validate_object(df)
    options_chains_model.validate_object(df.symbol)


@pytest.mark.vcr
def test_get_nearest_dte(recorder):
    df = options_chains_model.load_options_chains("OXY")
    nearest_dte = options_chains_model.get_nearest_dte(df, 23)
    recorder.capture(int(nearest_dte))


@pytest.mark.vcr
def test_get_nearest_call_strike(recorder):
    df = options_chains_model.load_options_chains("OXY")
    nearest_call_strike = options_chains_model.get_nearest_call_strike(df)
    assert isinstance(nearest_call_strike, float)
    recorder.capture(nearest_call_strike)


@pytest.mark.vcr
def test_get_nearest_put_strike(recorder):
    df = options_chains_model.load_options_chains("OXY")
    nearest_put_strike = options_chains_model.get_nearest_put_strike(df)
    assert isinstance(nearest_put_strike, float)
    recorder.capture(nearest_put_strike)


@pytest.mark.vcr
def test_get_nearest_otm_strike(recorder):
    df = options_chains_model.load_options_chains("OXY")
    nearest_otm_strike = options_chains_model.get_nearest_otm_strike(df)
    assert isinstance(nearest_otm_strike, dict)
    recorder.capture(nearest_otm_strike)


@pytest.mark.vcr
def test_calculate_straddle(recorder):
    df = options_chains_model.load_options_chains("OXY")
    assert isinstance(
        options_chains_model.calculate_straddle(df, payoff=True), pd.DataFrame
    )
    recorder.capture(options_chains_model.calculate_straddle(df))
    recorder.capture(options_chains_model.calculate_straddle(df, payoff=True))


@pytest.mark.vcr
def test_calculate_strangle(recorder):
    df = options_chains_model.load_options_chains("OXY")
    assert isinstance(
        options_chains_model.calculate_strangle(df, payoff=True), pd.DataFrame
    )
    recorder.capture(options_chains_model.calculate_strangle(df))
    recorder.capture(options_chains_model.calculate_strangle(df, payoff=True))


@pytest.mark.vcr
def test_get_strategies(recorder):
    df = options_chains_model.load_options_chains("OXY")
    assert isinstance(options_chains_model.get_strategies(df), pd.DataFrame)
    recorder.capture(options_chains_model.get_strategies(df))
    recorder.capture(options_chains_model.get_strategies(df, strangle=True))
    recorder.capture(
        options_chains_model.get_strategies(
            df,
            days=[1, 5, 10],
            moneyness=[0.5, 2.5, 5, 10],
            straddle=True,
            strangle=True,
        )
    )
