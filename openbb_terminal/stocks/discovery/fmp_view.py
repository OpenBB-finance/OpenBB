""" Financial Modeling Prep View """
__docformat__ = "numpy"

import datetime
import logging
import os
from typing import Optional

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import fmp_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_filings(
    pages: int = 1,
    limit: int = 5,
    today: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display recent forms submitted to the SEC
    Parameters
    ----------
    pages: int = 1
        The range of most-rececnt pages to get entries from (1000 per page, max 30 pages)
    limit: int = 5
        Limit the number of entries to display (default: 5)
    today: bool = False
        Show all from today
    export: str = ""
        Export data as csv, json, or xlsx
    Examples
    --------
    openbb.stocks.display_filings()
    openbb.stocks.display_filings(today = True, export = "csv")
    """
    filings = fmp_model.get_filings(pages)
    if today is True:
        now: str = datetime.datetime.now().strftime("%Y-%m-%d")
        iso_today: int = datetime.datetime.today().isoweekday()
        if iso_today < 6 and not filings.empty:
            filings = filings.filter(like=now, axis=0)
            limit = 1000
        else:
            console.print(
                "[red]No filings today, displaying the most recent submissions instead[/red]"
            )

    if not filings.empty:
        filings.reset_index(["Date"], inplace=True)
        for _, row in filings.head(limit).iterrows():
            console.print(
                "Timestamp: ",
                f"{row['Date']}",
                "  US/Eastern",
                "\n",
                "Ticker: ",
                f"{row['Ticker']}",
                "\n",
                "CIK: " f"{row['CIK']}",
                "\n",
                "Form Type: ",
                f"{row['Form Type']}",
                "\n",
                f"{row['Title']}",
                "\n",
                f"{row['URL']}\n",
                sep="",
            )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "filings",
            filings,
            sheet_name,
        )
    else:
        logger.error("Could not get data")
        console.print("[red]Could not get data[/red]\n")
