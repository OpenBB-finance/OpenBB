"""SDK Helper Functions"""
__docformat__ = "numpy"

import pandas as pd
from openbb_terminal.stocks.fundamental_analysis import (
    yahoo_finance_model,
    polygon_model,
    av_model,
    fmp_model,
    eodhd_model,
)


def get_income_statement(
    symbol: str,
    quarterly: bool = False,
    ratios: bool = False,
    source: str = "YahooFinance",
    limit: int = 10,
) -> pd.DataFrame:
    """Get income statement.

    Parameters
    ----------
    symbol : str
        Symbol to get income statement for
    source : str, optional
        Data source for income statement, by default "YahooFinance"
    quarterly : bool, optional
        Flag to get quarterly data
    ratios : bool, optional
       Flag to return data as a percent change.
    limit : int
        Number of statements to return (free tiers may be limited to 5 years)

    Returns
    -------
    pd.DataFrame
        Dataframe of income statement

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> income_statement = openbb.stocks.fa.income("AAPL", source="YahooFinance)

    If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
    >>> quarterly_income_statement = openbb.stocks.fa.income("AAPL", source="AlphaVantage", quarterly=True)
    """
    if source == "YahooFinance":
        if quarterly:
            print(
                "Quarterly income statement not available from Yahoo Finance.  Returning annual"
            )
        df = yahoo_finance_model.get_financials(
            symbol=symbol, statement="financials", ratios=ratios
        )
        return df
    if source == "AlphaVantage":
        df = av_model.get_income_statements(
            symbol=symbol, quarterly=quarterly, ratios=ratios, limit=limit
        )
        return df
    if source == "FinancialModelingPrep":
        df = fmp_model.get_income(
            symbol=symbol, limit=limit, quarterly=quarterly, ratios=ratios
        )
        return df
    if source == "Polygon":
        df = polygon_model.get_financials(symbol, "income", quarterly, ratios)
        return df
    if source == "EODHD":
        df = eodhd_model.get_financials(symbol, "income", quarterly, ratios)
        return df
    return pd.DataFrame()
