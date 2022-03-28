"""Chartexchange view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List
import pandas as pd

import mplfinance as mpf
import matplotlib.pyplot as plt

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.options import chartexchange_model
from gamestonk_terminal.config_terminal import theme

from gamestonk_terminal.helper_funcs import plot_autoscale

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_raw(
    ticker: str,
    date: str,
    call: bool,
    price: str,
    num: int = 5,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Return raw stock data[chartexchange]

    Parameters
    ----------
    ticker : str
        Ticker for the given option
    date : str
        Date of expiration for the option
    call : bool
        Whether the underlying asset should be a call or a put
    price : float
        The strike of the expiration
    num : int
        Number of rows to show
    export : str
        Export data as CSV, JSON, XLSX
    """

    df = chartexchange_model.get_option_history(ticker, date, call, price)[::-1]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")

    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "volume": True,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
    }
    # This plot has 2 axes
    option_type = "call" if call else "put"

    if not external_axes:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        fig, ax = mpf.plot(df, **candle_chart_kwargs)
        fig.suptitle(
            f"Historical quotes for {ticker} {option_type}",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )
        theme.visualize_output(force_tight_layout=False)
        ax[0].legend()
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of 1 axis items.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax1,) = external_axes
        candle_chart_kwargs["ax"] = ax1
        mpf.plot(df, **candle_chart_kwargs)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hist",
        df,
    )
    print_rich_table(
        df.head(num),
        headers=list(df.columns),
        show_index=True,
        title=f"{ticker.upper()} raw data",
    )

    console.print()
