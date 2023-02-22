"""Cramer View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import Optional, Union

import yfinance

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.behavioural_analysis import cramer_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_cramer_daily(
    inverse: bool = True, export: str = "", sheet_name: Optional[str] = None
):
    """Display Jim Cramer daily recommendations

    Parameters
    ----------
    inverse: bool
        Include inverse recommendation
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """

    recs = cramer_model.get_cramer_daily(inverse)
    if recs.empty:
        console.print("[red]Error getting request.\n[/red]")
        return
    date = recs.Date[0]
    recs = recs.drop(columns=["Date"])

    if datetime.today().strftime("%m-%d") != datetime.strptime(
        date.replace("/", "-"), "%m-%d"
    ):
        console.print(
            """
        \n[yellow]Warning[/yellow]: We noticed Jim Crammer recommendation data has not been updated for a while, \
and we're investigating on finding a replacement.
        """,
        )

    print_rich_table(
        recs, title=f"Jim Cramer Recommendations for {date}", export=bool(export)
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cramer",
        recs,
        sheet_name,
    )


@log_start_end(log=logger)
def display_cramer_ticker(
    symbol: str,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Display ticker close with Cramer recommendations

    Parameters
    ----------
    symbol: str
        Stock ticker
    raw: bool
        Display raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = cramer_model.get_cramer_ticker(symbol)
    if df.empty:
        return console.print(f"No recommendations found for {symbol}.\n")

    fig = OpenBBFigure(xaxis_title="Date", yaxis_title="Price")
    fig.set_title(f"{symbol.upper()} Close With Cramer Recommendations")

    close_prices = yfinance.download(symbol, start="2022-01-01", progress=False)[
        "Adj Close"
    ]

    fig.add_scatter(
        x=close_prices.index,
        y=close_prices,
        mode="lines",
        name="Close",
        showlegend=False,
        line=dict(color=theme.line_color),
    )
    color_map = {"Buy": theme.up_color, "Sell": theme.down_color}
    for name, group in df.groupby("Recommendation"):
        fig.add_scatter(
            x=group.Date,
            y=group.Price,
            mode="markers",
            name=name,
            marker=dict(color=color_map[name], size=10),
        )

    if raw:
        df["Date"] = df["Date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        print_rich_table(
            df, title=f"Jim Cramer Recommendations for {symbol}", export=bool(export)
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "jctr",
        df,
        sheet_name,
        fig,
    )

    fig.update_layout(legend=dict(yanchor="top", y=1, xanchor="right", x=1))

    return fig.show(external=external_axes)
