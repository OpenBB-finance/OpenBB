"""NASDAQ DataLink View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import Optional

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.discovery import nasdaq_model

# pylint: disable=E1123


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def display_top_retail(
    limit: int = 3, export: str = "", sheet_name: Optional[str] = None
):
    """Display the top 10 retail traded stocks for last days

    Parameters
    ----------
    limit : int, optional
        Number of days to show by default 3
    export : str, optional
        Format to export data, by default ""
    """
    retails = nasdaq_model.get_retail_tickers()

    if retails.empty:
        return

    for date, df in retails.head(limit * 10).groupby("Date"):
        clean_df = df.drop(columns=["Date"])
        clean_df = clean_df.reset_index(drop=True)
        print_rich_table(
            clean_df,
            headers=[x.title() for x in df.columns],
            show_index=False,
            title=f"[bold]{date} Top Retail:[/bold]",
            export=bool(export),
        )
        console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rtat",
        retails,
        sheet_name,
    )


@log_start_end(log=logger)
def display_dividend_calendar(
    date: Optional[str] = None,
    sortby: str = "Dividend",
    ascend: bool = False,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display NASDAQ dividend calendar

    Parameters
    ----------
    date: str
        Date to get dividend calendar for, format YYYY-MM-DD
    sortby: str
        Column to sort data for
    ascend: bool
        Flag to sort in ascending order
    limit: int
        Number of results to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """

    if date is None:
        date = datetime.today().strftime("%Y-%m-%d")

    div_map = {
        "symbol": "Symbol",
        "companyName": "Name",
        "dividend_Ex_Date": "Ex-Dividend Date",
        "payment_Date": "Payment Date",
        "record_Date": "Record Date",
        "dividend_Rate": "Dividend",
        "indicated_Annual_Dividend": "Annual Dividend",
        "announcement_Date": "Announcement Date",
    }
    calendar = nasdaq_model.get_dividend_cal(date)
    if calendar.empty:
        console.print(
            "No data found. Check that the date provided is a market day.  If it is then try this function"
            " again as the request may have not gone through.\n"
        )
        return
    calendar = calendar.drop(columns=["announcement_Date"])
    calendar.columns = calendar.columns.map(div_map)
    calendar = calendar.sort_values(by=sortby, ascending=ascend)
    print_rich_table(
        calendar,
        headers=[x.title() for x in calendar.columns],
        title=f"[bold]Dividend Calendar for {date}[/bold]",
        export=bool(export),
        limit=limit,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "divcal",
        calendar,
        sheet_name,
    )
