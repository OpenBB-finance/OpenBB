"""Beta view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.quantitative_analysis.beta_model import beta_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def beta_view(
    symbol: str,
    ref_symbol: str,
    data: Optional[pd.DataFrame] = None,
    ref_data: Optional[pd.DataFrame] = None,
    interval: int = 1440,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display the beta scatterplot + linear regression.

    Parameters
    ----------
    symbol : str
        A ticker to calculate beta for
    ref_symbol : str
        A reference ticker symbol for the beta calculation (default in terminal is SPY)
    data : pd.DataFrame
        The selected ticker symbols price data
    ref_data : pd.DataFrame
        The reference ticker symbols price data
    interval: int
        The interval of the ref_data. This will ONLY be used if ref_data is None
    """
    try:
        sr, rr, beta, alpha = beta_model(
            symbol, ref_symbol, data, ref_data, interval=interval
        )
    except Exception as e:
        if str(e) == "Invalid ref ticker":
            console.print(str(e) + "\n")
            return
        raise e

    _, ax = plt.subplots()
    ax.scatter(rr, sr)  # plot returns
    ax.plot(ax.get_xlim(), [x * beta + alpha for x in ax.get_xlim()])  # plot lin reg
    ax.set(
        xlabel=f"{ref_symbol} Returns (%)",
        ylabel=f"{symbol} Returns (%)",
        title=f"Beta of {symbol} with respect to {ref_symbol}",
    )
    beta_text = f"Raw Beta={round(beta, 2)}\nAlpha={round(alpha, 2)}"
    ax.text(0.9, 0.1, beta_text, horizontalalignment="right", transform=ax.transAxes)
    console.print()

    df = pd.DataFrame({"sr": sr, "rr": rr})

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"beta_alpha={alpha}_beta={beta}",
        df,
        sheet_name,
    )
