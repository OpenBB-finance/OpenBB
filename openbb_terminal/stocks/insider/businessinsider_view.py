""" Business Insider View """
__docformat__ = "numpy"

import logging
import math
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    get_next_stock_market_days,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.insider import businessinsider_model

logger = logging.getLogger(__name__)


# pylint: disable=R0912,too-many-arguments


@log_start_end(log=logger)
def insider_activity(
    data: pd.DataFrame,
    symbol: str,
    start_date: Optional[str] = None,
    interval: str = "1440min",
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Display insider activity. [Source: Business Insider]

    Parameters
    ----------
    data: pd.DataFrame
        Stock dataframe
    symbol: str
        Due diligence ticker symbol
    start_date: Optional[str]
        Initial date (e.g., 2021-10-01). Defaults to 3 years back
    interval: str
        Stock data interval
    limit: int
        Number of latest days of inside activity
    raw: bool
        Print to console
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes: bool, optional
        Whether to return the figure object or not, by default False
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d")

    df_ins = businessinsider_model.get_insider_activity(symbol)

    if df_ins.empty:
        logger.warning("The insider activity on the ticker does not exist")
        return console.print(
            "[red]The insider activity on the ticker does not exist.\n[/red]"
        )

    df_insider = df_ins[start_date:].copy() if start_date else df_ins.copy()  # type: ignore

    close_col = "Adj Close" if interval == "1440min" else "Close"

    fig = OpenBBFigure(yaxis_title="Share Price")
    fig.set_title(f"{symbol.upper()}'s Insider Trading Activity & Share Price")

    fig.add_scatter(x=data.index, y=data[close_col].values, name=symbol)

    df_insider_plot = df_insider.copy()
    df_insider_plot["Trade"] = df_insider_plot.apply(
        lambda row: (1, -1)[row.Type == "Sell"]
        * float(row["Shares Traded"].replace(",", "")),
        axis=1,
    )

    min_price, max_price = data[close_col].min(), data[close_col].max()
    price_range = max_price - min_price

    ins_buy = (
        df_insider_plot[df_insider_plot["Type"] == "Buy"]
        .groupby(by=["Date"])
        .sum(numeric_only=True)
    )
    ins_sell = (
        df_insider_plot[df_insider_plot["Type"] == "Sell"]
        .groupby(by=["Date"])
        .sum(numeric_only=True)
    )

    maxshares = ins_buy["Trade"].max()
    minshares = ins_sell["Trade"].min()

    if math.isnan(maxshares):
        shares_range = minshares
    elif math.isnan(minshares):
        shares_range = maxshares
    else:
        shares_range = maxshares - minshares

    n_proportion = price_range / shares_range

    for ind in ins_sell.index:
        ind_dt = ind if ind in data.index else get_next_stock_market_days(ind, 1)[0]

        n_stock_price = data[close_col][ind_dt]
        ins_loc = ins_sell.index.get_indexer([ind_dt], method="nearest")

        ymin = n_stock_price + n_proportion * float(ins_sell["Trade"][ins_loc])
        fig.add_scatter(
            x=[ind_dt, ind_dt],
            y=[ymin, n_stock_price],
            mode="lines",
            line=dict(color=theme.down_color, width=5),
            name="Insider Selling",
            showlegend=ind == ins_sell.index[0],
        )

    for ind in ins_buy.index:
        ind_dt = ind if ind in data.index else get_next_stock_market_days(ind, 1)[0]

        n_stock_price = data[close_col][ind_dt]
        ins_loc = ins_buy.index.get_indexer([ind_dt], method="nearest")

        ymax = n_stock_price + n_proportion * float(ins_buy["Trade"][ins_loc])
        fig.add_scatter(
            x=[ind_dt, ind_dt],
            y=[n_stock_price, ymax],
            mode="lines",
            line=dict(color=theme.up_color, width=5),
            name="Insider Buying",
            showlegend=ind == ins_buy.index[0],
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "act",
        df_insider,
        sheet_name,
        fig,
    )

    if raw:
        df_insider.index = pd.to_datetime(df_insider.index)

        return print_rich_table(
            df_insider.sort_index(ascending=False).applymap(
                lambda x: x.replace(".00", "").replace(",", "")
            ),
            headers=list(df_insider.columns),
            show_index=True,
            title="Insider Activity",
            export=bool(export),
            limit=limit,
        )

    return fig.show(external=external_axes)
