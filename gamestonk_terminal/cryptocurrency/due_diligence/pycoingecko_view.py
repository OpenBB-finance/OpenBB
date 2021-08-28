"""CoinGecko view"""
__docformat__ = "numpy"

import os
import argparse
from typing import List, Tuple

import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from tabulate import tabulate
import mplfinance as mpf
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    export_data,
)
from gamestonk_terminal.feature_flags import USE_ION as ion
import gamestonk_terminal.cryptocurrency.due_diligence.pycoingecko_model as gecko
from gamestonk_terminal.cryptocurrency.dataframe_helpers import wrap_text_in_df


register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


def load(other_args: List[str]):
    """Load selected Cryptocurrency. You can pass either symbol of id of the coin

    Parameters
    ----------
    other_args : List[str]
        argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="load",
        description="""Load cryptocurrency, from CoinGecko.
                    You will have access to a lot of statistics on that coin like price data,
                    coin development stats, social media and many others. Loading coin
                    also will open access to technical analysis menu.""",
    )
    parser.add_argument(
        "-c",
        "--coin",
        required="-h" not in other_args,
        type=str,
        dest="coin",
        help="Coin to load data for (symbol or coin id). You can use either symbol of the coin or coinId"
        "You can find all coins using command `coins` or visit  https://www.coingecko.com/en. "
        "To use load a coin use command load -c [symbol or coinId]",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        coin = gecko.Coin(ns_parser.coin)
        print("")
        return coin

    except KeyError:
        print(f"Could not find coin with the id: {ns_parser.coin}", "\n")
        return None
    except SystemExit:
        print("")
        return None
    except Exception as e:
        print(e, "\n")
        return None


def plot_chart(coin: gecko.Coin, other_args: List[str]):
    """Plots chart for loaded cryptocurrency

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    other_args : List[str]
        argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="chart",
        description="""
                        Display chart for loaded coin. You can specify currency vs which you want
                        to show chart and also number of days to get data for.
                        By default currency: usd and days: 30.
                        E.g. if you loaded in previous step Bitcoin and you want to see it's price vs ethereum
                        in last 90 days range use `chart --vs eth --days 90`
                        """,
    )
    parser.add_argument(
        "--vs", default="usd", dest="vs", help="Currency to display vs coin"
    )
    parser.add_argument(
        "-d", "--days", default=30, dest="days", help="Number of days to get data for"
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.get_coin_market_chart(ns_parser.vs, ns_parser.days)
        df = df["price"].resample("1D").ohlc().ffill()

        df.columns = [
            "Open",
            "High",
            "Low",
            "Close",
        ]

        title = (
            f"\n{coin.coin_symbol}/{ns_parser.vs} from {df.index[0].strftime('%Y/%m/%d')} "
            f"to {df.index[-1].strftime('%Y/%m/%d')}",
        )

        mpf.plot(
            df,
            type="candle",
            volume=False,
            title=str(title[0]) if isinstance(title, tuple) else title,
            xrotation=20,
            style="binance",
            figratio=(10, 7),
            figscale=1.10,
            figsize=(plot_autoscale()),
            update_width_config=dict(
                candle_linewidth=1.0, candle_width=0.8, volume_linewidth=1.0
            ),
        )

        if ion:
            plt.ion()
        plt.show()
        print("")
    except SystemExit:
        print("")

    except Exception as e:
        print(e, "\n")


def load_ta_data(coin: gecko.Coin, other_args: List[str]) -> Tuple[pd.DataFrame, str]:
    """Load data for Technical Analysis

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    other_args : List[str]
        argparse arguments

    Returns
    ----------
    Tuple[pd.DataFrame, str]
        dataframe with prices
        quoted currency

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ta",
        description="""
                        Loads data for technical analysis. You can specify currency vs which you want
                        to show chart and also number of days to get data for.
                        By default currency: usd and days: 30.
                        E.g. if you loaded in previous step Bitcoin and you want to see it's price vs ethereum
                        in last 90 days range use `ta --vs eth --days 90`
                        """,
    )
    parser.add_argument(
        "--vs", default="usd", dest="vs", help="Currency to display vs coin"
    )
    parser.add_argument(
        "-d", "--days", default=30, dest="days", help="Number of days to get data for"
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return pd.DataFrame(), ""

        df = coin.get_coin_market_chart(ns_parser.vs, ns_parser.days)
        df = df["price"].resample("1D").ohlc().ffill()
        df.columns = [
            "Open",
            "High",
            "Low",
            "Close",
        ]
        df.index.name = "date"
        return df, ns_parser.vs

    except SystemExit:
        print("")
        return pd.DataFrame(), ""
    except Exception as e:
        print(e, "\n")
        return pd.DataFrame(), ""


def display_info(coin: gecko.Coin, export: str) -> None:
    """Shows basic information about loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = wrap_text_in_df(coin.get_base_info, w=80)
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        df,
    )


def display_web(coin: gecko.Coin, export: str) -> None:
    """Shows found websites corresponding to loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coin.get_websites
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "web",
        df,
    )


def display_social(coin: gecko.Coin, export: str) -> None:
    """Shows social media corresponding to loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coin.get_social_media
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
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "social",
        df,
    )


def display_dev(coin: gecko.Coin, export: str) -> None:
    """Shows developers data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coin.get_developers_data
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
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dev",
        df,
    )


def display_ath(coin: gecko.Coin, currency: str, export: str) -> None:
    """Shows all time high data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency

    currency: str
        currency vs which coin ath will be displayed: usd or btc
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coin.get_all_time_high(currency=currency)
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ath",
        df,
    )


def display_atl(coin: gecko.Coin, currency: str, export: str) -> None:
    """Shows all time low data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency

    currency: str
        currency vs which coin ath will be displayed: usd or btc
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coin.get_all_time_low(currency=currency)
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "atl",
        df,
    )


def display_score(coin: gecko.Coin, export: str) -> None:
    """Shows different kind of scores for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file


    """
    df = coin.get_scores
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "score",
        df,
    )


def display_bc(coin: gecko.Coin, export: str) -> None:
    """Shows urls to blockchain explorers. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coin.get_blockchain_explorers
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
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "bc",
        df,
    )


def display_market(coin: gecko.Coin, export: str) -> None:
    """Shows market data for loaded coin. [Source: CoinGecko]

    Parameters
    ----------
    coin : gecko_coin.Coin
        Cryptocurrency
    export : str
        Export dataframe data to csv,json,xlsx file

    """

    df = coin.get_market_data
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

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "market",
        df,
    )
