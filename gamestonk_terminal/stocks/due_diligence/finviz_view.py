""" Finviz View """
__docformat__ = "numpy"

import os
from colorama import Fore, Style
from tabulate import tabulate
from gamestonk_terminal.stocks.due_diligence import finviz_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff


def category_color_red_green(val: str) -> str:
    """Add color to analyst rating

    Parameters
    ----------
    val : str
        Analyst rating - Upgrade/Downgrade

    Returns
    -------
    str
        Analyst rating with color
    """

    if val == "Upgrade":
        return Fore.GREEN + val + Style.RESET_ALL
    if val == "Downgrade":
        return Fore.RED + val + Style.RESET_ALL
    if val == "Reiterated":
        return Fore.YELLOW + val + Style.RESET_ALL
    return val


def news(ticker: str, num: int):
    """Display news for a given stock ticker

    Parameters
    ----------
    ticker : str
        Stock ticker
    num : int
        Number of latest news being printed
    """
    d_finviz_news = finviz_model.get_news(ticker)
    i = 0
    for s_news_title, s_news_link in {*d_finviz_news}:
        print(f"-> {s_news_title}")
        print(f"{s_news_link}\n")
        i += 1

        if i > (num - 1):
            break

    print("")


def analyst(ticker: str, export: str):
    """Display analyst ratings. [Source: Finviz]

    Parameters
    ----------
    ticker : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = finviz_model.get_analyst_data(ticker)

    if gtff.USE_COLOR:
        df["category"] = df["category"].apply(category_color_red_green)

    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "analyst",
        df,
    )
