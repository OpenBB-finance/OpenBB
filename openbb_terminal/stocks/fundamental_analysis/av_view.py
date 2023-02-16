""" Alpha Vantage View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    camel_case_split,
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.helpers_denomination import transform as transform_by_denomination
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import av_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_overview(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Alpha Vantage stock ticker overview

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    """
    df_fa = av_model.get_overview(symbol)
    if df_fa.empty:
        console.print("No API calls left. Try me later", "\n")
        return

    print_rich_table(
        df_fa.drop(index=["Description"]),
        headers=[""],
        title=f"{symbol} Overview",
        show_index=True,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "overview",
        df_fa,
        sheet_name,
    )

    console.print(f"Company Description:\n\n{df_fa.loc['Description'][0]}")


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_key(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Alpha Vantage key metrics

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    """
    df_key = av_model.get_key_metrics(symbol)

    if df_key.empty:
        return

    print_rich_table(
        df_key, headers=[""], title=f"{symbol} Key Metrics", show_index=True
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "key",
        df_key,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_income_statement(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage income statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements, by default 5
    quarterly: bool
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_income = av_model.get_income_statements(
        symbol, limit, quarterly, ratios, bool(plot)
    )

    if df_income.empty:
        return

    if plot:
        rows_plot = len(plot)
        income_plot_data = df_income.transpose()
        income_plot_data.columns = income_plot_data.columns.str.lower()

        if not ratios:
            (df_rounded, denomination) = transform_by_denomination(income_plot_data)
            if denomination == "Units":
                denomination = ""
        else:
            df_rounded = income_plot_data
            denomination = ""

        if rows_plot == 1:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            df_rounded[plot[0].replace("_", "")].plot()
            title = (
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()} {denomination}"
            )
            plt.title(title)
            theme.style_primary_axis(ax)
            theme.visualize_output()
        else:
            fig, axes = plt.subplots(rows_plot)
            for i in range(rows_plot):
                axes[i].plot(df_rounded[plot[i].replace("_", "")])
                axes[i].set_title(f"{plot[i].replace('_', ' ')} {denomination}")
            theme.style_primary_axis(axes[0])
            fig.autofmt_xdate()
    else:
        indexes = df_income.index
        new_indexes = [camel_case_split(ind) for ind in indexes]
        df_income.index = new_indexes

        print_rich_table(
            df_income,
            headers=list(df_income.columns),
            title=f"{symbol} Income Statement"
            if not ratios
            else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol} Income Statement",
            show_index=True,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "income",
        df_income,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_balance_sheet(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage balance sheet statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements, by default 5
    quarterly: bool
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_balance = av_model.get_balance_sheet(
        symbol, limit, quarterly, ratios, bool(plot)
    )

    if df_balance.empty:
        return

    if plot:
        rows_plot = len(plot)
        balance_plot_data = df_balance.transpose()
        balance_plot_data.columns = balance_plot_data.columns.str.lower()

        if not ratios:
            (df_rounded, denomination) = transform_by_denomination(balance_plot_data)
            if denomination == "Units":
                denomination = ""
        else:
            df_rounded = balance_plot_data
            denomination = ""

        if rows_plot == 1:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            df_rounded[plot[0].replace("_", "")].plot()
            title = (
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()} {denomination}"
            )
            plt.title(title)
            theme.style_primary_axis(ax)
            theme.visualize_output()
        else:
            fig, axes = plt.subplots(rows_plot)
            for i in range(rows_plot):
                axes[i].plot(df_rounded[plot[i].replace("_", "")])
                axes[i].set_title(f"{plot[i].replace('_', ' ')} {denomination}")
            theme.style_primary_axis(axes[0])
            fig.autofmt_xdate()

    else:
        indexes = df_balance.index
        new_indexes = [camel_case_split(ind) for ind in indexes]
        df_balance.index = new_indexes

        print_rich_table(
            df_balance,
            headers=list(df_balance.columns),
            title=f"{symbol} Balance Sheet"
            if not ratios
            else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol} Balance Sheet",
            show_index=True,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "balance",
        df_balance,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_cash_flow(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage income statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number of past statements, by default 5
    quarterly: bool
        Flag to get quarterly instead of annual, by default False
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_cash = av_model.get_cash_flow(symbol, limit, quarterly, ratios, bool(plot))

    if df_cash.empty:
        return

    if plot:
        rows_plot = len(plot)
        cash_plot_data = df_cash.transpose()
        cash_plot_data.columns = cash_plot_data.columns.str.lower()

        if not ratios:
            (df_rounded, denomination) = transform_by_denomination(cash_plot_data)
            if denomination == "Units":
                denomination = ""
        else:
            df_rounded = cash_plot_data
            denomination = ""

        if rows_plot == 1:
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            df_rounded[plot[0].replace("_", "")].plot()
            title = (
                f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                if ratios
                else f"{plot[0].replace('_', ' ')} of {symbol.upper()} {denomination}"
            )
            plt.title(title)
            theme.style_primary_axis(ax)
            theme.visualize_output()
        else:
            fig, axes = plt.subplots(rows_plot)
            for i in range(rows_plot):
                axes[i].plot(df_rounded[plot[i].replace("_", "")])
                axes[i].set_title(f"{plot[i].replace('_', ' ')} {denomination}")
            theme.style_primary_axis(axes[0])
            fig.autofmt_xdate()

    else:
        indexes = df_cash.index
        new_indexes = [camel_case_split(ind) for ind in indexes]
        df_cash.index = new_indexes

        print_rich_table(
            df_cash,
            headers=list(df_cash.columns),
            title=f"{symbol} Cash flow"
            if not ratios
            else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol} Cash flow",
            show_index=True,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cash",
        df_cash,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_earnings(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Alpha Vantage earnings

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit:int
        Number of events to show
    quarterly: bool
        Flag to show quarterly instead of annual
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_fa = av_model.get_earnings(symbol, quarterly)

    if df_fa.empty:
        return

    print_rich_table(
        df_fa.head(limit),
        headers=list(df_fa.columns),
        show_index=False,
        title=f"{symbol} Earnings",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "earnings",
        df_fa,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_fraud(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    help_text: bool = False,
    color: bool = True,
    detail: bool = False,
):
    """Fraud indicators for given ticker
    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    export : str
        Whether to export the dupont breakdown
    help_text : bool
        Whether to show help text
    color : bool
        Whether to show color in the dataframe
    detail : bool
        Whether to show the details for the mscore
    """
    df = av_model.get_fraud_ratios(symbol, detail=detail)

    if df.empty:
        return

    df_color = df.copy()
    if color:
        for column in df_color:
            df_color[column] = df_color[column].astype(str)
        df_color = df_color.apply(lambda x: av_model.replace_df(x.name, x), axis=1)

    print_rich_table(
        df_color,
        headers=list(df_color.columns),
        show_index=True,
        title="Fraud Risk Statistics",
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
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fraud",
        df,
        sheet_name,
    )
    return


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_dupont(
    symbol: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Shows the extended dupont ratio

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    raw : str
        Show raw data instead of a graph
    export : bool
        Whether to export the dupont breakdown
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df = av_model.get_dupont(symbol)
    if df.empty:
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dupont",
        df,
        sheet_name,
    )
