"""Trend Indicators Technical Analysis Model"""
__docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta


def adx(
    high_values: pd.Series,
    low_values: pd.Series,
    close_values: pd.Series,
    length: int = 14,
    scalar: int = 100,
    drift: int = 1,
):
    """ADX technical indicator

    Parameters
    ----------
    high_values: pd.Series
        High prices
    low_values: pd.Series
        Low prices
    close_values: pd.Series
        close prices
    length: int
        Length of window
    scalar: int
        Scalar variable
    drift: int
        Drift variable

    Returns
    -------
    pd.DataFrame
        DataFrame with adx indicator
    """
    return pd.DataFrame(
        ta.adx(
            high=high_values,
            low=low_values,
            close=close_values,
            length=length,
            scalar=scalar,
            drift=drift,
        ).dropna()
    )


def aroon(
    high_values: pd.Series, low_values: pd.Series, length: int = 25, scalar: int = 100
) -> pd.DataFrame:
    """Aroon technical indicator

    Parameters
    ----------
    high_values: pd.Series
        High prices
    low_values: pd.Series
        Low prices
    length : int
        Length of window
    scalar : int
        Scalar variable

    Returns
    -------
    pd.DataFrame
        DataFrame with aroon indicator
    """

    return pd.DataFrame(
        ta.aroon(
            high=high_values,
            low=low_values,
            length=length,
            scalar=scalar,
        ).dropna()
    )
