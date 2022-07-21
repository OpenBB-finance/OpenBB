""" Financial Modeling Prep View """
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import check_api_key
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table, plot_autoscale
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import fmp_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def valinvest_score(ticker: str):
    """Value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: FMP]

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    score = fmp_model.get_score(ticker)
    if score:
        console.print(f"Score: {score:.2f}".rstrip("0").rstrip(".") + " %")
        console.print("")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_profile(ticker: str):
    """Financial Modeling Prep ticker profile

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    profile = fmp_model.get_profile(ticker)

    if not profile.empty:
        print_rich_table(
            profile.drop(index=["description", "image"]),
            headers=[""],
            title=f"{ticker.upper()} Profile",
            show_index=True,
        )

        console.print(f"\nImage: {profile.loc['image'][0]}")
        console.print(f"\nDescription: {profile.loc['description'][0]}")
    else:
        logger.error("Could not get data")
        console.print("[red]Unable to get data[/red]\n")

    console.print()


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_quote(ticker: str):
    """Financial Modeling Prep ticker quote

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    """

    quote = fmp_model.get_quote(ticker)
    if quote.empty:
        console.print("[red]Data not found[/red]\n")
    else:
        print_rich_table(quote, headers=[""], title=f"{ticker} Quote", show_index=True)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_enterprise(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    df_fa = fmp_model.get_enterprise(ticker, number, quarterly)
    df_fa = df_fa[df_fa.columns[::-1]]

    # Re-order the returned columns so they are in a more logical ordering
    df_fa = df_fa.reindex(
        [
            "Symbol",
            "Stock price",
            "Number of shares",
            "Market capitalization",
            "Add total debt",
            "Minus cash and cash equivalents",
            "Enterprise value",
        ]
    )
    if df_fa.empty:
        console.print("[red]No data available[/red]\n")
    else:
        print_rich_table(
            df_fa,
            headers=list(df_fa.columns),
            title=f"{ticker} Enterprise",
            show_index=True,
        )

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "enterprise", df_fa
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_discounted_cash_flow(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker discounted cash flow

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    dcf = fmp_model.get_dcf(ticker, number, quarterly)
    dcf = dcf[dcf.columns[::-1]]
    dcf.columns = dcf.iloc[0].values
    dcf = dcf.drop("Date")
    if dcf.empty:
        console.print("[red]No data available[/red]\n")
    else:
        print_rich_table(dcf, title="Discounted Cash Flow", show_index=True)

        export_data(export, os.path.dirname(os.path.abspath(__file__)), "dcf", dcf)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_income_statement(
    ticker: str,
    number: int,
    quarterly: bool = False,
    ratios: bool = False,
    plot: list = None,
    export: str = "",
):
    """Financial Modeling Prep ticker income statement

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    export: str
        Format to export data
    """
    income = fmp_model.get_income(ticker, number, quarterly, ratios, bool(plot))

    if not income.empty:
        if plot:
            income_plot_data = income[income.columns[::-1]]
            rows_plot = len(plot)
            maximum_value = income_plot_data.max().max()
            income_plot_data = income_plot_data.transpose()
            income_plot_data.columns = income_plot_data.columns.str.lower()

            if not ratios:
                if maximum_value > 1_000_000_000_000:
                    df_rounded = income_plot_data / 1_000_000_000_000
                    denomination = " in Trillions"
                elif maximum_value > 1_000_000_000:
                    df_rounded = income_plot_data / 1_000_000_000
                    denomination = " in Billions"
                elif maximum_value > 1_000_000:
                    df_rounded = income_plot_data / 1_000_000
                    denomination = " in Millions"
                elif maximum_value > 1_000:
                    df_rounded = income_plot_data / 1_000
                    denomination = " in Thousands"
                else:
                    df_rounded = income_plot_data
                    denomination = ""
            else:
                df_rounded = income_plot_data
                denomination = ""
            if rows_plot == 1:
                fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
                df_rounded[plot[0].replace("_", "")].plot()
                title = (
                    f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {ticker.upper()}"
                    if ratios
                    else f"{plot[0].replace('_', ' ')} of {ticker.upper()} {denomination}"
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
            income = income[income.columns[::-1]]
            print_rich_table(
                income.drop(index=["Final link", "Link"]),
                headers=list(income.columns),
                title=f"{ticker.upper()} Income Statement"
                if not ratios
                else f"{'QoQ' if quarterly else 'YoY'} Change of {ticker.upper()} Income Statement",
                show_index=True,
            )

            pd.set_option("display.max_colwidth", None)

            console.print(income.loc["Final link"].to_frame().to_string())
            console.print()
            console.print(income.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "income", income
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_balance_sheet(
    ticker: str,
    number: int,
    quarterly: bool = False,
    ratios: bool = False,
    plot: list = None,
    export: str = "",
):
    """Financial Modeling Prep ticker balance sheet

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    export: str
        Format to export data
    """
    balance = fmp_model.get_balance(ticker, number, quarterly, ratios, bool(plot))

    if not balance.empty:
        if plot:
            balance_plot_data = balance[balance.columns[::-1]]
            rows_plot = len(plot)
            maximum_value = balance_plot_data.max().max()
            balance_plot_data = balance_plot_data.transpose()
            balance_plot_data.columns = balance_plot_data.columns.str.lower()

            if not ratios:
                if maximum_value > 1_000_000_000_000:
                    df_rounded = balance_plot_data / 1_000_000_000_000
                    denomination = " in Trillions"
                elif maximum_value > 1_000_000_000:
                    df_rounded = balance_plot_data / 1_000_000_000
                    denomination = " in Billions"
                elif maximum_value > 1_000_000:
                    df_rounded = balance_plot_data / 1_000_000
                    denomination = " in Millions"
                elif maximum_value > 1_000:
                    df_rounded = balance_plot_data / 1_000
                    denomination = " in Thousands"
                else:
                    df_rounded = balance_plot_data
                    denomination = ""
            else:
                df_rounded = balance_plot_data
                denomination = ""

            if rows_plot == 1:
                fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
                df_rounded[plot[0].replace("_", "")].plot()
                title = (
                    f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {ticker.upper()}"
                    if ratios
                    else f"{plot[0].replace('_', ' ')} of {ticker.upper()} {denomination}"
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
            balance = balance[balance.columns[::-1]]
            print_rich_table(
                balance.drop(index=["Final link", "Link"]),
                headers=list(balance.columns),
                title=f"{ticker.upper()} Balance Sheet",
                show_index=True,
            )

            pd.set_option("display.max_colwidth", None)

            console.print(balance.loc["Final link"].to_frame().to_string())
            console.print()
            console.print(balance.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "balance", balance
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_cash_flow(
    ticker: str,
    number: int,
    quarterly: bool = False,
    ratios: bool = False,
    plot: list = None,
    export: str = "",
):
    """Financial Modeling Prep ticker cash flow

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    export: str
        Format to export data
    """
    cash = fmp_model.get_cash(ticker, number, quarterly, ratios, bool(plot))

    if not cash.empty:
        if plot:
            cash_plot_data = cash[cash.columns[::-1]]
            rows_plot = len(plot)
            maximum_value = cash_plot_data.max().max()
            cash_plot_data = cash_plot_data.transpose()
            cash_plot_data.columns = cash_plot_data.columns.str.lower()

            if not ratios:
                if maximum_value > 1_000_000_000_000:
                    df_rounded = cash_plot_data / 1_000_000_000_000
                    denomination = " in Trillions"
                elif maximum_value > 1_000_000_000:
                    df_rounded = cash_plot_data / 1_000_000_000
                    denomination = " in Billions"
                elif maximum_value > 1_000_000:
                    df_rounded = cash_plot_data / 1_000_000
                    denomination = " in Millions"
                elif maximum_value > 1_000:
                    df_rounded = cash_plot_data / 1_000
                    denomination = " in Thousands"
                else:
                    df_rounded = cash_plot_data
                    denomination = ""
            else:
                df_rounded = cash_plot_data
                denomination = ""

            if rows_plot == 1:
                fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
                df_rounded[plot[0].replace("_", "")].plot()
                title = (
                    f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {ticker.upper()}"
                    if ratios
                    else f"{plot[0].replace('_', ' ')} of {ticker.upper()} {denomination}"
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
            cash = cash[cash.columns[::-1]]
            print_rich_table(
                cash.drop(index=["Final link", "Link"]),
                headers=list(cash.columns),
                title=f"{ticker.upper()} Cash Flow",
                show_index=True,
            )

            pd.set_option("display.max_colwidth", None)

            console.print(cash.loc["Final link"].to_frame().to_string())
            console.print()
            console.print(cash.loc["Link"].to_frame().to_string())
            console.print()
        export_data(export, os.path.dirname(os.path.abspath(__file__)), "cash", cash)
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_key_metrics(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker key metrics

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    key_metrics = fmp_model.get_key_metrics(ticker, number, quarterly)

    if not key_metrics.empty:
        key_metrics = key_metrics[key_metrics.columns[::-1]]
        print_rich_table(
            key_metrics,
            headers=list(key_metrics.columns),
            title=f"{ticker.upper()} Key Metrics",
            show_index=True,
        )

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "metrics", key_metrics
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_financial_ratios(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker ratios

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    ratios = fmp_model.get_key_ratios(ticker, number, quarterly)

    if not ratios.empty:
        ratios = ratios[ratios.columns[::-1]]
        print_rich_table(
            ratios,
            headers=list(ratios.columns),
            title=f"{ticker.upper()} Ratios",
            show_index=True,
        )

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "grratiosowth", ratios
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_financial_statement_growth(
    ticker: str, number: int, quarterly: bool = False, export: str = ""
):
    """Financial Modeling Prep ticker growth

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    number: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    export: str
        Format to export data
    """
    growth = fmp_model.get_financial_growth(ticker, number, quarterly)

    if not growth.empty:
        growth = growth[growth.columns[::-1]]
        print_rich_table(
            growth,
            headers=list(growth.columns),
            title=f"{ticker.upper()} Growth",
            show_index=True,
        )

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "growth", growth
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")
