""" Stockgrid View """
__docformat__ = "numpy"

import logging
import os
from datetime import timedelta
from typing import List, Optional

import matplotlib.pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import stockgrid_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def dark_pool_short_positions(
    limit: int = 10,
    sortby: str = "dpp_dollar",
    ascend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Get dark pool short positions. [Source: Stockgrid]

    Parameters
    ----------
    limit : int
        Number of top tickers to show
    sortby : str
        Field for which to sort by, where 'sv': Short Vol. [1M],
        'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],
        'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],
        'dpp_dollar': DP Position ($1B)
    ascend : bool
        Data in ascending order
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = stockgrid_model.get_dark_pool_short_positions(sortby, ascend)

    dp_date = df["Date"].values[0]
    df = df.drop(columns=["Date"])
    df["Net Short Volume $"] = df["Net Short Volume $"] / 100_000_000
    df["Short Volume"] = df["Short Volume"] / 1_000_000
    df["Net Short Volume"] = df["Net Short Volume"] / 1_000_000
    df["Short Volume %"] = df["Short Volume %"] * 100
    df["Dark Pools Position $"] = df["Dark Pools Position $"] / (1_000_000_000)
    df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000
    df.columns = [
        "Ticker",
        "Short Vol. [1M]",
        "Short Vol. %",
        "Net Short Vol. [1M]",
        "Net Short Vol. ($100M)",
        "DP Position [1M]",
        "DP Position ($1B)",
    ]

    # Assuming that the datetime is the same, which from my experiments seems to be the case
    print_rich_table(
        df.iloc[:limit],
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dppos",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def short_interest_days_to_cover(
    limit: int = 10,
    sortby: str = "float",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Print short interest and days to cover. [Source: Stockgrid]

    Parameters
    ----------
    limit : int
        Number of top tickers to show
    sortby : str
        Field for which to sort by, where 'float': Float Short %%,
        'dtc': Days to Cover, 'si': Short Interest
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = stockgrid_model.get_short_interest_days_to_cover(sortby)

    dp_date = df["Date"].values[0]
    df = df.drop(columns=["Date"])

    # Assuming that the datetime is the same, which from my experiments seems to be the case
    print_rich_table(
        df.iloc[:limit],
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortdtc",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def short_interest_volume(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot price vs short interest volume. [Source: Stockgrid]

    Parameters
    ----------
    symbol : str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None

    """

    df, prices = stockgrid_model.get_short_interest_volume(symbol)
    if df.empty:
        console.print("[red]No data available[/red]\n")
        return

    if raw:
        df.date = df.date.dt.date

        print_rich_table(
            df.iloc[:limit],
            headers=list(df.columns),
            show_index=False,
            title="Price vs Short Volume",
        )
    else:
        # This plot has 3 axes
        if not external_axes:
            _, axes = plt.subplots(
                2,
                1,
                sharex=True,
                figsize=plot_autoscale(),
                dpi=PLOT_DPI,
                gridspec_kw={"height_ratios": [2, 1]},
            )
            (ax, ax1) = axes
            ax2 = ax.twinx()
        elif is_valid_axes_count(external_axes, 3):
            (ax, ax1, ax2) = external_axes
        else:
            return

        ax.bar(
            df["date"],
            df["Total Vol. [1M]"],
            width=timedelta(days=1),
            color=theme.up_color,
            label="Total Volume",
        )
        ax.bar(
            df["date"],
            df["Short Vol. [1M]"],
            width=timedelta(days=1),
            color=theme.down_color,
            label="Short Volume",
        )

        ax.set_ylabel("Volume [1M]")

        ax2.plot(
            df["date"].values,
            prices[len(prices) - len(df) :],  # noqa: E203
            label="Price",
        )
        ax2.set_ylabel("Price ($)")

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax.set_xlim(
            df["date"].values[max(0, len(df) - limit)],
            df["date"].values[len(df) - 1],
        )

        ax.ticklabel_format(style="plain", axis="y")
        ax.set_title(f"Price vs Short Volume Interest for {symbol}")

        ax1.plot(
            df["date"].values,
            df["Short Vol. %"],
            label="Short Vol. %",
        )

        ax1.set_xlim(
            df["date"].values[max(0, len(df) - limit)],
            df["date"].values[len(df) - 1],
        )
        ax1.set_ylabel("Short Vol. %")

        lines, labels = ax1.get_legend_handles_labels()
        ax1.legend(lines, labels, loc="upper left")
        ax1.set_ylim([0, 100])

        theme.style_twin_axes(ax, ax2)
        theme.style_primary_axis(ax1)

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortint(stockgrid)",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def net_short_position(
    symbol: str,
    limit: int = 84,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot net short position. [Source: Stockgrid]

    Parameters
    ----------
    symbol: str
        Stock to plot for
    limit : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None

    """

    df = stockgrid_model.get_net_short_position(symbol)
    if df.empty:
        console.print("[red]No data available[/red]\n")
        return

    if raw:
        df["dates"] = df["dates"].dt.date

        print_rich_table(
            df.iloc[:limit],
            headers=list(df.columns),
            show_index=False,
            title="Net Short Positions",
        )

    else:
        # This plot has 2 axes
        if not external_axes:
            _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax2 = ax1.twinx()
        elif is_valid_axes_count(external_axes, 2):
            (ax1, ax2) = external_axes
        else:
            return

        df = df.sort_values(by=["dates"])
        ax1.bar(
            df["dates"],
            df["Net Short Vol. (1k $)"],
            color=theme.down_color,
            label="Net Short Vol. (1k $)",
        )
        ax1.set_ylabel("Net Short Vol. (1k $)")

        ax2.plot(
            df["dates"].values,
            df["Position (1M $)"],
            c=theme.up_color,
            label="Position (1M $)",
        )
        ax2.set_ylabel("Position (1M $)")

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax1.set_xlim(
            df["dates"].values[max(0, len(df) - limit)],
            df["dates"].values[len(df) - 1],
        )

        ax1.set_title(f"Net Short Vol. vs Position for {symbol}")

        theme.style_twin_axes(ax1, ax2)

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortpos",
        df,
        sheet_name,
    )
