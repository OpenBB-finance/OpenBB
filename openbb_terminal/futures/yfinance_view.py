"""Yahoo Finance view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.futures import yfinance_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_search(
    category: str = "",
    exchange: str = "",
    description: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display search futures [Source: Yahoo Finance]

    Parameters
    ----------
    category: str
        Select the category where the future exists
    exchange: str
        Select the exchange where the future exists
    description: str
        Select the description of the future
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    """
    df = yfinance_model.get_search_futures(category, exchange, description)
    if df.empty:
        console.print("[red]No futures data found.\n[/red]")
        return

    print_rich_table(df, export=bool(export))
    console.print()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "search",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_historical(
    symbols: List[str],
    expiry: str = "",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Display historical futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbols: List[str]
        List of future timeseries symbols to display
    expiry: str
        Future expiry date with format YYYY-MM
    start_date: Optional[str]
        Start date of the historical data with format YYYY-MM-DD
    end_date: Optional[str]
        End date of the historical data with format YYYY-MM-DD
    raw: bool
        Display futures timeseries in raw format
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    symbols_validated = list()
    for symbol in symbols:
        if symbol in yfinance_model.FUTURES_DATA["Ticker"].unique().tolist():
            symbols_validated.append(symbol)
        else:
            console.print(f"[red]{symbol} is not a valid symbol[/red]")

    symbols = symbols_validated

    if not symbols:
        return console.print("No symbol was provided.\n")

    historicals = yfinance_model.get_historical_futures(
        symbols, expiry, start_date, end_date
    )

    if historicals.empty:
        return None

    fig = OpenBBFigure()

    if len(symbols) > 1:
        for tick in historicals["Adj Close"].columns.tolist():
            if len(historicals["Adj Close"][tick].dropna()) == 1:
                console.print(
                    f"\nA single datapoint on {tick} is not enough to depict a chart, data shown below."
                )
                naming = yfinance_model.FUTURES_DATA[
                    yfinance_model.FUTURES_DATA["Ticker"] == tick
                ]["Description"].values[0]
                print_rich_table(
                    historicals["Adj Close"][tick].dropna().to_frame(),
                    headers=[naming],
                    show_index=True,
                    title="Futures timeseries",
                )
                continue

            name = yfinance_model.FUTURES_DATA[
                yfinance_model.FUTURES_DATA["Ticker"] == tick
            ]["Description"].values[0]

            fig.add_scatter(
                x=historicals["Adj Close"][tick].dropna().index,
                y=historicals["Adj Close"][tick].dropna().values,
                name=name,
            )

    else:
        if len(historicals["Adj Close"]) == 1:
            console.print(
                f"\nA single datapoint on {symbols[0]} is not enough to depict a chart, data shown below."
            )
            return print_rich_table(
                historicals,
                headers=list(historicals["Adj Close"].columns),
                show_index=True,
                title="Futures timeseries",
            )

        name = yfinance_model.FUTURES_DATA[
            yfinance_model.FUTURES_DATA["Ticker"] == symbols[0]
        ]["Description"].values[0]

        fig.add_scatter(
            x=historicals["Adj Close"].dropna().index,
            y=historicals["Adj Close"].dropna().values,
            name=name,
        )
        if expiry:
            name += f" with expiry {expiry}"

        fig.set_title(name)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "historical",
        historicals,
        sheet_name,
        fig,
    )

    if raw or len(historicals) == 1:
        if not raw and len(historicals) == 1:
            console.print(
                "\nA single datapoint is not enough to depict a chart, data is presented below."
            )

        print_rich_table(
            historicals,
            headers=list(historicals.columns),
            show_index=True,
            title="Futures timeseries",
            export=bool(export),
        )
        return console.print()

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_curve(
    symbol: str,
    date: Optional[str] = "",
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Display curve futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Curve future symbol to display
    date: str
        Optionally include historical futures prices for each contract
    raw: bool
        Display futures prices in raw format
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if symbol not in yfinance_model.FUTURES_DATA["Ticker"].unique().tolist():
        return console.print(f"[red]'{symbol}' is not a valid symbol[/red]")

    df = (
        yfinance_model.get_curve_futures(symbol)
        if date == ""
        else yfinance_model.get_curve_futures(symbol, date)
    )

    if df.empty:
        return console.print("[red]No future data found to generate curve.[/red]\n")

    fig = OpenBBFigure()

    name = yfinance_model.FUTURES_DATA[yfinance_model.FUTURES_DATA["Ticker"] == symbol][
        "Description"
    ].values[0]

    df.index = pd.to_datetime(df.index, format="%b-%Y")

    if date == "":
        fig.add_scatter(
            x=df.index,
            y=df.iloc[:, 0],
            mode="lines+markers",
            name=name,
            line=dict(dash="dash", width=4),
            marker=dict(size=10),
        )
    else:
        for col in df.columns.tolist():
            fig.add_scatter(
                x=df.index,
                y=df[col],
                mode="lines+markers",
                name=col,
                line=dict(dash="dash", width=4),
                marker=dict(size=10),
            )
    fig.set_title(name)
    fig.update_layout(xaxis=dict(tickformat="%b-%Y"))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "curve",
        df,
        sheet_name,
        fig,
    )

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title="Futures curve",
            export=bool(export),
        )
        return console.print()

    return fig.show(external=external_axes)
