""" Quandl View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.ticker
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.decorators import check_api_key
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
    plot_autoscale,
    is_valid_axes_count,
)
from openbb_terminal.stocks.dark_pool_shorts import quandl_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def plot_short_interest(
    symbol: str,
    data: pd.DataFrame,
    nyse: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    symbol : str
        ticker to get short interest from
    data: pd.DataFrame
        Short interest dataframe
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """

    # This plot has 2 axes
    if not external_axes:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax2 = ax1.twinx()
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    ax1.bar(
        data.index,
        data["Short Volume"],
        0.3,
        color=theme.down_color,
    )
    ax1.bar(
        data.index,
        data["Total Volume"] - data["Short Volume"],
        0.3,
        bottom=data["Short Volume"],
        color=theme.up_color,
    )
    ax1.set_ylabel("Shares")
    ax1.set_title(f"{('NASDAQ', 'NYSE')[nyse]} Short Interest on {symbol}")

    ax1.legend(labels=["Short Volume", "Total Volume"], loc="best")
    ax1.yaxis.set_major_formatter(matplotlib.ticker.EngFormatter())

    ax2.tick_params(axis="y")
    ax2.set_ylabel("Percentage of Volume Shorted")
    ax2.plot(
        data.index,
        data["% of Volume Shorted"],
    )
    ax2.tick_params(axis="y", which="major")
    ax2.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.0f%%"))

    theme.style_twin_axes(ax1, ax2)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def short_interest(
    symbol: str,
    nyse: bool = False,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    symbol : str
        ticker to get short interest from
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    limit: int
        Number of past days to show short interest
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_short_interest = quandl_model.get_short_interest(symbol, nyse)

    df_short_interest = df_short_interest.tail(limit)

    df_short_interest.columns = [
        "".join(" " + char if char.isupper() else char.strip() for char in idx).strip()
        for idx in df_short_interest.columns.tolist()
    ]
    pd.options.mode.chained_assignment = None

    vol_pct = (
        100
        * df_short_interest["Short Volume"].values
        / df_short_interest["Total Volume"].values
    )
    df_short_interest["% of Volume Shorted"] = [round(pct, 2) for pct in vol_pct]

    plot_short_interest(symbol, df_short_interest, nyse, external_axes)

    if raw:
        df_short_interest["% of Volume Shorted"] = df_short_interest[
            "% of Volume Shorted"
        ].apply(lambda x: f"{x/100:.2%}")
        df_short_interest = df_short_interest.applymap(
            lambda x: lambda_long_number_format(x)
        ).sort_index(ascending=False)

        df_short_interest.index = df_short_interest.index.date

        print_rich_table(
            df_short_interest,
            headers=list(df_short_interest.columns),
            show_index=True,
            title="Short Interest of Stock",
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "psi(quandl)",
        df_short_interest,
    )
