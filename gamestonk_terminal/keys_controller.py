"""Keys Controller Module"""
__docformat__ = "numpy"

import os
import argparse
import logging
from typing import List, Dict
from pathlib import Path
import dotenv

import praw
import pyEX
import quandl
import requests
from alpha_vantage.timeseries import TimeSeries
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from prawcore.exceptions import ResponseException
from pyEX.common.exception import PyEXception

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from gamestonk_terminal.cryptocurrency.coinbase_helpers import (
    CoinbaseProAuth,
    make_coinbase_request,
)
from gamestonk_terminal import config_terminal as cfg

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class KeysController(BaseController):
    """Keys Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "av",
        "fmp",
        "quandl",
        "polygon",
        "fred",
        "news",
        "tradier",
        "cmc",
        "finhub",
        "iex",
        "reddit",
        "twitter",
        "rh",
        "degiro",
        "oanda",
        "binance",
        "bitquery",
        "si",
        "cb",
        "wa",
        "glassnode",
        "coinglass",
        "cpanic",
        "ethplorer",
    ]
    PATH = "/keys/"
    key_dict: Dict = {}
    cfg_dict: Dict = {}
    env_file = ".env"
    env_files = [f for f in os.listdir() if f.endswith(".env")]
    if env_files:
        env_file = env_files[0]
        dotenv.load_dotenv(env_file)
    else:
        # create env file
        Path(".env")

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)
        self.check_keys_status()

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def check_av_key(self, show_output: bool = False) -> None:
        """Check Alpha Vantage key"""
        self.cfg_dict["ALPHA_VANTAGE"] = "av"
        if cfg.API_KEY_ALPHAVANTAGE == "REPLACE_ME":  # pragma: allowlist secret
            self.key_dict["ALPHA_VANTAGE"] = "not defined"
        else:
            df = TimeSeries(
                key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
            ).get_intraday(symbol="AAPL")
            if df[0].empty:
                self.key_dict["ALPHA_VANTAGE"] = "defined, test failed"
            else:
                self.key_dict["ALPHA_VANTAGE"] = "defined, test passed"

        if show_output:
            console.print(self.key_dict["ALPHA_VANTAGE"] + "\n")

    def check_fmp_key(self, show_output: bool = False) -> None:
        """Check Financial Modeling Prep key"""
        self.cfg_dict["FINANCIAL_MODELING_PREP"] = "fmp"
        if (
            cfg.API_KEY_FINANCIALMODELINGPREP
            == "REPLACE_ME"  # pragma: allowlist secret
        ):  # pragma: allowlist secret
            self.key_dict["FINANCIAL_MODELING_PREP"] = "not defined"
        else:
            r = requests.get(
                f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"
            )
            if r.status_code in [403, 401]:
                self.key_dict["FINANCIAL_MODELING_PREP"] = "defined, test failed"
            elif r.status_code == 200:
                self.key_dict["FINANCIAL_MODELING_PREP"] = "defined, test passed"
            else:
                self.key_dict["FINANCIAL_MODELING_PREP"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["FINANCIAL_MODELING_PREP"] + "\n")

    def check_quandl_key(self, show_output: bool = False) -> None:
        """Check Quandl key"""
        self.cfg_dict["QUANDL"] = "quandl"
        if cfg.API_KEY_QUANDL == "REPLACE_ME":  # pragma: allowlist secret
            self.key_dict["QUANDL"] = "not defined"
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
                self.key_dict["QUANDL"] = "defined, test passed"
            except Exception as _:  # noqa: F841
                self.key_dict["QUANDL"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["QUANDL"] + "\n")

    def check_polygon_key(self, show_output: bool = False) -> None:
        """Check Polygon key"""
        self.cfg_dict["POLYGON"] = "polygon"
        if cfg.API_POLYGON_KEY == "REPLACE_ME":
            self.key_dict["POLYGON"] = "not defined"
        else:
            r = requests.get(
                "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17"
                f"?apiKey={cfg.API_POLYGON_KEY}"
            )
            if r.status_code in [403, 401]:
                self.key_dict["POLYGON"] = "defined, test failed"
            elif r.status_code == 200:
                self.key_dict["POLYGON"] = "defined, test passed"
            else:
                self.key_dict["POLYGON"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["POLYGON"] + "\n")

    def check_fred_key(self, show_output: bool = False) -> None:
        """Check FRED key"""
        self.cfg_dict["FRED"] = "fred"
        if cfg.API_FRED_KEY == "REPLACE_ME":
            self.key_dict["FRED"] = "not defined"
        else:
            r = requests.get(
                f"https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key={cfg.API_FRED_KEY}"
            )
            if r.status_code in [403, 401, 400]:
                self.key_dict["FRED"] = "defined, test failed"
            elif r.status_code == 200:
                self.key_dict["FRED"] = "defined, test passed"
            else:
                self.key_dict["FRED"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["FRED"] + "\n")

    def check_news_key(self, show_output: bool = False) -> None:
        """Check News API key"""
        self.cfg_dict["NEWSAPI"] = "news"
        if cfg.API_NEWS_TOKEN == "REPLACE_ME":
            self.key_dict["NEWSAPI"] = "not defined"
        else:
            r = requests.get(
                f"https://newsapi.org/v2/everything?q=keyword&apiKey={cfg.API_NEWS_TOKEN}"
            )
            if r.status_code in [401, 403]:
                self.key_dict["NEWSAPI"] = "defined, test failed"
            elif r.status_code == 200:
                self.key_dict["NEWSAPI"] = "defined, test passed"
            else:
                self.key_dict["NEWSAPI"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["NEWSAPI"] + "\n")

    def check_tradier_key(self, show_output: bool = False) -> None:
        """Check Tradier key"""
        self.cfg_dict["TRADIER"] = "tradier"
        if cfg.TRADIER_TOKEN == "REPLACE_ME":
            self.key_dict["TRADIER"] = "not defined"
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
                self.key_dict["TRADIER"] = "defined, test failed"
            elif r.status_code == 200:
                self.key_dict["TRADIER"] = "defined, test passed"
            else:
                self.key_dict["TRADIER"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["TRADIER"] + "\n")

    def check_cmc_key(self, show_output: bool = False) -> None:
        """Check Coinmarketcap key"""
        self.cfg_dict["COINMARKETCAP"] = "cmc"
        if cfg.API_CMC_KEY == "REPLACE_ME":
            self.key_dict["COINMARKETCAP"] = "not defined"
        else:
            cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)
            try:
                cmc.exchange_info()
                self.key_dict["COINMARKETCAP"] = "defined, test passed"
            except CoinMarketCapAPIError:
                self.key_dict["COINMARKETCAP"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["COINMARKETCAP"] + "\n")

    def check_finhub_key(self, show_output: bool = False) -> None:
        """Check Finhub key"""
        self.cfg_dict["FINNHUB"] = "finhub"
        if cfg.API_FINNHUB_KEY == "REPLACE_ME":
            self.key_dict["FINNHUB"] = "not defined"
        else:
            r = r = requests.get(
                f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={cfg.API_FINNHUB_KEY}"
            )
            if r.status_code in [403, 401, 400]:
                self.key_dict["FINNHUB"] = "defined, test failed"
            elif r.status_code == 200:
                self.key_dict["FINNHUB"] = "defined, test passed"
            else:
                self.key_dict["FINNHUB"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["FINNHUB"] + "\n")

    def check_iex_key(self, show_output: bool = False) -> None:
        """Check IEX Cloud key"""
        self.cfg_dict["IEXCLOUD"] = "iex"
        if cfg.API_IEX_TOKEN == "REPLACE_ME":
            self.key_dict["IEXCLOUD"] = "not defined"
        else:
            try:
                pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")
                self.key_dict["IEXCLOUD"] = "defined, test passed"
            except PyEXception:
                self.key_dict["IEXCLOUD"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["IEXCLOUD"] + "\n")

    def check_reddit_key(self, show_output: bool = False) -> None:
        """Check Reddit key"""
        self.cfg_dict["REDDIT"] = "reddit"
        reddit_keys = [
            cfg.API_REDDIT_CLIENT_ID,
            cfg.API_REDDIT_CLIENT_SECRET,
            cfg.API_REDDIT_USERNAME,
            cfg.API_REDDIT_PASSWORD,
            cfg.API_REDDIT_USER_AGENT,
        ]
        if "REPLACE_ME" in reddit_keys:
            self.key_dict["REDDIT"] = "not defined"
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
                self.key_dict["REDDIT"] = "defined, test passed"
            except ResponseException:
                self.key_dict["REDDIT"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["REDDIT"] + "\n")

    def check_twitter_key(self, show_output: bool = False) -> None:
        """Check Twitter key"""
        self.cfg_dict["TWITTER"] = "twitter"
        twitter_keys = [
            cfg.API_TWITTER_KEY,
            cfg.API_TWITTER_SECRET_KEY,
            cfg.API_TWITTER_BEARER_TOKEN,
        ]
        if "REPLACE_ME" in twitter_keys:
            self.key_dict["TWITTER"] = "not defined"
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
                self.key_dict["TWITTER"] = "defined, test passed"
            elif r.status_code in [401, 403]:
                self.key_dict["TWITTER"] = "defined, test failed"
            else:
                self.key_dict["TWITTER"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["TWITTER"] + "\n")

    def check_rh_key(self, show_output: bool = False) -> None:
        """Check Robinhood key"""
        self.cfg_dict["ROBINHOOD"] = "rh"
        rh_keys = [cfg.RH_USERNAME, cfg.RH_PASSWORD]
        if "REPLACE_ME" in rh_keys:
            self.key_dict["ROBINHOOD"] = "not defined"
        else:
            self.key_dict["ROBINHOOD"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["ROBINHOOD"] + "\n")

    def check_degiro_key(self, show_output: bool = False) -> None:
        """Check Degiro key"""
        self.cfg_dict["DEGIRO"] = "degiro"
        dg_keys = [cfg.DG_USERNAME, cfg.DG_PASSWORD, cfg.DG_TOTP_SECRET]
        if "REPLACE_ME" in dg_keys:
            self.key_dict["DEGIRO"] = "not defined"
        else:
            self.key_dict["DEGIRO"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["DEGIRO"] + "\n")

    def check_oanda_key(self, show_output: bool = False) -> None:
        """Check Oanda key"""
        self.cfg_dict["OANDA"] = "oanda"
        oanda_keys = [cfg.OANDA_TOKEN, cfg.OANDA_ACCOUNT]
        if "REPLACE_ME" in oanda_keys:
            self.key_dict["OANDA"] = "not defined"
        else:
            self.key_dict["OANDA"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["OANDA"] + "\n")

    def check_binance_key(self, show_output: bool = False) -> None:
        """Check Binance key"""
        self.cfg_dict["BINANCE"] = "binance"
        bn_keys = [cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET]
        if "REPLACE_ME" in bn_keys:
            self.key_dict["BINANCE"] = "not defined"
        else:
            self.key_dict["BINANCE"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["BINANCE"] + "\n")

    def check_bitquery_key(self, show_output: bool = False) -> None:
        """Check Bitquery key"""
        self.cfg_dict["BITQUERY"] = "bitquery"
        bitquery = cfg.API_BITQUERY_KEY
        if "REPLACE_ME" in bitquery:
            self.key_dict["BITQUERY"] = "not defined"
        else:
            headers = {"x-api-key": cfg.API_BITQUERY_KEY}
            query = """
            {
            ethereum {
            dexTrades(options: {limit: 10, desc: "count"}) {
                count
                protocol
            }}}
            """
            r = requests.post(
                "https://graphql.bitquery.io", json={"query": query}, headers=headers
            )
            if r.status_code == 200:
                self.key_dict["BITQUERY"] = "defined, test passed"
            else:
                self.key_dict["BITQUERY"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["BITQUERY"] + "\n")

    def check_si_key(self, show_output: bool = False) -> None:
        """Check Sentiment Investor key"""
        self.cfg_dict["SENTIMENT_INVESTOR"] = "si"
        si_keys = [cfg.API_SENTIMENTINVESTOR_TOKEN]
        if "REPLACE_ME" in si_keys:
            self.key_dict["SENTIMENT_INVESTOR"] = "not defined"
        else:
            account = requests.get(
                f"https://api.sentimentinvestor.com/v1/trending"
                f"?token={cfg.API_SENTIMENTINVESTOR_TOKEN}"
            )
            if account.ok and account.json().get("success", False):
                self.key_dict["SENTIMENT_INVESTOR"] = "defined, test passed"
            else:
                self.key_dict["SENTIMENT_INVESTOR"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["SENTIMENT_INVESTOR"] + "\n")

    def check_coinbase_key(self, show_output: bool = False) -> None:
        """Check Coinbase key"""
        self.cfg_dict["COINBASE"] = "cb"
        if "REPLACE_ME" in [
            cfg.API_COINBASE_KEY,
            cfg.API_COINBASE_SECRET,
            cfg.API_COINBASE_PASS_PHRASE,
        ]:
            self.key_dict["COINBASE"] = "not defined"
        else:
            auth = CoinbaseProAuth(
                cfg.API_COINBASE_KEY,
                cfg.API_COINBASE_SECRET,
                cfg.API_COINBASE_PASS_PHRASE,
            )
            resp = make_coinbase_request("/accounts", auth=auth)
            if not resp:
                self.key_dict["COINBASE"] = "defined, test unsuccessful"
            else:
                self.key_dict["COINBASE"] = "defined, test passed"

        if show_output:
            console.print(self.key_dict["COINBASE"] + "\n")

    def check_walert_key(self, show_output: bool = False) -> None:
        """Check Walert key"""
        self.cfg_dict["WHALE_ALERT"] = "wa"
        if "REPLACE_ME" == cfg.API_WHALE_ALERT_KEY:
            self.key_dict["WHALE_ALERT"] = "not defined"
        else:
            url = (
                "https://api.whale-alert.io/v1/transactions?api_key="
                + cfg.API_WHALE_ALERT_KEY
            )
            response = requests.get(url)

            if not 200 <= response.status_code < 300:
                self.key_dict["WHALE_ALERT"] = "defined, test unsuccessful"
            try:
                self.key_dict["WHALE_ALERT"] = "defined, test passed"
            except Exception:
                self.key_dict["WHALE_ALERT"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["WHALE_ALERT"] + "\n")

    def check_glassnode_key(self, show_output: bool = False) -> None:
        """Check glassnode key"""
        self.cfg_dict["GLASSNODE"] = "glassnode"
        if "REPLACE_ME" == cfg.API_GLASSNODE_KEY:
            self.key_dict["GLASSNODE"] = "not defined"
        else:
            url = "https://api.glassnode.com/v1/metrics/market/price_usd_close"

            parameters = {
                "api_key": cfg.API_GLASSNODE_KEY,
                "a": "BTC",
                "i": "24h",
                "s": str(1_614_556_800),
                "u": str(1_641_227_783_561),
            }

            r = requests.get(url, params=parameters)
            if r.status_code == 200:
                self.key_dict["GLASSNODE"] = "defined, test passed"
            else:
                self.key_dict["GLASSNODE"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["GLASSNODE"] + "\n")

    def check_coinglass_key(self, show_output: bool = False) -> None:
        """Check coinglass key"""
        self.cfg_dict["COINGLASS"] = "coinglass"
        if "REPLACE_ME" == cfg.API_COINGLASS_KEY:
            self.key_dict["COINGLASS"] = "not defined"
        else:
            url = "https://open-api.coinglass.com/api/pro/v1/futures/openInterest/chart?&symbol=BTC&interval=0"

            headers = {"coinglassSecret": cfg.API_COINGLASS_KEY}

            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:
                self.key_dict["COINGLASS"] = "defined, test passed"
            else:
                self.key_dict["COINGLASS"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["COINGLASS"] + "\n")

    def check_cpanic_key(self, show_output: bool = False) -> None:
        """Check cpanic key"""
        self.cfg_dict["CRYPTO_PANIC"] = "cpanic"
        if "REPLACE_ME" == cfg.API_CRYPTO_PANIC_KEY:
            self.key_dict["CRYPTO_PANIC"] = "not defined"
        else:
            crypto_panic_url = f"https://cryptopanic.com/api/v1/posts/?auth_token={cfg.API_CRYPTO_PANIC_KEY}&kind=all"
            response = requests.get(crypto_panic_url)

            if not 200 <= response.status_code < 300:
                self.key_dict["CRYPTO_PANIC"] = "defined, test unsuccessful"
            try:
                self.key_dict["CRYPTO_PANIC"] = "defined, test passed"
            except Exception as _:  # noqa: F841
                self.key_dict["CRYPTO_PANIC"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["COINGLASS"] + "\n")

    def check_ethplorer_key(self, show_output: bool = False) -> None:
        """Check ethplorer key"""
        self.cfg_dict["ETHPLORER"] = "ethplorer"
        if "REPLACE_ME" == cfg.API_ETHPLORER_KEY:
            self.key_dict["ETHPLORER"] = "not defined"
        else:
            ethplorer_url = "https://api.ethplorer.io/getTokenInfo/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984?apiKey="
            ethplorer_url += cfg.API_ETHPLORER_KEY
            response = requests.get(ethplorer_url)
            try:
                if response.status_code == 200:
                    self.key_dict["ETHPLORER"] = "defined, test passed"
                else:
                    self.key_dict["ETHPLORER"] = "defined, test unsuccessful"
            except Exception as _:  # noqa: F841
                self.key_dict["ETHPLORER"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["ETHPLORER"] + "\n")

    def check_keys_status(self) -> None:
        """Check keys status"""
        self.check_av_key()
        self.check_fmp_key()
        self.check_quandl_key()
        self.check_polygon_key()
        self.check_fred_key()
        self.check_news_key()
        self.check_tradier_key()
        self.check_cmc_key()
        self.check_finhub_key()
        self.check_iex_key()
        self.check_reddit_key()
        self.check_twitter_key()
        self.check_rh_key()
        self.check_degiro_key()
        self.check_oanda_key()
        self.check_binance_key()
        self.check_bitquery_key()
        self.check_si_key()
        self.check_coinbase_key()
        self.check_walert_key()
        self.check_glassnode_key()
        self.check_coinglass_key()
        self.check_cpanic_key()
        self.check_ethplorer_key()

    def print_help(self):
        """Print help"""
        self.check_keys_status()
        help_text = "\n[info]Set API keys through environment variables:[/info]\n"
        for k, v in self.key_dict.items():
            cmd_name = self.cfg_dict[k]
            c = "red"
            if v == "defined, test passed":
                c = "green"
            elif v == "defined, test inconclusive":
                c = "yellow"
            elif v == "not defined":
                c = "grey30"
            help_text += f"   [cmds]{cmd_name}[/cmds] {(20 - len(cmd_name)) * ' '}"
            help_text += f" [{c}] {k} {(25 - len(k)) * ' '} {v} [/{c}]\n"

        console.print(text=help_text, menu="Keys")

    def call_av(self, other_args: List[str]):
        """Process av command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="av",
            description="Set Alpha Vantage API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_KEY_ALPHAVANTAGE"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_KEY_ALPHAVANTAGE", ns_parser.key)
            cfg.API_KEY_ALPHAVANTAGE = ns_parser.key
            self.check_av_key(show_output=True)

    def call_fmp(self, other_args: List[str]):
        """Process fmp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fmp",
            description="Set Financial Modeling Prep API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_KEY_FINANCIALMODELINGPREP"] = ns_parser.key
            dotenv.set_key(
                self.env_file, "GT_API_KEY_FINANCIALMODELINGPREP", ns_parser.key
            )
            cfg.API_KEY_FINANCIALMODELINGPREP = ns_parser.key
            self.check_fmp_key(show_output=True)

    def call_quandl(self, other_args: List[str]):
        """Process quandl command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quandl",
            description="Set Quandl API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_KEY_QUANDL"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_KEY_QUANDL", ns_parser.key)
            cfg.API_KEY_QUANDL = ns_parser.key
            self.check_quandl_key(show_output=True)

    def call_polygon(self, other_args: List[str]):
        """Process polygon command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="polygon",
            description="Set Polygon API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_POLYGON_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_POLYGON_KEY", ns_parser.key)
            cfg.API_POLYGON_KEY = ns_parser.key
            self.check_polygon_key(show_output=True)

    def call_fred(self, other_args: List[str]):
        """Process FRED command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fred",
            description="Set FRED API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_FRED_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_FRED_KEY", ns_parser.key)
            cfg.API_FRED_KEY = ns_parser.key
            self.check_fred_key(show_output=True)

    def call_news(self, other_args: List[str]):
        """Process News API command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="news",
            description="Set News API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_NEWS_TOKEN"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_NEWS_TOKEN", ns_parser.key)
            cfg.API_NEWS_TOKEN = ns_parser.key
            self.check_news_key(show_output=True)

    def call_tradier(self, other_args: List[str]):
        """Process Tradier API command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tradier",
            description="Set Tradier API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_TRADIER_TOKEN"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_TRADIER_TOKEN", ns_parser.key)
            cfg.TRADIER_TOKEN = ns_parser.key
            self.check_tradier_key(show_output=True)

    def call_cmc(self, other_args: List[str]):
        """Process CoinMarketCap API command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cmc",
            description="Set CMC API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_CMC_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_CMC_KEY", ns_parser.key)
            cfg.API_CMC_KEY = ns_parser.key
            self.check_cmc_key(show_output=True)

    def call_finhub(self, other_args: List[str]):
        """Process Finhub API command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="finhub",
            description="Set Finhub API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_FINNHUB_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_FINNHUB_KEY", ns_parser.key)
            cfg.API_FINNHUB_KEY = ns_parser.key
            self.check_finhub_key(show_output=True)

    def call_iex(self, other_args: List[str]):
        """Process iex command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="iex",
            description="Set IEX Cloud API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_IEX_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_IEX_KEY", ns_parser.key)
            cfg.API_IEX_TOKEN = ns_parser.key
            self.check_iex_key(show_output=True)

    def call_reddit(self, other_args: List[str]):
        """Process reddit command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="reddit",
            description="Set Reddit API key.",
        )
        parser.add_argument(
            "-i",
            "--id",
            type=str,
            dest="client_id",
            help="Client ID",
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="client_secret",
            help="Client Secret",
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            dest="username",
            help="Username",
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="Password",
        )
        parser.add_argument(
            "-a",
            "--agent",
            type=str,
            dest="user_agent",
            help="User agent",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_REDDIT_CLIENT_ID"] = ns_parser.client_id
            dotenv.set_key(
                self.env_file, "GT_API_REDDIT_CLIENT_ID", ns_parser.client_id
            )
            cfg.API_REDDIT_CLIENT_ID = ns_parser.client_id

            os.environ["GT_API_REDDIT_CLIENT_SECRET"] = ns_parser.client_secret
            dotenv.set_key(
                self.env_file, "GT_API_REDDIT_CLIENT_SECRET", ns_parser.client_secret
            )
            cfg.API_REDDIT_CLIENT_SECRET = ns_parser.client_secret

            os.environ["GT_API_REDDIT_PASSWORD"] = ns_parser.username
            dotenv.set_key(self.env_file, "GT_API_REDDIT_PASSWORD", ns_parser.username)
            cfg.API_REDDIT_USERNAME = ns_parser.username

            os.environ["GT_API_REDDIT_CLIENT_ID"] = ns_parser.password
            dotenv.set_key(self.env_file, "GT_API_REDDIT_CLIENT_ID", ns_parser.password)
            cfg.API_REDDIT_PASSWORD = ns_parser.password

            os.environ["GT_API_REDDIT_USER_AGENT"] = ns_parser.user_agent
            dotenv.set_key(
                self.env_file, "GT_API_REDDIT_USER_AGENT", ns_parser.user_agent
            )
            cfg.API_REDDIT_USER_AGENT = ns_parser.user_agent

            self.check_reddit_key(show_output=True)

    def call_twitter(self, other_args: List[str]):
        """Process twitter command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="twitter",
            description="Set Twitter API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="Key",
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="secret_key",
            help="Secret key",
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            dest="bearer_token",
            help="Bearer token",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_TWITTER_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_TWITTER_KEY", ns_parser.key)
            cfg.API_TWITTER_KEY = ns_parser.key

            os.environ["GT_API_TWITTER_SECRET_KEY"] = ns_parser.secret_key
            dotenv.set_key(
                self.env_file, "GT_API_TWITTER_SECRET_KEY", ns_parser.secret_key
            )
            cfg.API_TWITTER_SECRET_KEY = ns_parser.secret_key

            os.environ["GT_API_TWITTER_BEARER_TOKEN"] = ns_parser.bearer_token
            dotenv.set_key(
                self.env_file, "GT_API_TWITTER_BEARER_TOKEN", ns_parser.bearer_token
            )
            cfg.API_TWITTER_BEARER_TOKEN = ns_parser.bearer_token

            self.check_twitter_key(show_output=True)

    def call_rh(self, other_args: List[str]):
        """Process rh command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rh",
            description="Set Robinhood API key.",
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            dest="username",
            help="username",
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="password",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_RH_USERNAME"] = ns_parser.username
            dotenv.set_key(self.env_file, "GT_RH_USERNAME", ns_parser.username)
            cfg.RH_USERNAME = ns_parser.username

            os.environ["GT_RH_PASSWORD"] = ns_parser.password
            dotenv.set_key(self.env_file, "GT_RH_PASSWORD", ns_parser.password)
            cfg.RH_PASSWORD = ns_parser.password

            self.check_rh_key(show_output=True)

    def call_degiro(self, other_args: List[str]):
        """Process degiro command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="degiro",
            description="Set Degiro API key.",
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            dest="username",
            help="username",
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="password",
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="secret",
            help="TOPT Secret",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_DG_USERNAME"] = ns_parser.username
            dotenv.set_key(self.env_file, "GT_DG_USERNAME", ns_parser.username)
            cfg.DG_USERNAME = ns_parser.username

            os.environ["GT_DG_PASSWORD"] = ns_parser.password
            dotenv.set_key(self.env_file, "GT_DG_PASSWORD", ns_parser.password)
            cfg.DG_PASSWORD = ns_parser.password

            os.environ["GT_DG_TOTP_SECRET"] = ns_parser.secret
            dotenv.set_key(self.env_file, "GT_DG_TOTP_SECRET", ns_parser.secret)
            cfg.DG_TOTP_SECRET = ns_parser.secret

            self.check_degiro_key(show_output=True)

    def call_oanda(self, other_args: List[str]):
        """Process oanda command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="oanda",
            description="Set Oanda API key.",
        )
        parser.add_argument(
            "-a",
            "--account",
            type=str,
            dest="account",
            help="account",
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            dest="token",
            help="token",
        )
        parser.add_argument(
            "-t",
            "--account_type",
            type=str,
            dest="account_type",
            help="account type",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_OANDA_ACCOUNT"] = ns_parser.account
            dotenv.set_key(self.env_file, "GT_OANDA_ACCOUNT", ns_parser.account)
            cfg.OANDA_ACCOUNT = ns_parser.account

            os.environ["GT_OANDA_TOKEN"] = ns_parser.token
            dotenv.set_key(self.env_file, "GT_OANDA_TOKEN", ns_parser.token)
            cfg.OANDA_TOKEN = ns_parser.token

            os.environ["GT_OANDA_ACCOUNT_TYPE"] = ns_parser.account_type
            dotenv.set_key(
                self.env_file, "GT_OANDA_ACCOUNT_TYPE", ns_parser.account_type
            )
            cfg.OANDA_ACCOUNT_TYPE = ns_parser.account_type

            self.check_oanda_key(show_output=True)

    def call_binance(self, other_args: List[str]):
        """Process binance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="binance",
            description="Set Binance API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="Key",
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="secret_key",
            help="Secret key",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_BINANCE_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_BINANCE_KEY", ns_parser.key)
            cfg.API_BINANCE_KEY = ns_parser.key

            os.environ["GT_API_BINANCE_SECRET"] = ns_parser.secret_key
            dotenv.set_key(self.env_file, "GT_API_BINANCE_SECRET", ns_parser.secret_key)
            cfg.API_BINANCE_SECRET = ns_parser.secret_key

            self.check_binance_key(show_output=True)

    def call_bitquery(self, other_args: List[str]):
        """Process bitquery command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bitquery",
            description="Set Bitquery API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_BITQUERY_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_BITQUERY_KEY", ns_parser.key)
            cfg.API_BITQUERY_KEY = ns_parser.key

            self.check_bitquery_key(show_output=True)

    def call_si(self, other_args: List[str]):
        """Process si command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="si",
            description="Set Sentiment Investor API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_SENTIMENTINVESTOR_TOKEN"] = ns_parser.key
            dotenv.set_key(
                self.env_file, "GT_API_SENTIMENTINVESTOR_TOKEN", ns_parser.key
            )
            cfg.API_SENTIMENTINVESTOR_TOKEN = ns_parser.key

            self.check_si_key(show_output=True)

    def call_coinbase(self, other_args: List[str]):
        """Process coinbase command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="coinbase",
            description="Set Coinbase API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="Key",
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="secret_key",
            help="Secret key",
        )
        parser.add_argument(
            "-p",
            "--passphrase",
            type=str,
            dest="passphrase",
            help="Passphrase",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_COINBASE_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_COINBASE_KEY", ns_parser.key)
            cfg.API_COINBASE_KEY = ns_parser.key

            os.environ["GT_API_COINBASE_SECRET"] = ns_parser.secret_key
            dotenv.set_key(
                self.env_file, "GT_API_COINBASE_SECRET", ns_parser.secret_key
            )
            cfg.API_COINBASE_SECRET = ns_parser.secret_key

            os.environ["GT_API_COINBASE_PASS_PHRASE"] = ns_parser.passphrase
            dotenv.set_key(
                self.env_file, "GT_API_COINBASE_PASS_PHRASE", ns_parser.passphrase
            )
            cfg.API_COINBASE_PASS_PHRASE = ns_parser.passphrase

            self.check_coinbase_key(show_output=True)

    def call_walert(self, other_args: List[str]):
        """Process walert command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="walert",
            description="Set Whale Alert API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_WHALE_ALERT_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_WHALE_ALERT_KEY", ns_parser.key)
            cfg.API_WHALE_ALERT_KEY = ns_parser.key

            self.check_walert_key(show_output=True)

    def call_glassnode(self, other_args: List[str]):
        """Process glassnode command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="glassnode",
            description="Set Whale Alert API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_GLASSNODE_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_GLASSNODE_KEY", ns_parser.key)
            cfg.API_GLASSNODE_KEY = ns_parser.key

            self.check_glassnode_key(show_output=True)

    def call_coinglass(self, other_args: List[str]):
        """Process coinglass command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="coinglass",
            description="Set Coinglass API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_COINGLASS_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_COINGLASS_KEY", ns_parser.key)
            cfg.API_COINGLASS_KEY = ns_parser.key

            self.check_coinglass_key(show_output=True)

    def call_cpanic(self, other_args: List[str]):
        """Process cpanic command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpanic",
            description="Set Crypto Panic API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_CRYPTO_PANIC_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_CRYPTO_PANIC_KEY", ns_parser.key)
            cfg.API_CRYPTO_PANIC_KEY = ns_parser.key

            self.check_cpanic_key(show_output=True)

    def call_ethplorer(self, other_args: List[str]):
        """Process ethplorer command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ethplorer",
            description="Set Ethplorer API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["GT_API_ETHPLORER_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "GT_API_ETHPLORER_KEY", ns_parser.key)
            cfg.API_ETHPLORER_KEY = ns_parser.key

            self.check_ethplorer_key(show_output=True)
