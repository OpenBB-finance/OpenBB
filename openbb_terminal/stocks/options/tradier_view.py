"""Tradier options view"""
__docformat__ = "numpy"

import logging
import os
import warnings
from typing import Optional

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import tradier_model

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


# pylint: disable=too-many-arguments
@log_start_end(log=logger)
@check_api_key(["API_TRADIER_TOKEN"])
def display_historical(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    raw: bool = False,
    chain_id: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot historical option prices

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Expiry date of option
    strike: float
        Option strike price
    put: bool
        Is this a put option?
    raw: bool
        Print raw data
    chain_id: str
        OCC option symbol
    export: str
        Format of export file
    sheet_name: str
        Optionally specify the name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df_hist = tradier_model.get_historical_options(
        symbol, expiry, strike, put, chain_id
    )

    if df_hist.empty:
        if chain_id:
            console.print(f"No historical data found for {chain_id} ")
            return None
        console.print(f"No historical data found for {symbol} {expiry} ")
        return None

    if raw:
        print_rich_table(
            df_hist,
            headers=[x.title() for x in df_hist.columns],
            title="Historical Option Prices",
            export=bool(export),
            show_index=True,
            index_name="Date",
        )

    op_type = ["call", "put"][put]

    df_hist.columns = [x.title() for x in df_hist.columns]

    fig = OpenBBFigure.create_subplots(
        rows=1,
        cols=1,
        specs=[[{"secondary_y": True}]],
        vertical_spacing=0.06,
    )
    fig.set_title(f"Historical {symbol} {strike} {op_type.title()}")

    df_hist.index = df_hist.index.astype("datetime64[ns]")

    fig.add_candlestick(
        open=df_hist["Open"],
        high=df_hist["High"],
        low=df_hist["Low"],
        close=df_hist["Close"],
        x=df_hist.index,
        name=f"{symbol} OHLC",
        row=1,
        col=1,
        secondary_y=False,
    )
    fig.add_inchart_volume(df_hist)

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "hist",
            df_hist,
            sheet_name,
            fig,
        )

    return fig.show(external=raw or external_axes)
