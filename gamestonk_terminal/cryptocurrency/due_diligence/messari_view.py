import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.decorators import check_api_key
from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal.cryptocurrency.due_diligence.messari_model import (
    get_marketcap_dominance,
)
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_MESSARI_KEY"])
def display_marketcap_dominance(
    coin: str,
    start: str,
    end: str,
    interval: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display market dominance of a coin over time
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check market cap dominance
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    df = get_marketcap_dominance(coin=coin, start=start, end=end, interval=interval)

    if df.empty:
        return

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfgPlot.PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(df.index, df["marketcap_dominance"])

    ax.set_title(f"{coin}'s Market Cap Dominance over time")
    ax.set_ylabel(f"{coin} Percentage share")
    ax.set_xlim(df.index[0], df.index[-1])

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mcapdom",
        df,
    )
