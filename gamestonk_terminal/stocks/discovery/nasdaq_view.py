"""NASDAQ DataLink View"""
__docformat__ = "numpy"

import os

from colorama import Style
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data, rich_table_from_df
from gamestonk_terminal.stocks.discovery import nasdaq_model
import gamestonk_terminal.feature_flags as gtff
from gamestonk_terminal.rich_config import console


def display_top_retail(n_days: int = 3, export: str = ""):
    """Display the top 10 retail traded stocks for last days

    Parameters
    ----------
    n_days : int, optional
        Number of days to show by default 3
    export : str, optional
        Format to export data, by default ""
    """
    retails = nasdaq_model.get_retail_tickers()
    for date, df in retails.head(n_days * 10).groupby("Date"):
        console.print(f"{Style.BRIGHT}{date} Top Retail:{Style.RESET_ALL}")
        df = df.drop(columns=["Date"])
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df.reset_index(drop=True),
                    headers=df.columns[1:],
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )
        else:
            console.print(df.reset_index(drop=True).to_string(index=False))

        console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "rtat", retails)


def display_dividend_calendar(
    date: str,
    sort_col: str = "Dividend",
    ascending: bool = False,
    limit: int = 10,
    export: str = "",
):
    """Display NASDAQ dividend calendar

    Parameters
    ----------
    date: str
        Date to get dividend calendar for
    sort_col: str
        Column to sort data for
    ascending: bool
        Flag to sort in ascending order
    limit: int
        Number of results to show
    export: str
        Format to export data
    """
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
    calendar = calendar.sort_values(by=sort_col, ascending=ascending)
    if gtff.USE_TABULATE_DF:
        console.print(
            rich_table_from_df(
                calendar.head(limit),
                headers=list(calendar.columns),
                title=f"[bold]Dividend Calendar for {date}[/bold]",
            )
        )
    else:
        console.print(calendar.head(limit).to_string())
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "divcal", calendar)
