"""Quantitative Analysis Models"""
__docformat__ = "numpy"

from typing import Any, Tuple

import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose


def summary(df_stock: pd.DataFrame) -> pd.DataFrame:
    """Print summary statistics

    Parameters
    ----------
    other_args : str
        Command line arguments to be processed with argparse
    ticker : str
        Ticker of the stock
    stock : pd.DataFrame
        Stock data
    """

    df_stats = df_stock.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    df_stats.loc["var"] = df_stats.loc["std"] ** 2

    return df_stats


def seasonal_decomposition(
    df_stock: pd.DataFrame, multiplicative: bool
) -> Tuple[Any, pd.DataFrame, pd.DataFrame]:
    """Perform seasonal decomposition

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    multiplicative : bool
        Boolean to indicate multiplication instead of addition

    Returns
    -------
    result: Any
        Result of statsmodels seasonal_decompose
    cycle: pd.DataFrame
        Filtered cycle
    trend: pd.DataFrame
        Filtered Trend
    """
    seasonal_periods = 5
    # Hodrick-Prescott filter
    # See Ravn and Uhlig: http://home.uchicago.edu/~huhlig/papers/uhlig.ravn.res.2002.pdf
    lamb = 107360000000

    model = ["additive", "multiplicative"][multiplicative]

    result = seasonal_decompose(df_stock, model=model, period=seasonal_periods)
    cycle, trend = sm.tsa.filters.hpfilter(
        result.trend[result.trend.notna().values], lamb=lamb
    )

    return result, pd.DataFrame(cycle), pd.DataFrame(trend)
