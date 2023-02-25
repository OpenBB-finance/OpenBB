""" Finnhub View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.fundamental_analysis import finnhub_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def plot_rating_over_time(
    data: pd.DataFrame,
    symbol: str = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plot rating over time

    Parameters
    ----------
    data: pd.DataFrame
        Rating over time
    symbol: str
        Ticker symbol associated with ratings
    external_axes: bool, optional
        Whether to return the figure object or not, by default False
    """
    fig = OpenBBFigure(yaxis_title="Rating")
    fig.set_title(f"{symbol}'s ratings over time")

    rot = data.sort_values("period")
    fig.add_scatter(
        x=rot["period"], y=rot["strongBuy"], name="Strong Buy", line_color="green"
    )
    fig.add_scatter(x=rot["period"], y=rot["buy"], name="Buy", line_color="lightgreen")
    fig.add_scatter(x=rot["period"], y=rot["hold"], name="Hold", line_color="grey")
    fig.add_scatter(x=rot["period"], y=rot["sell"], name="Sell", line_color="pink")
    fig.add_scatter(
        x=rot["period"], y=rot["strongSell"], name="Strong Sell", line_color="red"
    )

    fig.update_traces(selector=dict(type="scatter"), line_width=3, mode="lines")

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def rating_over_time(
    symbol: str,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Rating over time (monthly). [Source: Finnhub]

    Parameters
    ----------
    ticker : str
        Ticker to get ratings from
    limit : int
        Number of last months ratings to show
    raw: bool
        Display raw data only
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_rot = finnhub_model.get_rating_over_time(symbol)

    if df_rot.empty:
        return None

    if raw:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "rot",
            df_rot,
            sheet_name,
        )

        d_cols = {
            "strongSell": "Strong Sell",
            "sell": "Sell",
            "hold": "Hold",
            "buy": "Buy",
            "strongBuy": "Strong Buy",
        }
        df_rot_raw = (
            df_rot[["period", "strongSell", "sell", "hold", "buy", "strongBuy"]]
            .rename(columns=d_cols)
            .head(limit)
        )
        return print_rich_table(
            df_rot_raw,
            headers=list(df_rot_raw.columns),
            show_index=False,
            title="Monthly Rating",
            export=bool(export),
        )

    fig = plot_rating_over_time(df_rot.head(limit), symbol, True)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rot",
        df_rot,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
