""" SEC View """
__docformat__ = "numpy"

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.stocks.dark_pool_shorts import sec_model

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def fails_to_deliver(
    symbol: str,
    data: Optional[pd.DataFrame] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 0,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
):
    """Display fails-to-deliver data for a given ticker. [Source: SEC]

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Stock data
    start_date: Optional[str]
        Start of data, in YYYY-MM-DD format
    end_date: Optional[str]
        End of data, in YYYY-MM-DD format
    limit : int
        Number of latest fails-to-deliver being printed
    raw: bool
        Print raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if data is None:
        data = stocks_helper.load(
            symbol=symbol, start_date=start_date, end_date=end_date
        )

    ftds_data = sec_model.get_fails_to_deliver(symbol, start_date, end_date, limit)

    fig = OpenBBFigure.create_subplots(
        shared_xaxes=True, specs=[[{"secondary_y": True}]]
    )
    if limit > 0:
        data_ftd = data[data.index > (datetime.now() - timedelta(days=limit + 31))]
    else:
        data_ftd = data[data.index > start_date]
        data_ftd = data_ftd[data_ftd.index < end_date]

    fig.add_bar(
        name="Fail Quantity",
        x=ftds_data["SETTLEMENT DATE"],
        y=ftds_data["QUANTITY (FAILS)"],
        secondary_y=False,
    )
    fig.add_scatter(
        name="Share Price",
        x=data_ftd.index,
        y=data_ftd["Adj Close"],
        yaxis="y2",
        line=dict(width=3),
        opacity=1,
        secondary_y=True,
    )
    fig.update_layout(
        margin=dict(l=30, r=0, t=30, b=10),
        yaxis2=dict(title="Share Price [$]", overlaying="y", nticks=20),
        yaxis=dict(side="left", title="Shares [K]", showgrid=False),
        title=f"Fails-to-deliver Data for {symbol}",
        xaxis_title="Date",
        legend=dict(yanchor="bottom", y=0, xanchor="right", x=0.95),
    )

    if raw:
        print_rich_table(
            ftds_data,
            headers=list(ftds_data.columns),
            show_index=False,
            title="Fails-To-Deliver Data",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ftd",
        ftds_data.reset_index(),
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
