# pylint: disable=no-member

# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import options_chains_model


@pytest.mark.vcr
def test_OptionsChains(recorder):
    df1 = options_chains_model.OptionsChains("AAPL")
    df2 = options_chains_model.OptionsChains("AAPL", "YahooFinance", pydantic=True)
    assert hasattr(df1, "chains")
    assert hasattr(df2, "underlying_price")
    assert isinstance(df1.underlying_price, pd.Series)
    assert isinstance(df2.chains, dict)
    recorder.capture(
        [df1.chains.columns.to_list(), df1.underlying_price.index.to_list()]
    )
    recorder.capture([df1.underlying_name, df2.underlying_name])
    stats1 = df1.get_stats()
    stats2 = df2.get_stats("strike")
    recorder.capture(stats1.columns.to_list())
    recorder.capture(stats2.columns.to_list())
    straddle = df1.get_straddle()
    recorder.capture([straddle.index.to_list(), straddle.columns.to_list()])
    strangle = df1.get_strangle(days=90, moneyness=20)
    recorder.capture([strangle.index.to_list(), strangle.columns.to_list()])
    call_spread = df1.get_vertical_call_spread()
    recorder.capture([call_spread.index.to_list(), call_spread.columns.to_list()])
    put_spread = df1.get_vertical_put_spread()
    recorder.capture([put_spread.index.to_list(), put_spread.columns.to_list()])
    strategies = df1.get_strategies(
        days=[30, 60, 90, 180],
        straddle_strike=df1.last_price,
        strangle_moneyness=[5, 10, 20],
        vertical_calls=[200, 180],
        vertical_puts=[150, 180],
    )
    recorder.capture(strategies["Strategy"].to_list())
    vertical_skew = df1.get_skew()
    recorder.capture(vertical_skew.columns.to_list())
    horizontal_skew = df2.get_skew(moneyness=10)
    recorder.capture(horizontal_skew.columns.to_list())
