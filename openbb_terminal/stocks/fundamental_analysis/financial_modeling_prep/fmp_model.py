""" Financial Modeling Prep Model"""
__docformat__ = "numpy"
import logging
from typing import Optional

from datetime import datetime
from requests.exceptions import HTTPError

import fundamentalanalysis as fa  # Financial Modeling Prep
import numpy as np
import pandas as pd
import valinvest

from openbb_terminal.rich_config import console
from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format
from openbb_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_score(ticker: str) -> Optional[np.number]:
    """Gets value score from fmp

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    np.number
        Value score
    """

    value_score = None

    try:
        valstock = valinvest.Fundamental(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        value_score = 100 * (valstock.fscore() / 9)
    except KeyError:
        console.print("[red]Invalid API Key[/red]\n")
    # Invalid ticker (Ticker should be a NASDAQ 100 ticker or SP 500 ticker)
    except ValueError as e:
        console.print(e, "\n")
    return value_score


@log_start_end(log=logger)
def get_profile(ticker: str) -> pd.DataFrame:
    """Get ticker profile from FMP"""
    df = pd.DataFrame()

    try:
        df = fa.profile(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
    # Invalid API Keys
    except ValueError:
        console.print("[red]Invalid API Key[/red]\n")
    # Premium feature, API plan is not authorized
    except HTTPError:
        console.print("[red]API Key not authorized for Premium feature[/red]\n")
    return df


@log_start_end(log=logger)
def get_quote(ticker) -> pd.DataFrame:
    """Gets ticker quote from FMP"""

    df_fa = pd.DataFrame()

    try:
        df_fa = fa.quote(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
    # Invalid API Keys
    except ValueError:
        console.print("[red]Invalid API Key[/red]\n")
    # Premium feature, API plan is not authorized
    except HTTPError:
        console.print("[red]API Key not authorized for Premium feature[/red]\n")

    if not df_fa.empty:
        clean_df_index(df_fa)
        df_fa.loc["Market cap"][0] = lambda_long_number_format(
            df_fa.loc["Market cap"][0]
        )
        df_fa.loc["Shares outstanding"][0] = lambda_long_number_format(
            df_fa.loc["Shares outstanding"][0]
        )
        df_fa.loc["Volume"][0] = lambda_long_number_format(df_fa.loc["Volume"][0])
        # Check if there is a valid earnings announcement
        if df_fa.loc["Earnings announcement"][0]:
            earning_announcement = datetime.strptime(
                df_fa.loc["Earnings announcement"][0][0:19], "%Y-%m-%dT%H:%M:%S"
            )
            df_fa.loc["Earnings announcement"][
                0
            ] = f"{earning_announcement.date()} {earning_announcement.time()}"
    return df_fa


@log_start_end(log=logger)
def get_enterprise(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data

    Returns
    ----------
    pd.DataFrame:
        Dataframe of enterprise information
    """
    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.enterprise(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.enterprise(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    if not df_fa.empty:
        df_fa = clean_metrics_df(df_fa, num=number, mask=False)
    return df_fa


@log_start_end(log=logger)
def get_dcf(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Get stocks dcf from FMP

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of dcf data
    """

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.discounted_cash_flow(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.discounted_cash_flow(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        df_fa = clean_metrics_df(df_fa, num=number, mask=False)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
def get_income(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Get income statements

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of income statements
    """

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.income_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.income_statement(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        df_fa = clean_metrics_df(df_fa, num=number)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
def get_balance(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Get balance sheets

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of balance sheets
    """

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.balance_sheet_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.balance_sheet_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=number)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
def get_cash(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Get cash flow

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of company cash flow
    """
    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.cash_flow_statement(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.cash_flow_statement(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=number)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
def get_key_metrics(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Get key metrics

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of key metrics
    """
    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.key_metrics(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.key_metrics(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=number)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
def get_key_ratios(ticker: str, number: int, quarterly: bool = False) -> pd.DataFrame:
    """Get key ratios

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of key ratios
    """
    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.financial_ratios(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.financial_ratios(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=number)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
def get_financial_growth(
    ticker: str, number: int, quarterly: bool = False
) -> pd.DataFrame:
    """Get financial statement growth

    Parameters
    ----------
    ticker : str
        Stock ticker
    number : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of financial statement growth
    """
    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.financial_statement_growth(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.financial_statement_growth(
                ticker, cfg.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=number)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
def clean_metrics_df(df_fa: pd.DataFrame, num: int, mask: bool = True) -> pd.DataFrame:
    """Clean metrics data frame

    Parameters
    ----------
    df_fa : pd.DataFrame
        Metrics data frame
    num : int
        Number of columns to clean
    mask : bool, optional
        Apply mask, by default True

    Returns
    -------
    pd.DataFrame
        Cleaned metrics data frame
    """

    df_fa = df_fa.iloc[:, 0:num]
    if mask:
        df_fa = df_fa.mask(df_fa.astype(object).eq(num * ["None"])).dropna()
        df_fa = df_fa.mask(df_fa.astype(object).eq(num * ["0"])).dropna()
    df_fa = df_fa.applymap(lambda x: lambda_long_number_format(x))
    clean_df_index(df_fa)
    df_fa.columns.name = "Fiscal Date Ending"
    df_fa = df_fa.rename(
        index={
            "Enterprise value over e b i t d a": "Enterprise value over EBITDA",
            "Net debt to e b i t d a": "Net debt to EBITDA",
            "D c f": "DCF",
            "Net income per e b t": "Net income per EBT",
        }
    )

    return df_fa
