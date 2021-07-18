"""CoinMarketCap API"""
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from tabulate import tabulate
from coinmarketcapapi import CoinMarketCapAPI
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.helper_funcs import check_positive, parse_known_args_and_warn

sort_options = ["Symbol", "CMC_Rank", "LastPrice", "DayPctChange", "MarketCap"]

sort_map = {
    "Symbol": "Symbol",
    "CMC_Rank": "CMC_Rank",
    "LastPrice": "Last Price",
    "DayPctChange": "1 Day Pct Change",
    "MarketCap": "Market Cap ($B)",
}


def get_cmc_top_n(other_args: List[str]):
    """
    Shows top n coins from coinmarketcap.com
    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="cmc_top_n",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="This gets the top ranked coins from coinmarketcap.com",
    )
    parser.add_argument(
        "-n",
        default=10,
        dest="n_to_get",
        type=check_positive,
        help="number of coins to display",
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="column to sort data by.",
        default="CMC_Rank",
        choices=sort_options,
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)
        ratings = cmc.cryptocurrency_listings_latest().data

        symbol, rank, price, pchange1d, mkt_cap = [], [], [], [], []
        for coin in ratings:
            symbol.append(coin["symbol"])
            rank.append(coin["cmc_rank"])
            price.append(coin["quote"]["USD"]["price"])
            pchange1d.append(coin["quote"]["USD"]["percent_change_24h"])
            mkt_cap.append(coin["quote"]["USD"]["market_cap"] / (10 ** 9))

        df = pd.DataFrame(data=[symbol, rank, price, pchange1d, mkt_cap]).transpose()
        df.columns = [
            "Symbol",
            "CMC_Rank",
            "Last Price",
            "1 Day Pct Change",
            "Market Cap ($B)",
        ]

        df = df.sort_values(by=sort_map[ns_parser.sortby], ascending=ns_parser.descend)

        print(
            tabulate(
                df.iloc[: ns_parser.n_to_get, :],
                headers=df.columns,
                showindex=False,
                tablefmt="fancy_grid",
                floatfmt=".2f",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")
