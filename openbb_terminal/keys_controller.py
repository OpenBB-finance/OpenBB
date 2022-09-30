"""Keys Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines

import argparse
import logging
from typing import Dict, List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal import keys_model
from openbb_terminal.core.config.paths import USER_ENV_FILE
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import parse_simple_args
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText, translate

logger = logging.getLogger(__name__)


class KeysController(BaseController):  # pylint: disable=too-many-public-methods
    """Keys Controller class"""

    API_LIST: List[str] = [
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
    CHOICES_COMMANDS: List[str] = API_LIST + []
    PATH = "/keys/"
    key_dict: Dict = {}
    alias_dict: Dict = {
        "av": "ALPHA_VANTAGE",
        "fmp": "FINANCIAL_MODELING_PREP",
        "quandl": "QUANDL",
        "polygon": "POLYGON",
        "fred": "FRED",
        "news": "NEWSAPI",
        "tradier": "TRADIER",
        "cmc": "COINMARKETCAP",
        "finnhub": "FINNHUB",
        "iex": "IEXCLOUD",
        "reddit": "REDDIT",
        "twitter": "TWITTER",
        "rh": "ROBINHOOD",
        "degiro": "DEGIRO",
        "oanda": "OANDA",
        "binance": "BINANCE",
        "bitquery": "BITQUERY",
        "si": "SENTIMENT_INVESTOR",
        "coinbase": "COINBASE",
        "walert": "WHALE_ALERT",
        "glassnode": "GLASSNODE",
        "coinglass": "COINGLASS",
        "cpanic": "CRYPTO_PANIC",
        "ethplorer": "ETHPLORER",
        "smartstake": "SMARTSTAKE",
        "github": "GITHUB",
        "eodhd": "EODHD",
        "messari": "MESSARI",
        "santiment": "SANTIMENT",
    }

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

    def check_keys_status(self) -> None:
        """Check keys status"""

        for api in self.API_LIST:
            status = getattr(keys_model, "check_" + str(api) + "_key")()
            self.key_dict[api] = keys_model.STATUS_MSG[status]

    def print_help(self):
        """Print help"""
        self.check_keys_status()
        mt = MenuText("keys/")
        mt.add_info("_keys_")
        mt.add_raw("\n")
        for cmd_name, status_msg in self.key_dict.items():
            alias_name = self.alias_dict[cmd_name]
            c = "red"
            if status_msg == "defined, test passed":
                c = "green"
            elif status_msg == "defined":
                c = "green"
            elif status_msg == "defined, test inconclusive":
                c = "yellow"
            elif status_msg == "not defined":
                c = "grey30"
            mt.add_raw(
                f"   [cmds]{cmd_name}[/cmds] {(20 - len(cmd_name)) * ' '}"
                f" [{c}] {alias_name} {(25 - len(alias_name)) * ' '} {translate(status_msg)} [/{c}]\n"
            )

        console.print(text=mt.menu_text, menu="Keys")

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
            self.key_dict["av"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["fmp"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["quandl"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["polygon"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["fred"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["news"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["tradier"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["cmc"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["finnhub"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["iex"] = keys_model.STATUS_MSG[status]

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
                useragent=useragent,
                persist=True,
                show_output=True,
            )
            self.key_dict["reddit"] = keys_model.STATUS_MSG[status]

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
            dest="secret",
            help="Secret key",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            dest="token",
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
                secret=ns_parser.secret,
                access_token=ns_parser.token,
                persist=True,
                show_output=True,
            )
            self.key_dict["twitter"] = keys_model.STATUS_MSG[status]

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
                show_output=True,
            )
            self.key_dict["rh"] = keys_model.STATUS_MSG[status]

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
            default="",
        )
        if not other_args:
            console.print("For your API Key, visit: https://www.degiro.fr\n")
            return
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_degiro_key(
                username=ns_parser.username,
                password=ns_parser.password,
                secret=ns_parser.secret,
                persist=True,
                show_output=True,
            )
            self.key_dict["degiro"] = keys_model.STATUS_MSG[status]

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
        if ns_parser:
            status = keys_model.set_oanda_key(
                account=ns_parser.account,
                access_token=ns_parser.token,
                account_type=ns_parser.account_type,
                persist=True,
                show_output=True,
            )
            self.key_dict["oanda"] = keys_model.STATUS_MSG[status]

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
            dest="secret",
            help="Secret key",
        )
        if not other_args:
            console.print("For your API Key, visit: https://binance.com\n")
            return
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_binance_key(
                key=ns_parser.key,
                secret=ns_parser.secret,
                persist=True,
                show_output=True,
            )
            self.key_dict["binance"] = keys_model.STATUS_MSG[status]

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
            self.key_dict["bitquery"] = keys_model.STATUS_MSG[status]

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
            "-t",
            "--token",
            type=str,
            dest="token",
            help="token",
        )
        if not other_args:
            console.print("For your API Key, visit: https://sentimentinvestor.com\n")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            status = keys_model.set_si_key(
                access_token=ns_parser.token, persist=True, show_output=True
            )
            self.key_dict["si"] = keys_model.STATUS_MSG[status]

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
            dest="secret",
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
            status = keys_model.set_coinbase_key(
                key=ns_parser.key,
                secret=ns_parser.secret,
                passphrase=ns_parser.passphrase,
                persist=True,
                show_output=True,
            )
            self.key_dict["coinbase"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_walert_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["walert"] = keys_model.STATUS_MSG[status]

    @log_start_end(log=logger)
    def call_glassnode(self, other_args: List[str]):
        """Process glassnode command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="glassnode",
            description="Set Glassnode API key.",
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
            self.key_dict["glassnode"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_coinglass_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["coinglass"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_cpanic_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["cpanic"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_ethplorer_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["ethplorer"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_smartstake_key(
                key=ns_parser.key,
                access_token=ns_parser.token,
                persist=True,
                show_output=True,
            )
            self.key_dict["smartstake"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_github_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["github"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_messari_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["messari"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_eodhd_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["eodhd"] = keys_model.STATUS_MSG[status]

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
            status = keys_model.set_santiment_key(
                key=ns_parser.key, persist=True, show_output=True
            )
            self.key_dict["santiment"] = keys_model.STATUS_MSG[status]
