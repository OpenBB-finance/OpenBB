"""AlphaVantage Forex View."""
__docformat__ = "numpy"

import logging

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from gamestonk_terminal import feature_flags as gtff
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
def display_candle(data: pd.DataFrame, to_symbol: str, from_symbol: str):
    """Show candle plot for fx data.

    Parameters
    ----------
    data : pd.DataFrame
        Loaded fx historical data
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol
    """
    mc = mpf.make_marketcolors(
        up="green",
        down="red",
        edge="black",
        wick="black",
        volume="in",
        ohlc="i",
    )

    s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=True)

    if gtff.USE_ION:
        plt.ion()

    mpf.plot(
        data,
        type="candle",
        mav=(20, 50),
        volume=False,
        title=f"\n{from_symbol}/{to_symbol}",
        xrotation=10,
        style=s,
        figratio=(10, 7),
        figscale=1.10,
        figsize=(plot_autoscale()),
        update_width_config=dict(
            candle_linewidth=0.7,
            candle_width=0.8,
        ),
    )

    console.print("")
