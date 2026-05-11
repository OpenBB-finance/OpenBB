"""Base controller for the CLI."""

import argparse
import difflib
import os
import re
import shlex
from abc import ABCMeta, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from openbb_cli.config.completer import NestedCompleter
from openbb_cli.config.constants import SCRIPT_TAGS
from openbb_cli.controllers.choices import build_controller_choice_map
from openbb_cli.controllers.utils import (
    check_file_type_saved,
    check_positive,
    get_flair_and_username,
    handle_obbject_display,
    parse_unknown_args_to_dict,
    system_clear,
    validate_register_key,
)
from openbb_cli.session import Session

controllers: dict[str, Any] = {}
session = Session()


RECORD_SESSION = False
SESSION_RECORDED = list()
SESSION_RECORDED_NAME = ""
SESSION_RECORDED_DESCRIPTION = ""
SESSION_RECORDED_TAGS = ""


class BaseController(metaclass=ABCMeta):
    """Base class for a cli controller."""

    CHOICES_COMMON = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "e",
        "exit",
        "r",
        "reset",
        "stop",
        "results",
        "load",
    ]

    CHOICES_COMMANDS: list[str] = []
    CHOICES_MENUS: list[str] = []
    NEWS_CHOICES: dict = {}
    COMMAND_SEPARATOR = "/"
    KEYS_MENU = "keys" + COMMAND_SEPARATOR
    PATH: str = ""
    FILE_PATH: str = ""
    CHOICES_GENERATION = False

    @property
    def choices_default(self):
        """Return the default choices."""
        choices = (
            build_controller_choice_map(controller=self)
            if self.CHOICES_GENERATION
            else {}
        )

        return choices

    def __init__(self, queue: list[str] | None = None) -> None:
        """Create the base class for any controller in the codebase.

        Used to simplify the creation of menus.

        queue: List[str]
            The current queue of jobs to process separated by "/"
            E.g. /stocks/load gme/dps/sidtc/../exit
        """
        self.check_path()
        self.path = [x for x in self.PATH.split("/") if x != ""]
        self.queue = (
            self.parse_input(an_input="/".join(queue))
            if (queue and self.PATH != "/")
            else list()
        )

        controller_choices = self.CHOICES_COMMANDS + self.CHOICES_MENUS
        if controller_choices:
            self.controller_choices = controller_choices + self.CHOICES_COMMON
        else:
            self.controller_choices = self.CHOICES_COMMON

        self.completer: None | NestedCompleter = None

        self.parser = argparse.ArgumentParser(
            add_help=False,
            prog=self.path[-1] if self.PATH != "/" else "cli",
        )
        self.parser.exit_on_error = False
        self.parser.add_argument("cmd", choices=self.controller_choices)

    def update_completer(self, choices) -> None:
        """Update the completer with new choices."""
        if session.prompt_session and session.settings.USE_PROMPT_TOOLKIT:
            from openbb_cli.controllers.utils import get_data_files_for_completion

            if "load" not in choices:
                choices["load"] = {}

            data_files = get_data_files_for_completion()
            if data_files:
                file_completions = {file: None for file in data_files}
                choices["load"]["--file"] = file_completions
                choices["load"]["-f"] = file_completions
            choices["load"]["--sheet-name"] = None
            choices["load"]["--register_key"] = None
            choices["load"]["--help"] = None
            choices["load"]["-h"] = "--help"

            if "results" not in choices:
                choices["results"] = {}

            registry_all = session.obbject_registry.all
            index_completions = {str(idx): None for idx in registry_all}
            # ``register_key`` lives under ``extra`` on the OBBject — the
            # registry surfaces the OBBject (minus ``results``) verbatim,
            # so reach through ``extra`` for the key to complete on.
            key_completions = {
                (data.get("extra") or {}).get("register_key"): None
                for data in registry_all.values()
                if (data.get("extra") or {}).get("register_key")
            }

            choices["results"]["--index"] = (
                index_completions if index_completions else None
            )
            choices["results"]["-i"] = "--index"
            choices["results"]["--key"] = key_completions if key_completions else None
            choices["results"]["-k"] = "--key"
            choices["results"]["--chart"] = None
            choices["results"]["-c"] = "--chart"
            choices["results"]["--export"] = {
                "csv": None,
                "json": None,
                "xlsx": None,
                "png": None,
                "jpg": None,
                "db": None,
                "sqlite": None,
                "sqlite3": None,
            }
            choices["results"]["-e"] = "--export"
            choices["results"]["--sheet-name"] = None
            choices["results"]["--help"] = None
            choices["results"]["-h"] = "--help"

            self.completer = NestedCompleter.from_nested_dict(choices)

    def check_path(self) -> None:
        """Check if command path is valid."""
        path = self.PATH
        if path[0] != "/":
            raise ValueError("Path must begin with a '/' character.")
        if path[-1] != "/":
            raise ValueError("Path must end with a '/' character.")
        if not re.match(r"^[a-z0-9_\-/]*$", path):
            raise ValueError(
                "Path must only contain lowercase letters, digits, '_', '-', "
                "and '/' characters."
            )

    def load_class(self, class_ins, *args, **kwargs):
        """Check for an existing instance of the controller before creating a new one."""
        self.save_class()
        arguments = len(args) + len(kwargs)

        if class_ins.PATH in controllers and arguments == 1:
            old_class = controllers[class_ins.PATH]
            old_class.queue = self.queue
            old_class.update_completer(old_class.choices_default)
            return old_class.menu()
        return class_ins(*args, **kwargs).menu()

    def save_class(self) -> None:
        """Save the current instance of the class to be loaded later."""
        controllers[self.PATH] = self

    def custom_reset(self) -> list[str]:
        """Implement custom reset.

        This will be replaced by any children with custom_reset functions.
        """
        return []

    @abstractmethod
    def print_help(self) -> None:
        """Print help placeholder."""
        raise NotImplementedError("Must override print_help.")

    def parse_input(self, an_input: str) -> list:
        """Parse controller input.

        Protects file paths with -f/--file flags from being split on '/'.
        """
        file_flag = r"(\ -f |\ --file )"
        up_to = r".*?"
        known_extensions = (
            r"(\.(xlsx|csv|xls|tsv|json|yaml|ini|openbb|ipynb|db|sqlite|sqlite3))"
        )
        optional_args = r"(?:\ [^/]+)*?"
        file_path_pattern = f"({file_flag}{up_to}{known_extensions}{optional_args})"

        placeholders: dict[str, str] = {}
        placeholder_count = 0

        while True:
            match = re.search(pattern=file_path_pattern, string=an_input)
            if match is None:
                break

            placeholder = f"{{placeholder{placeholder_count}}}"
            placeholders[placeholder] = an_input[match.span()[0] : match.span()[1]]
            an_input = (
                an_input[: match.span()[0]] + placeholder + an_input[match.span()[1] :]
            )
            placeholder_count += 1

        commands = re.split(r"/(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)", an_input)

        result = []
        for cmd in commands:
            cleaned = cmd.strip()
            if cleaned:
                for placeholder, original in placeholders.items():
                    cleaned = cleaned.replace(placeholder, original)
                result.append(cleaned)

        if an_input.startswith("/") and (not result or result[0] != "home"):
            result.insert(0, "home")

        return result

    def switch(self, an_input: str) -> list[str]:
        """Process and dispatch input.

        Returns
        -------
        List[str]
            list of commands in the queue to execute
        """
        actions = self.parse_input(an_input)

        if an_input and an_input != "reset":
            session.console.print()

        if len(actions) == 0:
            pass

        elif len(actions) > 1:
            if not actions[0]:  # pragma: no cover
                actions[0] = "home"

            for cmd in actions[::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        else:
            try:
                known_args, other_args = self.parser.parse_known_args(
                    shlex.split(an_input)
                )
            except Exception as exc:
                raise SystemExit from exc

            if RECORD_SESSION:
                SESSION_RECORDED.append(an_input)

            if known_args.cmd:
                if known_args.cmd in ("..", "q"):
                    known_args.cmd = "quit"
                elif known_args.cmd in ("e"):
                    known_args.cmd = "exit"
                elif known_args.cmd in ("?", "h"):
                    known_args.cmd = "help"
                elif known_args.cmd == "r":
                    known_args.cmd = "reset"

            getattr(
                self,
                "call_" + known_args.cmd,
                lambda _: "Command not recognized!",
            )(other_args)

        if (
            an_input
            and an_input != "reset"
            and (
                not self.queue or (self.queue and self.queue[0] not in ("quit", "help"))
            )
        ):
            session.console.print()

        return self.queue

    def call_cls(self, _) -> None:
        """Process cls command."""
        system_clear()

    def call_home(self, _) -> None:
        """Process home command."""
        self.save_class()
        if self.PATH.count("/") == 1 and session.settings.ENABLE_EXIT_AUTO_HELP:
            self.print_help()
        for _ in range(self.PATH.count("/") - 1):
            self.queue.insert(0, "quit")

    def call_help(self, _) -> None:
        """Process help command."""
        self.print_help()

    def call_quit(self, _) -> None:
        """Process quit menu command."""
        self.save_class()
        self.queue.insert(0, "quit")

    def call_exit(self, _) -> None:
        """Process exit cli command."""
        self.save_class()
        for _ in range(self.PATH.count("/")):
            self.queue.insert(0, "quit")

    def call_reset(self, _) -> None:
        """Process reset command.

        If you would like to have customization in the reset process define a method
        `custom_reset` in the child class.
        """
        self.save_class()
        if self.PATH != "/":
            if self.custom_reset():
                self.queue = self.custom_reset() + self.queue
            else:
                for val in self.path[::-1]:
                    self.queue.insert(0, val)
            self.queue.insert(0, "reset")
            for _ in range(len(self.path)):
                self.queue.insert(0, "quit")

    def call_record(self, other_args) -> None:
        """Process record command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="record",
            description="Start recording session into .openbb routine file",
        )
        parser.add_argument(
            "-n",
            "--name",
            action="store",
            dest="name",
            type=str,
            default="",
            help="Routine title name to be saved - only use characters, digits and whitespaces.",
            nargs="+",
        )
        parser.add_argument(
            "-d",
            "--description",
            type=str,
            dest="description",
            help="The description of the routine",
            default=f"Routine recorded at {datetime.now().strftime('%H:%M')} from the OpenBB Platform CLI",
            nargs="+",
        )
        parser.add_argument(
            "--tag1",
            type=str,
            dest="tag1",
            help=f"The tag associated with the routine. Select from: {', '.join(SCRIPT_TAGS)}",
            default="",
            nargs="+",
        )
        parser.add_argument(
            "--tag2",
            type=str,
            dest="tag2",
            help=f"The tag associated with the routine. Select from: {', '.join(SCRIPT_TAGS)}",
            default="",
            nargs="+",
        )
        parser.add_argument(
            "--tag3",
            type=str,
            dest="tag3",
            help=f"The tag associated with the routine. Select from: {', '.join(SCRIPT_TAGS)}",
            default="",
            nargs="+",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")

        ns_parser, _ = self.parse_simple_args(parser, other_args)

        if ns_parser:
            if not ns_parser.name:
                session.console.print(
                    "[red]Set a routine title by using the '-n' flag. E.g. 'record -n Morning routine'[/red]"
                )
                return

            tag1 = (
                " ".join(ns_parser.tag1)
                if isinstance(ns_parser.tag1, list)
                else ns_parser.tag1
            )
            if tag1 and tag1 not in SCRIPT_TAGS:
                session.console.print(
                    f"[red]The parameter 'tag1' needs to be one of the following {', '.join(SCRIPT_TAGS)}[/red]"
                )
                return

            tag2 = (
                " ".join(ns_parser.tag2)
                if isinstance(ns_parser.tag2, list)
                else ns_parser.tag2
            )
            if tag2 and tag2 not in SCRIPT_TAGS:
                session.console.print(
                    f"[red]The parameter 'tag2' needs to be one of the following {', '.join(SCRIPT_TAGS)}[/red]"
                )
                return

            tag3 = (
                " ".join(ns_parser.tag3)
                if isinstance(ns_parser.tag3, list)
                else ns_parser.tag3
            )
            if tag3 and tag3 not in SCRIPT_TAGS:
                session.console.print(
                    f"[red]The parameter 'tag3' needs to be one of the following {', '.join(SCRIPT_TAGS)}[/red]"
                )
                return

            title = " ".join(ns_parser.name) if ns_parser.name else ""
            pattern = re.compile(r"^[a-zA-Z0-9\s]+$")
            if not pattern.match(title):
                session.console.print(
                    f"[red]Title '{title}' has invalid format. Please use only digits, characters and whitespaces.[/]"
                )
                return

            global RECORD_SESSION  # noqa: PLW0603
            global SESSION_RECORDED_NAME  # noqa: PLW0603
            global SESSION_RECORDED_DESCRIPTION  # noqa: PLW0603
            global SESSION_RECORDED_TAGS  # noqa: PLW0603

            RECORD_SESSION = True
            SESSION_RECORDED_NAME = title
            SESSION_RECORDED_DESCRIPTION = (
                " ".join(ns_parser.description)
                if isinstance(ns_parser.description, list)
                else ns_parser.description
            )
            SESSION_RECORDED_TAGS = tag1 if tag1 else ""
            SESSION_RECORDED_TAGS += "," + tag2 if tag2 else ""
            SESSION_RECORDED_TAGS += "," + tag3 if tag3 else ""

            session.console.print(
                f"[green]The routine '{title}' is successfully being recorded.[/green]"
            )
            session.console.print(
                "\n[yellow]Remember to run 'stop' command when you are done!\n[/yellow]"
            )

    def call_stop(self, other_args) -> None:
        """Process stop command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stop",
            description="Stop recording session into .openbb routine file",
        )
        _, _ = self.parse_simple_args(parser, other_args)

        if "-h" not in other_args and "--help" not in other_args:
            global RECORD_SESSION  # noqa: PLW0603
            global SESSION_RECORDED  # noqa: PLW0603

            if not RECORD_SESSION:
                session.console.print(
                    "[red]There is no session being recorded. Start one using the command 'record'[/red]\n"
                )
            elif len(SESSION_RECORDED) < 5:
                session.console.print(
                    "[red]Run at least 4 commands before stopping recording a session.[/red]\n"
                )
            else:
                current_user = session.user
                title_for_local_storage = (
                    SESSION_RECORDED_NAME.replace(" ", "_") + ".openbb"
                )

                routine_file = os.path.join(
                    f"{current_user.preferences.export_directory}/routines",
                    title_for_local_storage,
                )

                if os.path.isfile(routine_file):
                    i = session.console.input(
                        "A local routine with the same name already exists, do you want to override it? (y/n): "
                    )
                    session.console.print("")
                    while i.lower() not in ["y", "yes", "n", "no"]:
                        i = session.console.input("Select 'y' or 'n' to proceed: ")
                        session.console.print("")

                    if i.lower() in ["n", "no"]:
                        new_name = (
                            datetime.now().strftime("%Y%m%d_%H%M%S_")
                            + title_for_local_storage
                        )
                        routine_file = os.path.join(
                            current_user.preferences.export_directory,
                            "routines",
                            new_name,
                        )
                        session.console.print(
                            f"[yellow]The routine name has been updated to '{new_name}'[/yellow]\n"
                        )

                Path(os.path.dirname(routine_file)).mkdir(parents=True, exist_ok=True)

                with open(routine_file, "w") as file1:
                    lines = ["# OpenBB Platform CLI - Routine", "\n"]
                    lines += [
                        f"# Title: {SESSION_RECORDED_NAME}",
                        "\n",
                        f"# Tags: {SESSION_RECORDED_TAGS}",
                        "\n\n",
                        f"# Description: {SESSION_RECORDED_DESCRIPTION}",
                        "\n\n",
                    ]
                    lines += [c + "\n" for c in SESSION_RECORDED[:-1]]
                    file1.writelines(lines)

                session.console.print(
                    f"[green]Your routine has been recorded and saved here: {routine_file}[/green]\n"
                )

                RECORD_SESSION = False
                SESSION_RECORDED = list()

    def call_results(self, other_args: list[str]):
        """Process results command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="results",
            description="Process results command. This command displays a registry of "
            "'OBBjects' where all execution results are stored. "
            "It is organized as a stack, with the most recent result at index 0.",
        )
        parser.add_argument("-i", "--index", dest="index", help="Index of the result.")
        parser.add_argument("-k", "--key", dest="key", help="Key of the result.")
        parser.add_argument(
            "--chart", action="store_true", dest="chart", help="Display chart."
        )
        parser.add_argument(
            "--export",
            default="",
            type=check_file_type_saved(
                ["csv", "json", "xlsx", "png", "jpg", "db", "sqlite", "sqlite3"]
            ),
            dest="export",
            help="Export raw data into csv, json, xlsx, db/sqlite and figure into png or jpg.",
            nargs="+",
        )
        parser.add_argument(
            "--sheet-name",
            dest="sheet_name",
            default=None,
            nargs="+",
            help="Name of excel sheet to save data to. Only valid for .xlsx files.",
        )

        ns_parser, unknown_args = self.parse_simple_args(
            parser, other_args, unknown_args=True
        )

        if ns_parser:
            kwargs = parse_unknown_args_to_dict(unknown_args)
            if not ns_parser.index and not ns_parser.key:
                results = session.obbject_registry.all
                if results:
                    df = pd.DataFrame.from_dict(results, orient="index")
                    session.output_adapter.display(
                        data=df,
                        title="OBBject Results",
                        export=False,
                        chart=False,
                    )
                else:
                    session.console.print("[info]No results found.[/info]")
            elif ns_parser.index:
                try:
                    index = int(ns_parser.index)
                except ValueError:
                    session.console.print(
                        f"[red]Index must be an integer, not '{ns_parser.index}'.[/red]"
                    )
                    return
                obbject = session.obbject_registry.get(index)
                if obbject:
                    handle_obbject_display(
                        obbject=obbject,
                        chart=ns_parser.chart,
                        export=ns_parser.export,
                        sheet_name=ns_parser.sheet_name,
                        **kwargs,
                    )
                else:
                    session.console.print(
                        f"[info]No result found at index {index}.[/info]"
                    )
            elif ns_parser.key:
                obbject = session.obbject_registry.get(ns_parser.key)
                if obbject:
                    handle_obbject_display(
                        obbject=obbject,
                        chart=ns_parser.chart,
                        export=ns_parser.export,
                        sheet_name=ns_parser.sheet_name,
                        **kwargs,
                    )
                else:
                    session.console.print(
                        f"[info]No result found with key '{ns_parser.key}'.[/info]"
                    )

    def call_load(self, other_args: list[str]):  # noqa: PLR0912
        """Load data from CSV, JSON, or Excel file."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load data from a CSV, JSON, or Excel file in OpenBBUserData folder. "
            "The loaded data will be added to the results cache.",
        )
        parser.add_argument(
            "-f",
            "--file",
            dest="file",
            type=str,
            required=True,
            help="Path to file relative to OpenBBUserData folder.",
        )
        parser.add_argument(
            "--sheet-name",
            dest="sheet_name",
            type=str,
            default=None,
            help="Name of excel sheet to load. Only for .xlsx files. If not provided, loads first sheet.",
        )
        parser.add_argument(
            "--register_key",
            dest="register_key",
            default="",
            help="Key to reference data in the OBBject registry.",
            type=validate_register_key,
        )

        ns_parser = self.parse_simple_args(parser, other_args)[0]

        if ns_parser and ns_parser.file:
            from openbb_core.app.model.obbject import OBBject

            file_path_str = ns_parser.file

            user_data_dir = Path(session.user.preferences.data_directory)
            file_path = user_data_dir / file_path_str

            if not file_path.exists():
                session.console.print(f"[red]File not found: {file_path}[/red]")
                return

            try:
                file_ext = file_path.suffix.lower()

                if file_ext == ".csv":
                    df = pd.read_csv(file_path, index_col=None)
                    df = df.loc[:, ~df.columns.str.startswith("Unnamed:")]

                    obbject = OBBject(results=df)

                    command = f"/load -f {file_path_str}"
                    obbject.extra["command"] = command

                    if ns_parser.register_key:
                        if (
                            ns_parser.register_key
                            not in session.obbject_registry.obbject_keys
                        ):
                            obbject.extra["register_key"] = ns_parser.register_key
                        else:
                            session.console.print(
                                f"[yellow]Key `{ns_parser.register_key}` already exists in the registry. "
                                "The `OBBject` was kept without the key.[/yellow]"
                            )

                    if session.max_obbjects_exceeded():
                        session.obbject_registry.remove()
                        session.console.print(
                            "[yellow]Maximum number of OBBjects reached. The oldest entry was removed.[/yellow]"
                        )

                    if session.obbject_registry.register(obbject):
                        session.console.print(
                            f"[green]Successfully loaded {len(df)} rows from {file_path.name}[/green]"
                        )

                        if hasattr(self, "_link_obbject_to_data_processing_commands"):
                            self._link_obbject_to_data_processing_commands()  # ty: ignore[call-non-callable]
                            self.update_completer(self.choices_default)

                        session.output_adapter.display(
                            data=obbject,
                            title=f"Loaded: {file_path_str}",
                            export=False,
                            chart=False,
                        )
                    else:
                        session.console.print(
                            "[yellow]Failed to register OBBject in registry.[/yellow]"
                        )

                elif file_ext == ".json":
                    df = pd.read_json(file_path)

                    obbject = OBBject(results=df)
                    command = f"/load -f {file_path_str}"
                    obbject.extra["command"] = command

                    if ns_parser.register_key:
                        if (
                            ns_parser.register_key
                            not in session.obbject_registry.obbject_keys
                        ):
                            obbject.extra["register_key"] = ns_parser.register_key
                        else:
                            session.console.print(
                                f"[yellow]Key `{ns_parser.register_key}` already exists in the registry. "
                                "The `OBBject` was kept without the key.[/yellow]"
                            )

                    if session.max_obbjects_exceeded():
                        session.obbject_registry.remove()
                        session.console.print(
                            "[yellow]Maximum number of OBBjects reached. The oldest entry was removed.[/yellow]"
                        )

                    if session.obbject_registry.register(obbject):
                        session.console.print(
                            f"[green]Successfully loaded {len(df)} rows from {file_path.name}[/green]"
                        )

                        if hasattr(self, "_link_obbject_to_data_processing_commands"):
                            self._link_obbject_to_data_processing_commands()  # ty: ignore[call-non-callable]
                            self.update_completer(self.choices_default)

                        session.output_adapter.display(
                            data=obbject,
                            title=f"Loaded: {file_path_str}",
                            export=False,
                            chart=False,
                        )
                    else:
                        session.console.print(
                            "[yellow]Failed to register OBBject in registry.[/yellow]"
                        )

                elif file_ext in [".xlsx", ".xls"]:
                    sheet_name = ns_parser.sheet_name if ns_parser.sheet_name else 0
                    df = pd.read_excel(file_path, sheet_name=sheet_name, index_col=None)
                    df = df.loc[:, ~df.columns.str.startswith("Unnamed:")]

                    obbject = OBBject(results=df)
                    command = f"/load -f {file_path_str}"
                    if ns_parser.sheet_name:
                        command += f" --sheet-name {ns_parser.sheet_name}"
                    obbject.extra["command"] = command

                    if ns_parser.register_key:
                        if (
                            ns_parser.register_key
                            not in session.obbject_registry.obbject_keys
                        ):
                            obbject.extra["register_key"] = ns_parser.register_key
                        else:
                            session.console.print(
                                f"[yellow]Key `{ns_parser.register_key}` already exists in the registry. "
                                "The `OBBject` was kept without the key.[/yellow]"
                            )

                    if session.max_obbjects_exceeded():
                        session.obbject_registry.remove()
                        session.console.print(
                            "[yellow]Maximum number of OBBjects reached. The oldest entry was removed.[/yellow]"
                        )

                    if session.obbject_registry.register(obbject):
                        session.console.print(
                            f"[green]Successfully loaded {len(df)} rows from {file_path.name}[/green]"
                        )

                        if hasattr(self, "_link_obbject_to_data_processing_commands"):
                            self._link_obbject_to_data_processing_commands()  # ty: ignore[call-non-callable]
                            self.update_completer(self.choices_default)

                        session.output_adapter.display(
                            data=obbject,
                            title=f"Loaded: {file_path_str}",
                            export=False,
                            chart=False,
                        )
                    else:
                        session.console.print(
                            "[yellow]Failed to register OBBject in registry.[/yellow]"
                        )

                elif file_ext in [".db", ".sqlite", ".sqlite3"]:
                    import sqlite3

                    from openbb_cli.controllers.utils import SQLiteTable

                    conn = sqlite3.connect(file_path)
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                        )
                        tables = [row[0] for row in cursor.fetchall()]

                        if not tables:
                            session.console.print(
                                f"[yellow]No tables found in database: {file_path.name}[/yellow]"
                            )
                            return

                        loaded_count = 0
                        for table_name in tables:
                            quoted = '"' + table_name.replace('"', '""') + '"'
                            cursor.execute(f"SELECT COUNT(*) FROM {quoted}")  # noqa: S608
                            row_count = cursor.fetchone()[0]

                            sqlite_table = SQLiteTable(
                                db_path=str(file_path),
                                table_name=table_name,
                                row_count=row_count,
                            )

                            obbject = OBBject(results=sqlite_table)
                            command = f"/load -f {file_path_str} --table {table_name}"
                            obbject.extra["command"] = command

                            base_name = file_path.stem
                            auto_key = f"{base_name}_{table_name}"

                            if ns_parser.register_key and len(tables) == 1:
                                if (
                                    ns_parser.register_key
                                    not in session.obbject_registry.obbject_keys
                                ):
                                    obbject.extra["register_key"] = (
                                        ns_parser.register_key
                                    )
                                else:
                                    session.console.print(
                                        f"[yellow]Key `{ns_parser.register_key}` already exists. "
                                        f"Using auto-generated key: {auto_key}[/yellow]"
                                    )
                                    obbject.extra["register_key"] = auto_key
                            elif auto_key not in session.obbject_registry.obbject_keys:
                                obbject.extra["register_key"] = auto_key
                            else:
                                session.console.print(
                                    f"[yellow]Key `{auto_key}` already exists in the registry. "
                                    "The `OBBject` was kept without the key.[/yellow]"
                                )

                            if session.max_obbjects_exceeded():
                                session.obbject_registry.remove()
                                session.console.print(
                                    "[yellow]Maximum number of OBBjects reached. The oldest entry was removed.[/yellow]"
                                )

                            if session.obbject_registry.register(obbject):
                                loaded_count += 1
                                cursor.execute(f"PRAGMA table_info({table_name})")
                                columns = [col[1] for col in cursor.fetchall()]

                                session.console.print(
                                    f"[green]Loaded table '{table_name}': {row_count} rows, "
                                    f"{len(columns)} columns (lazy)[/green]"
                                )

                        if loaded_count > 0:
                            session.console.print(
                                f"[green]Successfully loaded {loaded_count} table(s) from {file_path.name}[/green]"
                            )

                            if hasattr(
                                self, "_link_obbject_to_data_processing_commands"
                            ):
                                self._link_obbject_to_data_processing_commands()  # ty: ignore[call-non-callable]
                                self.update_completer(self.choices_default)
                    finally:
                        conn.close()

                else:
                    session.console.print(
                        f"[red]Unsupported file type: {file_ext}. "
                        "Supported: .csv, .json, .xlsx, .xls, .db, .sqlite, .sqlite3[/red]"
                    )
                    return

            except Exception as e:
                session.console.print(f"[red]Error loading file: {e}[/red]")

    @staticmethod
    def parse_simple_args(
        parser: argparse.ArgumentParser,
        other_args: list[str],
        unknown_args: bool = False,
    ) -> tuple[argparse.Namespace | None, list[str] | None]:
        """Parse list of arguments into the supplied parser.

        Parameters
        ----------
        parser: argparse.ArgumentParser
            Parser with predefined arguments
        other_args: List[str]
            List of arguments to parse
        unknown_args: bool
            Flag to indicate if unknown arguments should be returned

        Returns
        -------
        ns_parser: argparse.Namespace
            Namespace with parsed arguments
        l_unknown_args: List[str]
            List of unknown arguments
        """
        parser.add_argument(
            "-h", "--help", action="store_true", help="show this help message"
        )

        if session.settings.USE_CLEAR_AFTER_CMD:
            system_clear()

        try:
            ns_parser, l_unknown_args = parser.parse_known_args(other_args)
        except SystemExit:
            session.console.print("\n")
            return None, None

        if ns_parser.help:
            txt_help = parser.format_help()
            session.console.print(f"[help]{txt_help}[/help]")
            return None, None

        if l_unknown_args and not unknown_args:
            session.console.print(
                f"The following args couldn't be interpreted: {l_unknown_args}\n"
            )
        return ns_parser, l_unknown_args

    @classmethod
    def parse_known_args_and_warn(
        cls,
        parser: argparse.ArgumentParser,
        other_args: list[str],
        export_allowed: Literal[
            "no_export", "raw_data_only", "figures_only", "raw_data_and_figures"
        ] = "no_export",
        raw: bool = False,
        limit: int = 0,
    ):
        """Parse list of arguments into the supplied parser.

        Parameters
        ----------
        parser: argparse.ArgumentParser
            Parser with predefined arguments
        other_args: List[str]
            list of arguments to parse
        export_allowed: Literal["no_export", "raw_data_only", "figures_only", "raw_data_and_figures"]
            Export options
        raw: bool
            Add the --raw flag
        limit: int
            Add a --limit flag with this number default

        Returns
        -------
        ns_parser:
            Namespace with parsed arguments
        """
        parser.add_argument(
            "-h", "--help", action="store_true", help="show this help message"
        )

        if export_allowed != "no_export":
            choices_export = []
            help_export = "Does not export!"

            if export_allowed == "raw_data_only":
                choices_export = ["csv", "json", "xlsx"]
                help_export = "Export raw data into csv, json or xlsx."
            elif export_allowed == "figures_only":
                choices_export = ["png", "jpg"]
                help_export = "Export figure into png or jpg."
            else:
                choices_export = [
                    "csv",
                    "json",
                    "xlsx",
                    "png",
                    "jpg",
                    "db",
                    "sqlite",
                    "sqlite3",
                ]
                help_export = "Export raw data into csv, json, xlsx, db/sqlite and figure into png or jpg."

            parser.add_argument(
                "--export",
                default="",
                type=check_file_type_saved(choices_export),
                dest="export",
                help=help_export,
                nargs="+",
            )

            if export_allowed in [
                "raw_data_only",
                "raw_data_and_figures",
            ]:
                parser.add_argument(
                    "--sheet-name",
                    dest="sheet_name",
                    default=None,
                    nargs="+",
                    help="Name of excel sheet to save data to. Only valid for .xlsx files.",
                )

        if raw:
            parser.add_argument(
                "--raw",
                dest="raw",
                action="store_true",
                default=False,
                help="Flag to display raw data",
            )
        if limit > 0:
            parser.add_argument(
                "-l",
                "--limit",
                dest="limit",
                default=limit,
                help="Number of entries to show in data.",
                type=check_positive,
            )

        parser.add_argument(
            "--register_obbject",
            dest="register_obbject",
            action="store_false",
            default=True,
            help="Flag to store data in the OBBject registry, True by default.",
        )
        parser.add_argument(
            "--register_key",
            dest="register_key",
            default="",
            help="Key to reference data in the OBBject registry.",
            type=validate_register_key,
        )

        if session.settings.USE_CLEAR_AFTER_CMD:
            system_clear()

        if "--help" in other_args or "-h" in other_args:
            txt_help = parser.format_help() + "\n"
            session.console.print(f"[help]{txt_help}[/help]")
            return None

        try:
            routine_args_index = next(
                (
                    i + 1
                    for i, arg in enumerate(other_args)
                    if arg in ("-i", "--input")
                    and "routine_args" in [action.dest for action in parser._actions]
                ),
                -1,
            )
            no_split_indices: set[int] = set()
            if 0 <= routine_args_index < len(other_args):
                no_split_indices.add(routine_args_index)

            for i, arg in enumerate(other_args):
                if not arg.startswith("-"):
                    continue
                flag_part = arg.split("=", 1)[0] if "=" in arg else arg
                for action in parser._actions:
                    if flag_part in action.option_strings and action.nargs != 0:
                        if "=" in arg:
                            no_split_indices.add(i)
                        elif action.nargs in ("+", "*") or (
                            isinstance(action.nargs, int) and action.nargs > 1
                        ):
                            j = i + 1
                            while j < len(other_args) and not other_args[j].startswith(
                                "-"
                            ):
                                no_split_indices.add(j)
                                j += 1
                        elif i + 1 < len(other_args):
                            no_split_indices.add(i + 1)
                        break

            other_args = [
                part
                for index, arg in enumerate(other_args)
                for part in ([arg] if index in no_split_indices else arg.split(","))
            ]

            for action in parser._actions:
                if getattr(action, "optional_choices", None):
                    action.choices = None

            ns_parser, l_unknown_args = parser.parse_known_args(other_args)

            if export_allowed in [
                "raw_data_only",
                "raw_data_and_figures",
            ]:
                ns_parser.is_image = any(
                    ext in ns_parser.export for ext in ["png", "jpg"]
                )

        except SystemExit:
            return None

        if l_unknown_args:
            session.console.print(
                f"The following args couldn't be interpreted: {l_unknown_args}"
            )
        return ns_parser

    def menu(self, custom_path_menu_above: str = ""):
        """Enter controller menu."""
        settings = session.settings
        an_input = "HELP_ME"

        while True:
            if self.queue and len(self.queue) > 0:
                if self.queue[0] in ("q", "..", "quit"):
                    self.save_class()
                    if custom_path_menu_above:
                        self.queue.insert(1, custom_path_menu_above)

                    if len(self.queue) > 1:
                        return self.queue[1:]

                    if settings.ENABLE_EXIT_AUTO_HELP:
                        return ["help"]
                    return []

                an_input = self.queue[0]
                self.queue = self.queue[1:]

                if (
                    an_input
                    and an_input not in ("home", "help")
                    and an_input.split(" ")[0] in self.controller_choices
                ):
                    session.console.print(
                        f"{get_flair_and_username()} {self.PATH} $ {an_input}"
                    )

            else:
                if an_input == "HELP_ME":
                    self.print_help()

                try:
                    prompt_session = session.prompt_session
                    if prompt_session and settings.USE_PROMPT_TOOLKIT:
                        if settings.TOOLBAR_HINT:
                            an_input = prompt_session.prompt(
                                f"{get_flair_and_username()} {self.PATH} $ ",
                                completer=self.completer,
                                search_ignore_case=True,
                                bottom_toolbar=HTML(
                                    '<style bg="ansiblack" fg="ansiwhite">[h]</style> help menu    '
                                    '<style bg="ansiblack" fg="ansiwhite">[q]</style> return to previous menu    '
                                    '<style bg="ansiblack" fg="ansiwhite">[e]</style> exit the program    '
                                    '<style bg="ansiblack" fg="ansiwhite">[cmd -h]</style> '
                                    "see usage and available options    "
                                    f"{self.path[-1].capitalize()} (cmd/menu) Documentation"
                                ),
                                style=Style.from_dict(
                                    {"bottom-toolbar": "#ffffff bg:#333333"}
                                ),
                            )
                        else:
                            an_input = prompt_session.prompt(
                                f"{get_flair_and_username()} {self.PATH} $ ",
                                completer=self.completer,
                                search_ignore_case=True,
                            )
                    else:
                        an_input = input(f"{get_flair_and_username()} {self.PATH} $ ")

                except (KeyboardInterrupt, EOFError):
                    an_input = "exit"

            try:
                an_input = "home" if an_input == "/" else an_input

                self.queue = self.switch(an_input)

            except SystemExit:
                session.console.print(
                    f"[red]The command '{an_input}' doesn't exist on the {self.PATH} menu.[/red]\n",
                )
                similar_cmd = difflib.get_close_matches(
                    an_input.split(" ")[0] if " " in an_input else an_input,
                    self.controller_choices,
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    if " " in an_input:
                        candidate_input = (
                            f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                        )
                        if candidate_input == an_input:  # pragma: no cover
                            an_input = ""
                            self.queue = []
                            session.console.print("\n")
                            continue

                        an_input = candidate_input
                    else:
                        an_input = similar_cmd[0]

                    session.console.print(
                        f"[green]Replacing by '{an_input}'.[/green]\n"
                    )
                    self.queue.insert(0, an_input)
