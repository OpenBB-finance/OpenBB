"""Keys Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines

import argparse
import logging
import os
from typing import Dict, List

import binance
import oandapyV20.endpoints.pricing
import dotenv
import praw
import pyEX
import requests
from prawcore.exceptions import ResponseException
from prompt_toolkit.completion import NestedCompleter
from pyEX.common.exception import PyEXception
from oandapyV20 import API as oanda_API
from oandapyV20.exceptions import V20Error

from openbb_terminal import config_terminal as cfg
from openbb_terminal import feature_flags as obbff
from openbb_terminal import keys_model
from openbb_terminal.core.config.paths import USER_ENV_FILE
from openbb_terminal.cryptocurrency.coinbase_helpers import (
    CoinbaseProAuth,
    make_coinbase_request,
    CoinbaseApiException,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import parse_simple_args
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
        "coinbase",
        "walert",
        "glassnode",
        "coinglass",
        "cpanic",
        "ethplorer",
        "smartstake",
        "github",
        "eodhd",
        "messari",
        "santiment",
    ]
    PATH = "/keys/"
    key_dict: Dict = {}
    cfg_dict: Dict = {}

    def __init__(
        self,
        queue: List[str] = None,
        menu_usage: bool = True,
        env_file: str = str(USER_ENV_FILE),
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

    def check_av_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Alpha Vantage key"""
        self.cfg_dict["ALPHA_VANTAGE"] = "av"
        if not status:
            status = keys_model.check_av_key(show_output=show_output)
        self.key_dict["ALPHA_VANTAGE"] = status

    def check_fmp_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Financial Modeling Prep key"""
        self.cfg_dict["FINANCIAL_MODELING_PREP"] = "fmp"
        if not status:
            status = keys_model.check_fmp_key(show_output=show_output)
        self.key_dict["FINANCIAL_MODELING_PREP"] = status

    def check_quandl_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Quandl key"""
        self.cfg_dict["QUANDL"] = "quandl"
        if not status:
            status = keys_model.check_quandl_key(show_output=show_output)
        self.key_dict["QUANDL"] = status

    def check_polygon_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Polygon key"""
        self.cfg_dict["POLYGON"] = "polygon"
        if not status:
            status = keys_model.check_polygon_key(show_output=show_output)
        self.key_dict["POLYGON"] = status

    def check_fred_key(self, status: str = "", show_output: bool = False) -> None:
        """Check FRED key and update menu accordingly"""
        self.cfg_dict["FRED"] = "fred"
        if not status:
            status = keys_model.check_fred_key(show_output=show_output)
        self.key_dict["FRED"] = status

    def check_news_key(self, status: str = "", show_output: bool = False) -> None:
        """Check News API key"""
        self.cfg_dict["NEWSAPI"] = "news"
        if not status:
            status = keys_model.check_news_key(show_output=show_output)
        self.key_dict["NEWSAPI"] = status

    def check_tradier_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Tradier key"""
        self.cfg_dict["TRADIER"] = "tradier"
        if not status:
            status = keys_model.check_tradier_key(show_output=show_output)
        self.key_dict["TRADIER"] = status

    def check_cmc_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Coinmarketcap key"""
        self.cfg_dict["COINMARKETCAP"] = "cmc"
        if not status:
            status = keys_model.check_cmc_key(show_output=show_output)
        self.key_dict["COINMARKETCAP"] = status

    def check_finnhub_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Finnhub key"""
        self.cfg_dict["FINNHUB"] = "finnhub"
        if not status:
            status = keys_model.check_finnhub_key(show_output=show_output)
        self.key_dict["FINNHUB"] = status

    def check_iex_key(self, status: str = "", show_output: bool = False) -> None:
        """Check IEX Cloud key"""
        self.cfg_dict["IEXCLOUD"] = "iex"
        if not status:
            status = keys_model.check_iex_key(show_output=show_output)
        self.key_dict["IEXCLOUD"] = status

    def check_reddit_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Reddit key"""
        self.cfg_dict["REDDIT"] = "reddit"
        if not status:
            status = keys_model.check_reddit_key(show_output=show_output)
        self.key_dict["REDDIT"] = status

    def check_twitter_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Twitter key"""
        self.cfg_dict["TWITTER"] = "twitter"
        if not status:
            status = keys_model.check_twitter_key(show_output=show_output)
        self.key_dict["TWITTER"] = status

    def check_rh_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Robinhood key"""
        self.cfg_dict["ROBINHOOD"] = "rh"
        if not status:
            status = keys_model.check_rh_key(show_output=show_output)
        self.key_dict["ROBINHOOD"] = status

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
            client = oanda_API(access_token=cfg.OANDA_TOKEN)
            account = cfg.OANDA_ACCOUNT
            try:
                parameters = {"instruments": "EUR_USD"}
                request = oandapyV20.endpoints.pricing.PricingInfo(
                    accountID=account, params=parameters
                )
                client.request(request)
                logger.info("Oanda key defined, test passed")
                self.key_dict["OANDA"] = "defined, test passed"

            except V20Error as e:
                logger.exception(str(e))
                logger.info("Oanda key defined, test failed")
                self.key_dict["OANDA"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["OANDA"] + "\n")

    def check_binance_key(self, show_output: bool = False) -> None:
        """Check Binance key"""
        self.cfg_dict["BINANCE"] = "binance"

        if "REPLACE_ME" in [cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET]:
            logger.info("Binance key not defined")
            self.key_dict["BINANCE"] = "not defined"

        else:
            try:
                client = binance.Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
                candles = client.get_klines(
                    symbol="BTCUSDT", interval=client.KLINE_INTERVAL_1DAY
                )

                if len(candles) > 0:
                    logger.info("Binance key defined, test passed")
                    self.key_dict["BINANCE"] = "defined, test passed"
                else:
                    logger.info("Binance key defined, test failed")
                    self.key_dict["BINANCE"] = "defined, test failed"
            except Exception:
                logger.info("Binance key defined, test failed")
                self.key_dict["BINANCE"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["BINANCE"] + "\n")

    def check_bitquery_key(self, status: str = "", show_output: bool = False) -> None:
        """Check Bitquery key"""
        self.cfg_dict["BITQUERY"] = "bitquery"
        if not status:
            status = keys_model.check_bitquery_key(show_output=show_output)
        self.key_dict["BITQUERY"] = status

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
        self.cfg_dict["COINBASE"] = "coinbase"
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
            try:
                resp = make_coinbase_request("/accounts", auth=auth)
            except CoinbaseApiException:
                resp = None
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

    def check_glassnode_key(self, status: str = "", show_output: bool = False) -> None:
        """Check glassnode key"""
        self.cfg_dict["GLASSNODE"] = "glassnode"
        if not status:
            status = keys_model.check_glassnode_key(show_output=show_output)
        self.key_dict["GLASSNODE"] = status

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
            console.print(self.key_dict["CRYPTO_PANIC"] + "\n")

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

    def check_eodhd_key(self, show_output: bool = False) -> None:
        """Check End of Day Historical Data key"""
        self.cfg_dict["EODHD"] = "eodhd"
        if cfg.API_EODHD_TOKEN == "REPLACE_ME":  # nosec
            logger.info("End of Day Historical Data key not defined")
            self.key_dict["EODHD"] = "not defined"
        else:
            try:
                pyEX.Client(api_token=cfg.API_EODHD_TOKEN, version="v1")
                logger.info("End of Day Historical Data key defined, test passed")
                self.key_dict["EODHD"] = "defined, test passed"
            except PyEXception:
                logger.exception("End of Day Historical Data key defined, test failed")
                self.key_dict["EODHD"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["EODHD"] + "\n")

    def check_santiment_key(self, show_output: bool = False) -> None:
        """Check Santiment key"""
        self.cfg_dict["SANTIMENT"] = "santiment"
        if cfg.API_SANTIMENT_KEY == "REPLACE_ME":
            logger.info("santiment key not defined")
            self.key_dict["SANTIMENT"] = "not defined"
        else:
            headers = {
                "Content-Type": "application/graphql",
                "Authorization": f"Apikey {cfg.API_SANTIMENT_KEY}",
            }

            # pylint: disable=line-too-long
            data = '\n{{ getMetric(metric: "dev_activity"){{ timeseriesData( slug: "ethereum" from: ""2020-02-10T07:00:00Z"" to: "2020-03-10T07:00:00Z" interval: "1w"){{ datetime value }} }} }}'  # noqa: E501

            response = requests.post(
                "https://api.santiment.net/graphql", headers=headers, data=data
            )
            try:
                if response.status_code == 200:
                    logger.info("santiment key defined, test passed")
                    self.key_dict["SANTIMENT"] = "defined, test passed"
                else:
                    logger.warning("santiment key defined, test failed")
                    self.key_dict["SANTIMENT"] = "defined, test failed"
            except Exception as _:  # noqa: F841
                logger.exception("santiment key defined, test failed")
                self.key_dict["SANTIMENT"] = "defined, test failed"

        if show_output:
            console.print(self.key_dict["SANTIMENT"] + "\n")

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
        self.check_eodhd_key()
        self.check_santiment_key()

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
        ns_parser = parse_simple_args(parser, other_args)
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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_av_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_av_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_fmp_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_fmp_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_quandl_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_quandl_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_polygon_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_polygon_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_fred_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_fred_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_news_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_news_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_tradier_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_tradier_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_cmc_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_cmc_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_finnhub_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_finnhub_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_iex_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_iex_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:

            slash_components = "".join([f"/{val}" for val in self.queue])
            useragent = " ".join(ns_parser.user_agent) + " " + slash_components
            useragent = useragent.replace('"', "")
            self.queue = []

            status = keys_model.set_reddit_key(
                client_id=ns_parser.client_id,
                client_secret=ns_parser.client_secret,
                password=ns_parser.password,
                username=ns_parser.username,
                useragent=ns_parser.useragent,
                persist=True,
                show_output=True,
            )
            self.check_reddit_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_twitter_key(
                key=ns_parser.key, 
                secret_key=ns_parser.secret_key,
                bearer_token=ns_parser.bearer_token,
                persist=True, 
                show_output=True
            )
            self.check_twitter_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_rh_key(
                username=ns_parser.username,
                password=ns_parser.password,
                persist=True, 
                show_output=True
            )
            self.check_rh_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_DG_USERNAME"] = ns_parser.username
            dotenv.set_key(self.env_file, "OPENBB_DG_USERNAME", ns_parser.username)
            cfg.DG_USERNAME = ns_parser.username

            os.environ["OPENBB_DG_PASSWORD"] = ns_parser.password
            dotenv.set_key(self.env_file, "OPENBB_DG_PASSWORD", ns_parser.password)
            cfg.DG_PASSWORD = ns_parser.password

            if ns_parser.secret:
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
            help="account type ('live' or 'practice')",
        )
        if not other_args:
            console.print("For your API Key, visit: https://developer.oanda.com\n")
            return
        ns_parser = parse_simple_args(parser, other_args)
        if not ns_parser:
            return
        if ns_parser.account:
            os.environ["OPENBB_OANDA_ACCOUNT"] = ns_parser.account
            dotenv.set_key(self.env_file, "OPENBB_OANDA_ACCOUNT", ns_parser.account)
            cfg.OANDA_ACCOUNT = ns_parser.account
        if ns_parser.token:
            os.environ["OPENBB_OANDA_TOKEN"] = ns_parser.token
            dotenv.set_key(self.env_file, "OPENBB_OANDA_TOKEN", ns_parser.token)
            cfg.OANDA_TOKEN = ns_parser.token
        if ns_parser.account_type:
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
        ns_parser = parse_simple_args(parser, other_args)
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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_bitquery_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_bitquery_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
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
        ns_parser = parse_simple_args(parser, other_args)
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
        ns_parser = parse_simple_args(parser, other_args)
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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_glassnode_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.check_glassnode_key(status, show_output=False)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            print(type(ns_parser.key))
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
        ns_parser = parse_simple_args(parser, other_args)
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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_ETHPLORER_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_ETHPLORER_KEY", ns_parser.key)
            cfg.API_ETHPLORER_KEY = ns_parser.key

            self.check_ethplorer_key(show_output=True)

    @log_start_end(log=logger)
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
        ns_parser = parse_simple_args(parser, other_args)

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
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_MESSARI_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_MESSARI_KEY", ns_parser.key)
            cfg.API_MESSARI_KEY = ns_parser.key
            self.check_messari_key(show_output=True)

    @log_start_end(log=logger)
    def call_eodhd(self, other_args: List[str]):
        """Process eodhd command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="eodhd",
            description="Set End of Day Historical Data API key.",
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
                "For your API Key, visit: https://eodhistoricaldata.com/r/?ref=869U7F4J\n"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            os.environ["API_EODHD_TOKEN"] = ns_parser.key
            dotenv.set_key(self.env_file, "API_EODHD_TOKEN", ns_parser.key)
            cfg.API_EODHD_TOKEN = ns_parser.key
            self.check_eodhd_key(show_output=True)

    def call_santiment(self, other_args: List[str]):
        """Process santiment command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="santiment",
            description="Set Santiment API key.",
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
                "For your API Key, visit: "
                "https://academy.santiment.net/products-and-plans/create-an-api-key\n"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            os.environ["OPENBB_API_SANTIMENT_KEY"] = ns_parser.key
            dotenv.set_key(self.env_file, "OPENBB_API_SANTIMENT_KEY", ns_parser.key)
            cfg.API_SANTIMENT_KEY = ns_parser.key
            self.check_santiment_key(show_output=True)
