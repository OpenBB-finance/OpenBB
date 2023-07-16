"""Intrinio View Functions"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import intrinio_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_historical(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    raw: bool = False,
    chain_id: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
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
    op_type = ["Call", "Put"][put]
    if chain_id is not None:
        df_hist = intrinio_model.get_historical_options(chain_id)
    else:
        chain_id = f"{symbol}{''.join(expiry[2:].split('-'))}{'P' if put else 'C'}{str(int(1000*strike)).zfill(8)}"
        df_hist = intrinio_model.get_historical_options(chain_id)

    if df_hist.empty:
        console.print(f"[red]No data found for {chain_id}[/red]")
        return None

    if raw:
        print_rich_table(
            df_hist,
            headers=[x.title() for x in df_hist.columns],
            title="Historical Option Prices",
            export=bool(export),
        )

    df_hist.columns = [x.title() for x in df_hist.columns]

    titles_list = [symbol, strike, op_type]
    fig = OpenBBFigure.create_subplots(
        rows=1,
        cols=1,
        specs=[[{"secondary_y": True}]],
        vertical_spacing=0.03,
    ).set_title(" ".join([str(x) for x in titles_list if x]))

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


@log_start_end(log=logger)
def view_historical_greeks(
    symbol: str = "",
    expiry: str = "",
    strike: Union[float, str] = 0,
    greek: str = "Delta",
    chain_id: str = "",
    put: bool = False,
    raw: bool = False,
    limit: Union[int, str] = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots historical greeks for a given option.

    Parameters
    ----------
    symbol: str
        Stock ticker
    expiry: str
        Expiration date
    strike: Union[str, float]
        Strike price to consider
    greek: str
        Greek variable to plot
    chain_id: str
        OCC option chain.  Overwrites other variables
    put: bool
        Is this a put option?
    raw: bool
        Print to console
    limit: int
        Number of rows to show in raw
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if chain_id:
        df = intrinio_model.get_historical_options(chain_id)
        title = f"{(greek).capitalize()} historical for {chain_id}"
    else:
        chain_id = f"{symbol}{''.join(expiry[2:].split('-'))}{'P' if put else 'C'}{str(int(1000*strike)).zfill(8)}"
        df = intrinio_model.get_historical_options(chain_id)
        title = (
            f"Historical {(greek).capitalize()} for {symbol.upper()}"
            f"{strike} {['Call','Put'][put]} and {expiry} Expiration"
        )
    if df.empty:
        print(f"No data found for {chain_id}")
        return None

    df = df.rename(columns={"impliedVolatility": "iv", "close": "price"})

    if isinstance(limit, str):
        try:
            limit = int(limit)
        except ValueError:
            return console.print(
                f"[red]Could not convert limit of {limit} to a number.[/red]\n"
            )

    if raw:
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            headers=list(df.columns),
            title="Historical Greeks",
            show_index=True,
            export=bool(export),
            limit=limit,
        )

    if greek.lower() not in df.columns:
        return console.print(f"[red]Could not find greek {greek} in data.[/red]\n")

    fig = OpenBBFigure.create_subplots(
        shared_xaxes=True,
        specs=[[{"secondary_y": True}]],
        vertical_spacing=0.03,
        horizontal_spacing=0.1,
    )
    fig.set_title(title)

    fig.add_scatter(
        x=df.index,
        y=df.price.values,
        name="Option Premium",
        line=dict(color=theme.down_color),
        secondary_y=False,
    )
    fig.add_scatter(
        x=df.index,
        y=df[greek.lower()].values,
        name=greek.title(),
        line=dict(color=theme.up_color),
        yaxis="y2",
        secondary_y=True,
    )
    fig.update_layout(
        yaxis2=dict(
            side="left",
            title=greek.title(),
            anchor="x",
            overlaying="y",
        ),
        yaxis=dict(
            title=f"{symbol} Option Premium",
            side="right",
        ),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "grhist",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
