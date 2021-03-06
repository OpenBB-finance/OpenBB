import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_user_agent,
    parse_known_args_and_warn,
)


def high_short_interest(l_args):
    parser = argparse.ArgumentParser(
        prog="high_short",
        description="""
            Print top stocks being more heavily shorted. HighShortInterest.com provides
            a convenient sorted database of stocks which have a short interest of over
            20 percent. Additional key data such as the float, number of outstanding shares,
            and company industry is displayed. Data is presented for the Nasdaq Stock Market,
            the New York Stock Exchange, and the American Stock Exchange. [Source: www.highshortinterest.com]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of top stocks to print.",
    )

    ns_parser = parse_known_args_and_warn(parser, l_args)

    url_high_short_interested_stocks = "https://www.highshortinterest.com"
    text_soup_high_short_interested_stocks = BeautifulSoup(
        requests.get(
            url_high_short_interested_stocks, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    a_high_short_interest_header = list()
    for high_short_interest_header in text_soup_high_short_interested_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_high_short_interest_header.append(
            high_short_interest_header.text.strip("\n").split("\n")[0]
        )
    df_high_short_interest = pd.DataFrame(columns=a_high_short_interest_header)
    df_high_short_interest.loc[0] = ["", "", "", "", "", "", ""]

    stock_list_tr = text_soup_high_short_interested_stocks.find_all("tr")

    shorted_stock_data = list()
    for a_stock in stock_list_tr:
        a_stock_txt = a_stock.text

        if a_stock_txt == "":
            continue

        shorted_stock_data = a_stock_txt.split("\n")

        if len(shorted_stock_data) == 8:
            df_high_short_interest.loc[
                len(df_high_short_interest.index)
            ] = shorted_stock_data[:-1]

        shorted_stock_data = list()

    pd.set_option("display.max_colwidth", -1)
    print(df_high_short_interest.head(n=ns_parser.n_num).to_string(index=False))
    print("")


def low_float(l_args):
    parser = argparse.ArgumentParser(
        prog="low_float",
        description="""
            Print top stocks with lowest float. LowFloat.com provides a convenient
            sorted database of stocks which have a float of under 10 million shares. Additional key
            data such as the number of outstanding shares, short interest, and company industry is
            displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange,
            the American Stock Exchange, and the Over the Counter Bulletin Board. [Source: www.lowfloat.com]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of top stocks to print.",
    )

    ns_parser = parse_known_args_and_warn(parser, l_args)

    url_high_short_interested_stocks = "https://www.lowfloat.com"
    text_soup_low_float_stocks = BeautifulSoup(
        requests.get(
            url_high_short_interested_stocks, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    a_low_float_header = list()
    for low_float_header in text_soup_low_float_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_low_float_header.append(low_float_header.text.strip("\n").split("\n")[0])
    df_low_float = pd.DataFrame(columns=a_low_float_header)
    df_low_float.loc[0] = ["", "", "", "", "", "", ""]

    stock_list_tr = text_soup_low_float_stocks.find_all("tr")

    low_float_data = list()
    for a_stock in stock_list_tr:
        a_stock_txt = a_stock.text

        if a_stock_txt == "":
            continue

        low_float_data = a_stock_txt.split("\n")

        if len(low_float_data) == 8:
            df_low_float.loc[len(df_low_float.index)] = low_float_data[:-1]

        low_float_data = list()

    pd.set_option("display.max_colwidth", -1)
    print(df_low_float.head(n=ns_parser.n_num).to_string(index=False))
    print("")
