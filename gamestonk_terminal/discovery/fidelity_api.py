import argparse
from bs4 import BeautifulSoup
import requests
import pandas as pd
from gamestonk_terminal.helper_funcs import check_positive, get_user_agent

# ---------------------------------------------------- ORDERS ----------------------------------------------------
def orders(l_args):
    parser = argparse.ArgumentParser(
        prog="orders",
        description="""
            Orders by Fidelity customers. Information shown in the table below
            is based on the volume of orders entered on the "as of" date shown. Securities
            identified are not recommended or endorsed by Fidelity and are displayed for
            informational purposes only. [Source: Fidelity]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of top ordered stocks to be printed.",
    )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        url_orders = (
            "https://eresearch.fidelity.com/eresearch/gotoBL/fidelityTopOrders.jhtml"
        )

        text_soup_url_orders = BeautifulSoup(
            requests.get(url_orders, headers={"User-Agent": get_user_agent()}).text,
            "lxml",
        )

        l_orders = list()
        l_orders_vals = list()
        idx = 0
        for an_order in text_soup_url_orders.findAll(
            "td",
            {
                "class": [
                    "second",
                    "third",
                    "fourth",
                    "fifth",
                    "sixth",
                    "seventh",
                    "eight",
                ]
            },
        ):

            if ((idx + 1) % 3 == 0) or ((idx + 1) % 4 == 0) or ((idx + 1) % 6 == 0):
                if len(an_order) == 0:
                    l_orders_vals.append("")
                else:
                    l_orders_vals.append(an_order.contents[1])
            elif (idx + 1) % 5 == 0:
                s_orders = str(an_order)
                l_orders_vals.append(
                    s_orders[
                        s_orders.find('title="') + len('title="') : s_orders.find('"/>')
                    ]
                )
            else:
                l_orders_vals.append(an_order.text.strip())

            idx += 1

            # Add value to dictionary
            if (idx + 1) % 8 == 0:
                l_orders.append(l_orders_vals)
                l_orders_vals = list()
                idx = 0

        df_orders = pd.DataFrame(
            l_orders,
            columns=[
                "Symbol",
                "Company",
                "Price Change",
                "# Buy Orders",
                "Buy / Sell Ratio",
                "# Sell Orders",
                "Latest News",
            ],
        )

        df_orders = df_orders[
            [
                "Symbol",
                "Buy / Sell Ratio",
                "Price Change",
                "Company",
                "# Buy Orders",
                "# Sell Orders",
                "Latest News",
            ]
        ]

        print(
            text_soup_url_orders.findAll("span", {"class": "source"})[
                0
            ].text.capitalize()
            + ":"
        )

        pd.set_option("display.max_colwidth", -1)
        print(df_orders.head(n=ns_parser.n_num).iloc[:, :-1].to_string(index=False))
        print("")

    except SystemExit:
        print("")
        return
