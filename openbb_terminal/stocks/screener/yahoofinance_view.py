"""Yahoo Finance View"""
__docformat__ = "numpy"
import datetime
import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.screener import yahoofinance_model

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def historical(
    preset_loaded: str = "top_gainers",
    limit: int = 10,
    start_date: str = (
        datetime.datetime.now() - datetime.timedelta(days=6 * 30)
    ).strftime("%Y-%m-%d"),
    type_candle: str = "a",
    normalize: bool = True,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> List[str]:
    """View historical price of stocks that meet preset

    Parameters
    ----------
    preset_loaded: str
        Preset loaded to filter for tickers
    limit: int
        Number of stocks to display
    start_date: str
        Start date to display historical data, in YYYY-MM-DD format
    type_candle: str
        Type of candle to display
    normalize : bool
        Boolean to normalize all stock prices using MinMax
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    Returns
    -------
    list[str]
        List of stocks
    """
    df_screener, l_stocks, limit_random_stocks = yahoofinance_model.historical(
        preset_loaded, limit, start_date, type_candle, normalize
    )

    if df_screener.empty:
        return []

    if l_stocks:
        # This plot has 1 axis
        if not external_axes:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return []

        df_screener.plot(ax=ax)

        if limit_random_stocks:
            ax.set_title(
                f"Screener Historical Price with {preset_loaded}\non 10 random stocks"
            )
        else:
            ax.set_title(f"Screener Historical Price with {preset_loaded}")

        ax.set_ylabel(
            f"{['','Normalized'][normalize]} Share Price {['($)',''][normalize]}"
        )
        ax.legend()
        # ensures that the historical data starts from same datapoint
        ax.set_xlim([df_screener.index[0], df_screener.index[-1]])

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "historical",
            df_screener,
        )

        return l_stocks

    console.print("No screener stocks found with this preset", "\n")
    return []
