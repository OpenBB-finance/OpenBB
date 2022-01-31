"""Custom TA indicators"""
__docformat__ = "numpy"

import logging
import os
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import custom_indicators_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def fibonacci_retracement(
    df_stock: pd.DataFrame,
    period: int = 120,
    start_date: Any = None,
    end_date: Any = None,
    s_ticker: str = "",
    export: str = "",
):
    """Calculate fibonacci retracement levels

    Parameters
    ----------
    df_stock: pd.DataFrame
        Stock data
    period: int
        Days to lookback
    start_date: Any
        User picked date for starting retracement
    end_date: Any
        User picked date for ending retracement
    s_ticker:str
        Stock ticker
    export: str
        Format to export data
    """
    (
        df_fib,
        min_date,
        max_date,
        min_pr,
        max_pr,
    ) = custom_indicators_model.calculate_fib_levels(
        df_stock, period, start_date, end_date
    )

    levels = df_fib.Price
    fig, ax = plt.subplots(figsize=(plot_autoscale()), dpi=cfp.PLOT_DPI)

    ax.plot(df_stock["Adj Close"], "b")
    ax.plot([min_date, max_date], [min_pr, max_pr], c="k")

    for i in levels:
        ax.axhline(y=i, c="g", alpha=0.5)

    for i in range(5):
        ax.fill_between(df_stock.index, levels[i], levels[i + 1], alpha=0.6)

    ax.set_ylabel("Price")
    ax.set_title(f"Fibonacci Support for {s_ticker.upper()}")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])

    ax1 = ax.twinx()
    ax1.set_ylim(ax.get_ylim())
    ax1.set_yticks(levels)
    ax1.set_yticklabels([0, 0.235, 0.382, 0.5, 0.618, 1])

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    if gtff.USE_ION:
        plt.ion()
    plt.show()

    print_rich_table(
        df_fib,
        headers=["Fib Level", "Price"],
        show_index=False,
        title="Fibonacci retractment levels",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "fib",
        df_fib,
    )
