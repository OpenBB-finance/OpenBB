""" Stockgrid View """
__docformat__ = "numpy"

import logging
import os
from datetime import timedelta
from typing import List, Optional

import matplotlib.pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def dark_pool_short_positions(num: int, sort_field: str, ascending: bool, export: str):
    """Get dark pool short positions. [Source: Stockgrid]

    Parameters
    ----------
    num : int
        Number of top tickers to show
    sort_field : str
        Field for which to sort by, where 'sv': Short Vol. (1M),
        'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. (1M),
        'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position (1M),
        'dpp_dollar': DP Position ($1B)
    ascending : bool
        Data in ascending order
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = stockgrid_model.get_dark_pool_short_positions(sort_field, ascending)

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
        "Short Vol. (1M)",
        "Short Vol. %",
        "Net Short Vol. (1M)",
        "Net Short Vol. ($100M)",
        "DP Position (1M)",
        "DP Position ($1B)",
    ]

    # Assuming that the datetime is the same, which from my experiments seems to be the case
    print_rich_table(
        df.iloc[:num],
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dppos",
        df,
    )


@log_start_end(log=logger)
def short_interest_days_to_cover(num: int, sort_field: str, export: str):
    """Print short interest and days to cover. [Source: Stockgrid]

    Parameters
    ----------
    num : int
        Number of top tickers to show
    sort_field : str
        Field for which to sort by, where 'float': Float Short %%,
        'dtc': Days to Cover, 'si': Short Interest
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = stockgrid_model.get_short_interest_days_to_cover(sort_field)

    dp_date = df["Date"].values[0]
    df = df.drop(columns=["Date"])
    df["Short Interest"] = df["Short Interest"] / 1_000_000
    df.head()
    df.columns = [
        "Ticker",
        "Float Short %",
        "Days to Cover",
        "Short Interest (1M)",
    ]

    # Assuming that the datetime is the same, which from my experiments seems to be the case
    print_rich_table(
        df.iloc[:num],
        headers=list(df.columns),
        show_index=False,
        title=f"Data for: {dp_date}",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortdtc",
        df,
    )


@log_start_end(log=logger)
def short_interest_volume(
    ticker: str,
    num: int,
    raw: bool,
    export: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot price vs short interest volume. [Source: Stockgrid]

    Parameters
    ----------
    ticker : str
        Stock to plot for
    num : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axis is expected in the list), by default None

    """
    df, prices = stockgrid_model.get_short_interest_volume(ticker)

    if raw:
        df = df.sort_values(by="date", ascending=False)

        df["Short Vol. (1M)"] = df["short_volume"] / 1_000_000
        df["Short Vol. %"] = df["short_volume%"] * 100
        df["Short Exempt Vol. (1K)"] = df["short_exempt_volume"] / 1_000
        df["Total Vol. (1M)"] = df["total_volume"] / 1_000_000

        df = df[
            [
                "date",
                "Short Vol. (1M)",
                "Short Vol. %",
                "Short Exempt Vol. (1K)",
                "Total Vol. (1M)",
            ]
        ]

        df.date = df.date.dt.date

        print_rich_table(
            df.iloc[:num],
            headers=list(df.columns),
            show_index=False,
            title="Price vs Short Volume",
        )
    else:

        # This plot has 3 axis
        if not external_axes:
            _, (ax, ax1) = plt.subplots(
                2,
                1,
                sharex=True,
                figsize=plot_autoscale(),
                dpi=PLOT_DPI,
                gridspec_kw={"height_ratios": [2, 1]},
            )
            ax2 = ax.twinx()
        else:
            if len(external_axes) != 3:
                console.print("[red]Expected list of three axis item./n[/red]")
                return
            (ax, ax1, ax2) = external_axes

        ax.bar(
            df["date"],
            df["total_volume"] / 1_000_000,
            width=timedelta(days=1),
            color=theme.up_color,
            label="Total Volume",
        )
        ax.bar(
            df["date"],
            df["short_volume"] / 1_000_000,
            width=timedelta(days=1),
            color=theme.down_color,
            label="Short Volume",
        )

        ax.set_ylabel("Volume (1M)")

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
            df["date"].values[max(0, len(df) - num)],
            df["date"].values[len(df) - 1],
        )

        ax.ticklabel_format(style="plain", axis="y")
        ax.set_title(f"Price vs Short Volume Interest for {ticker}")

        ax1.plot(
            df["date"].values,
            100 * df["short_volume%"],
            label="Short Vol. %",
        )

        ax1.set_xlim(
            df["date"].values[max(0, len(df) - num)],
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

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortint(stockgrid)",
        df,
    )


@log_start_end(log=logger)
def net_short_position(
    ticker: str,
    num: int,
    raw: bool,
    export: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot net short position. [Source: Stockgrid]

    Parameters
    ----------
    ticker: str
        Stock to plot for
    num : int
        Number of last open market days to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None

    """
    df = stockgrid_model.get_net_short_position(ticker)

    if raw:
        df = df.sort_values(by="dates", ascending=False)

        df["Net Short Vol. (1k $)"] = df["dollar_net_volume"] / 1_000
        df["Position (1M $)"] = df["dollar_dp_position"]

        df = df[
            [
                "dates",
                "Net Short Vol. (1k $)",
                "Position (1M $)",
            ]
        ]

        df["dates"] = df["dates"].dt.date

        print_rich_table(
            df.iloc[:num],
            headers=list(df.columns),
            show_index=False,
            title="Net Short Positions",
        )

    else:

        # This plot has 2 axis
        if not external_axes:
            _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax2 = ax1.twinx()
        else:
            if len(external_axes) != 2:
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax1, ax2) = external_axes

        ax1.bar(
            df["dates"],
            df["dollar_net_volume"] / 1_000,
            color=theme.down_color,
            label="Net Short Vol. (1k $)",
        )
        ax1.set_ylabel("Net Short Vol. (1k $)")

        ax2.plot(
            df["dates"].values,
            df["dollar_dp_position"],
            c=theme.up_color,
            label="Position (1M $)",
        )
        ax2.set_ylabel("Position (1M $)")

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax1.set_xlim(
            df["dates"].values[max(0, len(df) - num)],
            df["dates"].values[len(df) - 1],
        )

        ax1.set_title(f"Net Short Vol. vs Position for {ticker}")

        theme.style_twin_axes(ax1, ax2)

        if not external_axes:
            theme.visualize_output()

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortpos",
        df,
    )
