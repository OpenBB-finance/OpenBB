import logging
import os
from datetime import datetime, timedelta

import pandas as pd

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.discovery import finnhub_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def past_ipo(
    num_days_behind: int,
    limit: int,
    export: str,
    start_date: datetime = None,
) -> pd.DataFrame:
    """Past IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_behind: int
        Number of days to look behind for IPOs dates
    starting_day: str
        The starting date (format YYYY-MM-DD) to look for IPOs
    export : str
        Export dataframe data to csv,json,xlsx file
    limit: int
        Limit number of IPOs to display. Default is 20


    Returns
    -------
    df_past_ipo : pd.DataFrame
        Past IPOs dates
    """
    today = datetime.now()

    if start_date is None:

        start_date = today - timedelta(days=num_days_behind)

    df_past_ipo = (
        finnhub_model.get_ipo_calendar(start_date, today.strftime("%Y-%m-%d"))
        .rename(columns={"Date": "Past"})
        .fillna("")
    )

    if df_past_ipo.empty:
        console.print(f"No IPOs found since the last {num_days_behind} days")
    else:
        df_past_ipo = df_past_ipo.sort_values("Past", ascending=False)
        print_rich_table(
            df_past_ipo.head(limit),
            headers=list(df_past_ipo.columns),
            show_index=False,
            title="IPO Dates",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pipo",
        df_past_ipo,
    )


@log_start_end(log=logger)
def future_ipo(
    num_days_ahead: int, limit: int, export: str, end_date: datetime = None
) -> pd.DataFrame:
    """Future IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_ahead: int
        Number of days to look ahead for IPOs dates
    end_date: datetime
        The end date (format YYYY-MM-DD) to look for IPOs from today onwards
    export : str
        Export dataframe data to csv,json,xlsx file
    limit: int
        Limit number of IPOs to display. Default is 20

    Returns
    -------
    df_future_ipo : pd.DataFrame
        Future IPOs dates
    """
    today = datetime.now()

    if end_date is None:
        end_date = today + timedelta(days=num_days_ahead)

    df_future_ipo = (
        finnhub_model.get_ipo_calendar(
            today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )
        .rename(columns={"Date": "Future"})
        .fillna("")
    )

    if df_future_ipo.empty:
        console.print(f"No IPOs found for the next {num_days_ahead} days")
    else:
        df_future_ipo = df_future_ipo.sort_values("Future", ascending=False)
        print_rich_table(
            df_future_ipo.head(limit),
            headers=list(df_future_ipo.columns),
            show_index=False,
            title="Future IPO Dates",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fipo",
        df_future_ipo,
    )
