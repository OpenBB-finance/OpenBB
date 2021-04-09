""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
import os
import configparser
import pandas as pd
from finvizfinance.screener import (
    technical,
    overview,
    valuation,
    financial,
    ownership,
    performance,
)
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
)

d_signals = {
    "top_gainers": "Top Gainers",
    "top_losers": "Top Losers",
    "new_high": "New High",
    "new_low": "New Low",
    "most_volatile": "Most Volatile",
    "most_active": "Most Active",
    "unusual_volume": "Unusual Volume",
    "overbought": "Overbought",
    "oversold": "Oversold",
    "downgrades": "Downgrades",
    "upgrades": "Upgrades",
    "earnings_before": "Earnings Before",
    "earnings_after": "Earnings After",
    "recent_insider_buying": "Recent Insider Buying",
    "recent_insider_selling": "Recent Insider Selling",
    "major_news": "Major News",
    "horizontal_sr": "Horizontal S/R",
    "tl_resistance": "TL Resistance",
    "tl_support": "TL Support",
    "wedge_up": "Wedge Up",
    "wedge_down": "Wedge Down",
    "wedge": "Wedge",
    "triangle_ascending": "Triangle Ascending",
    "triangle_descending": "Triangle Descending",
    "channel_up": "Channel Up",
    "channel_down": "Channel Down",
    "channel": "Channel",
    "double_top": "Double Top",
    "double_bottom": "Double Bottom",
    "multiple_top": "Multiple Top",
    "multiple_bottom": "Multiple Bottom",
    "head_shoulders": "Head & Shoulders",
    "head_shoulders_inverse": "Head & Shoulders Inverse",
}


def get_screener_data(
    preset_loaded: str, data_type: str, signal: str, limit: int, ascend: bool
):
    """Screener Overview

    Parameters
    ----------
    preset_loaded : str
        Loaded preset filter
    data_type : str
        Data type between: overview, valuation, financial, ownership, performance, technical
    signal : str
        Signal to use to filter data
    limit : int
        Limit of stocks filtered with presets to print
    ascend : bool
        Ascended order of stocks filtered to print

    Returns
    ----------
    pd.DataFrame
        Dataframe with loaded filtered stocks
    """
    preset_filter = configparser.RawConfigParser()
    preset_filter.optionxform = str  # type: ignore
    preset_filter.read("gamestonk_terminal/screener/presets/" + preset_loaded + ".ini")

    d_general = preset_filter["General"]
    d_filters = {
        **preset_filter["Descriptive"],
        **preset_filter["Fundamental"],
        **preset_filter["Technical"],
    }

    d_filters = {k: v for k, v in d_filters.items() if v}

    if data_type == "overview":
        screen = overview.Overview()
    elif data_type == "valuation":
        screen = valuation.Valuation()
    elif data_type == "financial":
        screen = financial.Financial()
    elif data_type == "ownership":
        screen = ownership.Ownership()
    elif data_type == "performance":
        screen = performance.Performance()
    elif data_type == "technical":
        screen = technical.Technical()
    else:
        print("Invalid selected screener type")
        return pd.DataFrame()

    if signal:
        screen.set_filter(signal=d_signals[signal])
    else:
        if d_general["Signal"]:
            screen.set_filter(filters_dict=d_filters, signal=d_general["Signal"])
        else:
            screen.set_filter(filters_dict=d_filters)

    if d_general["Order"]:
        if limit > 0:
            df_screen = screen.ScreenerView(
                order=d_general["Order"],
                limit=limit,
                ascend=ascend,
            )
        else:
            df_screen = screen.ScreenerView(order=d_general["Order"], ascend=ascend)

    else:
        if limit > 0:
            df_screen = screen.ScreenerView(limit=limit, ascend=ascend)
        else:
            df_screen = screen.ScreenerView(ascend=ascend)

    return df_screen


def screener(other_args: List[str], loaded_preset: str, data_type: str):
    """Screener

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Loaded preset filter
    data_type : str
        Data type string between: overview, valuation, financial, ownership, performance, technical
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
            for preset in os.listdir("gamestonk_terminal/screener/presets")
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_screen = get_screener_data(
            ns_parser.preset,
            data_type,
            ns_parser.signal,
            ns_parser.limit,
            ns_parser.ascend,
        )

        if isinstance(df_screen, pd.DataFrame):
            print(df_screen.to_string())
        print("")

    except Exception as e:
        print(e)
        print("")
        return


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
