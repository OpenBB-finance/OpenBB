import argparse
from typing import List
from datetime import datetime, timedelta
import requests
import pandas as pd
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_non_negative,
)


def get_ipo_calendar(from_date: str, to_date: str) -> pd.DataFrame:
    """Get IPO calendar

    Parameters
    ----------
    from_date : str
        from date (%Y-%m-%d) to get IPO calendar
    to_date : str
        to date (%Y-%m-%d) to get IPO calendar

    Returns
    -------
    pd.DataFrame
        Get dataframe with economic calendar events
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/calendar/ipo?from={from_date}&to={to_date}&token={cfg.API_FINNHUB_KEY}"
    )
    if response.status_code == 200:
        d_data = response.json()
        if "ipoCalendar" in d_data:
            d_refactor_columns = {
                "numberOfShares": "Number of Shares",
                "totalSharesValue": "Total Shares Value",
                "date": "Date",
                "exchange": "Exchange",
                "name": "Name",
                "price": "Price",
                "status": "Status",
            }
            return pd.DataFrame(d_data["ipoCalendar"]).rename(
                columns=d_refactor_columns
            )

    return pd.DataFrame()


def ipo_calendar(other_args: List[str]):
    """Past and future IPOs calendar [Finnhub]

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ipo",
        description="""
            Past and future IPOs. [Source: https://finnhub.io]
        """,
    )
    parser.add_argument(
        "-p",
        "--past",
        action="store",
        dest="past_days",
        type=check_non_negative,
        default=0,
        help="Number of past days to look for IPOs.",
    )
    parser.add_argument(
        "-f",
        "--future",
        action="store",
        dest="future_days",
        type=check_non_negative,
        default=10,
        help="Number of future days to look for IPOs.",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-f")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        today = datetime.now()

        if ns_parser.future_days > 0:
            future_date = today + timedelta(days=ns_parser.future_days)

            df_future_ipo = get_ipo_calendar(
                today.strftime("%Y-%m-%d"), future_date.strftime("%Y-%m-%d")
            ).rename(columns={"Date": "Future"})

            if df_future_ipo.empty:
                print(f"No IPOs found for the next {ns_parser.future_days} days")
            else:
                print(df_future_ipo.to_string(index=False))
            print("")

        if ns_parser.past_days > 0:
            past_date = today - timedelta(days=ns_parser.past_days)

            df_past_ipo = get_ipo_calendar(
                past_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
            ).rename(columns={"Date": "Past"})

            if df_past_ipo.empty:
                print(f"No IPOs found since the last {ns_parser.past_days} days")
            else:
                print(df_past_ipo.to_string(index=False))
            print("")

    except Exception as e:
        print(e, "\n")
