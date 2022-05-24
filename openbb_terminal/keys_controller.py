"""Keys Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines

import argparse
import logging
import os
from typing import Dict, List

import dotenv
import praw
import pyEX
import quandl
import requests
from prawcore.exceptions import ResponseException
from alpha_vantage.timeseries import TimeSeries
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from prompt_toolkit.completion import NestedCompleter
from pyEX.common.exception import PyEXception

from openbb_terminal import config_terminal as cfg
from openbb_terminal import feature_flags as obbff
from openbb_terminal.cryptocurrency.coinbase_helpers import (
    CoinbaseProAuth,
    make_coinbase_request,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import parse_known_args_and_warn
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText, translate
from openbb_terminal.terminal_helper import suppress_stdout

logger = logging.getLogger(__name__)


class KeysController(BaseController):  # pylint: disable=too-many-public-methods
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
        "finnhub",
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
        "walert",
        "glassnode",
        "coinglass",
        "cpanic",
        "ethplorer",
        "smartstake",
        "github",
        "mesari",
    ]
    PATH = "/keys/"
    key_dict: Dict = {}
    cfg_dict: Dict = {}

    def __init__(
        self, queue: List[str] = None, menu_usage: bool = True, env_file: str = ".env"
    ):
        """Constructor"""
        super().__init__(queue)
        self.env_file = env_file
        if menu_usage:
            self.check_keys_status()

            if session and obbff.USE_PROMPT_TOOLKIT:
                choices: dict = {c: {} for c in self.controller_choices}

                choices["support"] = self.SUPPORT_CHOICES

                self.completer = NestedCompleter.from_nested_dict(choices)

    def check_github_key(self, show_output: bool = False) -> None:
        """Check GitHub key"""
        self.cfg_dict["GITHUB"] = "github"
        if cfg.API_GITHUB_KEY == "REPLACE_ME":  # pragma: allowlist secret
            logger.info("GitHub key not defined")
            self.key_dict["GITHUB"] = "not defined"
        else:
            self.key_dict["GITHUB"] = "defined"
            # github api will not fail for the first requests without key
            # only after certain amount of requests the user will get rate limited

        if show_output:
            console.print(self.key_dict["GITHUB"] + "\n")

    def check_av_key(self, show_output: bool = False) -> None:
        """Check Alpha Vantage key"""
        self.cfg_dict["ALPHA_VANTAGE"] = "av"
        if cfg.API_KEY_ALPHAVANTAGE == "REPLACE_ME":  # pragma: allowlist secret
            logger.info("Alpha Vantage key not defined")
            self.key_dict["ALPHA_VANTAGE"] = "not defined"
        else:
            df = TimeSeries(
                key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
            ).get_intraday(symbol="AAPL")
            if df[0].empty:  # pylint: disable=no-member
                logger.warning("Alpha Vantage key defined, test failed")
                self.key_dict["ALPHA_VANTAGE"] = "defined, test failed"
            else:
                logger.info("Alpha Vantage key defined, test passed")
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
            logger.info("Financial Modeling Prep key not defined")
            self.key_dict["FINANCIAL_MODELING_PREP"] = "not defined"
        else:
            r = requests.get(
                f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"
            )
            if r.status_code in [403, 401]:
                logger.warning("Financial Modeling Prep key defined, test failed")
                self.key_dict["FINANCIAL_MODELING_PREP"] = "defined, test failed"
            elif r.status_code == 200:
                logger.info("Financial Modeling Prep key defined, test passed")
                self.key_dict["FINANCIAL_MODELING_PREP"] = "defined, test passed"
            else:
                logger.warning("Financial Modeling Prep key defined, test inconclusive")
                self.key_dict["FINANCIAL_MODELING_PREP"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["FINANCIAL_MODELING_PREP"] + "\n")

    def check_quandl_key(self, show_output: bool = False) -> None:
        """Check Quandl key"""
        self.cfg_dict["QUANDL"] = "quandl"
        if cfg.API_KEY_QUANDL == "REPLACE_ME":  # pragma: allowlist secret
            logger.info("Quandl key not defined")
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
                logger.info("Quandl key defined, test passed")
                self.key_dict["QUANDL"] = "defined, test passed"
            except Exception as _:  # noqa: F841
                logger.exception("Quandl key defined, test failed")
                self.key_dict["QUANDL"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["QUANDL"] + "\n")

    def check_polygon_key(self, show_output: bool = False) -> None:
        """Check Polygon key"""
        self.cfg_dict["POLYGON"] = "polygon"
        if cfg.API_POLYGON_KEY == "REPLACE_ME":
            logger.info("Polygon key not defined")
            self.key_dict["POLYGON"] = "not defined"
        else:
            r = requests.get(
                "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17"
                f"?apiKey={cfg.API_POLYGON_KEY}"
            )
            if r.status_code in [403, 401]:
                logger.warning("Polygon key defined, test failed")
                self.key_dict["POLYGON"] = "defined, test failed"
            elif r.status_code == 200:
                logger.info("Polygon key defined, test passed")
                self.key_dict["POLYGON"] = "defined, test passed"
            else:
                logger.warning("Polygon key defined, test inconclusive")
                self.key_dict["POLYGON"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["POLYGON"] + "\n")

    def check_fred_key(self, show_output: bool = False) -> None:
        """Check FRED key"""
        self.cfg_dict["FRED"] = "fred"
        if cfg.API_FRED_KEY == "REPLACE_ME":
            logger.info("FRED key not defined")
            self.key_dict["FRED"] = "not defined"
        else:
            r = requests.get(
                f"https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key={cfg.API_FRED_KEY}"
            )
            if r.status_code in [403, 401, 400]:
                logger.warning("FRED key defined, test failed")
                self.key_dict["FRED"] = "defined, test failed"
            elif r.status_code == 200:
                logger.info("FRED key defined, test passed")
                self.key_dict["FRED"] = "defined, test passed"
            else:
                logger.warning("FRED key defined, test inconclusive")
                self.key_dict["FRED"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["FRED"] + "\n")

    def check_news_key(self, show_output: bool = False) -> None:
        """Check News API key"""
        self.cfg_dict["NEWSAPI"] = "news"
        if cfg.API_NEWS_TOKEN == "REPLACE_ME":  # nosec
            logger.info("News API key not defined")
            self.key_dict["NEWSAPI"] = "not defined"
        else:
            r = requests.get(
                f"https://newsapi.org/v2/everything?q=keyword&apiKey={cfg.API_NEWS_TOKEN}"
            )
            if r.status_code in [401, 403]:
                logger.warning("News API key defined, test failed")
                self.key_dict["NEWSAPI"] = "defined, test failed"
            elif r.status_code == 200:
                logger.info("News API key defined, test passed")
                self.key_dict["NEWSAPI"] = "defined, test passed"
            else:
                logger.warning("News API key defined, test inconclusive")
                self.key_dict["NEWSAPI"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["NEWSAPI"] + "\n")

    def check_tradier_key(self, show_output: bool = False) -> None:
        """Check Tradier key"""
        self.cfg_dict["TRADIER"] = "tradier"
        if cfg.TRADIER_TOKEN == "REPLACE_ME":  # nosec
            logger.info("Tradier key not defined")
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
                logger.warning("Tradier key not defined, test failed")
                self.key_dict["TRADIER"] = "defined, test failed"
            elif r.status_code == 200:
                logger.info("Tradier key not defined, test passed")
                self.key_dict["TRADIER"] = "defined, test passed"
            else:
                logger.warning("Tradier key not defined, test inconclusive")
                self.key_dict["TRADIER"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["TRADIER"] + "\n")

    def check_cmc_key(self, show_output: bool = False) -> None:
        """Check Coinmarketcap key"""
        self.cfg_dict["COINMARKETCAP"] = "cmc"
        if cfg.API_CMC_KEY == "REPLACE_ME":
            logger.info("Coinmarketcap key not defined")
            self.key_dict["COINMARKETCAP"] = "not defined"
        else:
            cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)

            try:
                cmc.cryptocurrency_map()
                logger.info("Coinmarketcap key defined, test passed")
                self.key_dict["COINMARKETCAP"] = "defined, test passed"
            except CoinMarketCapAPIError:
                logger.exception("Coinmarketcap key defined, test failed")
                self.key_dict["COINMARKETCAP"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["COINMARKETCAP"] + "\n")

    def check_finnhub_key(self, show_output: bool = False) -> None:
        """Check Finnhub key"""
        self.cfg_dict["FINNHUB"] = "finnhub"
        if cfg.API_FINNHUB_KEY == "REPLACE_ME":
            logger.info("Finnhub key not defined")
            self.key_dict["FINNHUB"] = "not defined"
        else:
            r = r = requests.get(
                f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={cfg.API_FINNHUB_KEY}"
            )
            if r.status_code in [403, 401, 400]:
                logger.warning("Finnhub key defined, test failed")
                self.key_dict["FINNHUB"] = "defined, test failed"
            elif r.status_code == 200:
                logger.info("Finnhub key defined, test passed")
                self.key_dict["FINNHUB"] = "defined, test passed"
            else:
                logger.warning("Finnhub key defined, test inconclusive")
                self.key_dict["FINNHUB"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["FINNHUB"] + "\n")

    def check_iex_key(self, show_output: bool = False) -> None:
        """Check IEX Cloud key"""
        self.cfg_dict["IEXCLOUD"] = "iex"
        if cfg.API_IEX_TOKEN == "REPLACE_ME":  # nosec
            logger.info("IEX Cloud key not defined")
            self.key_dict["IEXCLOUD"] = "not defined"
        else:
            try:
                pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")
                logger.info("IEX Cloud key defined, test passed")
                self.key_dict["IEXCLOUD"] = "defined, test passed"
            except PyEXception:
                logger.exception("IEX Cloud key defined, test failed")
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
            logger.info("Reddit key not defined")
            self.key_dict["REDDIT"] = "not defined"
        else:

            try:
                with suppress_stdout():
                    praw_api = praw.Reddit(
                        client_id=cfg.API_REDDIT_CLIENT_ID,
                        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
                        username=cfg.API_REDDIT_USERNAME,
                        user_agent=cfg.API_REDDIT_USER_AGENT,
                        password=cfg.API_REDDIT_PASSWORD,
                    )

                    praw_api.user.me()
                logger.info("Reddit key defined, test passed")
                self.key_dict["REDDIT"] = "defined, test passed"
            except (Exception, ResponseException):
                logger.warning("Reddit key defined, test failed")
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
            logger.info("Twitter key not defined")
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
                logger.info("Twitter key defined, test passed")
                self.key_dict["TWITTER"] = "defined, test passed"
            elif r.status_code in [401, 403]:
                logger.warning("Twitter key defined, test failed")
                self.key_dict["TWITTER"] = "defined, test failed"
            else:
                logger.warning("Twitter key defined, test failed")
                self.key_dict["TWITTER"] = "defined, test inconclusive"

        if show_output:
            console.print(self.key_dict["TWITTER"] + "\n")

    def check_rh_key(self, show_output: bool = False) -> None:
        """Check Robinhood key"""
        self.cfg_dict["ROBINHOOD"] = "rh"
        rh_keys = [cfg.RH_USERNAME, cfg.RH_PASSWORD]
        if "REPLACE_ME" in rh_keys:
            logger.info("Robinhood key not defined")
            self.key_dict["ROBINHOOD"] = "not defined"
        else:
            logger.info("Robinhood key defined, not tested")
            self.key_dict["ROBINHOOD"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["ROBINHOOD"] + "\n")

    def check_degiro_key(self, show_output: bool = False) -> None:
        """Check Degiro key"""
        self.cfg_dict["DEGIRO"] = "degiro"
        dg_keys = [cfg.DG_USERNAME, cfg.DG_PASSWORD, cfg.DG_TOTP_SECRET]
        if "REPLACE_ME" in dg_keys:
            logger.info("Degiro key not defined")
            self.key_dict["DEGIRO"] = "not defined"
        else:
            logger.info("Degiro key defined, not tested")
            self.key_dict["DEGIRO"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["DEGIRO"] + "\n")

    def check_oanda_key(self, show_output: bool = False) -> None:
        """Check Oanda key"""
        self.cfg_dict["OANDA"] = "oanda"
        oanda_keys = [cfg.OANDA_TOKEN, cfg.OANDA_ACCOUNT]
        if "REPLACE_ME" in oanda_keys:
            logger.info("Oanda key not defined")
            self.key_dict["OANDA"] = "not defined"
        else:
            logger.info("Oanda key defined, not tested")
            self.key_dict["OANDA"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["OANDA"] + "\n")

    def check_binance_key(self, show_output: bool = False) -> None:
        """Check Binance key"""
        self.cfg_dict["BINANCE"] = "binance"
        bn_keys = [cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET]
        if "REPLACE_ME" in bn_keys:
            logger.info("Binance key not defined")
            self.key_dict["BINANCE"] = "not defined"
        else:
            logger.info("Binance key defined, not tested")
            self.key_dict["BINANCE"] = "defined, not tested"

        if show_output:
            console.print(self.key_dict["BINANCE"] + "\n")

    def check_bitquery_key(self, show_output: bool = False) -> None:
        """Check Bitquery key"""
        self.cfg_dict["BITQUERY"] = "bitquery"
        bitquery = cfg.API_BITQUERY_KEY
        if "REPLACE_ME" in bitquery:
            logger.info("Bitquery key not defined")
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
                logger.info("Bitquery key defined, test passed")
                self.key_dict["BITQUERY"] = "defined, test passed"
            else:
                logger.warning("Bitquery key defined, test failed")
                self.key_dict["BITQUERY"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["BITQUERY"] + "\n")

    def check_si_key(self, show_output: bool = False) -> None:
        """Check Sentiment Investor key"""
        self.cfg_dict["SENTIMENT_INVESTOR"] = "si"
        si_keys = [cfg.API_SENTIMENTINVESTOR_TOKEN]
        if "REPLACE_ME" in si_keys:
            logger.info("Sentiment Investor key not defined")
            self.key_dict["SENTIMENT_INVESTOR"] = "not defined"
        else:
            try:
                account = requests.get(
                    f"https://api.sentimentinvestor.com/v1/trending"
                    f"?token={cfg.API_SENTIMENTINVESTOR_TOKEN}"
                )
                if account.ok and account.json().get("success", False):
                    logger.info("Sentiment Investor key defined, test passed")
                    self.key_dict["SENTIMENT_INVESTOR"] = "defined, test passed"
                else:
                    logger.warning("Sentiment Investor key defined, test failed")
                    self.key_dict["SENTIMENT_INVESTOR"] = "defined, test unsuccessful"
            except Exception:
                logger.warning("Sentiment Investor key defined, test failed")
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
            logger.info("Coinbase key not defined")
            self.key_dict["COINBASE"] = "not defined"
        else:
            auth = CoinbaseProAuth(
                cfg.API_COINBASE_KEY,
                cfg.API_COINBASE_SECRET,
                cfg.API_COINBASE_PASS_PHRASE,
            )
            resp = make_coinbase_request("/accounts", auth=auth)
            if not resp:
                logger.warning("Coinbase key defined, test failed")
                self.key_dict["COINBASE"] = "defined, test unsuccessful"
            else:
                logger.info("Coinbase key defined, test passed")
                self.key_dict["COINBASE"] = "defined, test passed"

        if show_output:
            console.print(self.key_dict["COINBASE"] + "\n")

    def check_walert_key(self, show_output: bool = False) -> None:
        """Check Walert key"""
        self.cfg_dict["WHALE_ALERT"] = "walert"
        if cfg.API_WHALE_ALERT_KEY == "REPLACE_ME":
            logger.info("Walert key not defined")
            self.key_dict["WHALE_ALERT"] = "not defined"
        else:
            url = (
                "https://api.whale-alert.io/v1/transactions?api_key="
                + cfg.API_WHALE_ALERT_KEY
            )
            try:
                response = requests.get(url, timeout=2)
                if not 200 <= response.status_code < 300:
                    logger.warning("Walert key defined, test failed")
                    self.key_dict["WHALE_ALERT"] = "defined, test unsuccessful"
                else:
                    logger.info("Walert key defined, test passed")
                    self.key_dict["WHALE_ALERT"] = "defined, test passed"
            except Exception:
                logger.exception("Walert key defined, test failed")
                self.key_dict["WHALE_ALERT"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["WHALE_ALERT"] + "\n")

    def check_glassnode_key(self, show_output: bool = False) -> None:
        """Check glassnode key"""
        self.cfg_dict["GLASSNODE"] = "glassnode"
        if cfg.API_GLASSNODE_KEY == "REPLACE_ME":
            logger.info("Glassnode key not defined")
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
                logger.info("Glassnode key defined, test passed")
                self.key_dict["GLASSNODE"] = "defined, test passed"
            else:
                logger.warning("Glassnode key defined, test failed")
                self.key_dict["GLASSNODE"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["GLASSNODE"] + "\n")

    def check_coinglass_key(self, show_output: bool = False) -> None:
        """Check coinglass key"""
        self.cfg_dict["COINGLASS"] = "coinglass"
        if cfg.API_COINGLASS_KEY == "REPLACE_ME":
            logger.info("Coinglass key not defined")
            self.key_dict["COINGLASS"] = "not defined"
        else:
            url = "https://open-api.coinglass.com/api/pro/v1/futures/openInterest/chart?&symbol=BTC&interval=0"

            headers = {"coinglassSecret": cfg.API_COINGLASS_KEY}

            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:
                logger.info("Coinglass key defined, test passed")
                self.key_dict["COINGLASS"] = "defined, test passed"
            else:
                logger.warning("Coinglass key defined, test failed")
                self.key_dict["COINGLASS"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["COINGLASS"] + "\n")

    def check_cpanic_key(self, show_output: bool = False) -> None:
        """Check cpanic key"""
        self.cfg_dict["CRYPTO_PANIC"] = "cpanic"
        if cfg.API_CRYPTO_PANIC_KEY == "REPLACE_ME":
            logger.info("cpanic key not defined")
            self.key_dict["CRYPTO_PANIC"] = "not defined"
        else:
            crypto_panic_url = f"https://cryptopanic.com/api/v1/posts/?auth_token={cfg.API_CRYPTO_PANIC_KEY}&kind=all"
            response = requests.get(crypto_panic_url)

            if not 200 <= response.status_code < 300:
                logger.warning("cpanic key defined, test failed")
                self.key_dict["CRYPTO_PANIC"] = "defined, test unsuccessful"
            try:
                logger.info("cpanic key defined, test passed")
                self.key_dict["CRYPTO_PANIC"] = "defined, test passed"
            except Exception as _:  # noqa: F841
                logger.warning("cpanic key defined, test failed")
                self.key_dict["CRYPTO_PANIC"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["COINGLASS"] + "\n")

    def check_ethplorer_key(self, show_output: bool = False) -> None:
        """Check ethplorer key"""
        self.cfg_dict["ETHPLORER"] = "ethplorer"
        if cfg.API_ETHPLORER_KEY == "REPLACE_ME":
            logger.info("ethplorer key not defined")
            self.key_dict["ETHPLORER"] = "not defined"
        else:
            ethplorer_url = "https://api.ethplorer.io/getTokenInfo/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984?apiKey="
            ethplorer_url += cfg.API_ETHPLORER_KEY
            response = requests.get(ethplorer_url)
            try:
                if response.status_code == 200:
                    logger.info("ethplorer key defined, test passed")
                    self.key_dict["ETHPLORER"] = "defined, test passed"
                else:
                    logger.warning("ethplorer key defined, test failed")
                    self.key_dict["ETHPLORER"] = "defined, test unsuccessful"
            except Exception as _:  # noqa: F841
                logger.exception("ethplorer key defined, test failed")
                self.key_dict["ETHPLORER"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["ETHPLORER"] + "\n")

    def check_smartstake_key(self, show_output: bool = False) -> None:
        """Check Smartstake key"""
        self.cfg_dict["SMARTSTAKE"] = "smartstake"
        if "REPLACE_ME" in [
            cfg.API_SMARTSTAKE_TOKEN,
            cfg.API_SMARTSTAKE_KEY,
        ]:
            self.key_dict["SMARTSTAKE"] = "not defined"
        else:
            payload = {
                "type": "history",
                "dayCount": 30,
                "key": cfg.API_SMARTSTAKE_KEY,
                "token": cfg.API_SMARTSTAKE_TOKEN,
            }

            smartstake_url = "https://prod.smartstakeapi.com/listData?app=TERRA"
            response = requests.get(smartstake_url, params=payload)  # type: ignore

            try:
                if response.status_code == 200:
                    self.key_dict["SMARTSTAKE"] = "defined, test passed"
                else:
                    self.key_dict["SMARTSTAKE"] = "defined, test unsuccessful"
            except Exception as _:  # noqa: F841
                self.key_dict["SMARTSTAKE"] = "defined, test unsuccessful"

        if show_output:
            console.print(self.key_dict["SMARTSTAKE"] + "\n")

    def check_messari_key(self, show_output: bool = False) -> None:
        """Check Messari key"""
        self.cfg_dict["MESSARI"] = "messari"
        if (
            cfg.API_MESSARI_KEY == "REPLACE_ME"  # pragma: allowlist secret
        ):  # pragma: allowlist secret
            logger.info("Messari key not defined")
            self.key_dict["MESSARI"] = "not defined"
        else:

            url = "https://data.messari.io/api/v2/assets/bitcoin/profile"
            headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}
            params = {"fields": "profile/general/overview/official_links"}
            r = requests.get(url, headers=headers, params=params)

            if r.status_code == 200:
                logger.info("FMessari key defined, test passed")
                self.key_dict["MESSARI"] = "defined, test passed"
            else:
                logger.warning("Messari key defined, test failed")
                self.key_dict["MESSARI"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["MESSARI"] + "\n")

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
        self.check_finnhub_key()
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
        self.check_smartstake_key()
        self.check_github_key()
        self.check_messari_key()

    def print_help(self):
        """Print help"""
        self.check_keys_status()
        mt = MenuText("keys/")
        mt.add_info("_keys_")
        mt.add_raw("\n")
        for k, v in self.key_dict.items():
            cmd_name = self.cfg_dict[k]
            c = "red"
            if v == "defined, test passed":
                c = "green"
            elif v == "defined":
                c = "green"
            elif v == "defined, test inconclusive":
                c = "yellow"
            elif v == "not defined":
                c = "grey30"
            mt.add_raw(
                f"   [cmds]{cmd_name}[/cmds] {(20 - len(cmd_name)) * ' '}"
                f" [{c}] {k} {(25 - len(k)) * ' '} {translate(v)} [/{c}]\n"
            )

        console.print(text=mt.menu_text, menu="Keys")

    @log_start_end(log=logger)
    def call_github(self, other_args: List[str]):
        """Process github command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="github",
            description="Set GitHub API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print(
                "For your API Key, visit: https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api\n"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_GITHUB_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_GITHUB_KEY", ns_parser.key)
            cfg.API_GITHUB_KEY = ns_parser.key
            self.check_github_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print(
                "For your API Key, visit: https://www.alphavantage.co/support/#api-key\n"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_KEY_ALPHAVANTAGE"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_KEY_ALPHAVANTAGE", ns_parser.key)
            cfg.API_KEY_ALPHAVANTAGE = ns_parser.key
            self.check_av_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print(
                "For your API Key, visit: https://financialmodelingprep.com\n"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_KEY_FINANCIALMODELINGPREP"] = ns_parser.key
            dotenv.set_key(
                self.env_file, "OPENBB_API_KEY_FINANCIALMODELINGPREP", ns_parser.key
            )
            cfg.API_KEY_FINANCIALMODELINGPREP = ns_parser.key
            self.check_fmp_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://www.quandl.com\n")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_KEY_QUANDL"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_KEY_QUANDL", ns_parser.key)
            cfg.API_KEY_QUANDL = ns_parser.key
            self.check_quandl_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://polygon.io\n")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_POLYGON_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_POLYGON_KEY", ns_parser.key)
            cfg.API_POLYGON_KEY = ns_parser.key
            self.check_polygon_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://fred.stlouisfed.org\n")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_FRED_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_FRED_KEY", ns_parser.key)
            cfg.API_FRED_KEY = ns_parser.key
            self.check_fred_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://newsapi.org\n")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_NEWS_TOKEN"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_NEWS_TOKEN", ns_parser.key)
            cfg.API_NEWS_TOKEN = ns_parser.key
            self.check_news_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://developer.tradier.com\n")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_TRADIER_TOKEN"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_TRADIER_TOKEN", ns_parser.key)
            cfg.TRADIER_TOKEN = ns_parser.key
            self.check_tradier_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://coinmarketcap.com\n")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_CMC_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_CMC_KEY", ns_parser.key)
            cfg.API_CMC_KEY = ns_parser.key
            self.check_cmc_key(show_output=True)

    @log_start_end(log=logger)
    def call_finnhub(self, other_args: List[str]):
        """Process Finnhub API command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="finnhub",
            description="Set Finnhub API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, visit: https://finnhub.io\n")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_FINNHUB_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_FINNHUB_KEY", ns_parser.key)
            cfg.API_FINNHUB_KEY = ns_parser.key
            self.check_finnhub_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://iexcloud.io\n")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_IEX_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_IEX_KEY", ns_parser.key)
            cfg.API_IEX_TOKEN = ns_parser.key
            self.check_iex_key(show_output=True)

    @log_start_end(log=logger)
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
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="client_secret",
            help="Client Secret",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            dest="username",
            help="Username",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="Password",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-a",
            "--agent",
            type=str,
            dest="user_agent",
            help="User agent",
            required="-h" not in other_args,
            nargs="+",
        )
        if not other_args:
            console.print("For your API Key, visit: https://www.reddit.com\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_REDDIT_CLIENT_ID"] = ns_parser.client_id
            dotenv.set_key(
                self.env_file, "OPENBB_API_REDDIT_CLIENT_ID", ns_parser.client_id
            )
            cfg.API_REDDIT_CLIENT_ID = ns_parser.client_id

            os.environ["OPENBB_API_REDDIT_CLIENT_SECRET"] = ns_parser.client_secret
            dotenv.set_key(
                self.env_file,
                "OPENBB_API_REDDIT_CLIENT_SECRET",
                ns_parser.client_secret,
            )
            cfg.API_REDDIT_CLIENT_SECRET = ns_parser.client_secret

            os.environ["OPENBB_API_REDDIT_PASSWORD"] = ns_parser.password
            dotenv.set_key(
                self.env_file, "OPENBB_API_REDDIT_PASSWORD", ns_parser.password
            )
            cfg.API_REDDIT_PASSWORD = ns_parser.password

            os.environ["OPENBB_API_REDDIT_USERNAME"] = ns_parser.username
            dotenv.set_key(
                self.env_file, "OPENBB_API_REDDIT_USERNAME", ns_parser.username
            )
            cfg.API_REDDIT_USERNAME = ns_parser.username

            slash_components = "".join([f"/{val}" for val in self.queue])
            useragent = " ".join(ns_parser.user_agent) + " " + slash_components
            useragent = useragent.replace('"', "")
            self.queue = []

            os.environ["OPENBB_API_REDDIT_USER_AGENT"] = useragent
            dotenv.set_key(self.env_file, "OPENBB_API_REDDIT_USER_AGENT", useragent)
            cfg.API_REDDIT_USER_AGENT = useragent

            self.check_reddit_key(show_output=True)

    @log_start_end(log=logger)
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
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="secret_key",
            help="Secret key",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            dest="bearer_token",
            help="Bearer token",
            required="-h" not in other_args,
        )
        if not other_args:
            console.print("For your API Key, visit: https://developer.twitter.com\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_TWITTER_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_TWITTER_KEY", ns_parser.key)
            cfg.API_TWITTER_KEY = ns_parser.key

            os.environ["OPENBB_API_TWITTER_SECRET_KEY"] = ns_parser.secret_key
            dotenv.set_key(
                self.env_file, "OPENBB_API_TWITTER_SECRET_KEY", ns_parser.secret_key
            )
            cfg.API_TWITTER_SECRET_KEY = ns_parser.secret_key

            os.environ["OPENBB_API_TWITTER_BEARER_TOKEN"] = ns_parser.bearer_token
            dotenv.set_key(
                self.env_file, "OPENBB_API_TWITTER_BEARER_TOKEN", ns_parser.bearer_token
            )
            cfg.API_TWITTER_BEARER_TOKEN = ns_parser.bearer_token

            self.check_twitter_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://robinhood.com/us/en/\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_RH_USERNAME"] = ns_parser.username
            dotenv.set_key(self.env_file, "OPENBB_RH_USERNAME", ns_parser.username)
            cfg.RH_USERNAME = ns_parser.username

            os.environ["OPENBB_RH_PASSWORD"] = ns_parser.password
            dotenv.set_key(self.env_file, "OPENBB_RH_PASSWORD", ns_parser.password)
            cfg.RH_PASSWORD = ns_parser.password

            self.check_rh_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://www.degiro.fr\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_DG_USERNAME"] = ns_parser.username
            dotenv.set_key(self.env_file, "OPENBB_DG_USERNAME", ns_parser.username)
            cfg.DG_USERNAME = ns_parser.username

            os.environ["OPENBB_DG_PASSWORD"] = ns_parser.password
            dotenv.set_key(self.env_file, "OPENBB_DG_PASSWORD", ns_parser.password)
            cfg.DG_PASSWORD = ns_parser.password

            os.environ["OPENBB_DG_TOTP_SECRET"] = ns_parser.secret
            dotenv.set_key(self.env_file, "OPENBB_DG_TOTP_SECRET", ns_parser.secret)
            cfg.DG_TOTP_SECRET = ns_parser.secret

            self.check_degiro_key(show_output=True)

    @log_start_end(log=logger)
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
            "-at",
            "--account_type",
            type=str,
            dest="account_type",
            help="account type",
        )
        if not other_args:
            console.print("For your API Key, visit: https://developer.oanda.com\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_OANDA_ACCOUNT"] = ns_parser.account
            dotenv.set_key(self.env_file, "OPENBB_OANDA_ACCOUNT", ns_parser.account)
            cfg.OANDA_ACCOUNT = ns_parser.account

            os.environ["OPENBB_OANDA_TOKEN"] = ns_parser.token
            dotenv.set_key(self.env_file, "OPENBB_OANDA_TOKEN", ns_parser.token)
            cfg.OANDA_TOKEN = ns_parser.token

            os.environ["OPENBB_OANDA_ACCOUNT_TYPE"] = ns_parser.account_type
            dotenv.set_key(
                self.env_file, "OPENBB_OANDA_ACCOUNT_TYPE", ns_parser.account_type
            )
            cfg.OANDA_ACCOUNT_TYPE = ns_parser.account_type

            self.check_oanda_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://binance.com\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_BINANCE_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_BINANCE_KEY", ns_parser.key)
            cfg.API_BINANCE_KEY = ns_parser.key

            os.environ["OPENBB_API_BINANCE_SECRET"] = ns_parser.secret_key
            dotenv.set_key(
                self.env_file, "OPENBB_API_BINANCE_SECRET", ns_parser.secret_key
            )
            cfg.API_BINANCE_SECRET = ns_parser.secret_key

            self.check_binance_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://bitquery.io/\n")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_BITQUERY_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_BITQUERY_KEY", ns_parser.key)
            cfg.API_BITQUERY_KEY = ns_parser.key

            self.check_bitquery_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://sentimentinvestor.com\n")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_SENTIMENTINVESTOR_TOKEN"] = ns_parser.key
            dotenv.set_key(
                self.env_file, "OPENBB_API_SENTIMENTINVESTOR_TOKEN", ns_parser.key
            )
            cfg.API_SENTIMENTINVESTOR_TOKEN = ns_parser.key

            self.check_si_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://docs.pro.coinbase.com/\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_COINBASE_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_COINBASE_KEY", ns_parser.key)
            cfg.API_COINBASE_KEY = ns_parser.key

            os.environ["OPENBB_API_COINBASE_SECRET"] = ns_parser.secret_key
            dotenv.set_key(
                self.env_file, "OPENBB_API_COINBASE_SECRET", ns_parser.secret_key
            )
            cfg.API_COINBASE_SECRET = ns_parser.secret_key

            os.environ["OPENBB_API_COINBASE_PASS_PHRASE"] = ns_parser.passphrase
            dotenv.set_key(
                self.env_file, "OPENBB_API_COINBASE_PASS_PHRASE", ns_parser.passphrase
            )
            cfg.API_COINBASE_PASS_PHRASE = ns_parser.passphrase

            self.check_coinbase_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print("For your API Key, visit: https://docs.whale-alert.io/\n")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_WHALE_ALERT_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_WHALE_ALERT_KEY", ns_parser.key)
            cfg.API_WHALE_ALERT_KEY = ns_parser.key

            self.check_walert_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print(
                "For your API Key, visit: https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key/\n"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_GLASSNODE_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_GLASSNODE_KEY", ns_parser.key)
            cfg.API_GLASSNODE_KEY = ns_parser.key

            self.check_glassnode_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print(
                "For your API Key, visit: https://coinglass.github.io/API-Reference/#api-key\n"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_COINGLASS_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_COINGLASS_KEY", ns_parser.key)
            cfg.API_COINGLASS_KEY = ns_parser.key

            self.check_coinglass_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print(
                "For your API Key, visit: https://cryptopanic.com/developers/api/\n"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_CRYPTO_PANIC_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_CRYPTO_PANIC_KEY", ns_parser.key)
            cfg.API_CRYPTO_PANIC_KEY = ns_parser.key

            self.check_cpanic_key(show_output=True)

    @log_start_end(log=logger)
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
        if not other_args:
            console.print(
                "For your API Key, visit: https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API\n"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_ETHPLORER_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_ETHPLORER_KEY", ns_parser.key)
            cfg.API_ETHPLORER_KEY = ns_parser.key

            self.check_ethplorer_key(show_output=True)

    def call_smartstake(self, other_args: List[str]):
        """Process smartstake command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="smartstake",
            description="Set Smartstake Key and Token.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="Key",
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            dest="token",
            help="Token",
        )
        if not other_args:
            console.print("For your API Key, visit: https://www.smartstake.io\n")
            return
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            os.environ["OPENBB_API_SMARTSTAKE_TOKEN"] = ns_parser.token
            dotenv.set_key(
                self.env_file, "OPENBB_API_SMARTSTAKE_TOKEN", ns_parser.token
            )
            cfg.API_SMARTSTAKE_TOKEN = ns_parser.token

            os.environ["OPENBB_API_SMARTSTAKE_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_SMARTSTAKE_KEY", ns_parser.key)
            cfg.API_SMARTSTAKE_KEY = ns_parser.key

            self.check_smartstake_key(show_output=True)

    @log_start_end(log=logger)
    def call_messari(self, other_args: List[str]):
        """Process messari command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="messari",
            description="Set Messari API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, visit: https://messari.io/api/docs\n")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_MESSARI_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_MESSARI_KEY", ns_parser.key)
            cfg.API_MESSARI_KEY = ns_parser.key
            self.check_messari_key(show_output=True)
