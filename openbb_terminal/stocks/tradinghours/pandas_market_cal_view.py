import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.tradinghours import pandas_market_cal_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_all_holiday_exchange_short_names() -> pd.DataFrame:
    """Get all holiday exchanges short names.

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        All available exchange with holiday data short names
    """

    return pandas_market_cal_model.get_all_holiday_exchange_short_names()


@log_start_end(log=logger)
def display_exchange_holidays(exchange_symbol: str, year: int):
    """Display current exchange holiday calendar.

    Parameters
    ----------
    symbol : str
        Exchange symbol
    year : int
        Calendar year
    """

    exchange = pandas_market_cal_model.get_exchange_holidays(exchange_symbol, year)

    if len(exchange) == 0 or exchange.empty:
        console.print(
            "[red]"
            + "No exchange data loaded.\n"
            + "Make sure you picked a valid exchange symbol and year."
            + "[/red]\n"
        )
        return

    print_rich_table(
        exchange,
        show_index=False,
        title=f"[bold]{exchange_symbol}[/bold]",
    )
