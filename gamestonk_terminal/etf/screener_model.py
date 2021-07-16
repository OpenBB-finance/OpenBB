"""Screener model"""
__docformat__ = "numpy"

import argparse
from typing import List
import os
import configparser
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, export_data


def etf_screener(other_args: List[str]):
    """
    Screens the etfs pulled from my repo, which is updated daily at midnight EST
    Parameters
    ----------
    other_args:
        List or argparse arguments

    """
    parser = argparse.ArgumentParser(
        prog="etfscr",
        add_help=False,
        description="Screens ETFS from a personal scraping github repository.  Data scraped from stockanalysis.com",
    )

    parser.add_argument(
        "-p", "--min_price", help="min price", dest="min_price", default=False
    )
    parser.add_argument(
        "-P", "--max_price", help="max price", dest="max_price", default=False
    )
    parser.add_argument(
        "-a", "--min_assets", help="min assets ($M)", dest="min_assets", default=False
    )
    parser.add_argument(
        "-A", "--max_assets", help="max assets ($M)", dest="max_assets", default=False
    )
    parser.add_argument(
        "-n",
        "--min_nav",
        help="min nav (net asset value)",
        dest="min_nav",
        default=False,
    )

    parser.add_argument(
        "-N",
        "--max_nav",
        help="max nav (net asset value)",
        dest="max_nav",
        default=False,
    )
    parser.add_argument(
        "-e", "--min_exp", help="min expense ratio (%%)", dest="min_exp", default=False
    )

    parser.add_argument(
        "-E", "--max_exp", help="max expense ratio (%%)", dest="max_exp", default=False
    )

    parser.add_argument(
        "-r", "--min_pe", help="min pe ratio", dest="min_pe", default=False
    )
    parser.add_argument(
        "-R", "--max_pe", help="max pe ratio", dest="max_pe", default=False
    )

    parser.add_argument(
        "-d", "--min_div", help="min dividend yield (%%)", dest="min_div", default=False
    )
    parser.add_argument(
        "-D", "--max_div", help="max dividend yield (%%)", dest="max_div", default=False
    )
    parser.add_argument(
        "-b", "--min_beta", help="min 5Y beta", dest="min_beta", default=False
    )
    parser.add_argument(
        "-B", "--max_beta", help="max beta", dest="max_beta", default=False
    )
    parser.add_argument(
        "--num", type=int, help="Number of etfs to show", dest="num", default=20
    )

    parser.add_argument(
        "--config",
        help="Load options from config file",
        dest="config",
        action="store_true",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )
    # pylint: disable=no-member
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = pd.read_csv(
            "https://raw.githubusercontent.com/jmaslek/etf_scraper/main/etf_overviews.csv",
            index_col=0,
        )
        print("ETFs downloaded\n")
        param_string = "etf_screener"
        if ns_parser.config:
            cf = configparser.ConfigParser()
            cf.read("gamestonk_terminal/etf/etf_config.ini")
            cols = cf.sections()

            for col in cols:
                if cf[col]["Min"] != "None":
                    query = f"{col} > {cf[col]['Min']} "
                    df = df.query(query)
                if cf[col]["Max"] != "None":
                    query = f"{col} < {cf[col]['Max']} "
                    df = df.query(query)
            param_string += "_from_config"
        else:

            if ns_parser.min_price:
                df = df.query(f"Price > {ns_parser.min_price}")
                param_string += f"_p_{ns_parser.min_price}".replace(".", "p")

            if ns_parser.max_price:
                df = df.query(f"Price < {ns_parser.max_price}")
                param_string += f"_P_{ns_parser.max_price}".replace(".", "p")

            if ns_parser.min_assets:
                df = df.query(f"Assets > {ns_parser.min_assets}")
                param_string += f"_a_{ns_parser.min_assets}".replace(".", "p")

            if ns_parser.max_assets:
                df = df.query(f"Assets < {ns_parser.max_assets}")
                param_string += f"_A_{ns_parser.max_assets}".replace(".", "p")

            if ns_parser.min_nav:
                df = df.query(f"NAV > {ns_parser.min_nav}")
                param_string += f"_n_{ns_parser.min_nav}".replace(".", "p")

            if ns_parser.max_nav:
                df = df.query(f"NAV < {ns_parser.max_nav}")
                param_string += f"_N_{ns_parser.max_nav}".replace(".", "p")

            if ns_parser.min_exp:
                df = df.query(f"Expense > {ns_parser.min_exp}")
                param_string += f"_e_{ns_parser.min_exp}".replace(".", "p")

            if ns_parser.max_exp:
                df = df.query(f"Expense < {ns_parser.max_exp}")
                param_string += f"_E_{ns_parser.max_exp}".replace(".", "p")

            if ns_parser.min_pe:
                df = df.query(f"PE > {ns_parser.min_pe}")
                param_string += f"_r_{ns_parser.min_pe}".replace(".", "p")
            if ns_parser.max_pe:
                df = df.query(f"PE < {ns_parser.max_pe}")
                param_string += f"_R_{ns_parser.max_pe}".replace(".", "p")

            if ns_parser.min_div:
                df = df.query(f"DivYield > {ns_parser.min_div}")
                param_string += f"_d_{ns_parser.min_div}".replace(".", "p")
            if ns_parser.max_div:
                df = df.query(f"DivYield < {ns_parser.max_div}")
                param_string += f"_D_{ns_parser.max_div}".replace(".", "p")

            if ns_parser.min_beta:
                df = df.query(f"Beta > {ns_parser.min_beta}")
                param_string += f"_b_{ns_parser.min_beta}".replace(".", "p").replace(
                    "-", "neg"
                )

            if ns_parser.max_beta:
                df = df.query(f"Beta < {ns_parser.max_beta}")
                param_string += f"_B_{ns_parser.max_beta}".replace(".", "p").replace(
                    "-", "neg"
                )

        export_data(
            ns_parser.export,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "screeners"),
            param_string,
            df,
        )

        if df.shape[0] > int(ns_parser.num):
            df = df.sample(ns_parser.num)
        print(
            tabulate(
                df.fillna(""), tablefmt="fancy_grid", headers=df.columns, showindex=True
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")
