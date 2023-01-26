""" Financial Modeling Prep Model"""
__docformat__ = "numpy"
import logging
from typing import Optional

from datetime import datetime
import warnings
from requests.exceptions import HTTPError

import fundamentalanalysis as fa  # Financial Modeling Prep
import numpy as np
import pandas as pd
import valinvest

from openbb_terminal.rich_config import console
from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format
from openbb_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_score(symbol: str) -> Optional[np.number]:
    """Gets value score from fmp

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    np.number
        Value score
    """

    value_score = None

    try:
        valstock = valinvest.Fundamental(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)
        warnings.filterwarnings("ignore", category=FutureWarning)
        value_score = 100 * (valstock.fscore() / 9)
        warnings.filterwarnings("ignore", category=FutureWarning)
    except KeyError:
        console.print("[red]Invalid API Key[/red]\n")
    # Invalid ticker (Ticker should be a NASDAQ 100 ticker or SP 500 ticker)
    except ValueError as e:
        console.print(e, "\n")
    return value_score


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_profile(symbol: str) -> pd.DataFrame:
    """Get ticker profile from FMP

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of ticker profile
    """
    df = pd.DataFrame()

    try:
        df = fa.profile(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)
    # Invalid API Keys
    except ValueError:
        console.print("[red]Invalid API Key[/red]\n")
    # Premium feature, API plan is not authorized
    except HTTPError:
        console.print("[red]API Key not authorized for Premium feature[/red]\n")
    return df


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_quote(symbol: str) -> pd.DataFrame:
    """Gets ticker quote from FMP

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of ticker quote
    """

    df_fa = pd.DataFrame()

    try:
        df_fa = fa.quote(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)
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
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_enterprise(
    symbol: str, limit: int = 5, quarterly: bool = False
) -> pd.DataFrame:
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data

    Returns
    -------
    pd.DataFrame
        Dataframe of enterprise information
    """
    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.enterprise(
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.enterprise(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    if not df_fa.empty:
        df_fa = clean_metrics_df(df_fa, num=limit, mask=False)
    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_dcf(symbol: str, limit: int = 5, quarterly: bool = False) -> pd.DataFrame:
    """Get stocks dcf from FMP

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
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
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.discounted_cash_flow(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)
        df_fa = clean_metrics_df(df_fa, num=limit, mask=False)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_income(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get income statements

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of the income statements
    """

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.income_statement(
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.income_statement(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)

    # Invalid API Keys
    except ValueError as e:
        console.print(e)
        return pd.DataFrame()
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)
        return pd.DataFrame()

    if ratios:
        types = df_fa.copy().applymap(lambda x: isinstance(x, (float, int))).all(axis=1)
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df_fa.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df_fa.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    df_fa = df_fa.iloc[:, 0:limit]
    df_fa_c = clean_metrics_df(df_fa, num=limit)

    return df_fa_c if not plot else df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_balance(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get balance sheets

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of balance sheet
    """

    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.balance_sheet_statement(
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.balance_sheet_statement(
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP
            )

    # Invalid API Keys
    except ValueError as e:
        console.print(e)
        return pd.DataFrame()
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)
        return pd.DataFrame()

    if ratios:
        types = df_fa.copy().applymap(lambda x: isinstance(x, (float, int))).all(axis=1)
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df_fa.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df_fa.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    df_fa = df_fa.iloc[:, 0:limit]
    df_fa_c = clean_metrics_df(df_fa, num=limit)

    return df_fa_c if not plot else df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_cash(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: bool = False,
) -> pd.DataFrame:
    """Get cash flow

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
        Number to get
    quarterly : bool, optional
        Flag to get quarterly data, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: bool
        If the data shall be formatted ready to plot

    Returns
    -------
    pd.DataFrame
        Dataframe of company cash flow
    """
    df_fa = pd.DataFrame()

    try:
        if quarterly:
            df_fa = fa.cash_flow_statement(
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.cash_flow_statement(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)

    # Invalid API Keys
    except ValueError as e:
        console.print(e)
        return pd.DataFrame()
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)
        return pd.DataFrame()

    if ratios:
        types = df_fa.copy().applymap(lambda x: isinstance(x, (float, int))).all(axis=1)
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df_fa.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df_fa.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    df_fa = df_fa.iloc[:, 0:limit]
    df_fa_c = clean_metrics_df(df_fa, num=limit)

    return df_fa_c if not plot else df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_key_metrics(
    symbol: str, limit: int = 5, quarterly: bool = False
) -> pd.DataFrame:
    """Get key metrics

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
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
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.key_metrics(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=limit)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_key_ratios(
    symbol: str, limit: int = 5, quarterly: bool = False
) -> pd.DataFrame:
    """Get key ratios

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
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
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.financial_ratios(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = clean_metrics_df(df_fa, num=limit)
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_financial_growth(
    symbol: str, limit: int = 5, quarterly: bool = False
) -> pd.DataFrame:
    """Get financial statement growth

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    limit : int
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
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP, period="quarter"
            )
        else:
            df_fa = fa.financial_statement_growth(
                symbol, cfg.API_KEY_FINANCIALMODELINGPREP
            )

        df_fa = clean_metrics_df(df_fa, num=limit)

        df_fa = df_fa[df_fa.columns[::-1]]
    # Invalid API Keys
    except ValueError as e:
        console.print(e)
    # Premium feature, API plan is not authorized
    except HTTPError as e:
        console.print(e)

    return df_fa


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def clean_metrics_df(data: pd.DataFrame, num: int, mask: bool = True) -> pd.DataFrame:
    """Clean metrics data frame

    Parameters
    ----------
    data : pd.DataFrame
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
    # iloc will fail if number is greater than number of columns
    num = min(num, data.shape[1])
    data = data.iloc[:, 0:num]
    if mask:
        data = data.mask(data.astype(object).eq(num * ["None"])).dropna()
        data = data.mask(data.astype(object).eq(num * ["0"])).dropna()
    data = data.applymap(lambda x: lambda_long_number_format(x))
    clean_df_index(data)
    data.columns.name = "Fiscal Date Ending"
    data = data.rename(
        index={
            "Enterprise value over e b i t d a": "Enterprise value over EBITDA",
            "Net debt to e b i t d a": "Net debt to EBITDA",
            "D c f": "DCF",
            "Net income per e b t": "Net income per EBT",
        }
    )

    return data
