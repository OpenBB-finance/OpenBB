"""Chartexchange view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import chartexchange_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def plot_chart(
    df: pd.DataFrame, option_type: str, symbol: str, price: float
) -> OpenBBFigure:
    """Plot Candlestick chart

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with OHLC data
    option_type : str
        Type of option (call or put)
    symbol : str
        Ticker symbol

    Returns
    -------
    OpenBBFigure
        Plotly figure object
    """
    titles_list = ["Historical", symbol, price, option_type.title()]

    fig = OpenBBFigure.create_subplots(
        rows=1,
        cols=1,
        vertical_spacing=0.06,
        specs=[[{"secondary_y": True}]],
    )
    fig.set_title(" ".join(str(x) for x in titles_list if x))

    fig.add_candlestick(
        open=df.Open,
        high=df.High,
        low=df.Low,
        close=df.Close,
        x=df.index,
        name=f"{price} {option_type.title()} OHLC",
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_inchart_volume(df)

    return fig


@log_start_end(log=logger)
def display_raw(
    symbol: str = "GME",
    expiry: str = "2021-02-05",
    call: bool = True,
    price: float = 90,
    limit: int = 10,
    chain_id: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Return raw stock data[chartexchange]

    Parameters
    ----------
    symbol : str
        Ticker symbol for the given option
    expiry : str
        The expiry of expiration, format "YYYY-MM-DD", i.e. 2010-12-31.
    call : bool
        Whether the underlying asset should be a call or a put
    price : float
        The strike of the expiration
    limit : int
        Number of rows to show
    chain_id: str
        Optional chain id instead of ticker and expiry and strike
    export : str
        Export data as CSV, JSON, XLSX
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = chartexchange_model.get_option_history(symbol, expiry, call, price, chain_id)[
        ::-1
    ]
    if df.empty:
        return console.print("[red]No data found[/red]\n")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")

    option_type = "call" if call else "put"
    fig = plot_chart(df, option_type, symbol, price)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hist",
        df,
        sheet_name,
        fig,
    )
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=True,
        index_name="Date",
        title=f"{symbol.upper()} raw data",
        export=bool(export),
        limit=limit,
    )

    return fig.show(external=external_axes)
