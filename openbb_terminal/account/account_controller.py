import os
import logging
import argparse
import webbrowser
from typing import List, Dict
import requests

from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.decorators import log_start_end
from openbb_terminal.account import account_helpers as ah
from openbb_terminal.account import account_statics
from openbb_terminal.helper_funcs import parse_simple_args
from openbb_terminal import keys_model

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

        settings = account_statics.features_settings
        keys = account_statics.features_keys
        features_settings = ah.clean_keys_dict(settings)
        features_keys = ah.clean_keys_dict(keys)
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

        info = response.json()
        settings = info["features_settings"]
        keys = info["features_keys"]
        for key, value in settings.items():
            if key in account_statics.features_settings_objects and value:
                obj = account_statics.features_settings_objects[key]
                setattr(obj, key.replace("OPENBB_", ""), value)
                keys_model.set_key(key, value, True)
        for key, value in keys.items():
            if value:
                keys_model.set_key(key, value, True)

        console.print("Successfully downloaded your settings and keys.")
