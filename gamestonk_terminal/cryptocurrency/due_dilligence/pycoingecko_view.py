""" coingecko due dilligence """
__docformat__ = "numpy"

import argparse
from typing import List

import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
import gamestonk_terminal.cryptocurrency.due_dilligence.pycoingecko_model as gecko
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import wrap_text_in_df

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
        required=True,
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


def chart(coin: gecko.Coin, other_args: List[str]):
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
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        plt.plot(df.index, df.price, "-ok", ms=2)
        plt.xlabel("Time")
        plt.xlim(df.index[0], df.index[-1])
        plt.ylabel("Price")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        plt.title(f"{coin.coin_symbol}/{df['currency'][0]}")
        plt.show()
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def ta(coin: gecko.Coin, other_args: List[str]):
    """Load data for Technical Analysis

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
        df = df[["price"]].rename(columns={"price": "Close"})
        df.index.name = "date"
        return df, ns_parser.vs

    except SystemExit:
        print("")
        return pd.DataFrame(), ""
    except Exception as e:
        print(e, "\n")
        return pd.DataFrame(), ""


def info(coin: gecko.Coin, other_args: List[str]):
    """Shows basic information about loaded coin

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
        prog="info",
        description="""
                        Shows basic information about loaded coin like:
                        id, name, symbol, asset_platform, description, contract_address,
                        market_cap_rank, public_interest_score, total_supply, max_supply,
                        price_change_percentage_24h, price_change_percentage_7d, price_change_percentage_30d,
                        current_price_btc, current_price_eth, current_price_usd
                        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = wrap_text_in_df(coin.base_info, w=80)
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def web(coin: gecko.Coin, other_args: List[str]):
    """Shows found websites corresponding to loaded coin

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
        prog="web",
        description="""Websites found for given Coin. You can find there urls to
                       homepage, forum, announcement site and others.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.websites
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def social(coin: gecko.Coin, other_args: List[str]):
    """Shows social media corresponding to loaded coin

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
        prog="social",
        description="""Shows social media corresponding to loaded coin. You can find there name of
                    telegram channel, urls to twitter, reddit, bitcointalk, facebook and discord.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.social_media
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def dev(coin: gecko.Coin, other_args: List[str]):
    """Shows developers data for loaded coin

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
        prog="dev",
        description="""Developers data for loaded coin. If the development data is available you can see
                       how the code development of given coin is going on.
                       There are some statistics that shows number of stars, forks, subscribers, pull requests,
                       commits, merges, contributors on github.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.developers_data
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def ath(coin: gecko.Coin, other_args: List[str]):
    """Shows all time high data for loaded coin

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
        prog="ath",
        description="""All time high data for loaded coin. You can find there most important metrics regarding
                    ath of coin price like:
                    current_price_btc, current_price_eth, current_price_usd, ath_btc, ath_eth, ath_usd,
                    ath_date_btc, ath_date_eth, ath_date_usd, ath_change_percentage_btc, ath_change_percentage_btc,
                    ath_change_percentage_eth, ath_change_percentage_usd""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.all_time_high
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def atl(coin: gecko.Coin, other_args: List[str]):
    """Shows all time low data for loaded coin

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
        prog="atl",
        description="""
                        All time low data for loaded coin. You can find there most important metrics regarding
                        atl of coin price like:
                        current_price_btc,  ,current_price_eth, current_price_usd, atl_btc, atl_eth, atl_usd,
                        atl_date_btc, atl_date_eth, atl_date_usd, atl_change_percentage_btc, atl_change_percentage_btc,
                        atl_change_percentage_eth,  atl_change_percentage_usd
                        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.all_time_low
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def score(coin: gecko.Coin, other_args: List[str]):
    """Shows different kind of scores for loaded coin

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
        prog="score",
        description="""
                        In this view you can find different kind of scores for loaded coin.
                        Those scores represents different rankings, sentiment metrics, some user stats and others.
                        coingecko_rank, coingecko_score, developer_score, community_score, liquidity_score,
                        sentiment_votes_up_percentage, sentiment_votes_down_percentage, public_interest_score,
                        facebook_likes, twitter_followers, reddit_average_posts_48h, reddit_average_comments_48h,
                        reddit_subscribers, reddit_accounts_active_48h, telegram_channel_user_count, alexa_rank,
                        bing_matches
                        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.scores
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def bc(coin: gecko.Coin, other_args: List[str]):
    """Shows urls to blockchain explorers

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
        prog="bc",
        description="""
                        Blockchain explorers URLs for loaded coin. Those are sites like etherescan.io or polkascan.io
                        in which you can see all blockchain data e.g. all txs, all tokens, all contracts...
                        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.blockchain_explorers
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")


def market(coin: gecko.Coin, other_args: List[str]):
    """Shows market data for loaded coin

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
        prog="market",
        description="""
                        Market data for loaded coin. There you find metrics like:
                        market_cap_rank, total_supply, max_supply, circulating_supply,
                        price_change_percentage_24h, price_change_percentage_7d, 'price_change_percentage_30d',
                        price_change_percentage_60d', 'price_change_percentage_1y', 'market_cap_change_24h',
                        market_cap_btc', 'market_cap_eth', 'market_cap_usd', 'total_volume_btc', 'total_volume_eth',
                        total_volume_usd', 'high_24h_btc', 'high_24h_eth', 'high_24h_usd', 'low_24h_btc', 'low_24h_eth',
                        low_24h_usd'
                        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        df = coin.market_data
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")
