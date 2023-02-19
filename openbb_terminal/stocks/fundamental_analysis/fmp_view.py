""" Financial Modeling Prep View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale, print_rich_table
from openbb_terminal.helpers_denomination import transform as transform_by_denomination
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import fmp_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def valinvest_score(
    symbol: str, years: int, export: str = "", sheet_name: Optional[str] = None
):
    """Value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: FMP]

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    scores = pd.DataFrame.from_dict(
        fmp_model.get_score(symbol, years), orient="index", columns=["Score"]
    )

    if not scores.empty:
        updated_scores = []
        for score in scores["Score"]:
            updated_scores.append(f"{score:.2f}".rstrip("0").rstrip(".") + " %")

        scores["Score"] = updated_scores

        print_rich_table(
            scores, title=f"Value Investing Scores [{years} Years]", show_index=True
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "scores",
            scores,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_profile(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Financial Modeling Prep ticker profile

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    profile = fmp_model.get_profile(symbol)

    if not profile.empty:
        print_rich_table(
            profile.drop(index=["description", "image"]),
            headers=[""],
            title=f"{symbol.upper()} Profile",
            show_index=True,
        )

        console.print(f"\nImage: {profile.loc['image'][0]}")
        console.print(f"\nDescription: {profile.loc['description'][0]}")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "scores",
            profile,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Unable to get data[/red]\n")

    console.print()


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_enterprise(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_fa = fmp_model.get_enterprise(symbol, limit, quarterly)
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
            title=f"{symbol} Enterprise",
            show_index=True,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "enterprise",
            df_fa,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_discounted_cash_flow(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker discounted cash flow

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    dcf = fmp_model.get_dcf(symbol, limit, quarterly)
    dcf = dcf[dcf.columns[::-1]]
    dcf.columns = dcf.iloc[0].values
    dcf = dcf.drop("Date")
    if dcf.empty:
        console.print("[red]No data available[/red]\n")
    else:
        print_rich_table(dcf, title="Discounted Cash Flow", show_index=True)

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "dcf",
            dcf,
            sheet_name,
        )


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_income_statement(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker income statement

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    income = fmp_model.get_income(symbol, limit, quarterly, ratios, bool(plot))

    if not income.empty:
        if plot:
            income_plot_data = income[income.columns[::-1]]
            rows_plot = len(plot)
            income_plot_data = income_plot_data.transpose()
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
            income = income[income.columns[::-1]]
            print_rich_table(
                income.drop(index=["Final link", "Link"]),
                headers=list(income.columns),
                title=f"{symbol.upper()} Income Statement"
                if not ratios
                else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol.upper()} Income Statement",
                show_index=True,
            )

            pd.set_option("display.max_colwidth", None)

            console.print(income.loc["Final link"].to_frame().to_string())
            console.print()
            console.print(income.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "income",
            income,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_balance_sheet(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker balance sheet

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    balance = fmp_model.get_balance(symbol, limit, quarterly, ratios, bool(plot))

    if not balance.empty:
        if plot:
            balance_plot_data = balance[balance.columns[::-1]]
            rows_plot = len(plot)
            balance_plot_data = balance_plot_data.transpose()
            balance_plot_data.columns = balance_plot_data.columns.str.lower()

            if not ratios:
                (df_rounded, denomination) = transform_by_denomination(
                    balance_plot_data
                )
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
            balance = balance[balance.columns[::-1]]
            print_rich_table(
                balance.drop(index=["Final link", "Link"]),
                headers=list(balance.columns),
                title=f"{symbol.upper()} Balance Sheet",
                show_index=True,
            )

            pd.set_option("display.max_colwidth", None)

            console.print(balance.loc["Final link"].to_frame().to_string())
            console.print()
            console.print(balance.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "balance",
            balance,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_cash_flow(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    ratios: bool = False,
    plot: Optional[list] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker cash flow

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    ratios: bool
        Shows percentage change, by default False
    plot: list
        List of row labels to plot
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    cash = fmp_model.get_cash(symbol, limit, quarterly, ratios, bool(plot))

    if not cash.empty:
        if plot:
            cash_plot_data = cash[cash.columns[::-1]]
            rows_plot = len(plot)
            cash_plot_data = cash_plot_data.transpose()
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
            cash = cash[cash.columns[::-1]]
            print_rich_table(
                cash.drop(index=["Final link", "Link"]),
                headers=list(cash.columns),
                title=f"{symbol.upper()} Cash Flow",
                show_index=True,
            )

            pd.set_option("display.max_colwidth", None)

            console.print(cash.loc["Final link"].to_frame().to_string())
            console.print()
            console.print(cash.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cash",
            cash,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_key_metrics(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker key metrics

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    key_metrics = fmp_model.get_key_metrics(symbol, limit, quarterly)

    if not key_metrics.empty:
        key_metrics = key_metrics[key_metrics.columns[::-1]]
        print_rich_table(
            key_metrics,
            headers=list(key_metrics.columns),
            title=f"{symbol.upper()} Key Metrics",
            show_index=True,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "metrics",
            key_metrics,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_financial_ratios(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker ratios

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    ratios = fmp_model.get_key_ratios(symbol, limit, quarterly)

    if not ratios.empty:
        ratios = ratios[ratios.columns[::-1]]
        print_rich_table(
            ratios,
            headers=list(ratios.columns),
            title=f"{symbol.upper()} Ratios",
            show_index=True,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "grratiosowth",
            ratios,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_financial_statement_growth(
    symbol: str,
    limit: int = 5,
    quarterly: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Financial Modeling Prep ticker growth

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    limit: int
        Number to get
    quarterly: bool
        Flag to get quarterly data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    growth = fmp_model.get_financial_growth(symbol, limit, quarterly)

    if not growth.empty:
        print_rich_table(
            growth,
            headers=list(growth.columns),
            title=f"{symbol.upper()} Growth",
            show_index=True,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "growth",
            growth,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_filings(
    ticker: str = "",
    pages: int = 1,
    limit: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display recent forms submitted to the SEC

    Parameters
    ----------
    pages: int = 1
        The range of most-rececnt pages to get entries from (1000 per page, max 30 pages)
    limit: int = 20
        Limit the number of entries to display (default: 20)
    export: str = ""
        Export data as csv, json, or xlsx

    Examples
    --------

    openbb.stocks.display_filings()

    openbb.stocks.display_filings(today = True, export = "csv")
    """
    filings = fmp_model.get_filings(pages)
    ticker_filings = filings[filings["Ticker"] == ticker.upper()]

    if ticker_filings.empty:
        console.print(
            f"[red]No filings found for ticker {ticker}, consider increasing the value "
            "for --pages. Showing recent filings instead.[/red]\n"
        )
        print_rich_table(
            filings[:limit],
            title=f"Recent SEC Filings [Limit: {limit}]",
            show_index=True,
        )
    elif not ticker_filings.empty:
        print_rich_table(
            ticker_filings[:limit],
            title=f"SEC Filings for {ticker} [Limit: {limit}]]",
            show_index=True,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "filings",
            ticker_filings,
            sheet_name,
        )
    else:
        logger.error("Could not find any data.")
        console.print("[red]Could not find any data for {ticker}[/red]\n")


def add_color(value: str) -> str:
    if "buy" in value.lower():
        value = f"[green]{value}[/green]"
    elif "sell" in value.lower():
        value = f"[red]{value}[/red]"
    return value


@log_start_end(log=logger)
def rating(
    symbol: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """Display ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of last days ratings to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    """
    df = fmp_model.get_rating(symbol)

    if (isinstance(df, pd.DataFrame) and df.empty) or (
        not isinstance(df, pd.DataFrame) and not df
    ):
        return

    # TODO: This could be displayed in a nice rating plot over time

    df = df.astype(str).applymap(lambda x: add_color(x))

    print_rich_table(
        df.head(limit),
        headers=df.columns,
        show_index=True,
        title="Rating",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rot",
        df,
        sheet_name,
    )
