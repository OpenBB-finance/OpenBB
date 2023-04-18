"""DataBento view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.core.plots.plotly_helper import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import databento_model, stocks_helper

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_historical(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Optional[OpenBBFigure]:
    """Display historical futures [Source: DataBento]

    Parameters
    ----------
    symbol: List[str]
        Symbol to display
    start_date: Optional[str]
        Start date of the historical data with format YYYY-MM-DD
    end_date: Optional[str]
        End date of the historical data with format YYYY-MM-DD
    raw: bool
        Display futures timeseries in raw format
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Type of format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = databento_model.get_historical_futures(
        symbol.upper(), start_date=start_date, end_date=end_date
    )
    if data.empty:
        return console.print(f"No data found for {symbol}.")

    data = stocks_helper.process_candle(data)
    figure = stocks_helper.display_candle(
        symbol=symbol,
        data=data,
        external_axes=True,
    )

    if raw:
        print_rich_table(
            data,
            headers=list(data.columns),
            show_index=True,
            title="Futures timeseries",
            export=bool(export),
        )
        console.print()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "historical_db",
        data,
        sheet_name,
        figure,
    )

    return figure.show(external=raw or external_axes)  # type: ignore
