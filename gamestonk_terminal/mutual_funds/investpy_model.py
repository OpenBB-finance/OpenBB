"""Investpy Model"""
__docformat__ = "numpy"

from datetime import datetime, timedelta
from typing import Tuple

import investpy
import pandas as pd
from rich.console import Console

console = Console()


def search_funds(by: str = "name", value: str = "") -> pd.DataFrame:
    """Search investpy for matching funds

    Parameters
    ----------
    by : str
        Field to match on.  Can be name, issuer, isin or symbol
    value : str
        String that will be searched for

    Returns
    -------
    pd.DataFrame
        Dataframe containing matches
    """

    return investpy.funds.search_funds(by=by, value=value)


def get_overview(country: str = "united states", limit: int = 20) -> pd.DataFrame:
    """

    Parameters
    ----------
    country: str
        Country to get overview for
    limit: int
        Number of results to get
    """
    return investpy.funds.get_funds_overview(
        country=country, as_json=False, n_results=limit
    )


def get_fund_symbol_from_name(name: str) -> str:
    """Get fund symbol from name through investpy

    Parameters
    ----------
    Name: str
        Name to get fund symbol of

    Returns
    -------
    str
        Name of Symbol matching provided name
    """
    return investpy.funds.search_funds(by="name", value=name).symbol[0]


def get_fund_name_from_symbol(symbol: str) -> str:
    """Get fund name from symbol from investpy

    Parameters
    ----------
    symbol: str
        Symbol to get fund name of

    Returns
    -------
    str
        Name of fund matching provided symbol
    """
    symbol_search_results = investpy.search_funds(by="symbol", value=symbol)
    if symbol_search_results.empty:
        return ""
    name = symbol_search_results.loc[:, "name"][0]
    console.print(
        f"Name: [cyan][italic]{name.title()}[/italic][/cyan] found for {symbol}\n"
    )
    return name


def get_fund_info(fund: str, country: str = "united states") -> pd.DataFrame:
    """

    Parameters
    ----------
    fynd: str
        Name of fund (not symbol) to get information
    country: str
        Country of fund

    Returns
    -------
    pd.DataFrame
        Dataframe of fund information
    """
    return investpy.funds.get_fund_information(fund, country).T


def get_fund_historical(
    fund: str,
    country: str = "united states",
    name: bool = False,
    start_date: str = (datetime.now() - timedelta(days=366)).strftime("%d/%m/%Y"),
    end_date: str = datetime.now().strftime("%d/%m/%Y"),
) -> Tuple[pd.DataFrame, str, str]:
    """Get historical fund data

    Parameters
    ----------
    fund: str
        Fund to get data for.  If using fund name, include `name=True`
    country: str
        Country of fund
    name : bool
        Flag to search by name instead of symbol
    start_date: str
        Start date of data
    end_date: str
        End date of data

    Returns
    -------
    pd.DataFrame:
        Dataframe of OHLC prices
    str:
        Fund name
    str:
        Fund symbol
    """
    if name:
        fund_name = fund
        fund_symbol = get_fund_symbol_from_name(fund)
    else:
        fund_name = get_fund_name_from_symbol(fund)
        fund_symbol = fund

    return (
        investpy.funds.get_fund_historical_data(
            fund_name, country, from_date=start_date, to_date=end_date
        ),
        fund_name,
        fund_symbol,
    )
