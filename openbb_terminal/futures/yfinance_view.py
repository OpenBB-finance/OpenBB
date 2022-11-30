"""Yahoo Finance view"""
__docformat__ = "numpy"

from typing import Optional, List
from itertools import cycle
import logging
import os

from datetime import datetime, timedelta
from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.futures import yfinance_model
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console
from openbb_terminal.futures.futures_helper import make_white

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_search(
    category: str = "",
    exchange: str = "",
    description: str = "",
    export: str = "",
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
    export: str
        Type of format to export data
    """
    df = yfinance_model.get_search_futures(category, exchange, description)
    if df.empty:
        console.print("[red]No futures data found.\n[/red]")
        return

    print_rich_table(df)
    console.print()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "search",
        df,
    )


@log_start_end(log=logger)
def display_historical(
    symbols: List[str],
    expiry: str = "",
    start_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display historical futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbols: List[str]
        List of future timeseries symbols to display
    expiry: str
        Future expiry date with format YYYY-MM
    start_date : Optional[str]
        Initial date like string (e.g., 2021-10-01)
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=3 * 365)).strftime("%Y-%m-%d")

    symbols_validated = list()
    for symbol in symbols:
        if symbol in yfinance_model.FUTURES_DATA["Ticker"].unique().tolist():
            symbols_validated.append(symbol)
        else:
            console.print(f"[red]{symbol} is not a valid symbol[/red]")

    symbols = symbols_validated

    if not symbols:
        console.print("No symbol was provided.\n")
        return

    historicals = yfinance_model.get_historical_futures(symbols, expiry)

    if historicals.empty:
        console.print(f"No data was found for the symbols: {', '.join(symbols)}\n")
        return

    if raw or len(historicals) == 1:

        if not raw and len(historicals) == 1:
            console.print(
                "\nA single datapoint is not enough to depict a chart, data is presented below."
            )

        print_rich_table(
            historicals[historicals.index > datetime.strptime(start_date, "%Y-%m-%d")],
            headers=list(historicals.columns),
            show_index=True,
            title="Futures timeseries",
        )
        console.print()

    else:

        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        colors = cycle(theme.get_colors())
        if len(symbols) > 1:
            name = list()
            for tick in historicals["Adj Close"].columns.tolist():
                if len(historicals["Adj Close"][tick].dropna()) == 1:
                    console.print(
                        f"\nA single datapoint on {tick} is not enough to depict a chart, data shown below."
                    )
                    naming = yfinance_model.FUTURES_DATA[
                        yfinance_model.FUTURES_DATA["Ticker"] == tick
                    ]["Description"].values[0]
                    print_rich_table(
                        historicals[
                            historicals["Adj Close"][tick].index
                            > datetime.strptime(start_date, "%Y-%m-%d")
                        ]["Adj Close"][tick]
                        .dropna()
                        .to_frame(),
                        headers=[naming],
                        show_index=True,
                        title="Futures timeseries",
                    )
                    continue

                name.append(
                    yfinance_model.FUTURES_DATA[
                        yfinance_model.FUTURES_DATA["Ticker"] == tick
                    ]["Description"].values[0]
                )
                ax.plot(
                    historicals["Adj Close"][tick].dropna().index,
                    historicals["Adj Close"][tick].dropna().values,
                    color=next(colors, "#FCED00"),
                )
                ax.legend(name)

                first = datetime.strptime(start_date, "%Y-%m-%d")
                if historicals["Adj Close"].index[0] > first:
                    first = historicals["Adj Close"].index[0]
                ax.set_xlim(first, historicals["Adj Close"].index[-1])
                theme.style_primary_axis(ax)

                make_white(ax)

            if external_axes is None:
                theme.visualize_output()
        else:
            if len(historicals["Adj Close"]) == 1:
                console.print(
                    f"\nA single datapoint on {symbols[0]} is not enough to depict a chart, data shown below."
                )
                print_rich_table(
                    historicals[
                        historicals["Adj Close"].index
                        > datetime.strptime(start_date, "%Y-%m-%d")
                    ],
                    headers=list(historicals["Adj Close"].columns),
                    show_index=True,
                    title="Futures timeseries",
                )

            else:
                name = yfinance_model.FUTURES_DATA[
                    yfinance_model.FUTURES_DATA["Ticker"] == symbols[0]
                ]["Description"].values[0]
                ax.plot(
                    historicals["Adj Close"].dropna().index,
                    historicals["Adj Close"].dropna().values,
                    color=next(colors, "#FCED00"),
                )
                if expiry:
                    ax.set_title(f"{name} with expiry {expiry}")
                else:
                    ax.set_title(name)

                first = datetime.strptime(start_date, "%Y-%m-%d")
                if historicals["Adj Close"].index[0] > first:
                    first = historicals["Adj Close"].index[0]
                ax.set_xlim(first, historicals["Adj Close"].index[-1])
                theme.style_primary_axis(ax)

                make_white(ax)
                if external_axes is None:
                    theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "historical",
        historicals[historicals.index > datetime.strptime(start_date, "%Y-%m-%d")],
    )


@log_start_end(log=logger)
def display_curve(
    symbol: str,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display curve futures [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Curve future symbol to display
    raw: bool
        Display futures timeseries in raw format
    export: str
        Type of format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    if symbol not in yfinance_model.FUTURES_DATA["Ticker"].unique().tolist():
        console.print(f"[red]'{symbol}' is not a valid symbol[/red]")
        return

    df = yfinance_model.get_curve_futures(symbol)

    if df.empty:
        console.print("[red]No future data found to generate curve.[/red]\n")
        return

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title="Futures curve",
        )
        console.print()

    else:
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        name = yfinance_model.FUTURES_DATA[
            yfinance_model.FUTURES_DATA["Ticker"] == symbol
        ]["Description"].values[0]
        colors = cycle(theme.get_colors())
        ax.plot(
            df.index,
            df.values,
            marker="o",
            linestyle="dashed",
            linewidth=2,
            markersize=8,
            color=next(colors, "#FCED00"),
        )
        make_white(ax)
        ax.set_title(name)
        theme.style_primary_axis(ax)

        if external_axes is None:
            theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "curve",
            df,
        )
