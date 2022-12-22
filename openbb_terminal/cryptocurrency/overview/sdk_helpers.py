"""Crypto OV SDK Helper Functions."""
__docformat__ = "numpy"

import pandas as pd

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_long_number_format_with_type_check,
)
from openbb_terminal.cryptocurrency.overview import coinpaprika_model, pycoingecko_model


def globe(source: str = "CoinGecko") -> pd.DataFrame:
    """Get global crypto market data.

    Parameters
    ----------
    source : str, optional
        Source of data, by default "CoinGecko"

    Returns
    -------
    pd.DataFrame
        DataFrame with global crypto market data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> global_market_data = openbb.crypto.ov.globe()

    To get data from CoinPaprika, use the source parameter:
    >>> global_market_data = openbb.crypto.ov.globe(source="coinpaprika")

    """
    if source.lower() == "coingecko":
        df = pycoingecko_model.get_global_info()
        return df
    if source.lower() == "coinpaprika":
        df = coinpaprika_model.get_global_info()
        return df
    return pd.DataFrame()


def exchanges(source: str = "CoinGecko") -> pd.DataFrame:
    """Show top crypto exchanges.

    Parameters
    ----------
    source : str, optional
        Source to get exchanges, by default "CoinGecko"

    Returns
    -------
    pd.DataFrame
        DataFrame with top crypto exchanges

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> exchanges = openbb.crypto.ov.exchanges()
    """
    if source.lower() == "coingecko":
        df = pycoingecko_model.get_exchanges().sort_values(by="Rank", ascending=True)
        return df
    if source.lower() == "coinpaprika":
        df = coinpaprika_model.get_list_of_exchanges("USD")
        cols = [col for col in df.columns if col != "Rank"]
        df[cols] = df[cols].applymap(
            lambda x: lambda_long_number_format_with_type_check(x)
        )
        return df.sort_values(by="Rank", ascending=True).reset_index(drop=True).head(20)
    return pd.DataFrame()
