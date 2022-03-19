#!/usr/bin/env python
"""Main Terminal Module"""
__docformat__ = "numpy"

import argparse
import difflib
import logging
import os
import platform
import sys
from typing import List
from pathlib import Path
import pytz
import dotenv

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_path,
    get_flair,
    get_user_timezone_or_invalid,
    parse_known_args_and_warn,
    replace_user_timezone,
    set_export_folder,
)
from gamestonk_terminal.loggers import setup_logging, upload_archive_logs_s3
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.terminal_helper import (
    about_us,
    bootup,
    is_reset,
    print_goodbye,
    reset,
    suppress_stdout,
    update_terminal,
    welcome_message,
)

# pylint: disable=too-many-public-methods,import-outside-toplevel,too-many-branches

logger = logging.getLogger(__name__)

env_file = ".env"


class TerminalController(BaseController):
    """Terminal Controller class"""

    CHOICES_COMMANDS = [
        "update",
        "about",
        "keys",
        "settings",
        "tz",
        "exe",
        "export",
    ]
    CHOICES_MENUS = [
        "stocks",
        "economy",
        "crypto",
        "portfolio",
        "forex",
        "etf",
        "jupyter",
        "funds",
        "alternative",
        "econometrics",
    ]

    PATH = "/"

    all_timezones = pytz.all_timezones

    def __init__(self, jobs_cmds: List[str] = None):
        """Constructor"""
        super().__init__(jobs_cmds)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: None for c in self.controller_choices}
            choices["tz"] = {c: None for c in self.all_timezones}
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.queue: List[str] = list()

        if jobs_cmds:
            self.queue = " ".join(jobs_cmds).split("/")

        self.update_succcess = False

    def print_help(self):
        """Print help"""
        console.print(
            text=f"""
[info]Multiple jobs queue (where each '/' denotes a new command).[/info]
    E.g. '/stocks $ disc/ugs -n 3/../load tsla/candle'

[info]If you want to jump from crypto/ta to stocks you can use an absolute path that starts with a slash (/).[/info]
    E.g. '/crypto/ta $ /stocks'

[info]The previous logic also holds for when launching the terminal.[/info]
    E.g. '$ python terminal.py /stocks/disc/ugs -n 3/../load tsla/candle'

[info]You can run a standalone .gst routine file with:[/info]
    E.g. '$ python terminal.py routines/example.gst'

[info]You can run a .gst routine file with variable inputs:[/info]
    E.g. '$ python terminal.py routines/example_with_inputs.gst --input pltr,tsla,nio'

[info]The main commands you should be aware when navigating through the terminal are:[/info][cmds]
    cls             clear the screen
    help / h / ?    help menu
    quit / q / ..   quit this menu and go one menu above
    exit            exit the terminal
    reset / r       reset the terminal and reload configs from the current location
    resources       only available on main contexts (not sub-menus)

    about           about us
    update          update terminal automatically
    tz              set different timezone
    export          select export folder to output data
    exe             execute automated routine script[/cmds][menu]
>   settings        set feature flags and style charts
>   keys            set API keys and check their validity[/menu]

[param]Export Folder:[/param] {gtff.EXPORT_FOLDER_PATH if gtff.EXPORT_FOLDER_PATH else 'DEFAULT (folder: exports/)'}
[param]Timezone:     [/param] {get_user_timezone_or_invalid()}
[menu]
>   stocks
>   crypto
>   etf
>   economy
>   forex
>   funds
>   alternative
>   econometrics
>   portfolio
>   jupyter[/menu]
    """,
            menu="Home",
        )

    def call_update(self, _):
        """Process update command"""
        self.update_succcess = not update_terminal()

    def call_keys(self, _):
        """Process keys command"""
        from gamestonk_terminal.keys_controller import KeysController

        self.queue = self.load_class(KeysController, self.queue, env_file)

    def call_settings(self, _):
        """Process settings command"""
        from gamestonk_terminal.settings_controller import SettingsController

        self.queue = self.load_class(SettingsController, self.queue)

    def call_about(self, _):
        """Process about command"""
        about_us()

    def call_stocks(self, _):
        """Process stocks command"""
        from gamestonk_terminal.stocks.stocks_controller import StocksController

        self.queue = self.load_class(StocksController, self.queue)

    def call_crypto(self, _):
        """Process crypto command"""
        from gamestonk_terminal.cryptocurrency.crypto_controller import CryptoController

        self.queue = self.load_class(CryptoController, self.queue)

    def call_economy(self, _):
        """Process economy command"""
        from gamestonk_terminal.economy.economy_controller import EconomyController

        self.queue = self.load_class(EconomyController, self.queue)

    def call_etf(self, _):
        """Process etf command"""
        from gamestonk_terminal.etf.etf_controller import ETFController

        self.queue = self.load_class(ETFController, self.queue)

    def call_funds(self, _):
        """Process etf command"""
        from gamestonk_terminal.mutual_funds.mutual_fund_controller import (
            FundController,
        )

        self.queue = self.load_class(FundController, self.queue)

    def call_forex(self, _):
        """Process forex command"""
        from gamestonk_terminal.forex.forex_controller import ForexController

        self.queue = self.load_class(ForexController, self.queue)

    def call_jupyter(self, _):
        """Process jupyter command"""
        from gamestonk_terminal.jupyter.jupyter_controller import JupyterController

        self.queue = self.load_class(JupyterController, self.queue)

    def call_alternative(self, _):
        """Process alternative command"""
        from gamestonk_terminal.alternative.alt_controller import (
            AlternativeDataController,
        )

        self.queue = self.load_class(AlternativeDataController, self.queue)

    def call_econometrics(self, _):
        """Process econometrics command"""
        from gamestonk_terminal.econometrics.econometrics_controller import (
            EconometricsController,
        )

        self.queue = EconometricsController(self.queue).menu()

    def call_portfolio(self, _):
        """Process portfolio command"""
        from gamestonk_terminal.portfolio.portfolio_controller import (
            PortfolioController,
        )

        self.queue = self.load_class(PortfolioController, self.queue)

    def call_tz(self, other_args: List[str]):
        """Process tz command"""
        other_args.append(self.queue[0])
        self.queue = self.queue[1:]
        replace_user_timezone("/".join(other_args))

    def call_export(self, other_args: List[str]):
        """Process export command"""
        if other_args or self.queue:
            if other_args:
                export_path = ""
            else:
                # Re-add the initial slash for an absolute directory provided
                export_path = "/"

            other_args += self.queue
            self.queue = []

            export_path += "/".join(other_args)

            base_path = os.path.dirname(os.path.abspath(__file__))
            default_path = os.path.join(base_path, "exports")

            success_export = False
            while not success_export:
                if export_path.upper() == "DEFAULT":
                    console.print(
                        f"Export data to be saved in the default folder: '{default_path}'"
                    )
                    set_export_folder(env_file, path_folder="")
                    success_export = True
                else:
                    # If the path selected does not start from the user root, give relative location from terminal root
                    if export_path[0] == "~":
                        export_path = export_path.replace("~", os.environ["HOME"])
                    elif export_path[0] != "/":
                        export_path = os.path.join(base_path, export_path)

                    # Check if the directory exists
                    if os.path.isdir(export_path):
                        console.print(
                            f"Export data to be saved in the selected folder: '{export_path}'"
                        )
                        set_export_folder(env_file, path_folder=export_path)
                        success_export = True
                    else:
                        console.print(
                            "[red]The path selected to export data does not exist![/red]\n"
                        )
                        user_opt = "None"
                        while user_opt not in ("Y", "N"):
                            user_opt = input(
                                f"Do you wish to create folder: `{export_path}` ? [Y/N]\n"
                            ).upper()

                        if user_opt == "Y":
                            os.makedirs(export_path)
                            console.print(
                                f"[green]Folder '{export_path}' successfully created.[/green]"
                            )
                            set_export_folder(env_file, path_folder=export_path)
                        else:
                            # Do not update export_folder path since we will keep the same as before
                            path_display = (
                                gtff.EXPORT_FOLDER_PATH
                                if gtff.EXPORT_FOLDER_PATH
                                else "DEFAULT (folder: exports/)"
                            )
                            console.print(
                                f"[yellow]Export data to keep being saved in the selected folder: {path_display}[/yellow]"
                            )
                        success_export = True

        console.print()

    def call_exe(self, other_args: List[str]):
        """Process exe command"""
        # Merge rest of string path to other_args and remove queue since it is a dir
        other_args += self.queue

        if not other_args:
            console.print(
                "[red]Provide a path to the routine you wish to execute.\n[/red]"
            )
            return

        full_input = " ".join(other_args)
        if " " in full_input:
            other_args_processed = full_input.split(" ")
        else:
            other_args_processed = [full_input]
        self.queue = []

        path_routine = ""
        args = list()
        for idx, path_dir in enumerate(other_args_processed):
            if path_dir in ("-i", "--input"):
                args = [path_routine[1:]] + other_args_processed[idx:]
                break
            if path_dir not in ("-p", "--path"):
                path_routine += f"/{path_dir}"

        if not args:
            args = [path_routine[1:]]

        parser_exe = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exe",
            description="Execute automated routine script.",
        )
        parser_exe.add_argument(
            "-p",
            "--path",
            help="The path or .gst file to run.",
            dest="path",
            default="",
            type=check_path,
            required="-h" not in args,
        )
        parser_exe.add_argument(
            "-i",
            "--input",
            help="Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD",
            dest="routine_args",
            type=lambda s: [str(item) for item in s.split(",")],
            default=None,
        )
        if args and "-" not in args[0][0]:
            args.insert(0, "-p")
        ns_parser_exe = parse_known_args_and_warn(parser_exe, args)
        if ns_parser_exe:
            if ns_parser_exe.path:
                with open(ns_parser_exe.path) as fp:
                    raw_lines = [
                        x for x in fp if (not is_reset(x)) and ("#" not in x) and x
                    ]
                    raw_lines = [
                        raw_line.strip("\n")
                        for raw_line in raw_lines
                        if raw_line.strip("\n")
                    ]
                    if ns_parser_exe.routine_args:
                        lines = list()
                        idx = 0
                        for rawline in raw_lines:
                            templine = rawline
                            for i, arg in enumerate(ns_parser_exe.routine_args):
                                templine = templine.replace(f"$ARGV[{i}]", arg)
                            lines.append(templine)
                    else:
                        lines = raw_lines

                    simulate_argv = f"/{'/'.join([line.rstrip() for line in lines])}"
                    file_cmds = simulate_argv.replace("//", "/home/").split()
                    file_cmds = (
                        insert_start_slash(file_cmds) if file_cmds else file_cmds
                    )
                    cmds_with_params = " ".join(file_cmds)
                    self.queue = [val for val in cmds_with_params.split("/") if val]

                    if "export" in self.queue[0]:
                        export_path = self.queue[0].split(" ")[1]
                        # If the path selected does not start from the user root, give relative location from root
                        if export_path[0] == "~":
                            export_path = export_path.replace("~", os.environ["HOME"])
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
                        gtff.EXPORT_FOLDER_PATH = export_path
                        self.queue = self.queue[1:]


# pylint: disable=global-statement
def terminal(jobs_cmds: List[str] = None, appName: str = "gst"):
    """Terminal Menu"""
    setup_logging(appName)
    logger.info("START")
    logger.info("Python: %s", platform.python_version())
    logger.info("OS: %s", platform.system())
    log_settings()

    if jobs_cmds is not None and jobs_cmds:
        logger.info("INPUT: %s", "/".join(jobs_cmds))

    export_path = ""
    if jobs_cmds and "export" in jobs_cmds[0]:
        export_path = jobs_cmds[0].split("/")[0].split(" ")[1]
        jobs_cmds = ["/".join(jobs_cmds[0].split("/")[1:])]

    ret_code = 1
    t_controller = TerminalController(jobs_cmds)
    an_input = ""

    if export_path:
        # If the path selected does not start from the user root, give relative location from terminal root
        if export_path[0] == "~":
            export_path = export_path.replace("~", os.environ["HOME"])
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
        gtff.EXPORT_FOLDER_PATH = export_path

    bootup()
    if not jobs_cmds:
        welcome_message()
        t_controller.print_help()

    env_files = [f for f in os.listdir() if f.endswith(".env")]
    if env_files:
        global env_file
        env_file = env_files[0]
        dotenv.load_dotenv(env_file)
    else:
        # create env file
        Path(".env")

    while ret_code:
        if gtff.ENABLE_QUICK_EXIT:
            console.print("Quick exit enabled")
            break

        # There is a command in the queue
        if t_controller.queue and len(t_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if t_controller.queue[0] in ("q", "..", "quit"):
                print_goodbye()
                upload_archive_logs_s3(log_filter=r"gst_")
                break

            if gtff.ENABLE_EXIT_AUTO_HELP and len(t_controller.queue) > 1:
                t_controller.queue = t_controller.queue[1:]

            # Consume 1 element from the queue
            an_input = t_controller.queue[0]
            t_controller.queue = t_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in t_controller.CHOICES_COMMANDS:
                console.print(f"{get_flair()} / $ {an_input}")

        # Get input command from user
        else:
            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} / $ ",
                        completer=t_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    print_goodbye()
                    upload_archive_logs_s3(log_filter=r"gst_")
                    break
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} / $ ")

        try:
            # Process the input command
            t_controller.queue = t_controller.switch(an_input)
            if an_input in ("q", "quit", "..", "exit"):
                print_goodbye()
                upload_archive_logs_s3(log_filter=r"gst_")
                break

            # Check if the user wants to reset application
            if an_input in ("r", "reset") or t_controller.update_succcess:
                ret_code = reset(t_controller.queue if t_controller.queue else [])
                if ret_code != 0:
                    print_goodbye()
                    upload_archive_logs_s3(log_filter=r"gst_")
                    break

        except SystemExit:
            logger.exception(
                "The command '%s' doesn't exist on the / menu.",
                an_input,
            )
            console.print(
                f"\nThe command '{an_input}' doesn't exist on the / menu", end=""
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                t_controller.controller_choices,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
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
                else:
                    an_input = similar_cmd[0]

                console.print(f" Replacing by '{an_input}'.")
                t_controller.queue.insert(0, an_input)
            else:
                console.print("\n")


def insert_start_slash(cmds: List[str]) -> List[str]:
    if not cmds[0].startswith("/"):
        cmds[0] = f"/{cmds[0]}"
    if cmds[0].startswith("/home"):
        cmds[0] = f"/{cmds[0][5:]}"
    return cmds


def log_settings() -> None:
    """Log settings"""
    settings_dict = {}
    settings_dict["tab"] = "activated" if gtff.USE_TABULATE_DF else "deactivated"
    settings_dict["cls"] = "activated" if gtff.USE_CLEAR_AFTER_CMD else "deactivated"
    settings_dict["color"] = "activated" if gtff.USE_COLOR else "deactivated"
    settings_dict["promptkit"] = (
        "activated" if gtff.USE_PROMPT_TOOLKIT else "deactivated"
    )
    settings_dict["predict"] = "activated" if gtff.ENABLE_PREDICT else "deactivated"
    settings_dict["thoughts"] = (
        "activated" if gtff.ENABLE_THOUGHTS_DAY else "deactivated"
    )
    settings_dict["reporthtml"] = (
        "activated" if gtff.OPEN_REPORT_AS_HTML else "deactivated"
    )
    settings_dict["exithelp"] = (
        "activated" if gtff.ENABLE_EXIT_AUTO_HELP else "deactivated"
    )
    settings_dict["rcontext"] = "activated" if gtff.REMEMBER_CONTEXTS else "deactivated"
    settings_dict["rich"] = "activated" if gtff.ENABLE_RICH else "deactivated"
    settings_dict["richpanel"] = (
        "activated" if gtff.ENABLE_RICH_PANEL else "deactivated"
    )
    settings_dict["ion"] = "activated" if gtff.USE_ION else "deactivated"
    settings_dict["watermark"] = "activated" if gtff.USE_WATERMARK else "deactivated"
    settings_dict["autoscaling"] = (
        "activated" if gtff.USE_PLOT_AUTOSCALING else "deactivated"
    )
    settings_dict["dt"] = "activated" if gtff.USE_DATETIME else "deactivated"
    logger.info("SETTINGS: %s ", str(settings_dict))


def run_scripts(
    path: str,
    test_mode: bool = False,
    verbose: bool = False,
    routines_args: List[str] = None,
):
    """Runs a given .gst scripts

    Parameters
    ----------
    path : str
        The location of the .gst file
    test_mode : bool
        Whether the terminal is in test mode
    verbose : bool
        Whether to run tests in verbose mode
    routines_args : List[str]
        One or multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD
    """
    if os.path.isfile(path):
        with open(path) as fp:
            raw_lines = [x for x in fp if (not is_reset(x)) and ("#" not in x) and x]
            raw_lines = [
                raw_line.strip("\n") for raw_line in raw_lines if raw_line.strip("\n")
            ]

            if routines_args:
                lines = list()
                for rawline in raw_lines:
                    templine = rawline
                    for i, arg in enumerate(routines_args):
                        templine = templine.replace(f"$ARGV[{i}]", arg)
                    lines.append(templine)
            else:
                lines = raw_lines

            if test_mode and "exit" not in lines[-1]:
                lines.append("exit")

            export_folder = ""
            if "export" in lines[0]:
                export_folder = lines[0].split("export ")[1].rstrip()
                lines = lines[1:]

            simulate_argv = f"/{'/'.join([line.rstrip() for line in lines])}"
            file_cmds = simulate_argv.replace("//", "/home/").split()
            file_cmds = insert_start_slash(file_cmds) if file_cmds else file_cmds
            if export_folder:
                file_cmds = [f"export {export_folder}{' '.join(file_cmds)}"]
            else:
                file_cmds = [" ".join(file_cmds)]

            if not test_mode:
                terminal(file_cmds, appName="gst_script")
                # TODO: Add way to track how many commands are tested
            else:
                if verbose:
                    terminal(file_cmds, appName="gst_script")
                else:
                    with suppress_stdout():
                        terminal(file_cmds, appName="gst_script")
    else:
        console.print(f"File '{path}' doesn't exist. Launching base terminal.\n")
        if not test_mode:
            terminal()


def main(
    debug: bool,
    test: bool,
    filtert: str,
    paths: List[str],
    verbose: bool,
    routines_args: List[str] = None,
):
    """
    Runs the terminal with various options

    Parameters
    ----------
    debug : bool
        Whether to run the terminal in debug mode
    test : bool
        Whether to run the terminal in integrated test mode
    filtert : str
        Filter test files with given string in name
    paths : List[str]
        The paths to run for scripts or to test
    verbose : bool
        Whether to show output from tests
    routines_args : List[str]
        One or multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD
    """

    if test:
        os.environ["DEBUG_MODE"] = "true"

        if paths == []:
            console.print("Please send a path when using test mode")
            return
        test_files = []
        for path in paths:
            if "gst" in path:
                file = os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
                test_files.append(file)
            else:
                folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
                files = [
                    f"{folder}/{name}"
                    for name in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, name))
                    and name.endswith(".gst")
                    and (filtert in f"{folder}/{name}")
                ]
                test_files += files
        test_files.sort()
        SUCCESSES = 0
        FAILURES = 0
        fails = {}
        length = len(test_files)
        i = 0
        console.print("[green]Gamestonk Terminal Integrated Tests:\n[/green]")
        for file in test_files:
            file = file.replace("//", "/")
            file_name = file[file.rfind("GamestonkTerminal") :].replace("\\", "/")
            console.print(f"{file_name}  {((i/length)*100):.1f}%")
            try:
                if not os.path.isfile(file):
                    raise ValueError("Given file does not exist")
                run_scripts(file, test_mode=True, verbose=verbose)
                SUCCESSES += 1
            except Exception as e:
                fails[file] = e
                FAILURES += 1
            i += 1
        if fails:
            console.print("\n[red]Failures:[/red]\n")
            for key, value in fails.items():
                file_name = key[key.rfind("GamestonkTerminal") :].replace("\\", "/")
                logger.error("%s: %s failed", file_name, value)
                console.print(f"{file_name}: {value}\n")
        console.print(
            f"Summary: [green]Successes: {SUCCESSES}[/green] [red]Failures: {FAILURES}[/red]"
        )
    else:
        if debug:
            os.environ["DEBUG_MODE"] = "true"
        if isinstance(paths, list) and paths[0].endswith(".gst"):
            run_scripts(paths[0], routines_args=routines_args)
        elif paths:
            argv_cmds = list([" ".join(paths).replace(" /", "/home/")])
            argv_cmds = insert_start_slash(argv_cmds) if argv_cmds else argv_cmds
            terminal(argv_cmds)
        else:
            terminal()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="terminal",
        description="The gamestonk terminal.",
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
        "-p",
        "--path",
        help="The path or .gst file to run.",
        dest="path",
        nargs="+",
        default="",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--test",
        dest="test",
        action="store_true",
        default=False,
        help="Whether to run in test mode.",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="Send a keyword to filter in file name",
        dest="filtert",
        default="",
        type=str,
    )
    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", default=False
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD",
        dest="routine_args",
        type=lambda s: [str(item) for item in s.split(",")],
        default=None,
    )

    if sys.argv[1:] and "-" not in sys.argv[1][0]:
        sys.argv.insert(1, "-p")
    ns_parser = parser.parse_args()
    main(
        ns_parser.debug,
        ns_parser.test,
        ns_parser.filtert,
        ns_parser.path,
        ns_parser.verbose,
        ns_parser.routine_args,
    )
