import logging
import os
from typing import Optional

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.discovery import finnhub_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def past_ipo(
    num_days_behind: int = 5,
    start_date: Optional[str] = None,
    limit: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Past IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_behind: int
        Number of days to look behind for IPOs dates
    start_date: str
        The starting date (format YYYY-MM-DD) to look for IPOs
    limit: int
        Limit number of IPOs to display. Default is 20
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_past_ipo = finnhub_model.get_past_ipo(num_days_behind, start_date)

    if not df_past_ipo.empty:
        print_rich_table(
            df_past_ipo,
            headers=list(df_past_ipo.columns),
            show_index=False,
            title="IPO Dates",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pipo",
        df_past_ipo,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def future_ipo(
    num_days_ahead: int = 5,
    end_date: Optional[str] = None,
    limit: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Future IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_ahead: int
        Number of days to look ahead for IPOs dates
    end_date: datetime
        The end date (format YYYY-MM-DD) to look for IPOs from today onwards
    limit: int
        Limit number of IPOs to display. Default is 20
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_future_ipo = finnhub_model.get_future_ipo(num_days_ahead, end_date)

    if not df_future_ipo.empty:
        print_rich_table(
            df_future_ipo,
            headers=list(df_future_ipo.columns),
            show_index=False,
            title="Future IPO Dates",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fipo",
        df_future_ipo,
        sheet_name,
    )
