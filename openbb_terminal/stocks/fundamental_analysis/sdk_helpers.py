"""SDK Helper Functions"""
__docformat__ = "numpy"

import pandas as pd

from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import (
    av_model,
    eodhd_model,
    finviz_model,
    fmp_model,
    polygon_model,
    yahoo_finance_model,
)


def get_overview(symbol: str, source: str = "YahooFinance"):
    """Get overview.

    Parameters
    ----------
    symbol : str
        Symbol to get overview for
    source : str, optional
        Data source for overview, by default "YahooFinance"
        Sources: YahooFinance, AlphaVantage, FinancialModelingPrep, Finviz

    Returns
    -------
    pd.DataFrame
        Dataframe of overview

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> overview = openbb.stocks.fa.overview("AAPL", source="AlphaVantage")
    """
    if source == "YahooFinance":
        return yahoo_finance_model.get_info(symbol=symbol)
    if source == "AlphaVantage":
        return av_model.get_overview(symbol=symbol)
    if source == "FinancialModelingPrep":
        return fmp_model.get_profile(symbol=symbol)
    if source == "Finviz":
        return finviz_model.get_data(symbol=symbol)
    return pd.DataFrame()


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
        Sources: YahooFinance, AlphaVantage, FinancialModelingPrep, Polygon, EODHD
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
    >>> income_statement = openbb.stocks.fa.income("AAPL", source="YahooFinance")

    If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
    >>> quarterly_income_statement = openbb.stocks.fa.income("AAPL", source="AlphaVantage", quarterly=True)
    """
    if source == "YahooFinance":
        if quarterly:
            console.print(
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


def get_balance_sheet(
    symbol: str,
    quarterly: bool = False,
    ratios: bool = False,
    source: str = "YahooFinance",
    limit: int = 10,
) -> pd.DataFrame:
    """Get balance sheet.

    Parameters
    ----------
    symbol : str
        Symbol to get balance sheet for
    source : str, optional
        Data source for balance sheet, by default "YahooFinance"
        Sources: YahooFinance, AlphaVantage, FinancialModelingPrep, Polygon, EODHD
    quarterly : bool, optional
        Flag to get quarterly data
    ratios : bool, optional
       Flag to return data as a percent change.
    limit : int
        Number of statements to return (free tiers may be limited to 5 years)

    Returns
    -------
    pd.DataFrame
        Dataframe of balance sheet

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> balance_sheet = openbb.stocks.fa.balance("AAPL", source="YahooFinance")

    If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
    >>> quarterly_income_statement = openbb.stocks.fa.balance("AAPL", source="AlphaVantage", quarterly=True)
    """
    if source == "YahooFinance":
        if quarterly:
            console.print(
                "Quarterly statements not available from Yahoo Finance.  Returning annual"
            )
        df = yahoo_finance_model.get_financials(
            symbol=symbol, statement="balance-sheet", ratios=ratios
        )
        return df
    if source == "AlphaVantage":
        df = av_model.get_balance_sheet(
            symbol=symbol, quarterly=quarterly, ratios=ratios, limit=limit
        )
        return df
    if source == "FinancialModelingPrep":
        df = fmp_model.get_balance(
            symbol=symbol, limit=limit, quarterly=quarterly, ratios=ratios
        )
        return df
    if source == "Polygon":
        df = polygon_model.get_financials(symbol, "balance", quarterly, ratios)
        return df
    if source == "EODHD":
        df = eodhd_model.get_financials(symbol, "balance", quarterly, ratios)
        return df
    return pd.DataFrame()


def get_cash_flow(
    symbol: str,
    quarterly: bool = False,
    ratios: bool = False,
    source: str = "YahooFinance",
    limit: int = 10,
) -> pd.DataFrame:
    """Get Cash Flow.

    Parameters
    ----------
    symbol : str
        Symbol to get cash flow for
    source : str, optional
        Data source for cash flow, by default "YahooFinance"
        Sources: YahooFinance, AlphaVantage, FinancialModelingPrep, Polygon, EODHD
    quarterly : bool, optional
        Flag to get quarterly data
    ratios : bool, optional
       Flag to return data as a percent change.
    limit : int
        Number of statements to return (free tiers may be limited to 5 years)

    Returns
    -------
    pd.DataFrame
        Dataframe of cash flow

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> cash_flow = openbb.stocks.fa.cash("AAPL", source="YahooFinance")

    If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
    >>> quarterly_income_statement = openbb.stocks.fa.cash("AAPL", source="AlphaVantage", quarterly=True)
    """
    if source == "YahooFinance":
        if quarterly:
            console.print(
                "Quarterly statements not available from Yahoo Finance.  Returning annual"
            )
        df = yahoo_finance_model.get_financials(
            symbol=symbol, statement="cash-flow", ratios=ratios
        )
        return df
    if source == "AlphaVantage":
        df = av_model.get_cash_flow(
            symbol=symbol, quarterly=quarterly, ratios=ratios, limit=limit
        )
        return df
    if source == "FinancialModelingPrep":
        df = fmp_model.get_cash(
            symbol=symbol, limit=limit, quarterly=quarterly, ratios=ratios
        )
        return df
    if source == "Polygon":
        df = polygon_model.get_financials(symbol, "cash", quarterly, ratios)
        return df
    if source == "EODHD":
        df = eodhd_model.get_financials(symbol, "cash", quarterly, ratios)
        return df
    return pd.DataFrame()


def earnings(
    symbol: str, source: str = "YahooFinance", quarterly: bool = False
) -> pd.DataFrame:
    """Get earnings data.

    Parameters
    ----------
    symbol : str
        Stock ticker
    source : str, optional
         Source to use, by default "AlphaVantage"
         Sources: YahooFinance, AlphaVantage
    quarterly : bool, optional
        Flag to get quarterly data (AlphaVantage only), by default False.

    Returns
    -------
    pd.DataFrame
        Dataframe of earnings

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_earnings = openbb.stocks.fa.earnings("AAPL", source ="YahooFinance")

    To obtain quarterly earnings, use the quarterly flag with AlphaVantage
    >>> aapl_earnings = openbb.stocks.fa.metrics("earnings", source ="AlphaVantage", quarterly=True)
    """
    if source == "YahooFinance":
        df = yahoo_finance_model.get_earnings_history(symbol)
        return df
    if source == "AlphaVantage":
        df = av_model.get_earnings(symbol, quarterly)
        return df
    return pd.DataFrame()
