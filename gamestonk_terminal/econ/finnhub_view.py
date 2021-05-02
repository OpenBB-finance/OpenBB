import argparse
from typing import List
import math
from datetime import datetime
import requests
import yfinance as yf
import mplfinance as mpf
import pandas as pd
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    check_positive,
)


def get_economy_calendar_events() -> pd.DataFrame:
    """Get economic calendar events

    Returns
    -------
    pd.DataFrame
        Get dataframe with economic calendar events
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/calendar/economic?token={cfg.API_FINNHUB_KEY}"
    )
    if response.status_code == 200:
        d_data = response.json()
        if "economicCalendar" in d_data:
            return pd.DataFrame(d_data["economicCalendar"])

    return pd.DataFrame()


def economy_calendar_events(other_args: List[str]):
    """Output economy calendar events

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="events",
        description="""
            Output economy calendar events. [Source: https://finnhub.io]
        """,
    )
    parser.add_argument(
        "-c",
        "--country",
        action="store",
        dest="country",
        type=str,
        default="US",
        choices=["NZ", "AU", "ERL", "CA", "EU", "US", "JP", "CN", "GB", "CH"],
        help="Country from where to get economic calendar events",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="num",
        type=check_positive,
        default=10,
        help="Number economic calendar events to display",
    )
    parser.add_argument(
        "-i",
        "--impact",
        action="store",
        dest="impact",
        type=str,
        default="all",
        choices=["low", "medium", "high", "all"],
        help="Country from where to get economic calendar events",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_events = get_economy_calendar_events()

        if df_events.empty:
            print("No latest economy calendar events found\n")
            return

        df_econ_calendar = df_events[
            df_events["country"] == ns_parser.country
        ].sort_values("time", ascending=False)

        if df_econ_calendar.empty:
            print("No latet economy calendar events found in the specified country\n")
            return

        if ns_parser.impact != "all":
            df_econ_calendar = df_econ_calendar[
                df_econ_calendar["impact"] == ns_parser.impact
            ]

            if df_econ_calendar.empty:
                print(
                    "No latet economy calendar events found in the specified country with this impact\n"
                )
                return

        df_econ_calendar = df_econ_calendar.fillna("---").head(n=ns_parser.num)

        d_econ_calendar_map = {
            "actual": "Actual release",
            "prev": "Previous release",
            "country": "Country",
            "unit": "Unit",
            "estimate": "Estimate",
            "event": "Event",
            "impact": "Impact Level",
            "time": "Release time",
        }

        df_econ_calendar = df_econ_calendar[
            ["time", "event", "impact", "prev", "estimate", "actual", "unit"]
        ].rename(columns=d_econ_calendar_map)

        print(df_econ_calendar.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")
