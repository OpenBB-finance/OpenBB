"""Helper functions for scraping options data"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
import configparser
import requests
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")


def view_available_presets(other_args: List[str]):
    """View available presets.

    Parameters
    ----------
    other_args: List[str]
        Other arguments to be parsed
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="view",
        description="""View available presets under presets folder.""",
    )
    parser.add_argument(
        "-p",
        "--preset",
        action="store",
        dest="preset",
        type=str,
        help="View specific preset",
        default="",
        choices=[
            preset.split(".")[0]
            for preset in os.listdir(presets_path)
            if preset[-4:] == ".ini"
        ],
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.preset:
            preset_filter = configparser.RawConfigParser()
            preset_filter.optionxform = str  # type: ignore
            preset_filter.read(presets_path + ns_parser.preset + ".ini")

            filters_headers = ["FILTER"]

            print("")
            for filter_header in filters_headers:
                print(f" - {filter_header} -")
                d_filters = {**preset_filter[filter_header]}
                d_filters = {k: v for k, v in d_filters.items() if v}
                if d_filters:
                    max_len = len(max(d_filters, key=len))
                    for key, value in d_filters.items():
                        print(f"{key}{(max_len-len(key))*' '}: {value}")
                print("")

        else:
            presets = [
                preset.split(".")[0]
                for preset in os.listdir(presets_path)
                if preset[-4:] == ".ini"
            ]

            for preset in presets:
                with open(
                    presets_path + preset + ".ini",
                    encoding="utf8",
                ) as f:
                    description = ""
                    for line in f:
                        if line.strip() == "[FILTER]":
                            break
                        description += line.strip()
                print(f"\nPRESET: {preset}")
                print(description.split("Description: ")[1].replace("#", ""))
            print("")
    except Exception as e:
        print(e)


def screener_output(other_args: List[str]):
    """screener filter output"""
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="scr",
        description="""Sreener filter output from https://ops.syncretism.io/index.html.
Where: CS: Contract Symbol; S: Symbol, T: Option Type; Str: Strike; Exp v: Expiration;
IV: Implied Volatility; LP: Last Price; B: Bid; A: Ask; V: Volume; OI: Open Interest;
Y: Yield; MY: Monthly Yield; SMP: Regular Market Price; SMDL: Regular Market Day Low;
SMDH: Regular Market Day High; LU: Last Trade Date; LC: Last Crawl; ITM: In The Money;
PC: Price Change; PB: Price-to-book. """,
    )
    parser.add_argument(
        "-p",
        "--preset",
        action="store",
        dest="preset",
        type=str,
        default="template",
        help="Filter presets",
        choices=[
            preset.split(".")[0]
            for preset in os.listdir(presets_path)
            if preset[-4:] == ".ini"
        ],
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        d_cols = {
            "contractsymbol": "CS",
            "symbol": "S",
            "opttype": "T",
            "strike": "Str",
            "expiration": "Exp ∨",
            "impliedvolatility": "IV",
            "lastprice": "LP",
            "bid": "B",
            "ask": "A",
            "volume": "V",
            "openinterest": "OI",
            "yield": "Y",
            "monthlyyield": "MY",
            "regularmarketprice": "SMP",
            "regularmarketdaylow": "SMDL",
            "regularmarketdayhigh": "SMDH",
            "lasttradedate": "LU",
            "lastcrawl": "LC",
            "inthemoney": "ITM",
            "pchange": "PC",
            "pricetobook": "PB",
        }

        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_filter.read(presets_path + ns_parser.preset + ".ini")

        d_filters = {k: v for k, v in dict(preset_filter["FILTER"]).items() if v}
        s_filters = str(d_filters)
        s_filters = s_filters.replace(": '", ": ").replace("',", ",").replace("'}", "}")
        s_filters = s_filters.replace("'", '"')

        link = "https://api.syncretism.io/ops"

        res = requests.get(
            link, headers={"Content-type": "application/json"}, data=s_filters
        )

        if res.status_code == 200:
            df_res = pd.DataFrame(res.json())

            if df_res.empty:
                print(f"No options data found for preset: {ns_parser.preset}", "\n")
                return

            df_res = df_res.rename(columns=d_cols)[list(d_cols.values())[:17]]

            print(
                tabulate(
                    df_res,
                    headers=df_res.columns,
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )
        else:
            print("Wrong arguments specified. Error " + str(res.status_code))
        print("")

    except Exception as e:
        print(e, "\n")
