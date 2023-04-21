"""Quiverquant View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.government import quiverquant_model

# pylint: disable=C0302,inconsistent-return-statements


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_last_government(
    gov_type: str = "congress",
    limit: int = 5,
    representative: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display last government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    limit: int
        Number of days to look back
    representative: str
        Specific representative to look at
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """
    df_gov = quiverquant_model.get_last_government(gov_type, limit, representative)

    if df_gov.empty:
        if representative:
            console.print(
                f"No representative {representative} found in the past {limit}"
                f" days. The following are available: "
                f"{', '.join(df_gov['Representative'].str.split().str[0].unique())}"
            )
        else:
            console.print(f"No {gov_type} trading data found\n")
        return

    console.print(f"\nLast transactions for {gov_type.upper()}\n")

    print_rich_table(
        df_gov,
        headers=list(df_gov.columns),
        show_index=False,
        title="Representative Trading",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lasttrades",
        df_gov,
        sheet_name,
    )


@log_start_end(log=logger)
def display_government_buys(
    gov_type: str = "congress",
    past_transactions_months: int = 6,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Top buy government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for
    limit: int
        Number of tickers to show
    raw: bool
        Display raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    """
    df_gov = quiverquant_model.get_government_buys(gov_type, past_transactions_months)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    if raw:
        df = pd.DataFrame(
            df_gov.groupby("Ticker")["upper"]
            .sum()
            .div(1000)
            .sort_values(ascending=False)
            .head(n=limit)
        )
        print_rich_table(
            df,
            headers=["Amount ($1k)"],
            show_index=True,
            title="Top Government Buys",
            export=bool(export),
        )

    df_gov_sorted = (
        df_gov.groupby("Ticker")["upper"]
        .sum()
        .div(1000)
        .sort_values(ascending=False)
        .head(n=limit)
    )

    fig = OpenBBFigure(xaxis_title="Ticker", yaxis_title="Amount [1k $]")
    fig.set_title(
        f"{gov_type.upper()}'s top {limit} purchased stocks (upper) in last {past_transactions_months} months"
    )

    fig.add_bar(
        x=df_gov_sorted.index, y=df_gov_sorted.values, marker_color=theme.get_colors()
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "topbuys",
        df_gov,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_government_sells(
    gov_type: str = "congress",
    past_transactions_months: int = 6,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Top sell government trading [Source: quiverquant.com]

    Parameters
    ----------
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get trading for
    limit: int
        Number of tickers to show
    raw: bool
        Display raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_gov = quiverquant_model.get_government_sells(gov_type, past_transactions_months)

    if df_gov.empty:
        console.print(f"No {gov_type} trading data found\n")
        return

    if raw:
        df = pd.DataFrame(
            df_gov.groupby("Ticker")["upper"]
            .sum()
            .div(1000)
            .sort_values(ascending=True)
            .abs()
            .head(n=limit)
        )
        print_rich_table(
            df,
            headers=["Amount ($1k)"],
            show_index=True,
            title="Top Government Trades",
            export=bool(export),
        )

    df_gov_sorted = (
        df_gov.groupby("Ticker")["upper"]
        .sum()
        .div(1000)
        .sort_values()
        .abs()
        .head(n=limit)
    )

    fig = OpenBBFigure(xaxis_title="Ticker", yaxis_title="Amount ($1k)")
    fig.set_title(
        f"{limit} most sold stocks over last {past_transactions_months} months"
        f" (upper bound) for {gov_type}"
    )

    fig.add_bar(
        x=df_gov_sorted.index, y=df_gov_sorted.values, marker_color=theme.get_colors()
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "topsells",
        df_gov,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_last_contracts(
    past_transaction_days: int = 2,
    limit: int = 20,
    sum_contracts: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Last government contracts [Source: quiverquant.com]

    Parameters
    ----------
    past_transaction_days: int
        Number of days to look back
    limit: int
        Number of contracts to show
    sum_contracts: bool
        Flag to show total amount of contracts given out.
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = quiverquant_model.get_last_contracts(past_transaction_days)

    if df.empty:
        return

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Last Government Contracts",
        export=bool(export),
        limit=limit,
    )

    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.date
    df = df.groupby("Date").sum(True).div(1000)

    fig = OpenBBFigure(yaxis_title="Amount ($1k)", xaxis_title="Date")
    fig.set_title("Total amount of government contracts given")

    fig.add_bar(x=df.index, y=df["Amount"].values, marker_color=theme.get_colors())
    fig.update_layout(xaxis=dict(nticks=min(len(df.index) + 1, 10)))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lastcontracts",
        df,
        sheet_name,
        fig,
    )

    if not sum_contracts:
        return

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def plot_government(
    government: pd.DataFrame,
    symbol: str,
    gov_type: str,
    external_axes: bool = False,
) -> Optional[OpenBBFigure]:
    """Helper for plotting government trading

    Parameters
    ----------
    government: pd.DataFrame
        Data to plot
    symbol: str
        Ticker symbol to plot government trading
    gov_type: str
        Type of government data between: congress, senate and house
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    fig = OpenBBFigure(yaxis_title="Amount ($1k)", xaxis_title="Date")
    fig.set_title(f"{gov_type.capitalize()} trading on {symbol}")

    fig.add_scatter(
        name="lower",
        x=government["TransactionDate"].unique(),
        y=government.groupby("TransactionDate")["lower"].sum().values / 1000,
    )
    fig.add_scatter(
        name="upper",
        x=government["TransactionDate"].unique(),
        y=government.groupby("TransactionDate")["upper"].sum().values / 1000,
    )

    color = theme.get_colors()[0]
    fig.update_traces(mode="lines", line_color=color, fillcolor=color, fill="tonexty")
    fig.update_layout(showlegend=False)

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_government_trading(
    symbol: str,
    gov_type: str = "congress",
    past_transactions_months: int = 6,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Government trading for specific ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    gov_type: str
        Type of government data between: congress, senate and house
    past_transactions_months: int
        Number of months to get transactions for
    raw: bool
        Show raw output of trades
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_gov = quiverquant_model.get_cleaned_government_trading(
        symbol=symbol,
        gov_type=gov_type,
        past_transactions_months=past_transactions_months,
    )

    if df_gov is None or isinstance(df_gov, pd.DataFrame) and df_gov.empty:
        return console.print(f"No {gov_type} trading data found\n")

    fig = plot_government(df_gov, symbol, gov_type, True)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gtrades",
        df_gov,
        sheet_name,
        fig,
    )

    if raw:
        return print_rich_table(
            df_gov,
            headers=list(df_gov.columns),
            show_index=False,
            title=f"Government Trading for {symbol.upper()}",
            export=bool(export),
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_contracts(
    symbol: str,
    past_transaction_days: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Show government contracts for ticker [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker to get congress trading data from
    past_transaction_days: int
        Number of days to get transactions for
    raw: bool
        Flag to display raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_contracts = quiverquant_model.get_contracts(symbol, past_transaction_days)

    if df_contracts.empty:
        return

    if raw:
        print_rich_table(
            df_contracts,
            headers=list(df_contracts.columns),
            show_index=False,
            title=f"Government Contracts for {symbol.upper()}",
            export=bool(export),
        )

    if df_contracts.Amount.abs().sum() == 0:
        return console.print("Contracts found, but they are all equal to $0.00.\n")

    fig = OpenBBFigure(yaxis_title="Amount ($1k)", xaxis_title="Date")
    fig.set_title(f"Sum of latest government contracts to {symbol}")

    df_contracts_grouped = df_contracts.groupby("Date").sum(numeric_only=True)

    fig.add_bar(
        name="Amount",
        x=df_contracts["Date"].unique(),
        y=df_contracts_grouped["Amount"].values / 1000,
    )
    fig.update_layout(xaxis=dict(type="category"))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "contracts",
        df_contracts,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def display_qtr_contracts(
    analysis: str = "total",
    limit: int = 5,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Quarterly contracts [Source: quiverquant.com]

    Parameters
    ----------
    analysis: str
        Analysis to perform.  Either 'total', 'upmom' 'downmom'
    limit: int
        Number to show
    raw: bool
        Flag to display raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    symbols = quiverquant_model.get_qtr_contracts(analysis, limit)

    if symbols.empty:
        return None

    if analysis in ("upmom", "downmom"):
        if raw:
            return print_rich_table(
                pd.DataFrame(symbols.values),
                headers=["symbols"],
                show_index=True,
                title="Quarterly Contracts",
            )

        titles = {
            "upmom": "Highest increasing quarterly Government Contracts",
            "downmom": "Highest decreasing quarterly Government Contracts",
        }

        fig = OpenBBFigure(xaxis_title="Quarter", yaxis_title="Amount ($1M)")

        fig.set_title(title=titles[analysis])

        max_amount = 0
        quarter_ticks = []
        df_contracts = quiverquant_model.get_government_trading("quarter-contracts")
        for symbol in symbols:
            amounts = (
                df_contracts[df_contracts["Ticker"] == symbol]
                .sort_values(by=["Year", "Qtr"])["Amount"]
                .values
            )

            qtr = (
                df_contracts[df_contracts["Ticker"] == symbol]
                .sort_values(by=["Year", "Qtr"])["Qtr"]
                .values
            )
            year = (
                df_contracts[df_contracts["Ticker"] == symbol]
                .sort_values(by=["Year", "Qtr"])["Year"]
                .values
            )

            fig.add_scatter(
                x=np.arange(0, len(amounts)),
                y=amounts / 1_000_000,
                mode="lines+markers",
                name=symbol,
                marker=dict(size=16, line=dict(width=0), symbol="star"),
            )

            if len(amounts) > max_amount:
                max_amount = len(amounts)
                quarter_ticks = [
                    f"{quarter[0]} - Q{quarter[1]} " for quarter in zip(year, qtr)
                ]
                fig.update_layout(
                    xaxis=dict(
                        tickmode="array",
                        tickvals=np.arange(0, len(amounts)),
                        ticktext=quarter_ticks,
                    )
                )

                export_data(
                    export,
                    os.path.dirname(os.path.abspath(__file__)),
                    "qtrcontracts",
                    symbols,
                    sheet_name,
                    fig,
                )
            return fig.show(external=external_axes)

    if analysis == "total":
        print_rich_table(
            symbols,
            headers=["Total"],
            title="Quarterly Contracts",
            show_index=True,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "qtrcontracts",
        symbols,
        sheet_name,
    )
    return None


@log_start_end(log=logger)
def display_hist_contracts(
    symbol: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Show historical quarterly government contracts [Source: quiverquant.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to get congress trading data from
    raw: bool
        Flag to display raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_contracts = quiverquant_model.get_hist_contracts(symbol)

    if df_contracts.empty:
        return None

    amounts = df_contracts.sort_values(by=["Year", "Qtr"])["Amount"].values

    qtr = df_contracts.sort_values(by=["Year", "Qtr"])["Qtr"].values
    year = df_contracts.sort_values(by=["Year", "Qtr"])["Year"].values

    quarter_ticks = [
        f"{quarter[0]}" if quarter[1] == 1 else "" for quarter in zip(year, qtr)
    ]

    fig = OpenBBFigure(
        xaxis=dict(
            title="Quarter",
            tickmode="array",
            tickvals=np.arange(0, len(amounts)),
            ticktext=quarter_ticks,
        ),
        yaxis_title="Amount ($1k)",
    )

    fig.set_title(f"Historical Quarterly Government Contracts for {symbol.upper()}")

    fig.add_scatter(
        x=np.arange(0, len(amounts)),
        y=amounts / 1000,
        mode="lines+markers",
        name=symbol,
        marker=dict(
            size=15,
            line=dict(width=2, color=theme.get_colors()[0]),
            color=theme.down_color,
        ),
        line=dict(color=theme.get_colors()[0]),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "histcont",
        sheet_name=sheet_name,
        figure=fig,
    )

    if raw:
        return print_rich_table(
            df_contracts,
            headers=list(df_contracts.columns),
            floatfmt=[".0f", ".0f", ".2f"],
            title="Historical Quarterly Government Contracts",
            export=bool(export),
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_top_lobbying(
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Top lobbying tickers based on total spent

    Parameters
    ----------
    limit: int
        Number of tickers to show
    raw: bool
        Show raw data
    export:
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    """
    df_lobbying = quiverquant_model.get_top_lobbying()

    if df_lobbying.empty:
        return

    df_lobbying["Amount"] = df_lobbying.Amount.astype(float).fillna(0) / 100_000

    lobbying_by_ticker = pd.DataFrame(
        df_lobbying.groupby("Ticker")["Amount"].agg("sum")
    ).sort_values(by="Amount", ascending=False)

    df = lobbying_by_ticker.head(limit)

    fig = OpenBBFigure(xaxis_title="Ticker", yaxis_title="Total Amount ($100k)")
    fig.set_title(f"Corporate Lobbying Spent since {df_lobbying['Date'].min()}")

    fig.add_bar(
        x=df.index,
        y=df.Amount,
        name="Amount ($100k)",
        marker_color=theme.get_colors(),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lobbying",
        df_lobbying,
        sheet_name,
        fig,
    )

    if raw:
        return print_rich_table(
            lobbying_by_ticker,
            headers=["Amount ($100k)"],
            show_index=True,
            title="Top Lobbying Tickers",
            export=bool(export),
            limit=limit,
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_lobbying(symbol: str, limit: int = 10):
    """Corporate lobbying details

    Parameters
    ----------
    symbol: str
        Ticker symbol to get corporate lobbying data from
    limit: int
        Number of events to show
    """
    df_lobbying = quiverquant_model.get_lobbying(symbol, limit)

    if df_lobbying.empty:
        return

    for _, row in df_lobbying.iterrows():
        amount = (
            "$" + str(int(float(row["Amount"]))) if row["Amount"] is not None else "N/A"
        )
        console.print(f"{row['Date']}: {row['Client']} {amount}")
        if (row["Amount"] is not None) and (row["Specific_Issue"] is not None):
            console.print(
                "\t" + row["Specific_Issue"].replace("\n", " ").replace("\r", "")
            )
        console.print("")
    console.print("")
