""" Quandl View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.stocks.dark_pool_shorts import quandl_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def plot_short_interest(
    symbol: str,
    data: pd.DataFrame,
    nyse: bool = False,
    external_axes: bool = False,
):
    """Plot the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    symbol : str
        ticker to get short interest from
    data: pd.DataFrame
        Short interest dataframe
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    fig = OpenBBFigure.create_subplots(1, 1, specs=[[{"secondary_y": True}]])
    fig.set_title(f"{('NASDAQ', 'NYSE')[nyse]} Short Interest on {symbol}")

    data.index = pd.to_datetime(data.index).strftime("%Y-%m-%d")
    fig.add_bar(
        x=data.index,
        y=data["Short Volume"],
        name="Short Volume",
        marker_color=theme.down_color,
        secondary_y=False,
    )
    fig.add_bar(
        x=data.index,
        y=data["Total Volume"] - data["Short Volume"],
        name="Total Volume",
        marker_color=theme.up_color,
        secondary_y=False,
    )

    fig.add_scatter(
        x=data.index,
        y=data["% of Volume Shorted"].values,
        name="Fees",
        marker_color=theme.get_colors()[0],
        secondary_y=True,
        showlegend=False,
    )
    fig.update_yaxes(
        title_text="Percentage of Volume Shorted", secondary_y=True, tickformat="%.0f%%"
    )
    fig.update_yaxes(secondary_y=False, side="left", title_text="Shares")
    fig.update_xaxes(title_text="Date", type="category", nticks=6)
    fig.update_layout(barmode="stack", margin=dict(l=50))

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def short_interest(
    symbol: str,
    nyse: bool = False,
    limit: int = 10,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Plot the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    symbol : str
        ticker to get short interest from
    nyse : bool
        data from NYSE if true, otherwise NASDAQ
    limit: int
        Number of past days to show short interest
    raw : bool
        Flag to print raw data instead
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_short_interest = quandl_model.get_short_interest(symbol, nyse)

    df_short_interest = df_short_interest.tail(limit)

    df_short_interest.columns = [
        "".join(" " + char if char.isupper() else char.strip() for char in idx).strip()
        for idx in df_short_interest.columns.tolist()
    ]
    pd.options.mode.chained_assignment = None

    vol_pct = (
        100
        * df_short_interest["Short Volume"].values
        / df_short_interest["Total Volume"].values
    )
    df_short_interest["% of Volume Shorted"] = [round(pct, 2) for pct in vol_pct]

    fig = plot_short_interest(symbol, df_short_interest, nyse, True)

    if raw:
        if not get_current_user().preferences.USE_INTERACTIVE_DF:
            df_short_interest["% of Volume Shorted"] = df_short_interest[
                "% of Volume Shorted"
            ].apply(lambda x: f"{x/100:.2%}")

            df_short_interest = df_short_interest.applymap(
                lambda x: lambda_long_number_format(x)
            ).sort_index(ascending=False)

        print_rich_table(
            df_short_interest,
            headers=list(df_short_interest.columns),
            show_index=True,
            title="Short Interest of Stock",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "psi(quandl)",
        df_short_interest,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
