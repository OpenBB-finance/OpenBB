"""Beta view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
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
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
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
    export : str
        Export dataframe data or plot to csv,json,xlsx,jpeg,pdf,png,svg file
    sheet_name : str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    try:
        sr, rr, beta, alpha = beta_model(
            symbol, ref_symbol, data, ref_data, interval=interval
        )
    except Exception as e:
        if str(e) == "Invalid ref ticker":
            return console.print(str(e) + "\n")
        raise e

    beta_text = f"Raw Beta={round(beta, 2)}<br>Alpha={round(alpha, 2)}"

    fig = OpenBBFigure(
        xaxis_title=f"{ref_symbol} Returns (%)", yaxis_title=f"{symbol} Returns (%)"
    )
    fig.set_title(f"Beta of {symbol} with respect to {ref_symbol}")
    fig.add_scatter(x=rr, y=sr, mode="markers", name="Returns")

    fig.add_scatter(
        x=[min(rr), max(rr)],
        y=[x * beta + alpha for x in [min(rr), max(rr)]],
        mode="lines",
        name="Linear Regression",
    )
    fig.add_annotation(
        x=0.9,
        y=0.1,
        text=beta_text,
        xref="paper",
        yref="paper",
        xanchor="right",
        yanchor="bottom",
    )

    fig.update_layout(showlegend=False)

    df = pd.DataFrame({"sr": sr, "rr": rr})

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"beta_alpha={alpha}_beta={beta}",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
