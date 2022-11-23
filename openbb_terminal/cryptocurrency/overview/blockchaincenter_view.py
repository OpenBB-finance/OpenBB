"""Blockchain Center View"""
import logging
import os
from typing import List, Optional
from datetime import datetime

from matplotlib import pyplot as plt

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.cryptocurrency.overview.blockchaincenter_model import (
    DAYS,
    get_altcoin_index,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    is_valid_axes_count,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_altcoin_index(
    period: int = 365,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Displays altcoin index overtime
     [Source: https://blockchaincenter.net]

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD
    period: int
        Number of days to check the performance of coins and calculate the altcoin index.
        E.g., 365 will check yearly performance , 90 will check seasonal performance (90 days),
        30 will check monthly performance (30 days).
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if period in DAYS:
        df = get_altcoin_index(period, start_date, end_date)

        if df.empty:
            console.print("\nError scraping blockchain central\n")
        else:

            # This plot has 1 axis
            if not external_axes:
                _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            elif is_valid_axes_count(external_axes, 1):
                (ax,) = external_axes
            else:
                return

            ax.set_ylabel("Altcoin Index")
            ax.axhline(y=75, color=theme.up_color, label="Altcoin Season (75)")
            ax.axhline(y=25, color=theme.down_color, label="Bitcoin Season (25)")
            ax.set_title(f"Altcoin Index (Performance based on {period} days)")

            ax.plot(df.index, df["Value"], label="Altcoin Index")
            ax.legend(loc="best")

            theme.style_primary_axis(ax)

            if not external_axes:
                theme.visualize_output()

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "altindex",
                df,
            )
