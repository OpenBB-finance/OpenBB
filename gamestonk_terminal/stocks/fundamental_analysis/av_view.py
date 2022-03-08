""" Alpha Vantage View """
__docformat__ = "numpy"

import logging
import os

import numpy as np

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.decorators import check_api_key
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.fundamental_analysis import av_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_overview(ticker: str):
    """Alpha Vantage stock ticker overview

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    df_fa = av_model.get_overview(ticker)
    if df_fa.empty:
        console.print("No API calls left. Try me later", "\n")
        return

    print_rich_table(
        df_fa.drop(index=["Description"]),
        headers=[""],
        title=f"{ticker} Overview",
        show_index=True,
    )

    console.print(f"\nCompany Description:\n\n{df_fa.loc['Description'][0]}")
    console.print("")


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_key(ticker: str):
    """Alpha Vantage key metrics

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    df_key = av_model.get_key_metrics(ticker)

    if df_key.empty:
        return

    print_rich_table(
        df_key, headers=[""], title=f"{ticker} Key Metrics", show_index=True
    )

    console.print("")


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_income_statement(
    ticker: str, limit: int, quarterly: bool = False, export: str = ""
):
    """Alpha Vantage income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements
    quarterly: bool
        Flag to get quarterly instead of annual
    export: str
        Format to export data
    """
    df_income = av_model.get_income_statements(ticker, limit, quarterly)

    if df_income.empty:
        return

    print_rich_table(
        df_income,
        headers=list(df_income.columns),
        title=f"{ticker} Income Statement",
        show_index=True,
    )

    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "income", df_income)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_balance_sheet(
    ticker: str, limit: int, quarterly: bool = False, export: str = ""
):
    """Alpha Vantage income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements
    quarterly: bool
        Flag to get quarterly instead of annual
    export: str
        Format to export data
    """
    df_balance = av_model.get_balance_sheet(ticker, limit, quarterly)

    if df_balance.empty:
        return

    print_rich_table(
        df_balance,
        headers=list(df_balance.columns),
        title=f"{ticker} Balance Sheet",
        show_index=True,
    )

    console.print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "balance", df_balance
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_cash_flow(
    ticker: str, limit: int, quarterly: bool = False, export: str = ""
):
    """Alpha Vantage income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements
    quarterly: bool
        Flag to get quarterly instead of annual
    export: str
        Format to export data
    """
    df_cash = av_model.get_cash_flow(ticker, limit, quarterly)

    if df_cash.empty:
        return

    print_rich_table(
        df_cash,
        headers=list(df_cash.columns),
        title=f"{ticker} Balance Sheet",
        show_index=True,
    )

    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "cash", df_cash)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_earnings(
    ticker: str, limit: int, quarterly: bool = False, export: str = ""
):
    """Alpha Vantage earnings

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    limit:int
        Number of events to show
    quarterly: bool
        Flag to show quarterly instead of annual
    export: str
        Format to export data
    """
    df_fa = av_model.get_earnings(ticker, quarterly)

    if df_fa.empty:
        return

    print_rich_table(
        df_fa.head(limit),
        headers=list(df_fa.columns),
        show_index=False,
        title=f"{ticker} Earnings",
    )
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "earnings", df_fa)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_fraud(ticker: str):
    """Fraud indicators for given ticker
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """
    ratios, zscore, mckee = av_model.get_fraud_ratios(ticker)

    if ratios is None and zscore is None and mckee is None:
        return

    if ratios["MSCORE"] > -1.78:
        chance_m = "high"
    elif ratios["MSCORE"] > -2.22:
        chance_m = "moderate"
    else:
        chance_m = "low"

    chance_z = "high" if zscore < 0.5 else "low"

    chance_mcke = "low" if mckee < 0.5 else "high"

    if np.isnan(ratios["MSCORE"]) or np.isnan(zscore):
        console.print("Data incomplete for this ticker. Unable to calculate risk")
        return

    console.print("Mscore Sub Stats:")
    for rkey, value in ratios.items():
        if rkey != "MSCORE":
            console.print("  ", f"{rkey} : {value:.2f}")

    console.print(
        "\n" + "MSCORE: ",
        f"{ratios['MSCORE']:.2f} ({chance_m} chance of fraud)",
    )

    console.print("ZSCORE: ", f"{zscore:.2f} ({chance_z} chance of bankruptcy)", "\n")

    console.print("McKee: ", f"{mckee:.2f} ({chance_mcke} chance of bankruptcy)", "\n")
    return
