import argparse
from typing import List, Tuple, Any, Optional
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from gamestonk_terminal.cryptocurrency.due_dilligence import pycoingecko_model
from gamestonk_terminal.cryptocurrency.due_dilligence import coinpaprika_view as paprika
from gamestonk_terminal.cryptocurrency.due_dilligence import binance_view as binance
from gamestonk_terminal.cryptocurrency.due_dilligence import pycoingecko_view as gecko


DD_VIEWS_MAPPING = {
    "cg": gecko,
    "cp": paprika,
    "bin": binance,
}


def load(coin: str, other_args: List[str]) -> Tuple[Any, Any]:

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="load",
        description="Load crypto currency to perform analysis on. "
        "Available data sources are coingecko, coinpaprika, and binance"
        "By default main source used for analysis is coingecko (cg). To change it use --source flag",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Coin to get",
        dest="coin",
        type=str,
        required="-h" not in other_args,
    )

    parser.add_argument(
        "--source",
        dest="source",
        choices=["cp", "cg", "bin"],
        default="cg",
        help="Source of data.",
        type=str,
    )

    try:
        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return coin, None

        current_coin = ""  # type: Optional[Any]

        if ns_parser.source == "cg":
            current_coin = pycoingecko_model.Coin(ns_parser.coin)
            return current_coin, ns_parser.source

        if ns_parser.source == "bin":
            current_coin = binance.load(other_args)
            return current_coin, ns_parser.source

        if ns_parser.source == "cp":
            current_coin = paprika.load(other_args)
            return current_coin, ns_parser.source

        return current_coin, None

    except KeyError:
        print(f"Could not find coin: {ns_parser.coin}", "\n")
        return coin, None
    except SystemExit:
        print("")
        return coin, None
    except Exception as e:
        print(e, "\n")
        return coin, None
