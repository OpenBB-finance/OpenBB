"""CoinGecko view"""
__docformat__ = "numpy"

import os
from pandas.plotting import register_matplotlib_converters
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import (
    export_data,
)
import gamestonk_terminal.cryptocurrency.due_diligence.pycoingecko_model as gecko
from gamestonk_terminal.cryptocurrency.dataframe_helpers import wrap_text_in_df
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


def display_info(symbol: str, export: str) -> None:
    """Shows basic information about loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    coin = gecko.Coin(symbol)

    df = wrap_text_in_df(coin.get_base_info, w=80)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df,
    )


def display_web(symbol: str, export: str) -> None:
    """Shows found websites corresponding to loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    coin = gecko.Coin(symbol)

    df = coin.get_websites

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "web",
        df,
    )


def display_social(symbol: str, export: str) -> None:
    """Shows social media corresponding to loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)
    df = coin.get_social_media

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "social",
        df,
    )


def display_dev(symbol: str, export: str) -> None:
    """Shows developers data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_developers_data

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dev",
        df,
    )


def display_ath(symbol: str, currency: str, export: str) -> None:
    """Shows all time high data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency

    currency: str
        currency vs which coin ath will be displayed: usd or btc
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_all_time_high(currency=currency)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ath",
        df,
    )


def display_atl(symbol: str, currency: str, export: str) -> None:
    """Shows all time low data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency

    currency: str
        currency vs which coin ath will be displayed: usd or btc
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_all_time_low(currency=currency)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "atl",
        df,
    )


def display_score(symbol: str, export: str) -> None:
    """Shows different kind of scores for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_scores

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "score",
        df,
    )


def display_bc(symbol: str, export: str) -> None:
    """Shows urls to blockchain explorers. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_blockchain_explorers

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "bc",
        df,
    )


def display_market(symbol: str, export: str) -> None:
    """Shows market data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    symbol : str
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    coin = gecko.Coin(symbol)

    df = coin.get_market_data

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "market",
        df,
    )
