#!/usr/bin/env python
"""Main Terminal Module."""
__docformat__ = "numpy"

import argparse
import contextlib
import difflib
import logging
import os
import re
import sys
import time
import webbrowser
from datetime import datetime
from functools import partial, update_wrapper
from pathlib import Path
from types import MethodType
from typing import Any, Dict, List, Optional

import certifi
import pandas as pd
import requests
from openbb import obb
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from pydantic import BaseModel

from openbb_terminal.account.show_prompt import get_show_prompt, set_show_prompt
from openbb_terminal.core.config.paths import (
    HOME_DIRECTORY,
    MISCELLANEOUS_DIRECTORY,
    REPOSITORY_DIRECTORY,
    SETTINGS_ENV_FILE,
)
from openbb_terminal.core.session import constants, session_controller
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.core.session.current_user import get_current_user, set_preference
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.helper_funcs import (
    get_flair,
    parse_and_split_input,
    print_rich_table,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.platform_controller_factory import (
    PlatformControllerFactory,
)
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.routine_functions import is_reset, parse_openbb_script
from openbb_terminal.terminal_helper import (
    bootup,
    check_for_updates,
    first_time_user,
    is_auth_enabled,
    is_installer,
    print_goodbye,
    reset,
    suppress_stdout,
    welcome_message,
)

PLATFORM_ROUTERS = {
    d: "menu" if not isinstance(getattr(obb, d), BaseModel) else "command"
    for d in dir(obb)
    if "_" not in d
}

# pylint: disable=too-many-public-methods,import-outside-toplevel, too-many-function-args
# pylint: disable=too-many-branches,no-member,C0302,too-many-return-statements, inconsistent-return-statements

logger = logging.getLogger(__name__)

env_file = str(SETTINGS_ENV_FILE)

if is_installer():
    # Necessary for installer so that it can locate the correct certificates for
    # API calls and https
    # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
    os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    os.environ["SSL_CERT_FILE"] = certifi.where()


class TerminalController(BaseController):
    """Terminal Controller class."""

    CHOICES_COMMANDS = [
        "intro",
        "about",
        "support",
        "survey",
        "record",
        "stop",
        "exe",
    ]
    CHOICES_MENUS = [
        "featflags",
    ]

    for router, value in PLATFORM_ROUTERS.items():
        if value == "menu":
            CHOICES_MENUS.append(router)
        else:
            CHOICES_COMMANDS.append(router)

    if is_auth_enabled():
        CHOICES_MENUS.append("account")

    PATH = "/"

    GUESS_TOTAL_TRIES = 0
    GUESS_NUMBER_TRIES_LEFT = 0
    GUESS_SUM_SCORE = 0.0
    GUESS_CORRECTLY = 0
    CHOICES_GENERATION = False

    def __init__(self, jobs_cmds: Optional[List[str]] = None):
        """Construct terminal controller."""
        self.ROUTINE_FILES: Dict[str, str] = dict()
        self.ROUTINE_DEFAULT_FILES: Dict[str, str] = dict()
        self.ROUTINE_PERSONAL_FILES: Dict[str, str] = dict()
        self.ROUTINE_CHOICES: Dict[str, Any] = dict()

        super().__init__(jobs_cmds)

        self.queue: List[str] = list()

        if jobs_cmds:
            self.queue = parse_and_split_input(
                an_input=" ".join(jobs_cmds), custom_filters=[]
            )

        self.update_success = False

        self._generate_platform_commands()

        self.update_runtime_choices()

    def _generate_platform_commands(self):
        """Generate Platform based commands/menus."""

        def method_call_class(self, _, controller, name, parent_path, target):
            self.queue = self.load_class(
                controller, name, parent_path, target, self.queue
            )

        # pylint: disable=unused-argument
        def method_call_command(self, _, target: BaseModel):
            df = pd.DataFrame.from_dict(target.model_dump(), orient="index")
            return print_rich_table(df, show_index=True)

        for router, value in PLATFORM_ROUTERS.items():
            target = getattr(obb, router)

            if value == "menu":
                pcf = PlatformControllerFactory(
                    target, reference=obb.coverage.reference
                )
                DynamicController = pcf.create()

                # Bind the method to the class
                bound_method = MethodType(method_call_class, self)

                # Update the wrapper and set the attribute
                bound_method = update_wrapper(
                    partial(
                        bound_method,
                        controller=DynamicController,
                        name=router,
                        target=target,
                        parent_path=self.path,
                    ),
                    method_call_class,
                )
            else:
                bound_method = MethodType(method_call_command, self)
                bound_method = update_wrapper(
                    partial(bound_method, target=target), method_call_command
                )

            setattr(self, f"call_{router}", bound_method)

    def update_runtime_choices(self):
        """Update runtime choices."""
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            # choices: dict = self.choices_default
            choices: dict = {c: {} for c in self.controller_choices}  # type: ignore
            choices["support"] = self.SUPPORT_CHOICES
            choices["hold"] = {c: None for c in ["on", "off", "-s", "--sameaxis"]}
            choices["hold"]["off"] = {"--title": None}

            self.ROUTINE_FILES = {
                filepath.name: filepath
                for filepath in get_current_user().preferences.USER_ROUTINES_DIRECTORY.rglob(
                    "*.openbb"
                )
            }
            self.ROUTINE_DEFAULT_FILES = {
                filepath.name: filepath
                for filepath in Path(
                    get_current_user().preferences.USER_ROUTINES_DIRECTORY
                    / "hub"
                    / "default"
                ).rglob("*.openbb")
            }
            self.ROUTINE_PERSONAL_FILES = {
                filepath.name: filepath
                for filepath in Path(
                    get_current_user().preferences.USER_ROUTINES_DIRECTORY
                    / "hub"
                    / "personal"
                ).rglob("*.openbb")
            }

            choices["exe"] = {
                "--file": {
                    filename: {} for filename in list(self.ROUTINE_FILES.keys())
                },
                "-f": "--file",
                "--example": None,
                "-e": "--example",
                "--input": None,
                "-i": "--input",
                "--url": None,
            }

            choices["record"] = {
                "--name": None,
                "-n": "--name",
                "--description": None,
                "-d": "--description",
                "--public": None,
                "-p": "--public",
                "--local": None,
                "-l": "--local",
                "--tag1": {c: None for c in constants.SCRIPT_TAGS},
                "--tag2": {c: None for c in constants.SCRIPT_TAGS},
                "--tag3": {c: None for c in constants.SCRIPT_TAGS},
            }

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("")
        mt.add_raw("\n")
        mt.add_info("_home_")
        mt.add_cmd("intro")
        mt.add_cmd("about")
        mt.add_cmd("support")
        mt.add_cmd("survey")
        mt.add_raw("\n")
        mt.add_info("_configure_")
        mt.add_menu("featflags")
        mt.add_raw("\n")
        mt.add_info("_scripts_")
        mt.add_cmd("record")
        mt.add_cmd("stop")
        mt.add_cmd("exe")
        mt.add_raw("\n")
        mt.add_raw("\n")
        mt.add_info("Platform CLI")
        for router, value in PLATFORM_ROUTERS.items():
            if value == "menu":
                mt.add_menu(router)
            else:
                mt.add_cmd(router)

        console.print(text=mt.menu_text, menu="Home")
        self.update_runtime_choices()

    def parse_input(self, an_input: str) -> List:
        """Overwrite the BaseController parse_input for `askobb` and 'exe'

        This will allow us to search for something like "P/E" ratio
        """
        # Filtering out sorting parameters with forward slashes like P/E
        sort_filter = r"((\ -q |\ --question|\ ).*?(/))"
        # Filter out urls
        url = r"(exe (--url )?(https?://)?my\.openbb\.(dev|co)/u/.*/routine/.*)"
        custom_filters = [sort_filter, url]
        return parse_and_split_input(an_input=an_input, custom_filters=custom_filters)

    @staticmethod
    def call_survey(_) -> None:
        """Process survey command."""
        webbrowser.open("https://openbb.co/survey")

    def call_featflags(self, _):
        """Process feature flags command."""
        from openbb_terminal.featflags_controller import FeatureFlagsController

        self.queue = self.load_class(FeatureFlagsController, self.queue)

    def call_intro(self, _):
        """Process intro command."""
        webbrowser.open(
            "https://docs.openbb.co/terminal/usage/overview/structure-and-navigation"
        )

    def call_exe(self, other_args: List[str]):
        """Process exe command."""
        # Merge rest of string path to other_args and remove queue since it is a dir
        other_args += self.queue

        if not other_args:
            console.print(
                "[info]Provide a path to the routine you wish to execute. For an example, please use "
                "`exe --example` and for documentation and to learn how create your own script "
                "type `about exe`.\n[/info]"
            )
            return
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exe",
            description="Execute automated routine script. For an example, please use "
            "`exe --example` and for documentation and to learn how create your own script "
            "type `about exe`.",
        )
        parser.add_argument(
            "--file",
            "-f",
            help="The path or .openbb file to run.",
            dest="file",
            required="-h" not in other_args
            and "--help" not in other_args
            and "-e" not in other_args
            and "--example" not in other_args
            and "--url" not in other_args
            and "my.openbb" not in other_args[0],
            type=str,
            nargs="+",
        )
        parser.add_argument(
            "-i",
            "--input",
            help="Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD",
            dest="routine_args",
            type=lambda s: [str(item) for item in s.split(",")],
        )
        parser.add_argument(
            "-e",
            "--example",
            help="Run an example script to understand how routines can be used.",
            dest="example",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--url", help="URL to run openbb script from.", dest="url", type=str
        )
        if other_args and "-" not in other_args[0][0]:
            if other_args[0].startswith("my.") or other_args[0].startswith("http"):
                other_args.insert(0, "--url")
            else:
                other_args.insert(0, "--file")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.example:
                routine_path = (
                    MISCELLANEOUS_DIRECTORY / "routines" / "routine_example.openbb"
                )
                console.print(
                    "[info]Executing an example, please type `about exe` "
                    "to learn how to create your own script.[/info]\n"
                )
                time.sleep(3)
            elif ns_parser.url:
                if not ns_parser.url.startswith(
                    "https"
                ) and not ns_parser.url.startswith("http:"):
                    url = "https://" + ns_parser.url
                elif ns_parser.url.startswith("http://"):
                    url = ns_parser.url.replace("http://", "https://")
                else:
                    url = ns_parser.url
                username = url.split("/")[-3]
                script_name = url.split("/")[-1]
                file_name = f"{username}_{script_name}.openbb"
                final_url = f"{url}?raw=true"
                response = requests.get(final_url, timeout=10)
                if response.status_code != 200:
                    console.print("[red]Could not find the requested script.[/red]")
                    return
                routine_text = response.json()["script"]
                file_path = Path(get_current_user().preferences.USER_ROUTINES_DIRECTORY)
                routine_path = file_path / file_name
                with open(routine_path, "w") as file:
                    file.write(routine_text)
                self.update_runtime_choices()

            elif ns_parser.file:
                file_path = " ".join(ns_parser.file)  # type: ignore
                # if string is not in this format "default/file.openbb" then check for files in ROUTINE_FILES
                full_path = file_path
                hub_routine = file_path.split("/")  # type: ignore
                # Change with: my.openbb.co
                if hub_routine[0] == "default":
                    routine_path = Path(
                        self.ROUTINE_DEFAULT_FILES.get(hub_routine[1], full_path)
                    )
                elif hub_routine[0] == "personal":
                    routine_path = Path(
                        self.ROUTINE_PERSONAL_FILES.get(hub_routine[1], full_path)
                    )
                else:
                    routine_path = Path(self.ROUTINE_FILES.get(file_path, full_path))  # type: ignore
            else:
                return

            with open(routine_path) as fp:
                raw_lines = list(fp)

                # Capture ARGV either as list if args separated by commas or as single value
                if ns_parser.routine_args:
                    script_inputs = (
                        ns_parser.routine_args
                        if "," not in ns_parser.routine_args
                        else ns_parser.routine_args.split(",")
                    )

                err, parsed_script = parse_openbb_script(
                    raw_lines=raw_lines,
                    script_inputs=script_inputs if ns_parser.routine_args else None,
                )

                # If there err output is not an empty string then it means there was an
                # issue in parsing the routine and therefore we don't want to feed it
                # to the terminal
                if err:
                    console.print(err)
                    return

                self.queue = [
                    val
                    for val in parse_and_split_input(
                        an_input=parsed_script, custom_filters=[]
                    )
                    if val
                ]

                if "export" in self.queue[0]:
                    export_path = self.queue[0].split(" ")[1]
                    # If the path selected does not start from the user root, give relative location from root
                    if export_path[0] == "~":
                        export_path = export_path.replace(
                            "~", HOME_DIRECTORY.as_posix()
                        )
                    elif export_path[0] != "/":
                        export_path = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), export_path
                        )

                    # Check if the directory exists
                    if os.path.isdir(export_path):
                        console.print(
                            f"Export data to be saved in the selected folder: '{export_path}'"
                        )
                    else:
                        os.makedirs(export_path)
                        console.print(
                            f"[green]Folder '{export_path}' successfully created.[/green]"
                        )
                    set_preference("USER_EXPORTS_DIRECTORY", Path(export_path))
                    self.queue = self.queue[1:]


def handle_job_cmds(jobs_cmds: Optional[List[str]]) -> Optional[List[str]]:
    # If the path selected does not start from the user root,
    # give relative location from terminal root
    if jobs_cmds is not None and jobs_cmds:
        logger.info("INPUT: %s", "/".join(jobs_cmds))

    export_path = ""
    if jobs_cmds and "export" in jobs_cmds[0]:
        commands = jobs_cmds[0].split("/")
        first_split = commands[0].split(" ")
        if len(first_split) > 1:
            export_path = first_split[1]
        jobs_cmds = ["/".join(commands[1:])]
    if not export_path:
        return jobs_cmds
    if export_path[0] == "~":
        export_path = export_path.replace("~", HOME_DIRECTORY.as_posix())
    elif export_path[0] != "/":
        export_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), export_path
        )

    # Check if the directory exists
    if os.path.isdir(export_path):
        console.print(
            f"Export data to be saved in the selected folder: '{export_path}'"
        )
    else:
        os.makedirs(export_path)
        console.print(f"[green]Folder '{export_path}' successfully created.[/green]")
    set_preference("USER_EXPORTS_DIRECTORY", Path(export_path))
    return jobs_cmds


def terminal(jobs_cmds: Optional[List[str]] = None, test_mode=False):
    """Terminal Menu."""

    current_user = get_current_user()

    ret_code = 1
    t_controller = TerminalController(jobs_cmds)
    an_input = ""

    jobs_cmds = handle_job_cmds(jobs_cmds)

    bootup()
    if not jobs_cmds:
        welcome_message()

        if first_time_user():
            with contextlib.suppress(EOFError):
                webbrowser.open(
                    "https://docs.openbb.co/terminal/usage/overview/structure-and-navigation"
                )

        t_controller.print_help()
        check_for_updates()

    while ret_code:
        if current_user.preferences.ENABLE_QUICK_EXIT:
            console.print("Quick exit enabled")
            break

        # There is a command in the queue
        if t_controller.queue and len(t_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if t_controller.queue[0] in ("q", "..", "quit"):
                print_goodbye()
                break

            # Consume 1 element from the queue
            an_input = t_controller.queue[0]
            t_controller.queue = t_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in t_controller.CHOICES_COMMANDS:
                console.print(f"{get_flair()} / $ {an_input}")

        # Get input command from user
        else:
            try:
                # Get input from user using auto-completion
                if session and current_user.preferences.USE_PROMPT_TOOLKIT:
                    # Check if toolbar hint was enabled
                    if current_user.preferences.TOOLBAR_HINT:
                        an_input = session.prompt(
                            f"{get_flair()} / $ ",
                            completer=t_controller.completer,
                            search_ignore_case=True,
                            bottom_toolbar=HTML(
                                '<style bg="ansiblack" fg="ansiwhite">[h]</style> help menu    '
                                '<style bg="ansiblack" fg="ansiwhite">[q]</style> return to previous menu    '
                                '<style bg="ansiblack" fg="ansiwhite">[e]</style> exit terminal    '
                                '<style bg="ansiblack" fg="ansiwhite">[cmd -h]</style> '
                                "see usage and available options    "
                                '<style bg="ansiblack" fg="ansiwhite">[about (cmd/menu)]</style> '
                            ),
                            style=Style.from_dict(
                                {
                                    "bottom-toolbar": "#ffffff bg:#333333",
                                }
                            ),
                        )
                    else:
                        an_input = session.prompt(
                            f"{get_flair()} / $ ",
                            completer=t_controller.completer,
                            search_ignore_case=True,
                        )

                # Get input from user without auto-completion
                else:
                    an_input = input(f"{get_flair()} / $ ")

            except (KeyboardInterrupt, EOFError):
                print_goodbye()
                break

        try:
            if (
                an_input in ("login", "logout")
                and get_show_prompt()
                and is_auth_enabled()
            ):
                break

            # Process the input command
            t_controller.queue = t_controller.switch(an_input)

            if an_input in ("q", "quit", "..", "exit", "e"):
                print_goodbye()
                break

            # Check if the user wants to reset application
            if an_input in ("r", "reset") or t_controller.update_success:
                reset(t_controller.queue if t_controller.queue else [])
                break

        except SystemExit:
            logger.exception(
                "The command '%s' doesn't exist on the / menu.",
                an_input,
            )
            console.print(
                f"[red]The command '{an_input}' doesn't exist on the / menu.[/red]\n",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                t_controller.controller_choices,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                an_input = similar_cmd[0]
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        t_controller.queue = []
                        console.print("\n")
                        continue
                    an_input = candidate_input

                console.print(f"[green]Replacing by '{an_input}'.[/green]")
                t_controller.queue.insert(0, an_input)

    if an_input in ("login", "logout") and get_show_prompt() and is_auth_enabled():
        set_show_prompt(False)
        return session_controller.launch_terminal()


def insert_start_slash(cmds: List[str]) -> List[str]:
    """Insert a slash at the beginning of a command sequence."""
    if not cmds[0].startswith("/"):
        cmds[0] = f"/{cmds[0]}"
    if cmds[0].startswith("/home"):
        cmds[0] = f"/{cmds[0][5:]}"
    return cmds


def run_scripts(
    path: Path,
    test_mode: bool = False,
    verbose: bool = False,
    routines_args: Optional[List[str]] = None,
    special_arguments: Optional[Dict[str, str]] = None,
    output: bool = True,
):
    """Run given .openbb scripts.

    Parameters
    ----------
    path : str
        The location of the .openbb file
    test_mode : bool
        Whether the terminal is in test mode
    verbose : bool
        Whether to run tests in verbose mode
    routines_args : List[str]
        One or multiple inputs to be replaced in the routine and separated by commas.
        E.g. GME,AMC,BTC-USD
    special_arguments: Optional[Dict[str, str]]
        Replace `${key=default}` with `value` for every key in the dictionary
    output: bool
        Whether to log tests to txt files
    """
    if not path.exists():
        console.print(f"File '{path}' doesn't exist. Launching base terminal.\n")
        if not test_mode:
            terminal()

    # THIS NEEDS TO BE REFACTORED!!! - ITS USED FOR TESTING
    with path.open() as fp:
        raw_lines = [x for x in fp if (not is_reset(x)) and ("#" not in x) and x]
        raw_lines = [
            raw_line.strip("\n") for raw_line in raw_lines if raw_line.strip("\n")
        ]

        if routines_args:
            lines = []
            for rawline in raw_lines:
                templine = rawline
                for i, arg in enumerate(routines_args):
                    templine = templine.replace(f"$ARGV[{i}]", arg)
                lines.append(templine)
        # Handle new testing arguments:
        elif special_arguments:
            lines = []
            for line in raw_lines:
                new_line = re.sub(
                    r"\${[^{]+=[^{]+}",
                    lambda x: replace_dynamic(x, special_arguments),  # type: ignore
                    line,
                )
                lines.append(new_line)

        else:
            lines = raw_lines

        if test_mode and "exit" not in lines[-1]:
            lines.append("exit")

        # Deals with the export with a path with "/" in it
        export_folder = ""
        if "export" in lines[0]:
            export_folder = lines[0].split("export ")[1].rstrip()
            lines = lines[1:]

        simulate_argv = f"/{'/'.join([line.rstrip() for line in lines])}"
        file_cmds = simulate_argv.replace("//", "/home/").split()
        file_cmds = insert_start_slash(file_cmds) if file_cmds else file_cmds
        file_cmds = (
            [f"export {export_folder}{' '.join(file_cmds)}"]
            if export_folder
            else [" ".join(file_cmds)]
        )

        if not test_mode or verbose:
            terminal(file_cmds, test_mode=True)
        else:
            with suppress_stdout():
                console.print(f"To ensure: {output}")
                if output:
                    timestamp = datetime.now().timestamp()
                    stamp_str = str(timestamp).replace(".", "")
                    whole_path = Path(REPOSITORY_DIRECTORY / "integration_test_output")
                    whole_path.mkdir(parents=True, exist_ok=True)
                    first_cmd = file_cmds[0].split("/")[1]
                    with open(
                        whole_path / f"{stamp_str}_{first_cmd}_output.txt", "w"
                    ) as output_file, contextlib.redirect_stdout(output_file):
                        terminal(file_cmds, test_mode=True)
                else:
                    terminal(file_cmds, test_mode=True)


def replace_dynamic(match: re.Match, special_arguments: Dict[str, str]) -> str:
    """Replaces ${key=default} with value in special_arguments if it exists, else with default.

    Parameters
    ----------
    match: re.Match[str]
        The match object
    special_arguments: Dict[str, str]
        The key value pairs to replace in the scripts

    Returns
    ----------
    str
        The new string
    """

    cleaned = match[0].replace("{", "").replace("}", "").replace("$", "")
    key, default = cleaned.split("=")
    dict_value = special_arguments.get(key, default)
    if dict_value:
        return dict_value
    return default


def run_routine(file: str, routines_args=Optional[str]):
    """Execute command routine from .openbb file."""
    user_routine_path = (
        get_current_user().preferences.USER_DATA_DIRECTORY / "routines" / file
    )
    default_routine_path = MISCELLANEOUS_DIRECTORY / "routines" / file

    if user_routine_path.exists():
        run_scripts(path=user_routine_path, routines_args=routines_args)
    elif default_routine_path.exists():
        run_scripts(path=default_routine_path, routines_args=routines_args)
    else:
        console.print(
            f"Routine not found, please put your `.openbb` file into : {user_routine_path}."
        )


def main(
    debug: bool,
    dev: bool,
    path_list: List[str],
    routines_args: Optional[List[str]] = None,
    **kwargs,
):
    """Run the terminal with various options.

    Parameters
    ----------
    debug : bool
        Whether to run the terminal in debug mode
    dev:
        Points backend towards development environment instead of production
    test : bool
        Whether to run the terminal in integrated test mode
    filtert : str
        Filter test files with given string in name
    paths : List[str]
        The paths to run for scripts or to test
    verbose : bool
        Whether to show output from tests
    routines_args : List[str]
        One or multiple inputs to be replaced in the routine and separated by commas.
        E.g. GME,AMC,BTC-USD
    """
    if debug:
        set_system_variable("DEBUG_MODE", True)

    if dev:
        set_system_variable("DEV_BACKEND", True)
        constants.BackendEnvironment.BASE_URL = "https://payments.openbb.dev/"
        constants.BackendEnvironment.HUB_URL = "https://my.openbb.dev/"

    if isinstance(path_list, list) and path_list[0].endswith(".openbb"):
        run_routine(file=path_list[0], routines_args=routines_args)
    elif path_list:
        argv_cmds = list([" ".join(path_list).replace(" /", "/home/")])
        argv_cmds = insert_start_slash(argv_cmds) if argv_cmds else argv_cmds
        terminal(argv_cmds)
    else:
        terminal()


def parse_args_and_run():
    """Parse input arguments and run terminal."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="terminal",
        description="The OpenBB Terminal.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Runs the terminal in debug mode.",
    )
    parser.add_argument(
        "--dev",
        dest="dev",
        action="store_true",
        default=False,
        help="Points backend towards development environment instead of production",
    )
    parser.add_argument(
        "--file",
        help="The path or .openbb file to run.",
        dest="path",
        nargs="+",
        default="",
        type=str,
    )
    parser.add_argument(
        "-i",
        "--input",
        help=(
            "Select multiple inputs to be replaced in the routine and separated by commas."
            "E.g. GME,AMC,BTC-USD"
        ),
        dest="routine_args",
        type=lambda s: [str(item) for item in s.split(",")],
        default=None,
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help=(
            "Run the terminal in testing mode. Also run this option and '-h'"
            " to see testing argument options."
        ),
    )
    if is_auth_enabled():
        parser.add_argument(
            "--login",
            action="store_true",
            help="Go to login prompt.",
        )
    # The args -m, -f and --HistoryManager.hist_file are used only in reports menu
    # by papermill and that's why they have suppress help.
    parser.add_argument(
        "-m",
        help=argparse.SUPPRESS,
        dest="module",
        default="",
        type=str,
    )
    parser.add_argument(
        "-f",
        help=argparse.SUPPRESS,
        dest="module_file",
        default="",
        type=str,
    )
    parser.add_argument(
        "--HistoryManager.hist_file",
        help=argparse.SUPPRESS,
        dest="module_hist_file",
        default="",
        type=str,
    )
    if sys.argv[1:] and "-" not in sys.argv[1][0]:
        sys.argv.insert(1, "--file")
    ns_parser, unknown = parser.parse_known_args()

    # This ensures that if terminal.py receives unknown args it will not start.
    # Use -d flag if you want to see the unknown args.
    if unknown:
        if ns_parser.debug:
            console.print(unknown)
        else:
            sys.exit(-1)

    main(
        ns_parser.debug,
        ns_parser.dev,
        ns_parser.path,
        ns_parser.routine_args,
        module=ns_parser.module,
        module_file=ns_parser.module_file,
        module_hist_file=ns_parser.module_hist_file,
    )


if __name__ == "__main__":
    parse_args_and_run()
