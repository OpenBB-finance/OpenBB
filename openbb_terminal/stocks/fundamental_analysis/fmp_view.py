""" Financial Modeling Prep View """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
    revert_lambda_long_number_format,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.fundamental_analysis import fmp_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments, R1710


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def valinvest_score(
    symbol: str, years: int, export: str = "", sheet_name: Optional[str] = None
):
    """
    Value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: FMP]
    The data is gathered from fmp and the scores are calculated using the valinvest library. The repository
    For this library can be found here: https://github.com/astro30/valinvest

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
            scores,
            title=f"Value Investing Scores [{years} Years]",
            show_index=True,
            export=bool(export),
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
        console.print(f"\nImage: {profile.loc['image'][0]}")
        console.print(f"\nDescription: {profile.loc['description'][0]}")

        profile.drop(index=["description", "image"], inplace=True)
        profile.columns = [" "]

        print_rich_table(
            profile,
            title=f"{symbol.upper()} Profile",
            show_index=True,
            export=bool(export),
        )

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
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    quarterly: bool = False,
    method: str = "market_cap",
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Financial Modeling Prep ticker enterprise

    Parameters
    ----------
    symbol : str
        Fundamental analysis ticker symbol
    start_date: str
        Start date of the data
    end_date: str
        End date of the data
    quarterly: bool
        Flag to get quarterly data
    plot: bool
        Flag to plot the data
    method: str
        Type of data to plot, market_cap or enterprise_value
    raw: bool
        Flag to print raw data
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_fa = fmp_model.get_enterprise(symbol, start_date, end_date, quarterly)

    # Re-order the returned columns so they are in a more logical ordering
    df_fa = df_fa.reindex(
        columns=[
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
        df_fa_plot = df_fa.applymap(revert_lambda_long_number_format)

        type_str = (
            "Market capitalization" if method == "market_cap" else "Enterprise value"
        )

        fig = OpenBBFigure(yaxis_title=f"{type_str} in Billions")
        fig.set_title(f"{type_str} of {symbol}")
        fig.add_scatter(
            x=df_fa_plot.index,
            y=df_fa_plot[type_str].values / 1e9,
            mode="lines",
            name=type_str,
            line_color=theme.up_color,
            stackgroup="one",
        )

        if raw:
            print_rich_table(
                df_fa,
                headers=list(df_fa.columns),
                title=f"{symbol} Enterprise Value",
                show_index=True,
                export=bool(export),
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            method,
            df_fa,
            sheet_name,
        )

        return fig.show(external=raw or external_axes)


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
        print_rich_table(
            dcf, title="Discounted Cash Flow", show_index=True, export=bool(export)
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "dcf",
            dcf.transpose(),
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
        fig = OpenBBFigure()

        income.index = [
            stocks_helper.INCOME_PLOT["FinancialModelingPrep"][i]
            for i in [i.replace(" ", "_") for i in income.index.str.lower()]
        ]

        if plot:
            income_plot_data = income[income.columns[::-1]]
            rows_plot = len(plot)
            income_plot_data = income_plot_data.transpose()

            if rows_plot == 1:
                title = (
                    f"{plot[0].replace('_', ' ').title()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                    if ratios
                    else f"{plot[0].replace('_', ' ').title()} of {symbol.upper()}"
                )
                fig.add_scatter(
                    x=income_plot_data.index,
                    y=income_plot_data[plot[0]],
                    mode="lines",
                    name=f'{symbol.upper()} {plot[0].replace("_", "")}',
                )
                fig.set_title(title)

            else:
                fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
                for i in range(rows_plot):
                    fig.add_scatter(
                        x=income_plot_data.index,
                        y=income_plot_data[plot[i]],
                        mode="lines",
                        name=f'{symbol.upper()} {plot[i].replace("_", "")}',
                        row=i + 1,
                        col=1,
                    )
                    fig.set_title(f"{plot[i].replace('_', ' ')}", row=i + 1, col=1)

            fig.show(external=fig.is_image_export(export))
        else:
            income = income[income.columns[::-1]]
            # Snake case to english
            income.index = income.index.to_series().apply(
                lambda x: x.replace("_", " ").title()
            )
            print_rich_table(
                income.drop(index=["Final Link", "Link"]),
                headers=list(income.columns),
                title=f"{symbol.upper()} Income Statement"
                if not ratios
                else f"{'QoQ' if quarterly else 'YoY'} Change of {symbol.upper()} Income Statement",
                show_index=True,
                export=bool(export),
            )

            console.print(income.loc["Final Link"].to_frame().to_string())
            console.print()
            console.print(income.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "income",
            income,
            sheet_name,
            fig,
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
        fig = OpenBBFigure()

        balance.index = [
            stocks_helper.BALANCE_PLOT["FinancialModelingPrep"][i]
            for i in [i.replace(" ", "_") for i in balance.index.str.lower()]
        ]

        if plot:
            balance_plot_data = balance[balance.columns[::-1]]
            rows_plot = len(plot)
            balance_plot_data = balance_plot_data.transpose()

            if rows_plot == 1:
                fig.add_scatter(
                    x=balance_plot_data.index,
                    y=balance_plot_data[plot[0]],
                    mode="lines",
                    name=f'{symbol.upper()} {plot[0].replace("_", " ")}',
                )
                fig.set_title(
                    f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                    if ratios
                    else f"{plot[0].replace('_', ' ').title()} of {symbol.upper()}"
                )
            else:
                fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
                for i in range(rows_plot):
                    fig.add_scatter(
                        x=balance_plot_data.index,
                        y=balance_plot_data[plot[i]],
                        mode="lines",
                        name=f'{symbol.upper()} {plot[i].replace("_", " ")}',
                        row=i + 1,
                        col=1,
                    )
                    fig.set_title(f"{plot[i].replace('_', ' ')}", row=i + 1, col=1)

            fig.show(external=fig.is_image_export(export))
        else:
            balance = balance[balance.columns[::-1]]
            # Snake case to english
            balance.index = balance.index.to_series().apply(
                lambda x: x.replace("_", " ").title()
            )
            print_rich_table(
                balance.drop(index=["Final Link", "Link"]),
                headers=list(balance.columns),
                title=f"{symbol.upper()} Balance Sheet",
                show_index=True,
                export=bool(export),
            )

            console.print(balance.loc["Final Link"].to_frame().to_string())
            console.print()
            console.print(balance.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "balance",
            balance,
            sheet_name,
            fig,
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
        fig = OpenBBFigure()

        cash.index = [
            stocks_helper.CASH_PLOT["FinancialModelingPrep"][i]
            for i in [i.replace(" ", "_") for i in cash.index.str.lower()]
        ]

        if plot:
            cash_plot_data = cash[cash.columns[::-1]]
            rows_plot = len(plot)
            cash_plot_data = cash_plot_data.transpose()

            if rows_plot == 1:
                fig.add_scatter(
                    x=cash_plot_data.index,
                    y=cash_plot_data[plot[0]],
                    mode="lines",
                    name=f'{symbol.upper()} {plot[0].replace("_", " ")}',
                )
                fig.set_title(
                    f"{plot[0].replace('_', ' ').lower()} {'QoQ' if quarterly else 'YoY'} Growth of {symbol.upper()}"
                    if ratios
                    else f"{plot[0].replace('_', ' ').title()} of {symbol.upper()}"
                )
            else:
                fig = OpenBBFigure.create_subplots(rows=rows_plot, cols=1)
                for i in range(rows_plot):
                    fig.add_scatter(
                        x=cash_plot_data.index,
                        y=cash_plot_data[plot[i]],
                        mode="lines",
                        name=f'{symbol.upper()} {plot[i].replace("_", " ")}',
                        row=i + 1,
                        col=1,
                    )
                    fig.set_title(f"{plot[i].replace('_', ' ')}", row=i + 1, col=1)
            fig.show(external=fig.is_image_export(export))
        else:
            cash = cash[cash.columns[::-1]]
            # Snake case to english
            cash.index = cash.index.to_series().apply(
                lambda x: x.replace("_", " ").title()
            )

            print_rich_table(
                cash.drop(index=["Final Link", "Link"]),
                headers=list(cash.columns),
                title=f"{symbol.upper()} Cash Flow",
                show_index=True,
                export=bool(export),
            )

            console.print(cash.loc["Final Link"].to_frame().to_string())
            console.print()
            console.print(cash.loc["Link"].to_frame().to_string())
            console.print()
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "cash",
            cash,
            sheet_name,
            fig,
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
            export=bool(export),
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
            export=bool(export),
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
            export=bool(export),
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
        df,
        headers=df.columns,
        show_index=True,
        title="Rating",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rot",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_price_targets(
    symbol: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """Display price targets for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol : str
        Symbol
    limit: int
        Number of last days ratings to display
    export: str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    """
    columns_to_show = [
        "publishedDate",
        "analystCompany",
        "adjPriceTarget",
        "priceWhenPosted",
    ]
    price_targets = fmp_model.get_price_targets(symbol)
    if price_targets.empty:
        console.print(f"[red]No price targets found for {symbol}[/red]\n")
        return
    price_targets["publishedDate"] = price_targets["publishedDate"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
            "%Y-%m-%d %H:%M"
        )
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt",
        price_targets,
        sheet_name,
    )

    print_rich_table(
        price_targets[columns_to_show].head(limit),
        headers=["Date", "Company", "Target", "Posted Price"],
        show_index=False,
        title=f"{symbol.upper()} Price Targets",
    )
