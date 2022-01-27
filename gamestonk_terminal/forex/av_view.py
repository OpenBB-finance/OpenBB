"""AlphaVantage Forex View."""
__docformat__ = "numpy"

import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from gamestonk_terminal.forex import av_model
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import plot_autoscale, print_rich_table
from gamestonk_terminal.rich_config import console


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
    if gtff.USE_ION:
        plt.ion()

    mpf.plot(
        data,
        type="candle",
        style=cfg.style.mpf_style,
        mav=(20, 50),
        volume=False,
        title=f"\n{from_symbol}/{to_symbol}",
        xrotation=10,
        figratio=(10, 7),
        figscale=1.10,
        scale_padding={"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        figsize=(plot_autoscale()),
        update_width_config=dict(
            candle_linewidth=0.6,
            candle_width=0.8,
            volume_linewidth=0.8,
            volume_width=0.8,
        ),
    )

    console.print("")
