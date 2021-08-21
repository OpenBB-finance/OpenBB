"""Terminal helper"""
__docformat__ = "numpy"
import hashlib
import os
import random
import subprocess
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import praw
import pyEX
import quandl
import requests
from alpha_vantage.timeseries import TimeSeries
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from colorama import Fore, Style
from prawcore.exceptions import ResponseException
from pyEX.common.exception import PyEXception
from tabulate import tabulate

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import thought_of_the_day as thought

# import git

# pylint: disable=no-member,too-many-branches,C0302


# pylint: disable=too-many-statements


def check_api_keys():
    """Check api keys and if they are supplied"""

    key_dict = {}
    if cfg.API_KEY_ALPHAVANTAGE == "REPLACE_ME":  # pragma: allowlist secret
        key_dict["ALPHA_VANTAGE"] = "Not defined"
    else:
        df = TimeSeries(
            key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
        ).get_intraday(symbol="AAPL")
        if df[0].empty:
            key_dict["ALPHA_VANTAGE"] = "defined, test failed"
        else:
            key_dict["ALPHA_VANTAGE"] = "defined, test passed"

    if cfg.API_KEY_FINANCIALMODELINGPREP == "REPLACE_ME":  # pragma: allowlist secret
        key_dict["FINANCIAL_MODELING_PREP"] = "Not defined"
    else:
        r = requests.get(
            f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"
        )
        if r.status_code in [403, 401]:
            key_dict["FINANCIAL_MODELING_PREP"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["FINANCIAL_MODELING_PREP"] = "defined, test passed"
        else:
            key_dict["FINANCIAL_MODELING_PREP"] = "defined, test inconclusive"

    if cfg.API_KEY_QUANDL == "REPLACE_ME":  # pragma: allowlist secret
        key_dict["QUANDL"] = "Not defined"
    else:
        try:
            quandl.save_key(cfg.API_KEY_QUANDL)
            quandl.get_table(
                "ZACKS/FC",
                paginate=True,
                ticker=["AAPL", "MSFT"],
                per_end_date={"gte": "2015-01-01"},
                qopts={"columns": ["ticker", "per_end_date"]},
            )
            key_dict["QUANDL"] = "defined, test passed"
        except quandl.errors.quandl_error.ForbiddenError:
            key_dict["QUANDL"] = "defined, test failed"

    if cfg.API_POLYGON_KEY == "REPLACE_ME":
        key_dict["POLYGON"] = "Not defined"
    else:
        r = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17?apiKey={cfg.API_POLYGON_KEY}"
        )
        if r.status_code in [403, 401]:
            key_dict["POLYGON"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["POLYGON"] = "defined, test passed"
        else:
            key_dict["POLYGON"] = "defined, test inconclusive"

    if cfg.API_FRED_KEY == "REPLACE_ME":
        key_dict["FRED"] = "Not defined"
    else:
        r = requests.get(
            f"https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key={cfg.API_FRED_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            key_dict["FRED"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["FRED"] = "defined, test passed"
        else:
            key_dict["FRED"] = "defined, test inconclusive"

    if cfg.API_NEWS_TOKEN == "REPLACE_ME":
        key_dict["NEWSAPI"] = "Not defined"
    else:
        r = requests.get(
            f"https://newsapi.org/v2/everything?q=keyword&apiKey={cfg.API_NEWS_TOKEN}"
        )
        if r.status_code in [401, 403]:
            key_dict["NEWSAPI"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["NEWSAPI"] = "defined, test passed"
        else:
            key_dict["NEWSAPI"] = "defined, test inconclusive"

    if cfg.TRADIER_TOKEN == "REPLACE_ME":
        key_dict["TRADIER"] = "Not defined"
    else:
        r = requests.get(
            "https://sandbox.tradier.com/v1/markets/quotes",
            params={"symbols": "AAPL"},
            headers={
                "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
                "Accept": "application/json",
            },
        )
        if r.status_code in [401, 403]:
            key_dict["TRADIER"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["TRADIER"] = "defined, test passed"
        else:
            key_dict["TRADIER"] = "defined, test inconclusive"

    if cfg.API_CMC_KEY == "REPLACE_ME":
        key_dict["COINMARKETCAP"] = "Not defined"
    else:
        cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)
        try:
            cmc.exchange_info()
            key_dict["COINMARKETCAP"] = "defined, test passed"
        except CoinMarketCapAPIError:
            key_dict["COINMARKETCAP"] = "defined, test failed"

    if cfg.API_FINNHUB_KEY == "REPLACE_ME":
        key_dict["FINNHUB"] = "Not defined"
    else:
        r = r = requests.get(
            f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={cfg.API_FINNHUB_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            key_dict["FINNHUB"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["FINNHUB"] = "defined, test passed"
        else:
            key_dict["FINNHUB"] = "defined, test inconclusive"

    if cfg.API_IEX_TOKEN == "REPLACE_ME":
        key_dict["IEXCLOUD"] = "Not defined"
    else:
        try:
            pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")
            key_dict["IEXCLOUD"] = "defined, test passed"
        except PyEXception:
            key_dict["IEXCLOUD"] = "defined, test failed"

    # Reddit
    reddit_keys = [
        cfg.API_REDDIT_CLIENT_ID,
        cfg.API_REDDIT_CLIENT_SECRET,
        cfg.API_REDDIT_USERNAME,
        cfg.API_REDDIT_PASSWORD,
        cfg.API_REDDIT_USER_AGENT,
    ]
    if "REPLACE_ME" in reddit_keys:
        key_dict["REDDIT"] = "Not defined"
    else:
        praw_api = praw.Reddit(
            client_id=cfg.API_REDDIT_CLIENT_ID,
            client_secret=cfg.API_REDDIT_CLIENT_SECRET,
            username=cfg.API_REDDIT_USERNAME,
            user_agent=cfg.API_REDDIT_USER_AGENT,
            password=cfg.API_REDDIT_PASSWORD,
        )

        try:
            praw_api.user.me()
            key_dict["REDDIT"] = "defined, test passed"
        except ResponseException:
            key_dict["REDDIT"] = "defined, test failed"

    # Twitter keys
    twitter_keys = [
        cfg.API_TWITTER_KEY,
        cfg.API_TWITTER_SECRET_KEY,
        cfg.API_TWITTER_BEARER_TOKEN,
    ]
    if "REPLACE_ME" in twitter_keys:
        key_dict["TWITTER"] = "Not defined"
    else:
        params = {
            "query": "(\\$AAPL) (lang:en)",
            "max_results": "10",
            "tweet.fields": "created_at,lang",
        }
        r = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            params=params,  # type: ignore
            headers={"authorization": "Bearer " + cfg.API_TWITTER_BEARER_TOKEN},
        )
        if r.status_code == 200:
            key_dict["TWITTER"] = "defined, test passed"
        elif r.status_code in [401, 403]:
            key_dict["TWITTER"] = "defined, test failed"
        else:
            key_dict["TWITTER"] = "defined, test inconclusive"

    # Robinhood keys
    rh_keys = [cfg.RH_USERNAME, cfg.RH_PASSWORD]
    if "REPLACE_ME" in rh_keys:
        key_dict["ROBINHOOD"] = "Not defined"
    else:
        key_dict["ROBINHOOD"] = "defined, not tested"
    # Degiro keys
    dg_keys = [cfg.DG_USERNAME, cfg.DG_PASSWORD, cfg.DG_TOTP_SECRET]
    if "REPLACE_ME" in dg_keys:
        key_dict["DEGIRO"] = "Not defined"
    else:
        key_dict["DEGIRO"] = "defined, not tested"
    # OANDA keys
    oanda_keys = [cfg.OANDA_TOKEN, cfg.OANDA_ACCOUNT]
    if "REPLACE_ME" in oanda_keys:
        key_dict["OANDA"] = "Not defined"
    else:
        key_dict["OANDA"] = "defined, not tested"
    # Binance keys
    bn_keys = [cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET]
    if "REPLACE_ME" in bn_keys:
        key_dict["BINANCE"] = "Not defined"
    else:
        key_dict["BINANCE"] = "defined, not tested"

    # SentimentInvestor keys
    si_keys = [cfg.API_SENTIMENTINVESTOR_KEY, cfg.API_SENTIMENTINVESTOR_TOKEN]
    if "REPLACE_ME" in si_keys:
        key_dict["SENTIMENT_INVESTOR"] = "Not defined"
    else:
        account = requests.get(
            f"https://api.sentimentinvestor.com/v4/account"
            f"?token={cfg.API_SENTIMENTINVESTOR_TOKEN}&key={cfg.API_SENTIMENTINVESTOR_KEY}"
        )
        if account.ok and account.json().get("success", False):
            key_dict["SENTIMENT_INVESTOR"] = "Defined, test passed"
        else:
            key_dict["SENTIMENT_INVESTOR"] = "Defined, test unsuccessful"

    print(
        tabulate(
            pd.DataFrame(key_dict.items()),
            showindex=False,
            headers=[],
            tablefmt="fancy_grid",
        ),
        "\n",
    )


def print_goodbye():
    """Prints a goodbye message when quitting the terminal"""
    goodbye_msg = [
        "An informed ape, is a strong ape. ",
        "Remember that stonks only go up. ",
        "Diamond hands. ",
        "Apes together strong. ",
        "This is our way. ",
        "Keep the spacesuit ape, we haven't reached the moon yet. ",
        "I am not a cat. I'm an ape. ",
        "We like the terminal. ",
    ]

    goodbye_hr = datetime.now().hour
    if goodbye_hr < 5:
        goodbye_msg_time = "Go get some rest soldier!"
    elif goodbye_hr < 11:
        goodbye_msg_time = "Rise and shine baby!"
    elif goodbye_hr < 17:
        goodbye_msg_time = "Enjoy your day!"
    elif goodbye_hr < 23:
        goodbye_msg_time = "Tomorrow's another day!"
    else:
        goodbye_msg_time = "Go get some rest soldier!"

    print(
        goodbye_msg[random.randint(0, len(goodbye_msg) - 1)] + goodbye_msg_time + "\n"
    )


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def update_terminal():
    """Updates the terminal by running git pull in the directory.  Runs poetry install if needed"""
    poetry_hash = sha256sum("poetry.lock")

    completed_process = subprocess.run("git pull", shell=True, check=False)
    if completed_process.returncode != 0:
        return completed_process.returncode

    new_poetry_hash = sha256sum("poetry.lock")

    if poetry_hash == new_poetry_hash:
        print("Great, seems like poetry hasn't been updated!")
        return completed_process.returncode
    print(
        "Seems like more modules have been added, grab a coke, this may take a while."
    )

    completed_process = subprocess.run("poetry install", shell=True, check=False)
    if completed_process.returncode != 0:
        return completed_process.returncode

    return 0


def about_us():
    """Prints an about us section"""
    print(
        f"\n{Fore.GREEN}Thanks for using Gamestonk Terminal. This is our way!{Style.RESET_ALL}\n"
        "\n"
        f"{Fore.CYAN}Join our community on discord: {Style.RESET_ALL}https://discord.gg/Up2QGbMKHY\n"
        f"{Fore.CYAN}Follow our twitter for updates: {Style.RESET_ALL}https://twitter.com/gamestonkt\n"
        f"{Fore.CYAN}Access our landing page: {Style.RESET_ALL}https://gamestonkterminal.vercel.app\n"
        "\n"
        f"{Fore.YELLOW}Author:{Style.RESET_ALL} DidierRLopes\n"
        f"{Fore.YELLOW}Main Devs:{Style.RESET_ALL} jmaslek, aia\n"
        "\n"
        f"{Fore.YELLOW}Main Contributors:{Style.RESET_ALL}\n"
        f"{Fore.MAGENTA}Working towards a GUI using Qt:{Style.RESET_ALL} piiq, hinxx\n"
        f"{Fore.MAGENTA}Working on our landing page:{Style.RESET_ALL} jose-donato, crspy, martiaaz\n"
        f"{Fore.MAGENTA}Managing Twitter account:{Style.RESET_ALL} Meghan Hone\n"
        f"{Fore.MAGENTA}Responsible by developing Forex menu:{Style.RESET_ALL} alokan\n"
        f"{Fore.MAGENTA}Degiro's integration:{Style.RESET_ALL} Chavithra, Deel18\n"
        f"{Fore.MAGENTA}Preset screeners:{Style.RESET_ALL} Traceabl3\n"
        "\n"
        f"{Fore.YELLOW}Partnerships:{Style.RESET_ALL}\n"
        f"{Fore.CYAN}FinBrain: {Style.RESET_ALL}https://finbrain.tech\n"
        f"{Fore.CYAN}Quiver Quantitative: {Style.RESET_ALL}https://www.quiverquant.com\n"
        f"{Fore.CYAN}Ops.Syncretism: {Style.RESET_ALL}https://ops.syncretism.io/api.html\n"
        f"{Fore.CYAN}SentimentInvestor: {Style.RESET_ALL}https://sentimentinvestor.com\n"
        f"\n{Fore.RED}"
        "DISCLAIMER: Trading in financial instruments involves high risks including the risk of losing some, "
        "or all, of your investment amount, and may not be suitable for all investors. Before deciding to trade in "
        "financial instrument you should be fully informed of the risks and costs associated with trading the financial "
        "markets, carefully consider your investment objectives, level of experience, and risk appetite, and seek "
        "professional advice where needed. The data contained in Gamestonk Terminal (GST) is not necessarily accurate. "
        "GST and any provider of the data contained in this website will not accept liability for any loss or damage "
        "as a result of your trading, or your reliance on the information displayed."
        f"\n{Style.RESET_ALL}"
    )


def bootup():
    # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607
    if sys.platform == "win32":
        os.system("")

    try:
        if os.name == "nt":
            # pylint: disable=E1101
            sys.stdin.reconfigure(encoding="utf-8")
            # pylint: disable=E1101
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception as e:
        print(e, "\n")

    # Print first welcome message and help
    print("\nWelcome to Gamestonk Terminal Beta")

    # The commit has was commented out because the terminal was crashing due to git import for multiple users
    # ({str(git.Repo('.').head.commit)[:7]})

    if gtff.ENABLE_THOUGHTS_DAY:
        print("-------------------")
        try:
            thought.get_thought_of_the_day()
        except Exception as e:
            print(e)
        print("")


def reset():
    """Resets the terminal.  Allows for checking code or keys without quitting"""
    print("resetting...")
    plt.close("all")
    completed_process = subprocess.run("python terminal.py", shell=True, check=False)
    if completed_process.returncode != 0:
        completed_process = subprocess.run(
            "python3 terminal.py", shell=True, check=False
        )
        if completed_process.returncode != 0:
            print("Unfortunately, resetting wasn't possible!\n")

    return completed_process.returncode
