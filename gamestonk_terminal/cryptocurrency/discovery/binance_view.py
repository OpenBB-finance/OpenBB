"""Binance view"""
__docformat__ = "numpy"

import argparse
from typing import List
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, check_positive
from gamestonk_terminal.cryptocurrency.discovery import binance_model


def coins(other_args: List[str]):
    """Shows list of all trading pairs on Binance

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="coins",
        description="""Shows list of all available coins on Binance
        In Binance terminology symbol means a pair of 2 coins e.g
        symbol = ETHBTC - it means that baseAsset is ETH and quoteAsset is BTC.
        You can display top N number of coins with --top N flag,
        You can search by starting letters with -l/--letter flag like `coins -l M`
        And you can also specify by which column you are searching for coin with --key
        Displays columns like:
            symbol, quoteAsset, baseAsset""",
    )
    parser.add_argument(
        "-s",
        "--skip",
        default=0,
        dest="skip",
        help="Skip n of records",
        type=check_positive,
    )
    parser.add_argument(
        "-t",
        "--top",
        default=20,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )
    parser.add_argument("-l", "--letter", dest="letter", help="First letters", type=str)
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Search in column symbol, quoteAsset, baseAsset",
        type=str,
        choices=["symbol", "quoteAsset", "baseAsset"],
        default="symbol",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = binance_model.get_all_binance_trading_pairs()

        letter = ns_parser.letter
        if letter and isinstance(letter, str):
            df = df[
                df[ns_parser.key].str.match(f"^({letter.lower()}|{letter.upper()})")
            ]

        try:
            df = df[ns_parser.skip : ns_parser.skip + ns_parser.top]
        except Exception:
            df = binance_model.get_all_binance_trading_pairs()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")
