""" Alpha Vantage View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt
from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
    plot_autoscale,
    camel_case_split,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import av_model

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

    console.print(f"Company Description:\n\n{df_fa.loc['Description'][0]}")
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

    indexes = df_income.index
    new_indexes = [camel_case_split(ind) for ind in indexes]
    df_income.index = new_indexes

    print_rich_table(
        df_income,
        headers=list(df_income.columns),
        title=f"{ticker} Income Statement",
        show_index=True,
    )

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

    indexes = df_balance.index
    new_indexes = [camel_case_split(ind) for ind in indexes]
    df_balance.index = new_indexes

    print_rich_table(
        df_balance,
        headers=list(df_balance.columns),
        title=f"{ticker} Balance Sheet",
        show_index=True,
    )

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

    indexes = df_cash.index
    new_indexes = [camel_case_split(ind) for ind in indexes]
    df_cash.index = new_indexes

    print_rich_table(
        df_cash,
        headers=list(df_cash.columns),
        title=f"{ticker} Balance Sheet",
        show_index=True,
    )

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

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "earnings", df_fa)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_fraud(ticker: str, export: str = "", help_text: bool = False):
    """Fraud indicators for given ticker
    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    export : str
        Whether to export the dupont breakdown
    help_text : bool
        Whether to show help text
    """
    df = av_model.get_fraud_ratios(ticker)
    if df.empty:
        console.print(
            "[red]AlphaVantage API limit reached, please wait one minute[/red]\n"
        )
    else:
        print_rich_table(
            df, headers=list(df.columns), show_index=True, title="Fraud Risk Statistics"
        )

        help_message = """
MSCORE:
An mscore above -1.78 indicates a high risk of fraud, and one above  -2.22 indicates a medium risk of fraud.

ZSCORE:
A zscore less than 0.5 indicates a high risk of fraud.

Mckee:
A mckee less than 0.5 indicates a high risk of fraud.
    """

    if help_text:
        console.print(help_message)
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dupont", df)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_dupont(
    ticker: str,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Shows the extended dupont ratio

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    raw : str
        Show raw data instead of a graph
    export : bool
        Whether to export the dupont breakdown
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df = av_model.get_dupont(ticker)
    if df.empty:
        console.print("[red]Invalid response from AlphaVantage[/red]\n")
        return
    if raw:
        print_rich_table(
            df, headers=list(df.columns), show_index=True, title="Extended Dupont"
        )
        return
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    colors = theme.get_colors()
    df.transpose().plot(kind="line", ax=ax, color=colors)
    ax.set_title("Extended Dupont by Year")
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "dupont", df)
