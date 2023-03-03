"""Yahoo Finance View"""
__docformat__ = "numpy"
import datetime
import logging
import os
from typing import List, Optional, Tuple, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.screener import yahoofinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def historical(
    preset_loaded: str = "top_gainers",
    limit: int = 10,
    start_date: str = (
        datetime.datetime.now() - datetime.timedelta(days=6 * 30)
    ).strftime("%Y-%m-%d"),
    type_candle: str = "a",
    normalize: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[List[str], Tuple[List[str], OpenBBFigure]]:
    """View historical price of stocks that meet preset

    Parameters
    ----------
    preset_loaded: str
        Preset loaded to filter for tickers
    limit: int
        Number of stocks to display
    start_date: str
        Start date to display historical data, in YYYY-MM-DD format
    type_candle: str
        Type of candle to display
    normalize : bool
        Boolean to normalize all stock prices using MinMax
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    list[str]
        List of stocks
    """
    df_screener, l_stocks, limit_random_stocks = yahoofinance_model.historical(
        preset_loaded, limit, start_date, type_candle, normalize
    )

    if df_screener.empty:
        return []

    if l_stocks:
        fig = OpenBBFigure(
            xaxis_title="Date",
            yaxis_title=f"{['','Normalized'][normalize]} Share Price {['($)',''][normalize]}",
        )

        if limit_random_stocks:
            fig.set_title(
                f"Screener Historical Price with {preset_loaded}\non 10 random stocks"
            )
        else:
            fig.set_title(f"Screener Historical Price with {preset_loaded}")

        for column in df_screener.columns:
            fig.add_scatter(
                x=df_screener.index,
                y=df_screener[column],
                mode="lines",
                name=column,
            )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "historical",
            df_screener,
            sheet_name,
            fig,
        )
        fig.show(external=external_axes)

        if external_axes:
            return l_stocks, fig

        return l_stocks

    console.print("No screener stocks found with this preset", "\n")
    return []
