"""Helper functions for scraping options data"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
import configparser

import requests
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    export_data,
    plot_autoscale,
)
from gamestonk_terminal.options import yfinance_model
from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff

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


possible_greeks = [
    "iv",
    "gamma",
    "theta",
    "vega",
    "delta",
    "rho",
    "premium",
]


def check_valid_option_greek_header(headers: str) -> List[str]:
    """Check valid greek selection

    Parameters
    ----------
    headers : str
        Option chains headers

    Returns
    ----------
    List[str]
        List of columns string
    """
    columns = [str(item) for item in headers.split(",")]

    for header in columns:
        if header not in possible_greeks:
            raise argparse.ArgumentTypeError("Invalid option chains header selected!")

    return columns


def historical_greeks(ticker: str, expiry: str, other_args: List[str]):
    """Get historical greeks

    Parameters
    ----------
    ticker: str
        Ticker
    expiry: str
        Expiration date
    other_args: List[str]
        Argparse arguments
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="grhist",
        description="Plot historical option greeks.",
    )

    parser.add_argument(
        "-s",
        "--strike",
        dest="strike",
        type=float,
        required="--chain" not in other_args or "-h" not in other_args,
        help="Strike price to look at",
    )
    parser.add_argument(
        "--put",
        dest="put",
        action="store_true",
        default=False,
        help="Flag for showing put option",
    )

    parser.add_argument(
        "-g",
        "--greek",
        dest="greek",
        type=str,
        choices=possible_greeks,
        default="delta",
        help="Greek column to select",
    )

    parser.add_argument("--chain", dest="chain_id", type=str, help="OCC option symbol")

    parser.add_argument(
        "--raw", dest="raw", action="store_true", default=False, help="Display raw data"
    )

    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not ns_parser.chain_id:
            options = yfinance_model.get_option_chain(ticker, expiry)

            if ns_parser.put:
                options = options.puts
            else:
                options = options.calls

            chain_id = options.loc[
                options.strike == ns_parser.strike, "contractSymbol"
            ].values[0]
        else:
            chain_id = ns_parser.chain_id

        r = requests.get(f"https://api.syncretism.io/ops/historical/{chain_id}")

        if r.status_code != 200:
            print("Error in request.")
            return

        history = r.json()

        iv, delta, gamma, theta, rho, vega, premium, price, time = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )

        for entry in history:

            time.append(pd.to_datetime(entry["timestamp"], unit="s"))
            iv.append(entry["impliedVolatility"])
            gamma.append(entry["gamma"])
            delta.append(entry["delta"])
            theta.append(entry["theta"])
            rho.append(entry["rho"])
            vega.append(entry["vega"])
            premium.append(entry["premium"])
            price.append(entry["regularMarketPrice"])

        data = {
            "iv": iv,
            "gamma": gamma,
            "delta": delta,
            "theta": theta,
            "rho": rho,
            "vega": vega,
            "premium": premium,
            "price": price,
        }

        df = pd.DataFrame(data, index=time)

        if ns_parser.raw:
            print(df.tail(20))
        if ns_parser.export:
            export_data(
                ns_parser.export,
                os.path.dirname(os.path.abspath(__file__)),
                f"historical_greek_{ticker}_{expiry}_{ns_parser.greek}_{str(ns_parser.strike).replace('.', 'p')}"
                f"_{['Call','Put'][ns_parser.put]}",
                df,
            )
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
        im1 = ax.plot(time, df[ns_parser.greek], c="firebrick", label=ns_parser.greek)
        ax.set_ylabel(ns_parser.greek)
        ax1 = ax.twinx()
        im2 = ax1.plot(time, price, c="dodgerblue", label="Stock Price")
        ax1.set_ylabel(f"{ticker} Price")
        ax1.set_xlabel("Date")
        ax.grid("on")
        ax.set_title(
            f"{ns_parser.greek} historical for {ticker.upper()} {ns_parser.strike} {['Call','Put'][ns_parser.put]}"
        )
        plt.gcf().autofmt_xdate()

        if gtff.USE_ION:
            plt.ion()

        ims = im1 + im2
        labels = [lab.get_label() for lab in ims]
        plt.legend(ims, labels, loc=0)
        fig.tight_layout(pad=1)
        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
