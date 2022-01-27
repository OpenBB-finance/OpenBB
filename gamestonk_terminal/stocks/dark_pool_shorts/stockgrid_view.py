""" Stockgrid View """
__docformat__ = "numpy"

import os
from datetime import timedelta
import matplotlib.pyplot as plt
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.feature_flags import USE_ION
from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model
from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
    export_data,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console


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


def short_interest_volume(ticker: str, num: int, raw: bool, export: str):
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
        _, axes = plt.subplots(
            2,
            1,
            figsize=(plot_autoscale()),
            dpi=PLOT_DPI,
            gridspec_kw={"height_ratios": [2, 1]},
        )

        axes[0].bar(
            df["date"],
            df["total_volume"] / 1_000_000,
            width=timedelta(days=1),
            color="b",
            alpha=0.4,
            label="Total Volume",
        )
        axes[0].bar(
            df["date"],
            df["short_volume"] / 1_000_000,
            width=timedelta(days=1),
            color="r",
            alpha=0.4,
            label="Short Volume",
        )

        axes[0].set_ylabel("Volume (1M)")
        ax2 = axes[0].twinx()
        ax2.plot(
            df["date"].values, prices[len(prices) - len(df) :], c="k", label="Price"
        )
        ax2.set_ylabel("Price ($)")

        lines, labels = axes[0].get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        axes[0].set_xlim(
            df["date"].values[max(0, len(df) - num)],
            df["date"].values[len(df) - 1],
        )

        axes[0].grid()
        axes[0].ticklabel_format(style="plain", axis="y")
        plt.title(f"Price vs Short Volume Interest for {ticker}")
        plt.gcf().autofmt_xdate()

        axes[1].plot(
            df["date"].values,
            100 * df["short_volume%"],
            c="green",
            label="Short Vol. %",
        )

        axes[1].set_xlim(
            df["date"].values[max(0, len(df) - num)],
            df["date"].values[len(df) - 1],
        )
        axes[1].set_ylabel("Short Vol. %")

        axes[1].grid(axis="y")
        lines, labels = axes[1].get_legend_handles_labels()
        axes[1].legend(lines, labels, loc="upper left")
        axes[1].set_ylim([0, 100])

        if USE_ION:
            plt.ion()

        plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortint(stockgrid)",
        df,
    )


def net_short_position(ticker: str, num: int, raw: bool, export: str):
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
        fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        ax = fig.add_subplot(111)
        ax.bar(
            df["dates"],
            df["dollar_net_volume"] / 1_000,
            color="r",
            alpha=0.4,
            label="Net Short Vol. (1k $)",
        )
        ax.set_ylabel("Net Short Vol. (1k $)")

        ax2 = ax.twinx()
        ax2.plot(
            df["dates"].values,
            df["dollar_dp_position"],
            c="tab:blue",
            label="Position (1M $)",
        )
        ax2.set_ylabel("Position (1M $)")

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax.set_xlim(
            df["dates"].values[max(0, len(df) - num)],
            df["dates"].values[len(df) - 1],
        )

        ax.grid()
        plt.title(f"Net Short Vol. vs Position for {ticker}")
        plt.gcf().autofmt_xdate()

        if USE_ION:
            plt.ion()

        plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shortpos",
        df,
    )
