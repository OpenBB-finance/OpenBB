"""AlphaVantage Forex View."""
__docformat__ = "numpy"

import logging
from typing import Optional, List

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.forex import av_model
from gamestonk_terminal.helper_funcs import plot_autoscale, print_rich_table
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_quote(to_symbol: str, from_symbol: str):
    """Display current forex pair exchange rate.

    Parameters
    ----------
    to_symbol : str
        To symbol
    from_symbol : str
        From forex symbol
    """
    quote = av_model.get_quote(to_symbol, from_symbol)

    if not quote:
        logger.error("Quote not pulled from AlphaVantage.  Check API key.")
        console.print("[red]Quote not pulled from AlphaVantage.  Check API key.[/red]")
        return

    df = pd.DataFrame.from_dict(quote)
    df.index = df.index.to_series().apply(lambda x: x[3:]).values
    df = df.iloc[[0, 2, 5, 4, 7, 8]]
    print_rich_table(
        df,
        show_index=True,
        title=f"[bold]{from_symbol}/{to_symbol} Quote [/bold]",
    )
    console.print("")


@log_start_end(log=logger)
def display_candle(
    data: pd.DataFrame,
    to_symbol: str,
    from_symbol: str,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Show candle plot for fx data.

    Parameters
    ----------
    data : pd.DataFrame
        Loaded fx historical data
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol
    external_axes: Optional[List[plt.Axes]]
        External axes (1 axis are expected in the list), by default None
    """
    candle_chart_kwargs = {
        "type": "candle",
        "style": theme.mpf_style,
        "mav": (20, 50),
        "volume": False,
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
    if not external_axes:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        fig, ax = mpf.plot(data, **candle_chart_kwargs)
        fig.suptitle(
            f"{from_symbol}/{to_symbol}",
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
        mpf.plot(data, **candle_chart_kwargs)
