""" pycoingecko_api """
__docformat__ = "numpy"

import argparse
from typing import List
import textwrap
import difflib
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from tabulate import tabulate
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
import gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_overview_model as gecko
import gamestonk_terminal.cryptocurrency.coingecko.pycoingecko_coin_model as gecko_coin
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import wrap_text_in_df

register_matplotlib_converters()

# Generate a list of valid coins to be checked against later
cg_api = CoinGeckoAPI()
coins = cg_api.get_coins()

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

        coin = gecko_coin.Coin(ns_parser.coin)
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


def chart(coin: gecko_coin.Coin, other_args: List[str]):
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


def ta(coin: gecko_coin.Coin, other_args: List[str]):
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
            return None, None

        df = coin.get_coin_market_chart(ns_parser.vs, ns_parser.days)
        return df, ns_parser.vs

    except SystemExit:
        print("")
        return None, None
    except Exception as e:
        print(e, "\n")
        return None, None


def info(coin: gecko_coin.Coin, other_args: List[str]):
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


def web(coin: gecko_coin.Coin, other_args: List[str]):
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


def social(coin: gecko_coin.Coin, other_args: List[str]):
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


def dev(coin: gecko_coin.Coin, other_args: List[str]):
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


def ath(coin: gecko_coin.Coin, other_args: List[str]):
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


def atl(coin: gecko_coin.Coin, other_args: List[str]):
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


def score(coin: gecko_coin.Coin, other_args: List[str]):
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


def bc(coin: gecko_coin.Coin, other_args: List[str]):
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


def market(coin: gecko_coin.Coin, other_args: List[str]):
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


def holdings_overview(other_args: List[str]):
    """Shows overview of public companies that holds ethereum or bitcoin from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="hold",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows overview of public companies that holds ethereum or bitcoin.
        You can find there most important metrics like:
        Total Bitcoin Holdings, Total Value (USD), Public Companies Bitcoin Dominance, Companies
        """,
    )
    parser.add_argument(
        "-c",
        "--coin",
        dest="coin",
        type=str,
        help="companies with ethereum or bitcoin",
        default="bitcoin",
        choices=["ethereum", "bitcoin"],
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_holdings_overview(endpoint=ns_parser.coin)
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

    except Exception as e:
        print(e, "\n")


def holdings_companies_list(other_args: List[str]):
    """Shows Ethereum/Bitcoin Holdings by Public Companies from www.coingecko.com

    Track publicly traded companies around the world that are buying ethereum as part of corporate treasury

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="hold_comp",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Track publicly traded companies around the world that
        are buying ethereum or bitcoin as part of corporate treasury:
        rank, company, ticker, country, total_btc, entry_value, today_value, pct_of_supply
        You can use additional flag --links to see urls to announcement about buying btc or eth by given company.
        In this case you will see only columns like rank, company, url
        """,
    )
    parser.add_argument(
        "-c",
        "--coin",
        dest="coin",
        type=str,
        help="companies with ethereum or bitcoin",
        default="bitcoin",
        choices=["ethereum", "bitcoin"],
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls. If you will use that flag you will see only rank, company, url columns",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_companies_assets(endpoint=ns_parser.coin)

        if ns_parser.links is True:
            df = df[["rank", "company", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

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

    except Exception as e:
        print(e, "\n")


def gainers(other_args: List[str]):
    """Shows Largest Gainers - coins which gain the most in given period from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="gainers",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows Largest Gainers - coins which gain the most in given period.
        You can use parameter --period to set which timeframe are you interested in. eg. 1h, 24h, 7d, 14d, 30d, 60d, 1y
        You can look on only top N number of records with --top,
        You can sort by rank, symbol, name, volume, price, change with --sort and also with --descend flag to set it
        to sort descending.
        There is --links flag, which will display one additional column you all urls for coins.
        """,
    )
    parser.add_argument(
        "-p",
        "--period",
        dest="period",
        type=str,
        help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
        default="1h",
        choices=["1h", "24h", "7d", "14d", "30d", "60d", "1y"],
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=int,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "symbol", "name", "volume", "price", "change"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls. If you will use that flag you will additional column with urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.sortby == "change":
            sortby = f"%change_{ns_parser.period}"
        else:
            sortby = ns_parser.sortby

        df = gecko.get_gainers_or_losers(
            period=ns_parser.period, typ="gainers"
        ).sort_values(by=sortby, ascending=ns_parser.descend)

        if not ns_parser.links:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def losers(other_args: List[str]):
    """Shows Largest Losers - coins which lost the most in given period of time from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="losers",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows Largest Losers - coins which price dropped the most in given period
        You can use parameter --period to set which timeframe are you interested in. eg. 1h, 24h, 7d, 14d, 30d, 60d, 1y
        You can look on only top N number of records with --top,
        You can sort by rank, symbol, name, volume, price, change with --sort and also with --descend flag
        to sort descending.
        Flag --links will display one additional column with all coingecko urls for listed coins.
        """,
    )
    parser.add_argument(
        "-p",
        "--period",
        dest="period",
        type=str,
        help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
        default="1h",
        choices=["1h", "24h", "7d", "14d", "30d", "60d", "1y"],
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: change",
        default="rank",
        choices=["rank", "symbol", "name", "volume", "price", "change"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls. If you will use that flag you will additional column with urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.sortby == "change":
            sortby = f"%change_{ns_parser.period}"
        else:
            sortby = ns_parser.sortby

        df = gecko.get_gainers_or_losers(
            period=ns_parser.period, typ="losers"
        ).sort_values(by=sortby, ascending=ns_parser.descend)

        if not ns_parser.links:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def discover(category: str, other_args: List[str]):
    """Discover coins by different categories
        - Most voted coins
        - Most popular coins
        - Recently added coins
        - Most positive sentiment coins

    Parameters
    ----------
    category: str
        one from list: [trending, most_voted, positive_sentiment, most_visited]
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog=f"{category}",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=f"""Discover {category} coins.
        Use --top parameter to display only top N number of records,
        You can sort by rank, name, price_btc, price_usd, using --sort parameter and also with --descend flag
        to sort descending.
        Flag --links will display one additional column with all coingecko urls for listed coins.
        {category} will display: rank, name, price_usd, price_btc
        """,
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "name", "price_usd", "price_btc"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls. If you will use that flag you will additional column with urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.discover_coins(category=category)
        df.index = df.index + 1
        df.reset_index(inplace=True)
        df.rename(columns={"index": "rank"}, inplace=True)

        df = df.sort_values(by=ns_parser.sortby, ascending=ns_parser.descend)

        if not ns_parser.links:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".5f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def news(other_args: List[str]):
    """Shows latest crypto news from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="news",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Shows latest crypto news from CoinGecko. "
        "You will see index, title, author, posted columns. "
        "You can sort by each of column above, using --sort parameter and also do it descending with --descend flag"
        "To display urls to news use --links flag.",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=int,
        help="top N number of news >=10",
        default=50,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: index",
        default="index",
        choices=["index", "title", "author", "posted"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls. If you will use that flag you will additional column with urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_news(n=ns_parser.top).sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        df["title"] = df["title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=50)) if isinstance(x, str) else x
        )

        if not ns_parser.links:
            df.drop("url", axis=1, inplace=True)
        else:
            df = df[["index", "url"]]

        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def categories(other_args: List[str]):
    """Shows top cryptocurrency categories by market capitalization from https://www.coingecko.com/en/categories

    The cryptocurrency category ranking is based on market capitalization.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="categories",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows top cryptocurrency categories by market capitalization. It includes categories like:
        stablecoins, defi, solana ecosystem, polkadot ecosystem and many others.
        "You can sort by each of column above, using --sort parameter and also do it descending with --descend flag"
        "To display urls to news use --links flag.",
        Displays: rank, name, change_1h, change_24h, change_7d, market_cap, volume_24h, n_of_coins""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number of news >=10",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "name",
            "change_1h",
            "change_24h",
            "change_7d",
            "market_cap",
            "volume_24h",
            "n_of_coins",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls. If you will use that flag you will additional column with urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_crypto_categories().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if not ns_parser.links:
            df.drop("url", axis=1, inplace=True)
        else:
            df = df[["rank", "name", "url"]]

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def recently_added(other_args: List[str]):
    """Shows recently added coins from "https://www.coingecko.com/en/coins/recently_added"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="recently",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows recently added coins on CoinGecko. You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, symbol, price, change_24h, change_1h, added with --sort
        and also with --descend flag to sort descending.
        Flag --links will display urls""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "name", "symbol", "price", "change_24h", "change_1h", "added"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_recently_added_coins().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["rank", "symbol", "added", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def stablecoins(other_args: List[str]):
    """Shows stablecoins data from "https://www.coingecko.com/en/stablecoins"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="stables",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows stablecoins by market capitalization.
        Stablecoins are cryptocurrencies that attempt to peg their market value to some external reference
        like the U.S. dollar or to a commodity's price such as gold.
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, symbol, price, change_24h, exchanges, market_cap, change_30d with --sort
        and also with --descend flag to sort descending.
        Flag --links will display stablecoins urls""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "name",
            "symbol",
            "price",
            "change_24h",
            "exchanges",
            "market_cap",
            "change_30d",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_stable_coins().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["rank", "name", "symbol", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def yfarms(other_args: List[str]):
    """Shows Top Yield Farming Pools by Value Locked from "https://www.coingecko.com/en/yield-farming"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="yfarms",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top Yield Farming Pools by Value Locked
        Yield farming, also referred to as liquidity mining, is a way to generate rewards with cryptocurrency holdings.
        In simple terms, it means locking up cryptocurrencies and getting rewards.
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, value_locked, return_year with --sort parameter
        and also with --descend flag to sort descending.""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="Top N of records. Default 20",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "name", "value_locked", "return_year"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_yield_farms()
        df = df.sort_values(by=ns_parser.sortby, ascending=ns_parser.descend)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def top_volume_coins(other_args: List[str]):
    """Shows Top 100 Coins by Trading Volume from "https://www.coingecko.com/en/yield-farming"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="top_volume",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top Coins by Trading Volume.
        You can display only top N number of coins with --top parameter.
        You can sort data by on of columns rank, name, symbol, price, change_1h, change_24h, change_7d , volume_24h ,
        market_cap with --sort parameter and also with --descend flag to sort descending.
        Displays columns: rank, name, symbol, price, change_1h, change_24h, change_7d , volume_24h ,market_cap""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="Top N of records. Default 20",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "name",
            "symbol",
            "price",
            "change_1h",
            "change_24h",
            "change_7d",
            "volume_24h",
            "market_cap",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_volume_coins().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def top_defi_coins(other_args: List[str]):
    """Shows Top 100 DeFi Coins by Market Capitalization from "https://www.coingecko.com/en/defi"
    DeFi or Decentralized Finance refers to financial services that are built
    on top of distributed networks with no central intermediaries.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_defi",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top DeFi Coins by Market Capitalization
        DeFi or Decentralized Finance refers to financial services that are built
        on top of distributed networks with no central intermediaries.
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, symbol, price, change_24h, change_1h, change_7d,
        volume_24h, market_cap with --sort and also with --descend flag to sort descending.
        Flag --links will display  urls""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "name",
            "symbol",
            "price",
            "change_1h",
            "change_24h",
            "change_7d",
            "volume_24h",
            "market_cap",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_defi_coins().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["rank", "name", "symbol", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")
    except Exception as e:
        print(e, "\n")


def top_dex(other_args: List[str]):
    """Shows Top Decentralized Exchanges on CoinGecko by Trading Volume from "https://www.coingecko.com/en/dex"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_dex",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows Top Decentralized Exchanges on CoinGecko by Trading Volume
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, volume_24h, n_coins, n_pairs, visits, most_traded, market_share_by_vol
        most_traded_pairs, market_share_by_volume with --sort and also with --descend flag to sort descending.
        Display columns:
             rank, name, volume_24h, n_coins, n_pairs, visits, most_traded, market_share_by_vol""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "name",
            "volume_24h",
            "n_coins",
            "visits",
            "most_traded",
            "market_share_by_vol",
            "n_pairs",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_dexes().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def top_nft(other_args: List[str]):
    """Shows Top 100 NFT Coins by Market Capitalization from "https://www.coingecko.com/en/nft"
    Top 100 NFT Coins by Market Capitalization
    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_nft",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top NFT Coins by Market Capitalization
        NFT (Non-fungible Token) refers to digital assets with unique characteristics.
        Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, symbol, price, change_24h, change_1h, change_7d,
        volume_24h, market_cap with --sort and also with --descend flag to sort descending.
        Flag --links will display urls
        Displays : rank, name, symbol, price, change_1h, change_24h, change_7d, market_cap, url""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "name",
            "symbol",
            "price",
            "change_1h",
            "change_24h",
            "change_7d",
            "volume_24h",
            "market_cap",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_nfts().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["rank", "name", "symbol", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".4f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def nft_of_the_day(other_args: List[str]):
    """Shows NFT of the day "https://www.coingecko.com/en/nft"

    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="nft_today",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows NFT of the day
        NFT (Non-fungible Token) refers to digital assets with unique characteristics.
        Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
        With nft_today command you will display:
            author, description, url, img url for NFT which was chosen on CoinGecko as a nft of the day.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_nft_of_the_day()
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

    except Exception as e:
        print(e, "\n")


def nft_market_status(other_args: List[str]):
    """Shows overview data of nft markets "https://www.coingecko.com/en/nft"

    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="nft_market",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows NFT market status
        NFT (Non-fungible Token) refers to digital assets with unique characteristics.
        Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
        Displays: NFT Market Cap, 24h Trading Volume, NFT Dominance vs Global market, Theta Network NFT Dominance
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_nft_market_status()
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

    except Exception as e:
        print(e, "\n")


def exchanges(other_args: List[str]):
    """Shows list of top exchanges from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="exchanges",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top Crypto Exchanges
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, trust_score, id, name, country, established, trade_volume_24h_btc with --sort
        and also with --descend flag to sort descending.
        Flag --links will display urls.
        Displays: rank, trust_score, id, name, country, established, trade_volume_24h_btc""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "trust_score",
            "id",
            "name",
            "country",
            "year_established",
            "trade_volume_24h_btc",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )
    parser.add_argument(
        "-l",
        "--links",
        dest="links",
        action="store_true",
        help="Flag to show urls",
        default=False,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_exchanges().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["rank", "name", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def platforms(other_args: List[str]):
    """Shows list of financial platforms from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="platforms",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top Crypto Financial Platforms in which you can borrow or lend your crypto.
        e.g Celsius, Nexo, Crypto.com, Aave and others.
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, category, centralized with --sort
        and also with --descend flag to sort descending.
        Displays: rank, name, category, centralized, website_url""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "name", "category", "centralized"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_financial_platforms().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def products(other_args: List[str]):
    """Shows list of financial products from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="products",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top Crypto Financial Products with which you can earn yield, borrow or lend your crypto.
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, platform, identifier, supply_rate_percentage, borrow_rate_percentage  with --sort
        and also with --descend flag to sort descending.
        Displays: rank, platform, identifier, supply_rate_percentage, borrow_rate_percentage""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "platform",
            "identifier",
            "supply_rate_percentage",
            "borrow_rate_percentage",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_finance_products().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )
        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def indexes(other_args: List[str]):
    """Shows list of crypto indexes from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="indexes",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows list of crypto indexes from CoinGecko.
        Each crypto index is made up of a selection of cryptocurrencies, grouped together and weighted by market cap.
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, id, market, last, is_multi_asset_composite with --sort
        and also with --descend flag to sort descending.
        Displays: rank, name, id, market, last, is_multi_asset_composite
        """,
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "name", "id", "market", "last", "is_multi_asset_composite"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_indexes().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def derivatives(other_args: List[str]):
    """Shows  list of crypto derivatives from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="derivatives",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows list of crypto derivatives from CoinGecko
        Crypto derivatives are secondary contracts or financial tools that derive their value from a primary
        underlying asset. In this case, the primary asset would be a cryptocurrency such as Bitcoin.
        The most popular crypto derivatives are crypto futures, crypto options, and perpetual contracts.
        You can look on only top N number of records with --top,
        You can sort by rank, market, symbol, price, pct_change_24h, contract_type, basis, spread,
        funding_rate, volume_24h with --sort and also with --descend flag to set it to sort descending.
        Displays:
            rank, market, symbol, price, pct_change_24h, contract_type, basis, spread, funding_rate, volume_24h""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=[
            "rank",
            "market",
            "symbol",
            "price",
            "pct_change_24h",
            "contract_type",
            "basis",
            "spread",
            "funding_rate",
            "volume_24h",
        ],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_derivatives().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def exchange_rates(other_args: List[str]):
    """Shows  list of crypto, fiats, commodity exchange rates from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="ex_rates",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows list of crypto, fiats, commodity exchange rates from CoinGecko
        You can look on only top N number of records with --top,
        You can sort by index,name,unit, value, type, and also use --descend flag to sort descending.""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: index",
        default="index",
        choices=["index", "name", "unit", "value", "type"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_exchange_rates().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )
        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def global_market_info(other_args: List[str]):
    """Shows global statistics about crypto from CoinGecko
        - market cap change
        - number of markets
        - icos
        - number of active crypto
        - market_cap_pct

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="global",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows global statistics about Crypto Market like:
        active_cryptocurrencies, upcoming_icos, ongoing_icos, ended_icos, markets, market_cap_change_percentage_24h,
        eth_market_cap_in_pct, btc_market_cap_in_pct, altcoin_market_cap_in_pct""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_global_info()
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

    except Exception as e:
        print(e, "\n")


def global_defi_info(other_args: List[str]):
    """Shows global statistics about Decentralized Finances from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="defi",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows global DeFi statistics
        DeFi or Decentralized Finance refers to financial services that are built
        on top of distributed networks with no central intermediaries.
        Displays metrics like:
            defi_market_cap, eth_market_cap, defi_to_eth_ratio, trading_volume_24h, defi_dominance, top_coin_name,
            top_coin_defi_dominance""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_global_defi_info()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def coin_list(other_args: List[str]):
    """Shows list of coins available on CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="coins",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Shows list of coins available on CoinGecko",
    )
    parser.add_argument(
        "-s",
        "--skip",
        default=0,
        dest="skip",
        help="Skip n of records",
        type=check_positive,
    )
    parser.add_argument(
        "-t",
        "--top",
        default=100,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )
    parser.add_argument("-l", "--letter", dest="letter", help="First letters", type=str)
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Search in column symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_coin_list()

        letter = ns_parser.letter
        if letter and isinstance(letter, str):
            if letter.isalpha():
                letter = letter.lower()
            df = df[df[ns_parser.key].str.startswith(letter)]

        try:
            df = df[ns_parser.skip : ns_parser.skip + ns_parser.top]
        except Exception:
            df = gecko.get_coin_list()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def find(other_args: List[str]):
    """Find similar coin by coin name,symbol or id.

    If you don't remember exact name or id of the Coin at CoinGecko,
    you can use this command to display coins with similar name, symbol or id to your search query.
    Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.
      -c, --coin stands for coin - you provide here your search query
      -k, --key it's a searching key. You can search by symbol, id or name of coin
      -t, --top it displays top N number of records.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="find",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at CoinGecko,
        you can use this command to display coins with similar name, symbol or id to your search query.
        Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
        It will search for coin that has similar name to polka and display top 25 matches.
        -c, --coin stands for coin - you provide here your search query
        -k, --key it's a searching key. You can search by symbol, id or name of coin
        -t, --top it displays top N number of records.""",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Symbol Name or Id of Coin",
        dest="coin",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Specify by which column you would like to search: symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )
    parser.add_argument(
        "-t",
        "--top",
        default=10,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        coins_df = gecko.get_coin_list()
        coins_list = coins_df[ns_parser.key].to_list()
        sim = difflib.get_close_matches(ns_parser.coin, coins_list, ns_parser.top)
        df = pd.Series(sim).to_frame().reset_index()
        df.columns = ["index", ns_parser.key]
        coins_df.drop("index", axis=1, inplace=True)
        df = df.merge(coins_df, on=ns_parser.key)
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")
