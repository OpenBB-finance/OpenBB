"""TA Overlap View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import List, Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def view_ma(
    data: pd.Series,
    window: Optional[List[int]] = None,
    offset: int = 0,
    ma_type: str = "EMA",
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots MA technical indicator

    Parameters
    ----------
    data: pd.Series
        Series of prices
    window: List[int]
        Length of EMA window
    offset: int
        Offset variable
    ma_type: str
        Type of moving average.  Either "EMA" "ZLMA" or "SMA"
    symbol: str
        Ticker
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.ma_chart(data=df["Adj Close"], symbol="AAPL", ma_type="EMA", window=[20, 50, 100])


    >>> from openbb_terminal.sdk import openbb
    >>> spuk_index = openbb.economy.index(indices = ["^SPUK"])
    >>> openbb.ta.ma_chart(data = spuk_index["^SPUK"], symbol = "S&P UK Index", ma_type = "EMA", window = [20, 50, 100])
    """
    # Define a dataframe for adding EMA series to it
    price_df = pd.DataFrame(data)
    price_df.index.name = "date"

    if not window:
        window = [50]

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        {f"{ma_type.lower()}": dict(length=window, offset=offset)},
        f"{symbol.upper()} {ma_type.upper()}",
        False,
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        f"{ma_type.lower()}{'_'.join([str(win) for win in window])}",  # type: ignore
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def view_vwap(
    data: pd.DataFrame,
    symbol: str = "",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    offset: int = 0,
    interval: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots VWMA technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    symbol : str
        Ticker
    offset : int
        Offset variable
    start_date: Optional[str]
        Initial date, format YYYY-MM-DD
    end_date: Optional[str]
        Final date, format YYYY-MM-DD
    interval : str
        Interval of data
    export : str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    data.index = data.index.tz_localize(None)

    if start_date is None:
        start = data.index[0].date()
        console.print(f"No start date specified. Start date: {start}")
    else:
        start = datetime.date(start_date)

    if end_date is None:
        end = data.index[-1].date()
        console.print(f"No end date specified. End date: {end}")
    else:
        end = datetime.date(end_date)

    day_df = data[(start <= data.index.date) & (data.index.date <= end)]

    if len(day_df) == 0:
        return console.print(
            f"[red]No data found between {start.strftime('%Y-%m-%d')} and {end.strftime('%Y-%m-%d')}[/red]"
        )

    ta = PlotlyTA()
    fig = ta.plot(
        day_df,
        dict(vwap=dict(offset=offset)),
        f"{symbol.upper()} {interval} VWAP",
        volume=False,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "VWAP",
        ta.df_ta,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)
