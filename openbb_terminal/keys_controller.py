"""Keys Controller Module"""
__docformat__ = "numpy"

# pylint: disable=too-many-lines

import argparse
import logging
from typing import Callable, Dict, List, Optional

from openbb_terminal import keys_model, keys_view
from openbb_terminal.core.session.constants import BackendEnvironment
from openbb_terminal.core.session.current_user import get_current_user, is_local
from openbb_terminal.core.session.env_handler import get_reading_order
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import (
    MenuText,
    console,
    optional_rich_track,
    translate,
)

logger = logging.getLogger(__name__)


class KeysController(BaseController):  # pylint: disable=too-many-public-methods
    """Keys Controller class"""

    API_DICT = keys_model.API_DICT
    API_LIST = list(API_DICT.keys())
    CHOICES_COMMANDS: List[str] = ["mykeys", "status"] + API_LIST
    PATH = "/keys/"
    status_dict: Dict = {}
    help_status_text: str = ""

    def __init__(
        self,
        queue: Optional[List[str]] = None,
        menu_usage: bool = True,
    ):
        """Constructor"""
        super().__init__(queue)
        if menu_usage and session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def get_check_keys_function(self, key: str) -> Callable:
        """Get check `key` function from keys_model"""
        return getattr(keys_model, f"check_{key}_key")

    def check_keys_status(self, reevaluate: bool = False) -> None:
        """Check keys status"""
        if not self.status_dict or reevaluate:
            for api in optional_rich_track(self.API_LIST, desc="Checking keys status"):
                try:
                    self.status_dict[api] = self.get_check_keys_function(api)()
                except Exception:
                    self.status_dict[api] = str(
                        keys_model.KeyStatus.DEFINED_TEST_INCONCLUSIVE
                    )

    def get_source_hierarchy(self) -> str:
        """Hierarchy is equivalent to reverse order of reading .env files.

        Returns
        -------
        str
            Source priority string.
        """
        reading_order = get_reading_order()
        hierarchy = "\n        ".join(list(map(str, reversed(reading_order))))
        return (
            hierarchy
            if is_local()
            else f"{BackendEnvironment.HUB_URL + 'app/terminal/api-keys'}\n        {hierarchy}"
        )

    def print_help(self, update_status: bool = True, reevaluate: bool = True):
        """Print help"""
        self.check_keys_status(reevaluate=reevaluate)
        mt = MenuText("keys/")
        mt.add_param(
            "_source",
            self.get_source_hierarchy(),
        )
        mt.add_raw("\n")
        mt.add_info("_keys_")
        mt.add_raw("\n")
        mt.add_cmd("mykeys")
        mt.add_cmd("status")
        mt.add_raw("\n")
        mt.add_info("_status_")

        status_color_map = {
            keys_model.KeyStatus.DEFINED_TEST_PASSED.value: "green",
            keys_model.KeyStatus.DEFINED_TEST_FAILED.value: "red",
            keys_model.KeyStatus.DEFINED_NOT_TESTED.value: "yellow",
            keys_model.KeyStatus.DEFINED_TEST_INCONCLUSIVE.value: "yellow",
            keys_model.KeyStatus.NOT_DEFINED.value: "grey30",
        }

        if not self.help_status_text or update_status:
            for cmd_name, status_msg in self.status_dict.items():
                api_name = self.API_DICT[cmd_name]

                c = status_color_map.get(status_msg, "grey30")
                clean_status_msg = status_msg or keys_model.KeyStatus.NOT_DEFINED.value

                mt.add_raw(
                    f"    [cmds]{cmd_name}[/cmds] {(20 - len(cmd_name)) * ' '}"
                    f" [{c}] {api_name} {(25 - len(api_name)) * ' '} {translate(clean_status_msg)} [/{c}]\n"
                )
            self.help_status_text = mt.menu_text

        console.print(text=self.help_status_text, menu="Keys")

    @log_start_end(log=logger)
    def call_mykeys(self, other_args: List[str]):
        """Display current keys"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mykeys",
            description="Display current keys.",
        )
        parser.add_argument(
            "-s",
            "--show",
            type=bool,
            dest="show",
            help="See keys in raw text instead of the default protected display.",
            default=False,
        )
        if other_args and "-s" in other_args[0]:
            other_args.insert(1, "True")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            keys_view.display_keys(
                show=ns_parser.show,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_status(self, other_args: List[str]):
        """Display current keys status with the option to force the check"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="status",
            description="Reevaluate keys status.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="Force the status to reevaluate for a specific key.",
            default=None,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        is_key = bool(ns_parser and ns_parser.key)

        if is_key:
            if ns_parser.key in self.API_LIST:
                try:
                    status = self.get_check_keys_function(ns_parser.key)(True)
                    self.status_dict[ns_parser.key] = status
                    console.print("")
                except Exception:
                    status = keys_model.KeyStatus.DEFINED_TEST_INCONCLUSIVE
                    self.status_dict[ns_parser.key] = str(status)
                    console.print(f"{status.colorize()}\n")
            else:
                console.print(f"[red]Key `{ns_parser.key}` is not a valid key.[/red]")
                return

        if "-h" not in other_args and "--help" not in other_args:
            self.print_help(update_status=True, reevaluate=not is_key)

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
                "For your API Key, visit: https://www.alphavantage.co/support/#api-key"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["av"] = keys_model.set_av_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://financialmodelingprep.com")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["fmp"] = keys_model.set_fmp_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://www.quandl.com")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["quandl"] = keys_model.set_quandl_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://polygon.io")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["polygon"] = keys_model.set_polygon_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_intrinio(self, other_args: List[str]):
        """Process polygon command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="intrinio",
            description="Set Intrinio API key.",
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
                "For your API Key, sign up for a subscription: https://intrinio.com/starter-plan\n"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["intrinio"] = keys_model.set_intrinio_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://fred.stlouisfed.org")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["fred"] = keys_model.set_fred_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://newsapi.org")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["news"] = keys_model.set_news_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_biztoc(self, other_args: List[str]):
        """Process BizToc API command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="news",
            description="Set BizToc API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, visit: https://api.biztoc.com")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["biztoc"] = keys_model.set_biztoc_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://developer.tradier.com")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["tradier"] = keys_model.set_tradier_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://coinmarketcap.com")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["cmc"] = keys_model.set_cmc_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://finnhub.io")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["finnhub"] = keys_model.set_finnhub_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="client_secret",
            help="Client Secret",
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            dest="username",
            help="Username",
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="Password",
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-a",
            "--agent",
            type=str,
            dest="user_agent",
            help="User agent",
            required="-h" not in other_args and "--help" not in other_args,
            nargs="+",
        )
        if not other_args:
            console.print("For your API Key, visit: https://www.reddit.com")
            return
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            slash_components = "".join([f"/{val}" for val in self.queue])
            useragent = " ".join(ns_parser.user_agent) + " " + slash_components
            useragent = useragent.replace('"', "")
            self.queue = []

            self.status_dict["reddit"] = keys_model.set_reddit_key(
                client_id=ns_parser.client_id,
                client_secret=ns_parser.client_secret,
                password=ns_parser.password,
                username=ns_parser.username,
                useragent=useragent,
                persist=True,
                show_output=True,
            )

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
            console.print("For your API Key, visit: https://robinhood.com/us/en/")
            return
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["rh"] = keys_model.set_rh_key(
                username=ns_parser.username,
                password=ns_parser.password,
                persist=True,
                show_output=True,
            )

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
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="password",
            required="-h" not in other_args and "--help" not in other_args,
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
            console.print("For your API Key, visit: https://www.degiro.fr")
            return
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["degiro"] = keys_model.set_degiro_key(
                username=ns_parser.username,
                password=ns_parser.password,
                secret=ns_parser.secret,
                persist=True,
                show_output=True,
            )

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
            console.print("For your API Key, visit: https://developer.oanda.com")
            return
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["oanda"] = keys_model.set_oanda_key(
                account=ns_parser.account,
                access_token=ns_parser.token,
                account_type=ns_parser.account_type,
                persist=True,
                show_output=True,
            )

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
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="secret",
            help="Secret key",
            required="-h" not in other_args and "--help" not in other_args,
        )
        if not other_args:
            console.print("For your API Key, visit: https://binance.com")
            return
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["binance"] = keys_model.set_binance_key(
                key=ns_parser.key,
                secret=ns_parser.secret,
                persist=True,
                show_output=True,
            )

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
            console.print("For your API Key, visit: https://bitquery.io/")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["bitquery"] = keys_model.set_bitquery_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--secret",
            type=str,
            dest="secret",
            help="Secret key",
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-p",
            "--passphrase",
            type=str,
            dest="passphrase",
            help="Passphrase",
            required="-h" not in other_args and "--help" not in other_args,
        )
        if not other_args:
            console.print("For your API Key, visit: https://docs.pro.coinbase.com/")
            return
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["coinbase"] = keys_model.set_coinbase_key(
                key=ns_parser.key,
                secret=ns_parser.secret,
                passphrase=ns_parser.passphrase,
                persist=True,
                show_output=True,
            )

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
            console.print("For your API Key, visit: https://docs.whale-alert.io/")
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["walert"] = keys_model.set_walert_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
                "For your API Key, visit: https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key/"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["glassnode"] = keys_model.set_glassnode_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
                "For your API Key, visit: https://coinglass.github.io/API-Reference/#api-key"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["coinglass"] = keys_model.set_coinglass_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
                "For your API Key, visit: https://cryptopanic.com/developers/api/"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["cpanic"] = keys_model.set_cpanic_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
                "For your API Key, visit: https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["ethplorer"] = keys_model.set_ethplorer_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            required="-h" not in other_args and "--help" not in other_args,
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            dest="token",
            help="Token",
            required="-h" not in other_args and "--help" not in other_args,
        )
        if not other_args:
            console.print("For your API Key, visit: https://www.smartstake.io")
            return
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            self.status_dict["smartstake"] = keys_model.set_smartstake_key(
                key=ns_parser.key,
                access_token=ns_parser.token,
                persist=True,
                show_output=True,
            )

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
                "For your API Key, visit: https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["github"] = keys_model.set_github_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
            console.print("For your API Key, visit: https://messari.io/api/docs")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["messari"] = keys_model.set_messari_key(
                key=ns_parser.key, persist=True, show_output=True
            )

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
                "For your API Key, visit: https://eodhistoricaldata.com/r/?ref=869U7F4J"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["eodhd"] = keys_model.set_eodhd_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
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
                "https://academy.santiment.net/products-and-plans/create-an-api-key"
            )
            return
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["santiment"] = keys_model.set_santiment_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_tokenterminal(self, other_args: List[str]):
        """Process tokenterminal command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tokenterminal",
            description="Set Token Terminal API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, visit: https://tokenterminal.com/")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["tokenterminal"] = keys_model.set_tokenterminal_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_stocksera(self, other_args: List[str]):
        """Process stocksera command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stocksera",
            description="Set Stocksera API key.",
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
                "For your API Key, https://stocksera.pythonanywhere.com/accounts/developers"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["stocksera"] = keys_model.set_stocksera_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_databento(self, other_args: List[str]):
        """Process databento command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="databento",
            description="Set DataBento API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, https://databento.com")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["databento"] = keys_model.set_databento_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_openai(self, other_args: List[str]):
        """Process openai command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="openai",
            description="Set OpenAI API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, https://openai.com")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")

        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            self.status_dict["openai"] = keys_model.set_openai_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_ultima(self, other_args: List[str]):
        """Process ultima command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ultima",
            description="Set Ultima Insights API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, https://ultimainsights.ai/")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["ultima"] = keys_model.set_ultima_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_dappradar(self, other_args: List[str]):
        """Process dappradar command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dappradar",
            description="Set DappRadar API key.",
        )
        parser.add_argument(
            "-k",
            "--key",
            type=str,
            dest="key",
            help="key",
        )
        if not other_args:
            console.print("For your API Key, visit: https://dappradar.com/api")
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["dappradar"] = keys_model.set_dappradar_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_companieshouse(self, other_args: List[str]):
        """Process companies house command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="companieshouse",
            description="Set Companies House API key.",
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
                "For your API Key, visit: https://developer.company-information.service.gov.uk/overview"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["companieshouse"] = keys_model.set_companieshouse_key(
                key=ns_parser.key, persist=True, show_output=True
            )

    @log_start_end(log=logger)
    def call_nixtla(self, other_args: List[str]):
        """Process nixtla command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="nixtla",
            description="Set Nixtla API key.",
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
                "For your API Key, visit: https://docs.nixtla.io/docs/getting-started"
            )
            return

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-k")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.status_dict["nixtla"] = keys_model.set_nixtla_key(
                key=ns_parser.key, persist=True, show_output=True
            )
