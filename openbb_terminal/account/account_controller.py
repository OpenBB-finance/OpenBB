import os
import json
import logging
import argparse
from typing import List, Dict
from pathlib import Path

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.decorators import log_start_end
from openbb_terminal.core.config.paths import (
    USER_ROUTINES_DIRECTORY,
    SETTINGS_DIRECTORY,
)
from openbb_terminal import feature_flags as obbff
from openbb_terminal.menu import session
from openbb_terminal.account import account_model

logger = logging.getLogger(__name__)


class AccountController(BaseController):
    """Account Controller Class"""

    CHOICES_COMMANDS = [
        "login",
        "register",
        "upload",
        "download",
        "send",
        "get",
    ]

    PATH = "/account/"

    def __init__(self, queue: List[str] = None):
        super().__init__(queue)
        dev = os.environ.get("DEBUG_MODE", "false") == "true"
        self.base_url = f"https://payments.openbb.{'dev' if dev else 'co'}"
        self.token: Dict[str, str] = {}
        self.ROUTINE_FILES: Dict[str, Path] = {}
        self.ROUTINE_CHOICES: Dict[str, None] = {}
        self.update_runtime_choices()
        login_file = SETTINGS_DIRECTORY / "login.json"
        if login_file.exists():
            with open(login_file) as file:
                self.token = json.load(file)

    def update_runtime_choices(self):
        """Update runtime choices"""
        self.ROUTINE_FILES = {
            filepath.name: filepath
            for filepath in USER_ROUTINES_DIRECTORY.rglob("*.openbb")
        }
        self.ROUTINE_CHOICES = {filename: None for filename in self.ROUTINE_FILES}
        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["send"] = self.ROUTINE_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

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
        mt.add_info("_settings_")
        mt.add_cmd("upload")
        mt.add_cmd("download")
        mt.add_raw("\n")
        mt.add_info("_scripts_")
        mt.add_cmd("send")
        mt.add_cmd("get")
        console.print(text=mt.menu_text, menu="Account")

    @log_start_end(log=logger)
    def call_login(self, other_args: List[str]):
        """Login"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="login",
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

        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.token = account_model.get_login(
                ns_parser.email, ns_parser.password, self.base_url
            )

    @log_start_end(log=logger)
    def call_register(self, _):
        """Register"""
        account_model.get_register()

    @log_start_end(log=logger)
    def call_upload(self, _):
        account_model.get_upload(self.get_token(), self.base_url)

    @log_start_end(log=logger)
    def call_download(self, _):
        account_model.get_download(self.get_token(), self.base_url)

    @log_start_end(log=logger)
    def call_send(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="send",
            description="Load custom dataset (from previous export, custom imports).",
        )
        parser.add_argument(
            "-n",
            "--name",
            help="Name for the script.",
            default="",
            type=str,
        )
        parser.add_argument(
            "-f",
            "--file",
            help="Script to submit.",
            choices=self.ROUTINE_FILES.keys(),
            required="-h" not in other_args,
            type=str,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            account_model.get_send(
                self.get_token(), ns_parser.file, ns_parser.name, self.base_url
            )

    @log_start_end(log=logger)
    def call_get(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="send",
            description="Load custom dataset (from previous export, custom imports).",
        )
        parser.add_argument(
            "-n",
            "--name",
            help="Name for the script.",
            default="",
            type=str,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            account_model.get_get(self.get_token(), ns_parser.name, self.base_url)
