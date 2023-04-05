import argparse
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from openbb_terminal.account.account_model import (
    get_routines_info,
    set_login_called,
)
from openbb_terminal.account.account_view import display_routines_list
from openbb_terminal.core.session import (
    hub_model as Hub,
    local_model as Local,
)
from openbb_terminal.core.session.current_user import (
    get_current_user,
    is_local,
)
from openbb_terminal.core.session.session_model import logout
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import check_positive
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.terminal_helper import print_guest_block_msg

logger = logging.getLogger(__name__)


class AccountController(BaseController):
    """Account Controller Class"""

    CHOICES_COMMANDS = [
        "login",
        "logout",
        "clear",
        "list",
        "upload",
        "download",
        "delete",
        "generate",
        "show",
        "revoke",
    ]

    PATH = "/account/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)
        self.ROUTINE_FILES: Dict[str, Path] = {}
        self.REMOTE_CHOICES: List[str] = []
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            self.choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def update_runtime_choices(self):
        """Update runtime choices"""
        self.ROUTINE_FILES = self.get_routines()
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            self.choices["upload"]["--file"].update({c: {} for c in self.ROUTINE_FILES})
            self.choices["download"]["--name"].update(
                {c: {} for c in self.REMOTE_CHOICES}
            )
            self.choices["delete"]["--name"].update(
                {c: {} for c in self.REMOTE_CHOICES}
            )
            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def get_routines(self):
        """Get routines"""
        current_user = get_current_user()
        routines = {
            filepath.name: filepath
            for filepath in current_user.preferences.USER_ROUTINES_DIRECTORY.glob(
                "*.openbb"
            )
        }
        user_folder = (
            current_user.preferences.USER_ROUTINES_DIRECTORY
            / get_current_user().profile.get_uuid()
        )
        if os.path.exists(user_folder):
            routines.update(
                {filepath.name: filepath for filepath in user_folder.rglob("*.openbb")}
            )
        return routines

    def print_help(self):
        """Print help"""
        mt = MenuText("account/", 100)
        mt.add_info("_info_")
        mt.add_cmd("clear")
        mt.add_raw("\n")
        mt.add_info("_routines_")
        mt.add_cmd("list")
        mt.add_cmd("upload")
        mt.add_cmd("download")
        mt.add_cmd("delete")
        mt.add_raw("\n")
        mt.add_info("_personal_access_token_")
        mt.add_cmd("generate")
        mt.add_cmd("show")
        mt.add_cmd("revoke")
        mt.add_raw("\n")
        mt.add_info("_authentication_")
        mt.add_cmd("login")
        mt.add_cmd("logout")
        self.update_runtime_choices()
        console.print(text=mt.menu_text, menu="Account")

    @log_start_end(log=logger)
    def call_login(self, other_args: List[str]) -> None:
        """Process login command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="login",
            description="Login into new session.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if not is_local() and "-h" not in other_args and "--help" not in other_args:
            console.print("[info]You are already logged in.[/info]")
        else:
            if ns_parser:
                set_login_called(True)

    @log_start_end(log=logger)
    def call_logout(self, other_args: List[str]) -> None:
        """Process logout command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="logout",
            description="Logout from current session.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                current_user = get_current_user()
                logout(
                    auth_header=current_user.profile.get_auth_header(),
                    token=current_user.profile.get_token(),
                    guest=is_local(),
                    cls=True,
                )
                self.print_help()

    @log_start_end(log=logger)
    def call_clear(self, other_args: List[str]):
        """Clear data"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clear",
            description="Clear stored configurations from the cloud.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                i = console.input(
                    "[bold red]This action is irreversible![/bold red]\n"
                    "Are you sure you want to permanently delete your keys? (y/n): "
                )
                console.print("")
                if i.lower() in ["y", "yes"]:
                    Hub.clear_user_configs(
                        config="features_keys",
                        auth_header=get_current_user().profile.get_auth_header(),
                    )
                else:
                    console.print("[info]Aborted.[/info]")

    @log_start_end(log=logger)
    def call_list(self, other_args: List[str]):
        """List routines"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="list",
            description="List routines available in the cloud.",
        )
        parser.add_argument(
            "-p",
            "--page",
            type=check_positive,
            dest="page",
            default=1,
            help="The page number.",
        )
        parser.add_argument(
            "-s",
            "--size",
            type=check_positive,
            dest="size",
            default=10,
            help="The number of results per page.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                response = Hub.list_routines(
                    auth_header=get_current_user().profile.get_auth_header(),
                    page=ns_parser.page,
                    size=ns_parser.size,
                )
                df, page, pages = get_routines_info(response)
                if not df.empty:
                    self.REMOTE_CHOICES += list(df["name"])
                    self.update_runtime_choices()
                    display_routines_list(df, page, pages)
                else:
                    console.print("[red]No routines found.[/red]")

    @log_start_end(log=logger)
    def call_upload(self, other_args: List[str]):
        """Upload"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="upload",
            description="Upload a routine to the cloud.",
        )
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            dest="file",
            required="-h" not in other_args
            and "--help" not in other_args
            and not is_local(),
            help="The file to be loaded",
            metavar="FILE",
            nargs="+",
        )
        parser.add_argument(
            "-d",
            "--description",
            type=str,
            dest="description",
            help="The description of the routine",
            default="",
            nargs="+",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            help="The name of the routine.",
            nargs="+",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                routine = Local.get_routine(file_name=" ".join(ns_parser.file))
                if routine:
                    description = " ".join(ns_parser.description)

                    name = (
                        " ".join(ns_parser.name)
                        if ns_parser.name
                        else " ".join(ns_parser.file).split(sep=".openbb", maxsplit=-1)[
                            0
                        ]
                    )

                    current_user = get_current_user()

                    response = Hub.upload_routine(
                        auth_header=current_user.profile.get_auth_header(),
                        name=name,
                        description=description,
                        routine=routine,
                    )
                    if response is not None and response.status_code == 409:
                        i = console.input(
                            "A routine with the same name already exists, "
                            "do you want to replace it? (y/n): "
                        )
                        console.print("")
                        if i.lower() in ["y", "yes"]:
                            response = Hub.upload_routine(
                                auth_header=current_user.profile.get_auth_header(),
                                name=name,
                                description=description,
                                routine=routine,
                                override=True,
                            )
                        else:
                            console.print("[info]Aborted.[/info]")

                    if response and response.status_code == 200:
                        self.REMOTE_CHOICES.append(name)
                        self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_download(self, other_args: List[str]):
        """Download"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="download",
            description="Download a routine from the cloud.",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            help="The name of the routine.",
            required="-h" not in other_args
            and "--help" not in other_args
            and not is_local(),
            nargs="+",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                response = Hub.download_routine(
                    auth_header=get_current_user().profile.get_auth_header(),
                    name=" ".join(ns_parser.name),
                )

                if response and response.status_code == 200:
                    data = response.json()
                    if data:
                        name = data.get("name", "")
                        if name:
                            console.print(f"[info]Name:[/info] {name}")

                        description = data.get("description", "")
                        if description:
                            console.print(f"[info]Description:[/info] {description}")

                        script = data.get("script", "")
                        if script:
                            file_name = f"{name}.openbb"
                            file_path = Local.save_routine(
                                file_name=file_name,
                                routine=script,
                            )
                            if file_path == "File already exists":
                                i = console.input(
                                    "\nA file with the same name already exists, "
                                    "do you want to replace it? (y/n): "
                                )
                                console.print("")
                                if i.lower() in ["y", "yes"]:
                                    file_path = Local.save_routine(
                                        file_name=file_name,
                                        routine=script,
                                        force=True,
                                    )
                                    if file_path:
                                        console.print(
                                            f"[info]Location:[/info] {file_path}"
                                        )
                                else:
                                    console.print("[info]Aborted.[/info]")
                            elif file_path:
                                console.print(f"[info]Location:[/info] {file_path}")

    @log_start_end(log=logger)
    def call_delete(self, other_args: List[str]):
        """Delete"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="delete",
            description="Delete a routine on the cloud.",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            help="The name of the routine",
            required="-h" not in other_args
            and "--help" not in other_args
            and not is_local(),
            nargs="+",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                name = " ".join(ns_parser.name)

                i = console.input(
                    "[bold red]This action is irreversible![/bold red]\n"
                    "Are you sure you want to delete this routine? (y/n): "
                )
                console.print("")
                if i.lower() in ["y", "yes"]:
                    response = Hub.delete_routine(
                        auth_header=get_current_user().profile.get_auth_header(),
                        name=name,
                    )
                    if (
                        response
                        and response.status_code == 200
                        and name in self.REMOTE_CHOICES
                    ):
                        self.REMOTE_CHOICES.remove(name)
                        self.update_runtime_choices()
                else:
                    console.print("[info]Aborted.[/info]")

    @log_start_end(log=logger)
    def call_generate(self, other_args: List[str]) -> None:
        """Process generate command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="generate",
            description="Generate an OpenBB Personal Access Token.",
        )
        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            help="Number of days the token will be valid",
            type=check_positive,
            default=30,
        )
        parser.add_argument(
            "-s",
            "--save",
            dest="save",
            default=False,
            help="Save the token to the keys",
            action="store_true",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                i = console.input(
                    "[bold yellow]This will revoke any token that was previously generated."
                    "\nThis action is irreversible.[/bold yellow]"
                    "\nAre you sure you want to generate a new token? (y/n): "
                )
                if i.lower() not in ["y", "yes"]:
                    console.print("\n[info]Aborted.[/info]")
                    return

                response = Hub.generate_personal_access_token(
                    auth_header=get_current_user().profile.get_auth_header(),
                    days=ns_parser.days,
                )
                if response and response.status_code == 200:
                    token = response.json().get("token", "")
                    if token:
                        console.print(f"\n[info]Token:[/info] {token}\n")

    @log_start_end(log=logger)
    def call_show(self, other_args: List[str]) -> None:
        """Process show command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Show your current OpenBB Personal Access Token.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                response = Hub.get_personal_access_token(
                    auth_header=get_current_user().profile.get_auth_header()
                )
                if response and response.status_code == 200:
                    token = response.json().get("token", "")
                    if token:
                        console.print(f"[info]Token:[/info] {token}")

    @log_start_end(log=logger)
    def call_revoke(self, other_args: List[str]) -> None:
        """Process revoke command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="revoke",
            description="Revoke your current OpenBB Personal Access Token.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if is_local() and "-h" not in other_args and "--help" not in other_args:
            print_guest_block_msg()
        else:
            if ns_parser:
                i = console.input(
                    "[bold red]This action is irreversible![/bold red]\n"
                    "Are you sure you want to revoke your token? (y/n): "
                )
                if i.lower() in ["y", "yes"]:
                    response = Hub.revoke_personal_access_token(
                        auth_header=get_current_user().profile.get_auth_header()
                    )
                    if response and response.status_code in [200, 202]:
                        console.print("[info]Token revoked.[/info]")
                else:
                    console.print("[info]Aborted.[/info]")
