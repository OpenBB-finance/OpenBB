# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import options_chains_model


@pytest.mark.vcr
def test_OptionsChains(recorder):
    op = options_chains_model.OptionsChains()
    df1 = op.load_options_chains("AAPL")
    df2 = op.load_options_chains("AAPL", "YahooFinance", pydantic=True)
    assert hasattr(df1, "chains")
    assert hasattr(df2, "underlying_price")
    assert isinstance(df1.underlying_price, pd.Series)
    assert isinstance(df2.chains, dict)
    recorder.capture(
        [df1.chains.columns.to_list(), df1.underlying_price.index.to_list()]
    )
    recorder.capture([df1.underlying_name, df2.underlying_name])
    stats1 = op.calculate_stats(df1)
    stats2 = op.calculate_stats(df2, "strike")
    recorder.capture(stats1.columns.to_list())
    recorder.capture(stats2.columns.to_list())
    straddle = op.calculate_straddle(df1)
    recorder.capture([straddle.index.to_list(), straddle.columns.to_list()])
    strangle = op.calculate_strangle(df2, days=90, moneyness=20)
    recorder.capture([strangle.index.to_list(), strangle.columns.to_list()])
    call_spread = op.calculate_vertical_call_spread(df1)
    recorder.capture([call_spread.index.to_list(), call_spread.columns.to_list()])
    put_spread = op.calculate_vertical_put_spread(df2)
    recorder.capture([put_spread.index.to_list(), put_spread.columns.to_list()])
    strategies = op.get_strategies(
        df1,
        days=[30, 60, 90, 180],
        straddle_strike=df1.last_price,
        strangle_moneyness=[5, 10, 20],
        vertical_calls=[200, 180],
        vertical_puts=[150, 180],
    )
    recorder.capture(strategies["Strategy"].to_list())
