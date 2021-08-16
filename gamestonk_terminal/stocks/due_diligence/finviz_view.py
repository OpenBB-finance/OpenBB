""" Finviz View """
__docformat__ = "numpy"

from colorama import Fore, Style
from tabulate import tabulate
from gamestonk_terminal.stocks.due_diligence import finviz_model
from gamestonk_terminal.helper_funcs import (
    patch_pandas_text_adjustment,
)


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


def analyst(ticker: str, no_color: bool):
    """Display analyst ratings. [Source: Finviz]

    Parameters
    ----------
    ticker : str
        Stock ticker
    no_color : bool
        Select if no color is wanted
    """
    df_fa = finviz_model.get_analyst_data(ticker)

    if not no_color:
        df_fa["category"] = df_fa["category"].apply(category_color_red_green)

        patch_pandas_text_adjustment()

    print(
        tabulate(
            df_fa,
            headers=df_fa.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        ),
        "\n",
    )
