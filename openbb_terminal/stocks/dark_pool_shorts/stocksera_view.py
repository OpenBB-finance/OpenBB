""" Stocksera View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import stocksera_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_cost_to_borrow(
    symbol: str,
    data: pd.DataFrame,
    external_axes: bool = False,
):
    """Plot the cost to borrow of a stock. [Source: Stocksera]

    Parameters
    ----------
    symbol : str
        ticker to get cost to borrow from
    data: pd.DataFrame
        Cost to borrow dataframe
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if data.empty:
        return None

    fig = OpenBBFigure.create_subplots(1, 1, specs=[[{"secondary_y": True}]])
    fig.set_title(f"Cost to Borrow of {symbol}")

    fig.add_bar(
        x=data.index,
        y=data["Available"],
        name="Number Shares",
        marker_color=theme.up_color,
        secondary_y=False,
    )

    fig.add_scatter(
        x=data.index,
        y=data["Fees"].values,
        name="Fees",
        marker_color=theme.get_colors()[0],
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Fees %", secondary_y=True)
    fig.update_yaxes(secondary_y=False, side="left")
    fig.update_xaxes(title_text="Date", type="category", nticks=6)
    fig.update_layout(margin=dict(l=50))

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_STOCKSERA_KEY"])
def cost_to_borrow(
    symbol: str,
    limit: int = 100,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plot the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]
    Parameters
    ----------
    symbol : str
        ticker to get cost to borrow from
    limit: int
        Number of historical cost to borrow data to show
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    # Note: if you send an empty string stocksera will search every ticker
    if not symbol:
        return console.print("[red]No symbol provided[/red]\n")

    df_cost_to_borrow = stocksera_model.get_cost_to_borrow(symbol)

    df_cost_to_borrow = df_cost_to_borrow.head(limit)[::-1]

    pd.options.mode.chained_assignment = None

    fig = plot_cost_to_borrow(symbol, df_cost_to_borrow, True)

    if raw:
        if not get_current_user().preferences.USE_INTERACTIVE_DF:
            df_cost_to_borrow["Available"] = df_cost_to_borrow["Available"].apply(
                lambda x: lambda_long_number_format(x)
            )
        print_rich_table(
            df_cost_to_borrow,
            headers=list(df_cost_to_borrow.columns),
            show_index=True,
            title=f"Cost to Borrow of {symbol}",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stocksera",
        df_cost_to_borrow,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
