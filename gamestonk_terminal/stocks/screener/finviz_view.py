""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
import os
from datetime import datetime
import pandas as pd
from gamestonk_terminal.stocks.report import due_diligence_view
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
)
from gamestonk_terminal.stocks.screener.finviz_model import (
    d_signals,
    presets_path,
    get_screener_data,
)


def screener(other_args: List[str], loaded_preset: str, data_type: str) -> List[str]:
    """Screener

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Loaded preset filter
    data_type : str
        Data type string between: overview, valuation, financial, ownership, performance, technical

    Returns
    -------
    List[str]
        List of stocks that meet preset criteria
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="screener",
        description="""
            Prints screener data of the companies that meet the pre-set filtering.
            The following information fields are expected: overview, valuation, financial,
            ownership, performance, technical. Note that when the signal parameter (-s)
            is specified, the preset is disregarded. [Source: Finviz]
        """,
    )
    parser.add_argument(
        "-p",
        "--preset",
        action="store",
        dest="preset",
        type=str,
        default=loaded_preset,
        help="Filter presets",
        choices=[
            preset.split(".")[0]
            for preset in os.listdir(presets_path)
            if preset[-4:] == ".ini"
        ],
    )
    parser.add_argument(
        "-s",
        "--signal",
        action="store",
        dest="signal",
        type=str,
        default=None,
        help="Signal",
        choices=list(d_signals.keys()),
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="limit",
        type=check_positive,
        default=0,
        help="Limit of stocks to print",
    )
    parser.add_argument(
        "-a",
        "--ascend",
        action="store_true",
        default=False,
        dest="ascend",
        help="Set order to Ascend, the default is Descend",
    )
    parser.add_argument(
        "-e",
        "--export",
        action="store_true",
        dest="exportFile",
        help="Save list as a text file",
    )
    parser.add_argument(
        "-m",
        "--mill",
        action="store_true",
        dest="mill",
        help="Run papermill on list",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return []

        df_screen = get_screener_data(
            ns_parser.preset,
            data_type,
            ns_parser.signal,
            ns_parser.limit,
            ns_parser.ascend,
        )

        if isinstance(df_screen, pd.DataFrame):
            if df_screen.empty:
                return []

            print(df_screen.to_string())
            print("")
            if ns_parser.exportFile:
                now = datetime.now()
                if not os.path.exists("reports/screener"):
                    os.makedirs("reports/screener")
                with open(
                    f"reports/screener/{ns_parser.signal}-{now.strftime('%Y-%m-%d_%H:%M:%S')}",
                    "w",
                ) as file:
                    file.write(df_screen.to_string(index=False) + "\n")
            if ns_parser.mill:
                for i in range(len(df_screen)):
                    ticker = [df_screen.iat[i, 0]]
                    due_diligence_view.due_diligence_report(ticker)
            return list(df_screen["Ticker"].values)

        print("")
        return []

    except Exception as e:
        print(e, "\n")
        return []


def view_signals(other_args: List[str]):
    """View list of available signals

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="signals",
        description="""
            Prints list of available signals. [Source: Finviz]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        print("top_gainers             stocks with the highest %% price gain today")
        print("top_losers              stocks with the highest %% price loss today.")
        print("new_high                stocks making 52-week high today")
        print("new_low                 stocks making 52-week low today")
        print(
            "most_volatile           stocks with the highest widest high/low trading range today"
        )
        print("most_active             stocks with the highest trading volume today")
        print(
            "unusual_volume          stocks with unusually high volume today - the highest relative volume ratio"
        )
        print(
            "overbought              stock is becoming overvalued and may experience a pullback."
        )
        print(
            "oversold                oversold stocks may represent a buying opportunity for investors."
        )
        print("downgrades              stocks downgraded by analysts today")
        print("upgrades                stocks upgraded by analysts today.")
        print(
            "earnings_before         companies reporting earnings today, before market open"
        )
        print(
            "earnings_after          companies reporting earnings today, after market close"
        )
        print("recent_insider_buying   stocks with recent insider buying activity")
        print("recent_insider_selling  stocks with recent insider selling activity")
        print("major_news              stocks with the highest news coverage today")
        print(
            "horizontal_sr           horizontal channel of price range between support and resistance trendlines"
        )
        print("tl_resistance           once a rising trendline is broken")
        print("tl_support              once a falling trendline is broken")
        print(
            "wedge_up                upward trendline support and upward trendline resistance (reversal)"
        )
        print(
            "wedge_down              downward trendline support and downward trendline resistance (reversal)"
        )
        print(
            "wedge                   upward trendline support, downward trendline resistance (contiunation)"
        )
        print(
            "triangle_ascending      upward trendline support and horizontal trendline resistance"
        )
        print(
            "triangle_descending     horizontal trendline support and downward trendline resistance"
        )
        print(
            "channel_up              both support and resistance trendlines slope upward"
        )
        print(
            "channel_down            both support and resistance trendlines slope downward"
        )
        print(
            "channel                 both support and resistance trendlines are horizontal"
        )
        print(
            "double_top              stock with 'M' shape that indicates a bearish reversal in trend"
        )
        print(
            "double_bottom           stock with 'W' shape that indicates a bullish reversal in trend"
        )
        print("multiple_top            same as double_top hitting more highs")
        print("multiple_bottom         same as double_bottom hitting more lows")
        print(
            "head_shoulders          chart formation that predicts a bullish-to-bearish trend reversal"
        )
        print(
            "head_shoulders_inverse  chart formation that predicts a bearish-to-bullish trend reversal"
        )
        print("")

    except Exception as e:
        print(e)
        print("")
        return
