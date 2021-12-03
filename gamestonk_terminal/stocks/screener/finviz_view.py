""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
import os
import difflib
from tabulate import tabulate
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    try_except,
    export_data,
)
from gamestonk_terminal.stocks.screener.finviz_model import (
    d_signals,
    presets_path,
    get_screener_data,
)
from gamestonk_terminal import feature_flags as gtff

d_cols_to_sort = {
    "overview": [
        "Ticker",
        "Company",
        "Sector",
        "Industry",
        "Country",
        "Market Cap",
        "P/E",
        "Price",
        "Change",
        "Volume",
    ],
    "valuation": [
        "Ticker",
        "Market Cap",
        "P/E",
        "Fwd P/E",
        "PEG",
        "P/S",
        "P/B",
        "P/C",
        "P/FCF",
        "EPS this Y",
        "EPS next Y",
        "EPS past 5Y",
        "EPS next 5Y",
        "Sales past 5Y",
        "Price",
        "Change",
        "Volume",
    ],
    "financial": [
        "Ticker",
        "Market Cap",
        "Dividend",
        "ROA",
        "ROE",
        "ROI",
        "Curr R",
        "Quick R",
        "LTDebt/Eq",
        "Debt/Eq",
        "Gross M",
        "Oper M",
        "Profit M",
        "Earnings",
        "Price",
        "Change",
        "Volume",
    ],
    "ownership": [
        "Ticker",
        "Market Cap",
        "Outstanding",
        "Float",
        "Insider Own",
        "Insider Trans",
        "Inst Own",
        "Inst Trans",
        "Float Short",
        "Short Ratio",
        "Avg Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "performance": [
        "Ticker",
        "Perf Week",
        "Perf Month",
        "Perf Quart",
        "Perf Half",
        "Perf Year",
        "Perf YTD",
        "Volatility W",
        "Volatility M",
        "Recom",
        "Avg Volume",
        "Rel Volume",
        "Price",
        "Change",
        "Volume",
    ],
    "technical": [
        "Ticker",
        "Beta",
        "ATR",
        "SMA20",
        "SMA50",
        "SMA200",
        "52W High",
        "52W Low",
        "RSI",
        "Price",
        "Change",
        "from Open",
        "Gap",
        "Volume",
    ],
}


@try_except
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
        ]
        + list(d_signals.keys()),
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="limit",
        type=check_positive,
        default=10,
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
        "-s",
        "--sort",
        action="store",
        dest="sort",
        default="",
        nargs="+",
        help=f"Sort elements of the table. Use {', '.join(d_cols_to_sort[data_type])}",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return []

    df_screen = get_screener_data(
        ns_parser.preset,
        data_type,
        0,
        ns_parser.ascend,
    )

    if isinstance(df_screen, pd.DataFrame):
        if df_screen.empty:
            return []

        df_screen = df_screen.dropna(axis="columns", how="all")

        if ns_parser.sort:
            if " ".join(ns_parser.sort) in d_cols_to_sort[data_type]:
                df_screen = df_screen.sort_values(
                    by=[" ".join(ns_parser.sort)],
                    ascending=ns_parser.ascend,
                    na_position="last",
                )
            else:
                similar_cmd = difflib.get_close_matches(
                    " ".join(ns_parser.sort),
                    d_cols_to_sort[data_type],
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    print(
                        f"Replacing '{' '.join(ns_parser.sort)}' by '{similar_cmd[0]}' so table can be sorted."
                    )
                    df_screen = df_screen.sort_values(
                        by=[similar_cmd[0]],
                        ascending=ns_parser.ascend,
                        na_position="last",
                    )
                else:
                    print(
                        f"Wrong sort column provided! Provide one of these: {', '.join(d_cols_to_sort[data_type])}"
                    )

        df_screen = df_screen.fillna("")

        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_screen.head(n=ns_parser.limit),
                    headers=df_screen.columns,
                    floatfmt=".2f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
            )
        else:
            print(df_screen.head(n=ns_parser.limit).to_string())
        print("")

        export_data(
            ns_parser.export,
            os.path.dirname(os.path.abspath(__file__)),
            data_type,
            df_screen,
        )

        return list(df_screen.head(n=ns_parser.limit)["Ticker"].values)

    print("")
    return []
