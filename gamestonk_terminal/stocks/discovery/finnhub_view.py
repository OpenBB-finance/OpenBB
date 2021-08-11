import os
from datetime import datetime, timedelta
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.discovery import finnhub_model


def past_ipo(num_days_behind: int, export: str) -> pd.DataFrame:
    """Past IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_behind: int
        Number of days to look behind for IPOs dates
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    df_past_ipo : pd.DataFrame
        Past IPOs dates
    """
    today = datetime.now()
    past_date = today - timedelta(days=num_days_behind)

    df_past_ipo = (
        finnhub_model.get_ipo_calendar(
            past_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        )
        .rename(columns={"Date": "Past"})
        .fillna("")
    )

    if df_past_ipo.empty:
        print(f"No IPOs found since the last {num_days_behind} days")
    else:
        print(
            tabulate(
                df_past_ipo,
                headers=df_past_ipo.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pipo",
        df_past_ipo,
    )


def future_ipo(num_days_ahead: int, export: str) -> pd.DataFrame:
    """Future IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_ahead: int
        Number of days to look ahead for IPOs dates
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    df_future_ipo : pd.DataFrame
        Future IPOs dates
    """
    today = datetime.now()
    future_date = today + timedelta(days=num_days_ahead)

    df_future_ipo = (
        finnhub_model.get_ipo_calendar(
            today.strftime("%Y-%m-%d"), future_date.strftime("%Y-%m-%d")
        )
        .rename(columns={"Date": "Future"})
        .fillna("")
    )

    if df_future_ipo.empty:
        print(f"No IPOs found for the next {num_days_ahead} days")
    else:
        print(
            tabulate(
                df_future_ipo,
                headers=df_future_ipo.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fipo",
        df_future_ipo,
    )
