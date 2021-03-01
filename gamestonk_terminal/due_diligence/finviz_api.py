import argparse
from colorama import Fore, Style
import finviz
import pandas as pd
from gamestonk_terminal.helper_funcs import check_positive, patch_pandas_text_adjustment
from gamestonk_terminal.config_terminal import USE_COLOR


def category_color_red_green(val: str) -> str:
    if val == "Upgrade":
        return Fore.GREEN + val + Style.RESET_ALL
    elif val == "Downgrade":
        return Fore.RED + val + Style.RESET_ALL
    return val


# ---------------------------------------------------- INSIDER ----------------------------------------------------
def insider(l_args, s_ticker):
    parser = argparse.ArgumentParser(
        prog="insider",
        description="""
            Prints information about inside traders. The following fields are expected: Date, Relationship,
            Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading, SEC Form 4. [Source: Finviz]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of latest inside traders.",
    )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        d_finviz_insider = finviz.get_insider(s_ticker)
        df_fa = pd.DataFrame.from_dict(d_finviz_insider)
        df_fa.set_index("Date", inplace=True)
        df_fa = df_fa[
            [
                "Relationship",
                "Transaction",
                "#Shares",
                "Cost",
                "Value ($)",
                "#Shares Total",
                "Insider Trading",
                "SEC Form 4",
            ]
        ]
        print(df_fa.head(n=ns_parser.n_num))

        print("")

    except Exception as e:
        print(e)
        print("")
        return


# ---------------------------------------------------- NEWS ----------------------------------------------------
def news(l_args, s_ticker):
    parser = argparse.ArgumentParser(
        prog="news",
        description="""
            Prints latest news about company, including title and web link. [Source: Finviz]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=5,
        help="Number of latest news being printed.",
    )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        d_finviz_news = finviz.get_news(s_ticker)
        i = 0
        for s_news_title, s_news_link in {*d_finviz_news}:
            print(f"-> {s_news_title}")
            print(f"{s_news_link}\n")
            i += 1

            if i > (ns_parser.n_num - 1):
                break

        print("")

    except Exception as e:
        print(e)
        print("")
        return


# ---------------------------------------------------- ANALYST ----------------------------------------------------
def analyst(l_args, s_ticker):
    parser = argparse.ArgumentParser(
        prog="analyst",
        description="""
            Print analyst prices and ratings of the company. The following fields are expected:
            date, analyst, category, price from, price to, and rating. [Source: Finviz]
        """,
    )

    try:
        (_, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        d_finviz_analyst_price = finviz.get_analyst_price_targets(s_ticker)
        df_fa = pd.DataFrame.from_dict(d_finviz_analyst_price)
        df_fa.set_index("date", inplace=True)

        if USE_COLOR:
            df_fa["category"] = df_fa["category"].apply(category_color_red_green)

            patch_pandas_text_adjustment()

        print(df_fa)
        print("")

    except Exception as e:
        print(e)
        print("")
        return
