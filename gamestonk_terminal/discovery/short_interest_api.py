import argparse
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from gamestonk_terminal.helper_funcs import check_positive


# ------------------------------------------------ HIGH_SHORT_INTEREST -------------------------------------------------
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

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")
        return

    url_high_short_interested_stocks = "https://www.highshortinterest.com"
    text_soup_high_short_interested_stocks = BeautifulSoup(
        requests.get(url_high_short_interested_stocks).text, "lxml"
    )

    # print(text_soup_high_short_interested_stocks.text)
    # html = text_soup_high_short_interested_stocks.prettify("utf-8")
    # stock_list = text_soup_high_short_interested_stocks.find_all("td")
    # stock_list_tr = text_soup_high_short_interested_stocks.find_all("tr")

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


# ---------------------------------------------------- LOW_FLOAT -----------------------------------------------------
def low_float(l_args):
    parser = argparse.ArgumentParser(
        prog="low_float",
        description="""Print top stocks with lowest float. LowFloat.com provides a convenient
                                     sorted database of stocks which have a float of under 10 million shares. Additional key
                                     data such as the number of outstanding shares, short interest, and company industry is
                                     displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange,
                                     the American Stock Exchange, and the Over the Counter Bulletin Board.
                                     [Source: www.lowfloat.com]""",
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

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    url_high_short_interested_stocks = "https://www.lowfloat.com"
    text_soup_low_float_stocks = BeautifulSoup(
        requests.get(url_high_short_interested_stocks).text, "lxml"
    )

    a_low_float_header = list()
    for low_float_header in text_soup_low_float_stocks.findAll(
        "td", {"class": "tblhdr"}
    ):
        a_low_float_header.append(low_float_header.text.strip("\n").split("\n")[0])
    df_low_float = pd.DataFrame(columns=a_low_float_header)
    df_low_float.loc[0] = ["", "", "", "", "", "", ""]

    a_low_float_stocks = re.sub(
        "<!--.*?//-->",
        "",
        text_soup_low_float_stocks.find_all("td")[3].text,
        flags=re.DOTALL,
    ).split("\n")[2:]
    a_low_float_stocks[0] = a_low_float_stocks[0].replace(
        "TickerCompanyExchangeFloatOutstdShortIntIndustry", ""
    )

    l_stock_info = list()
    for elem in a_low_float_stocks:
        if elem is "":
            continue

        l_stock_info.append(elem)

        if len(l_stock_info) == 7:
            df_low_float.loc[len(df_low_float.index)] = l_stock_info
            l_stock_info = list()

    pd.set_option("display.max_colwidth", -1)
    print(df_low_float.head(n=ns_parser.n_num).to_string(index=False))
    print("")
