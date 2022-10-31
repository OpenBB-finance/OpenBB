import os
import logging
import argparse
import webbrowser
from typing import List, Dict
import requests

from openbb_terminal import feature_flags as obbff
from openbb_terminal import config_terminal as cfg
from openbb_terminal import config_plot as cfg_plot
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import parse_simple_args, get_user_timezone
from openbb_terminal.account import account_helpers as ah

logger = logging.getLogger(__name__)


class AccountController(BaseController):
    """Account Controller Class"""

    CHOICES_COMMANDS = [
        "login",
        "register",
        "upload",
        "download",
    ]

    PATH = "/account/"

    def __init__(self, queue: List[str] = None):
        super().__init__(queue)
        dev = os.environ.get("DEBUG_MODE", "false") == "true"
        self.base_url = f"https://payments.openbb.{'dev' if dev else 'co'}"
        self.token: Dict[str, str] = {}

    def get_token(self):
        """Get token"""

        if not self.token:
            return ""
        return f"{self.token['token_type'].title()} {self.token['access_token']}"

    def print_help(self):
        """Print help"""

        mt = MenuText("account/", 100)
        mt.add_info("_auth_")
        mt.add_cmd("login")
        mt.add_cmd("register")
        mt.add_raw("\n")
        mt.add_info("_save_")
        mt.add_cmd("upload")
        mt.add_cmd("download")
        console.print(text=mt.menu_text, menu="Account")

    @log_start_end(log=logger)
    def call_login(self, other_args: List[str]):
        """Login"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="reddit",
            description="Login to your openbb account",
        )
        parser.add_argument(
            "-e",
            "--email",
            type=str,
            dest="email",
            help="The email for the user",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            dest="password",
            help="The password for the user",
            required="-h" not in other_args,
        )

        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            data = {
                "email": ns_parser.email,
                "password": ns_parser.password,
                "remember": True,
            }
            response = requests.post(self.base_url + "/terminal/login", json=data)
            code = response.status_code
            if code == 200:
                console.print("Login successful\n")
                self.token = response.json()
            elif code == 401:
                console.print(f"[red]{response.json()['detail']}[/red]\n")
            elif code == 403:
                console.print(f"[red]{response.json()['message']}[/red]\n")
            else:
                console.print("[red]Unknown error[/red]\n")

    @log_start_end(log=logger)
    def call_register(self, _):
        """Register"""
        webbrowser.open("https://my.openbb.dev/register")

    @log_start_end(log=logger)
    def call_upload(self, _):
        # TODO: add colors
        if self.token == {}:
            console.print("You need to login first\n")
            return

        features_settings = {
            "OPENBB_USE_DATETIME": obbff.USE_DATETIME,
            "OPENBB_PREFERRED_DATA_SOURCE_FILE": obbff.PREFERRED_DATA_SOURCE_FILE,
            "OPENBB_USE_PLOT_AUTOSCALING": obbff.USE_PLOT_AUTOSCALING,
            "OPENBB_PLOT_DPI": cfg_plot.PLOT_DPI,
            "OPENBB_PLOT_HEIGHT": cfg_plot.PLOT_HEIGHT,
            "OPENBB_PLOT_WIDTH": cfg_plot.PLOT_WIDTH,
            "OPENBB_PLOT_HEIGHT_PERCENTAGE": cfg_plot.PLOT_HEIGHT_PERCENTAGE,
            "OPENBB_PLOT_WIDTH_PERCENTAGE": cfg_plot.PLOT_WIDTH_PERCENTAGE,
            "OPENBB_MONITOR": cfg_plot.MONITOR,
            "OPENBB_BACKEND": cfg_plot.BACKEND,
            "OPENBB_USE_LANGUAGE": obbff.USE_LANGUAGE,
            "OPENBB_TIMEZONE": get_user_timezone(),
            "OPENBB_USE_FLAIR": obbff.USE_FLAIR,
        }
        features_keys = {
            "OPENBB_API_KEY_ALPHAVANTAGE": cfg.API_KEY_ALPHAVANTAGE,
            "OPENBB_API_KEY_FINANCIALMODELINGPREP": cfg.API_KEY_FINANCIALMODELINGPREP,
            "OPENBB_API_KEY_QUANDL": cfg.API_KEY_QUANDL,
            "OPENBB_API_POLYGON_KEY": cfg.API_POLYGON_KEY,
            "OPENBB_API_FRED_KEY": cfg.API_FRED_KEY,
            "OPENBB_API_NEWS_TOKEN": cfg.API_NEWS_TOKEN,
            "OPENBB_API_TRADIER_TOKEN": cfg.API_TRADIER_TOKEN,
            "OPENBB_API_CMC_KEY": cfg.API_CMC_KEY,
            "OPENBB_API_FINNHUB_KEY": cfg.API_FINNHUB_KEY,
            "OPENBB_API_IEX_TOKEN": cfg.API_IEX_TOKEN,
            "OPENBB_API_REDDIT_CLIENT_ID": cfg.API_REDDIT_CLIENT_ID,
            "OPENBB_API_REDDIT_CLIENT_SECRET": cfg.API_REDDIT_CLIENT_SECRET,
            "OPENBB_API_REDDIT_PASSWORD": cfg.API_REDDIT_PASSWORD,
            "OPENBB_API_REDDIT_USERNAME": cfg.API_REDDIT_USERNAME,
            "OPENBB_API_REDDIT_USER_AGENT": cfg.API_REDDIT_USER_AGENT,
            "OPENBB_API_TWITTER_KEY": cfg.API_TWITTER_KEY,
            "OPENBB_API_TWITTER_SECRET_KEY": cfg.API_TWITTER_SECRET_KEY,
            "OPENBB_API_TWITTER_BEARER_TOKEN": cfg.API_TWITTER_BEARER_TOKEN,
            "OPENBB_RH_USERNAME": cfg.RH_USERNAME,
            "OPENBB_RH_PASSWORD": cfg.RH_PASSWORD,
            "OPENBB_DG_USERNAME": cfg.DG_USERNAME,
            "OPENBB_DG_PASSWORD": cfg.DG_PASSWORD,
            "OPENBB_DG_TOTP_SECRET": cfg.DG_TOTP_SECRET,
            "OPENBB_OANDA_ACCOUNT": cfg.OANDA_ACCOUNT,
            "OPENBB_OANDA_TOKEN": cfg.OANDA_TOKEN,
            "OPENBB_OANDA_ACCOUNT_TYPE": cfg.OANDA_ACCOUNT_TYPE,
            "OPENBB_API_BINANCE_KEY": cfg.API_BINANCE_KEY,
            "OPENBB_API_BINANCE_SECRET": cfg.API_BINANCE_SECRET,
            "OPENBB_API_BITQUERY_KEY": cfg.API_REDDIT_USER_AGENT,
            "OPENBB_API_SENTIMENTINVESTOR_TOKEN": cfg.API_SENTIMENTINVESTOR_TOKEN,
            "OPENBB_API_COINBASE_KEY": cfg.API_COINBASE_KEY,
            "OPENBB_API_COINBASE_SECRET": cfg.API_COINBASE_SECRET,
            "OPENBB_API_COINBASE_PASS_PHRASE": cfg.API_COINBASE_PASS_PHRASE,
            "OPENBB_API_WHALE_ALERT_KEY": cfg.API_WHALE_ALERT_KEY,
            "OPENBB_API_GLASSNODE_KEY": cfg.API_GLASSNODE_KEY,
            "OPENBB_API_COINGLASS_KEY": cfg.API_COINGLASS_KEY,
            "OPENBB_API_CRYPTO_PANIC_KEY": cfg.API_CRYPTO_PANIC_KEY,
            "OPENBB_API_ETHPLORER_KEY": cfg.API_ETHPLORER_KEY,
            "OPENBB_API_SMARTSTAKE_KEY": cfg.API_SMARTSTAKE_KEY,
            "OPENBB_API_SMARTSTAKE_TOKEN": cfg.API_SMARTSTAKE_TOKEN,
            "OPENBB_API_GITHUB_KEY": cfg.API_GITHUB_KEY,
            "OPENBB_API_MESSARI_KEY": cfg.API_MESSARI_KEY,
            "OPENBB_API_EODHD_KEY": cfg.API_EODHD_KEY,
            "OPENBB_API_SANTIMENT_KEY": cfg.API_SANTIMENT_KEY,
            "OPENBB_API_TOKEN_TERMINAL_KEY": cfg.API_TOKEN_TERMINAL_KEY,
            "OPENBB_API_SHROOM_KEY": cfg.API_SHROOM_KEY,
            "OPENBB_API_STOCKSERA_KEY": cfg.API_STOCKSERA_KEY,
        }
        features_settings = ah.clean_keys_dict(features_settings)
        features_keys = ah.clean_keys_dict(features_keys)
        data = {
            "features_settings": features_settings,
            "features_keys": features_keys,
        }
        response = requests.put(
            self.base_url + "/terminal/user",
            json=data,
            headers={"Authorization": self.get_token()},
        )
        if response.status_code == 200:
            console.print("Successfully uploaded your settings and keys.")
        else:
            console.print("[red]Error uploading your settings and keys.[/red]")

    @log_start_end(log=logger)
    def call_download(self, _):
        # TODO: add colors
        if self.token == {}:
            console.print("You need to login first\n")
            return

        response = requests.get(
            self.base_url + "/terminal/user",
            headers={"Authorization": self.get_token()},
        )
        if response.status_code != 200:
            console.print("[red]Error downloading your settings and keys.[/red]")
            return

        print(response.json())
