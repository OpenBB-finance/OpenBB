"""Main CLI Module."""

import argparse
import contextlib
import difflib
import os
import re
import sys
import webbrowser
from datetime import datetime
from functools import partial, update_wrapper
from pathlib import Path
from types import MethodType
from typing import Any

import pandas as pd
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from openbb_cli.backend import Backend, LocalBackend
from openbb_cli.config import constants
from openbb_cli.config.constants import (
    ASSETS_DIRECTORY,
    ENV_FILE_SETTINGS,
    HOME_DIRECTORY,
    REPOSITORY_DIRECTORY,
)
from openbb_cli.config.menu_text import MenuText
from openbb_cli.controllers.base_controller import BaseController
from openbb_cli.controllers.platform_controller_factory import (
    PlatformControllerFactory,
)
from openbb_cli.controllers.script_parser import is_reset, parse_openbb_script
from openbb_cli.controllers.utils import (
    bootup,
    first_time_user,
    get_flair_and_username,
    parse_and_split_input,
    print_goodbye,
    print_rich_table,
    reset,
    suppress_stdout,
    welcome_message,
)
from openbb_cli.session import Session

NON_DATA_ROUTERS = ["coverage", "reference", "system", "user"]
DATA_PROCESSING_ROUTERS = ["technical", "quantitative", "econometrics"]
env_file = str(ENV_FILE_SETTINGS)
session = Session()


def _result_to_obbject(result: Any, router: str, other_args: list[str]) -> Any:
    """Lift a spec-mode dispatcher result to an ``OBBject`` for registry insert.

    Two cases:

    * The dispatcher already produced a live ``OBBject`` instance (spec
      command had column metadata) — pass it through unchanged. The
      private attrs (``_route``, ``_standard_params``) the dispatcher
      already set are preserved that way; reconstruction would lose them.
    * Bare rows (list / single dict) — the spec had no column metadata,
      so wrap them in a fresh ``OBBject`` so the registry can still
      surface the call.

    In both cases ``extra['command']`` gets stamped with the invocation
    line so the legacy ``results`` recall table shows what was run.
    Returns ``None`` if there's nothing wrappable (scalars, ``None``).
    """
    try:
        from openbb_core.app.model.obbject import OBBject
    except ImportError:
        return None
    if isinstance(result, OBBject):
        obbject = result
    elif isinstance(result, (list, dict)):
        try:
            obbject = OBBject(results=result)
            obbject._route = "/" + router.replace(".", "/").strip("/")
        except Exception:  # noqa: BLE001 — registration is best-effort
            return None
    else:
        return None
    obbject.extra["command"] = f"/{router} {' '.join(other_args)}".strip()
    return obbject


def _params_to_completions(parameters: list[dict[str, Any]]) -> dict[str, Any]:
    """Translate normalized spec parameters into a NestedCompleter dict.

    Each parameter becomes ``--name: {choice1: None, choice2: None}`` when
    the spec declares ``choices``, otherwise ``--name: None`` for free-form
    values. ``--help`` / ``-h`` are appended so users can tab through to
    the help flag.
    """
    out: dict[str, Any] = {}
    for p in parameters or []:
        name = p.get("name")
        if not name:
            continue
        flag = f"--{name}"
        choices_list = p.get("choices") or []
        if choices_list:
            out[flag] = {str(c): None for c in choices_list}
        else:
            out[flag] = None
    out["--help"] = None
    out["-h"] = "--help"
    return out


class CLIController(BaseController):
    """CLI Controller class.

    Sources its top-level menu and command choices from a ``Backend`` —
    ``LocalBackend`` (in-process ``obb``, the historical default) or any
    other implementation passed in by the launcher (e.g. ``SpecBackend``
    for spec-driven REPL use).
    """

    CHOICES_COMMANDS_BUILTIN = ["record", "stop", "exe", "results"]
    CHOICES_MENUS_BUILTIN = ["settings", "user", "feature"]

    PATH = "/"
    CHOICES_GENERATION = False

    def __init__(
        self,
        jobs_cmds: list[str] | None = None,
        *,
        backend: Backend | None = None,
    ):
        """Construct CLI controller."""
        self.ROUTINE_FILES: dict[str, Path] = dict()
        self.ROUTINE_CHOICES: dict[str, Any] = dict()

        self._backend: Backend = backend if backend is not None else LocalBackend()

        platform_routers = self._backend.routers
        menus = list(self.CHOICES_MENUS_BUILTIN)
        commands = list(self.CHOICES_COMMANDS_BUILTIN)
        for router, kind in platform_routers.items():
            if router == "user":
                continue
            (menus if kind == "menu" else commands).append(router)
        self.CHOICES_MENUS = menus
        self.CHOICES_COMMANDS = commands

        super().__init__(jobs_cmds)

        self.queue: list[str] = list()

        if jobs_cmds:
            self.queue = parse_and_split_input(
                an_input=" ".join(jobs_cmds), custom_filters=[]
            )

        self.update_success = False

        self._generate_platform_commands()

        self.update_runtime_choices()

    def _generate_platform_commands(self):
        """Generate Platform based commands/menus from the configured backend."""
        backend = self._backend

        def method_call_class(self, _, controller, name, parent_path, target):
            self.queue = self.load_class(
                controller, name, parent_path, target, self.queue
            )

        def method_call_command_legacy(self, _, router: str):
            """Display the static command-target metadata for in-process ``obb``."""
            mdl = backend.get_command_target(router)
            df = pd.DataFrame.from_dict(mdl.model_dump(), orient="index")
            if isinstance(df.columns, pd.RangeIndex):
                df.columns = [str(i) for i in df.columns]
            return print_rich_table(df, show_index=True)

        def method_call_command_spec(self, other_args: list[str], router: str):
            """Dispatch a top-level command-typed router via SpecBackend.

            Builds a ``SpecTranslator`` for the leaf command, parses
            ``other_args`` against its parser (so ``--help`` works), executes,
            and renders the result. Without this, top-level leaves like
            ``law`` for the Congress.gov spec would silently dump their spec
            metadata instead of invoking the API.

            Registers the result in ``session.obbject_registry`` so the
            legacy ``results`` recall command surfaces it — same UX as
            installed-extension calls. When the dispatcher already
            produced an OBBject dump (spec carries column metadata), the
            dict is round-tripped via ``OBBject.model_validate``;
            otherwise the bare rows get wrapped in a fresh OBBject.
            """
            from openbb_cli.backend import SpecTranslator

            spec_doc: dict[str, Any] = getattr(backend, "_spec", {})
            cmd_spec = spec_doc.get("commands", {}).get(router)
            if cmd_spec is None:
                session.console.print(f"[red]Command not found in spec: {router}[/red]")
                return
            translator = SpecTranslator(
                router, cmd_spec, getattr(backend, "_dispatcher", None)
            )
            ns_parser = self.parse_known_args_and_warn(
                parser=translator.parser,
                other_args=other_args,
                export_allowed="raw_data_only",
            )
            if not ns_parser:
                return
            try:
                result = translator.execute_func(ns_parser)
            except Exception as exc:  # noqa: BLE001 — surface dispatch errors to user
                session.console.print(f"[red]error: {exc}[/red]")
                return

            obbject = _result_to_obbject(result, router, other_args)
            if obbject is not None and obbject.results is not None:
                if session.max_obbjects_exceeded():
                    session.obbject_registry.remove()
                    session.console.print(
                        "[yellow]Maximum number of OBBjects reached. "
                        "The oldest entry was removed.[/yellow]"
                    )
                if session.obbject_registry.register(obbject) and (
                    session.settings.SHOW_MSG_OBBJECT_REGISTRY
                ):
                    session.console.print("Added `OBBject` to cached results.")

            # ``obbject`` is either the live OBBject the dispatcher
            # built (when there's column metadata) or a freshly-wrapped
            # one. Either way ``obbject.results`` is the row payload to
            # render; falling back to ``result`` covers the
            # unwrap-failed case where ``obbject`` is None.
            payload: Any
            if obbject is not None:
                payload = obbject.results
            elif isinstance(result, dict):
                payload = result.get("results", result)
            else:
                payload = result
            if isinstance(payload, dict):
                df = pd.DataFrame([payload])
            elif isinstance(payload, list):
                df = pd.DataFrame(payload)
            else:
                df = pd.DataFrame({"value": [payload]})
            session.output_adapter.display(df, title=f"/{router}")

        is_spec_backend = hasattr(backend, "_spec") and hasattr(backend, "_dispatcher")
        method_call_command: Any = (
            method_call_command_spec if is_spec_backend else method_call_command_legacy
        )

        spec_commands: dict[str, Any] = (
            getattr(backend, "_spec", {}).get("commands", {}) if is_spec_backend else {}
        )

        def method_call_menu_or_leaf(
            self,
            other_args: list[str],
            controller,
            name: str,
            parent_path: list[str],
            target,
            router: str,
        ):
            """Hybrid for routers that have both a leaf path and nested commands.

            Bare invocation (no args) opens the submenu — the user explores
            sub-commands. Any args fall through to the leaf so e.g.
            ``bill --limit 5`` lists the most-recent bills via ``/bill``
            instead of pointlessly dropping into a submenu where every
            sub-command needs a ``congress``/``billNumber`` you don't have yet.
            """
            if other_args:
                method_call_command_spec(self, other_args, router)
                return
            self.queue = self.load_class(
                controller, name, parent_path, target, self.queue
            )

        for router, value in backend.routers.items():
            if router == "user":
                continue

            has_leaf = router in spec_commands

            if value == "menu":
                pcf = PlatformControllerFactory(backend=backend, router_name=router)
                DynamicController = pcf.create()

                if has_leaf:
                    bound_method = MethodType(method_call_menu_or_leaf, self)
                    bound_method = update_wrapper(
                        partial(
                            bound_method,
                            controller=DynamicController,
                            name=router,
                            target=None,
                            parent_path=self.path,
                            router=router,
                        ),
                        method_call_menu_or_leaf,
                    )
                else:
                    bound_method = MethodType(method_call_class, self)
                    bound_method = update_wrapper(
                        partial(
                            bound_method,
                            controller=DynamicController,
                            name=router,
                            target=None,
                            parent_path=self.path,
                        ),
                        method_call_class,
                    )
            else:
                bound_method = MethodType(method_call_command, self)
                bound_method = update_wrapper(
                    partial(bound_method, router=router),
                    method_call_command,  # ty: ignore[invalid-argument-type]
                )

            setattr(self, f"call_{router}", bound_method)

    def _spec_command_completions(self) -> dict[str, dict[str, Any]]:
        """Build per-command completion choices from the SpecBackend's metadata.

        Returns ``{command: {--flag: {choice: None, ...} | None}}``.
        Includes both pure-command routers (``law``, ``treaty``) and hybrid
        menu/leaf routers (``bill``, ``congress`` — they're menus by router
        classification but the same name is also a leaf in ``spec.commands``,
        so ``bill --limit 5`` should suggest the leaf's flags).
        """
        out: dict[str, dict[str, Any]] = {}
        backend = getattr(self, "_backend", None)
        if backend is None:
            return out
        spec_doc = getattr(backend, "_spec", None)
        if not isinstance(spec_doc, dict):
            return out
        commands = spec_doc.get("commands", {})
        for router in backend.routers:
            if router not in self.controller_choices:
                continue
            cmd_spec = commands.get(router)
            if not cmd_spec:
                continue
            out[router] = _params_to_completions(cmd_spec.get("parameters", []))
        return out

    def update_runtime_choices(self):
        """Update runtime choices."""
        routines_directory = Path(session.user.preferences.export_directory, "routines")

        if session.prompt_session and session.settings.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices.update(self._spec_command_completions())

            self.ROUTINE_FILES = {
                filepath.name: filepath
                for filepath in routines_directory.rglob("*.openbb")
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
                "--help": None,
                "-h": "--help",
            }
            choices["record"] = {
                "--name": None,
                "-n": "--name",
                "--description": None,
                "-d": "--description",
                "--tag1": {c: None for c in constants.SCRIPT_TAGS},
                "--tag2": {c: None for c in constants.SCRIPT_TAGS},
                "--tag3": {c: None for c in constants.SCRIPT_TAGS},
                "--help": None,
                "-h": "--help",
            }
            choices["stop"] = {"--help": None, "-h": "--help"}

            registry_all = session.obbject_registry.all
            index_completions = {str(idx): None for idx in registry_all}
            # ``register_key`` lives under ``extra`` (it's an OBBject
            # extra field stamped in via ``--register-key NAME``); read
            # from there so completions still surface user-named entries.
            key_completions = {
                (data.get("extra") or {}).get("register_key"): None
                for data in registry_all.values()
                if (data.get("extra") or {}).get("register_key")
            }

            choices["results"] = {
                "--index": index_completions if index_completions else None,
                "-i": "--index",
                "--key": key_completions if key_completions else None,
                "-k": "--key",
                "--chart": None,
                "-c": "--chart",
                "--export": {
                    c: None
                    for c in [
                        "csv",
                        "json",
                        "xlsx",
                        "png",
                        "jpg",
                        "db",
                        "sqlite",
                        "sqlite3",
                    ]
                },
                "-e": "--export",
                "--sheet-name": None,
                "--help": None,
                "-h": "--help",
            }
            choices["load"] = {
                "--file": None,
                "-f": "--file",
                "--sheet-name": None,
                "--register_key": None,
                "--help": None,
                "-h": "--help",
            }

            self.update_completer(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("")
        mt.add_info("\nConfigure CLI")
        mt.add_menu(
            "settings",
            description="enable and disable feature flags, preferences and settings",
        )
        mt.add_menu(
            "user",
            description="view and set platform user preferences for the session",
        )
        mt.add_raw("\n")
        mt.add_info("Record and execute your own .openbb routine scripts")
        mt.add_cmd("record", description="start recording current session")
        mt.add_cmd(
            "stop", description="stop session recording and convert to .openbb routine"
        )
        mt.add_cmd(
            "exe",
            description="execute .openbb routine scripts (use exe --example for an example)",
        )
        mt.add_raw("\n")
        mt.add_info("Retrieve data from different asset classes and providers")

        platform_routers = self._backend.routers
        reference_routers = self._backend.reference_routers
        reference_paths = self._backend.reference_paths

        def _menu_description(router: str) -> str:
            """Return the menu's reference description (tolerant of trailing slash)."""
            for key in (f"{self.PATH}{router}/", f"{self.PATH}{router}"):
                desc = reference_routers.get(key, {}).get("description") or ""
                if desc:
                    return desc.split(".")[0].lower()
            return ""

        def _command_description(router: str) -> str:
            """Return the operation description for top-level command-typed routers."""
            for key in (f"{self.PATH}{router}", f"{self.PATH}{router}/"):
                desc = reference_paths.get(key, {}).get("description") or ""
                if desc:
                    return desc.split(".")[0].lower()
            return ""

        for router, value in platform_routers.items():
            if router in NON_DATA_ROUTERS or router in DATA_PROCESSING_ROUTERS:
                continue
            if value == "menu":
                mt.add_menu(name=router, description=_menu_description(router))
            else:
                mt.add_cmd(name=router, description=_command_description(router))

        if any(router in platform_routers for router in DATA_PROCESSING_ROUTERS):
            mt.add_info("\nAnalyze and process previously obtained data")

            for router, value in platform_routers.items():
                if router not in DATA_PROCESSING_ROUTERS:
                    continue
                if value == "menu":
                    mt.add_menu(name=router, description=_menu_description(router))
                else:
                    mt.add_cmd(name=router, description=_command_description(router))

        mt.add_raw("\n")
        mt.add_info("Data manipulation and feature engineering")
        mt.add_menu("feature", description="feature engineering and table operations")
        mt.add_cmd("load", description="load data from file in OpenBBUserData")
        mt.add_cmd("results")
        if session.obbject_registry.obbjects:
            mt.add_info("\nCached Results")
            for key, value in list(session.obbject_registry.all.items())[
                : session.settings.N_TO_DISPLAY_OBBJECT_REGISTRY
            ]:
                # ``command`` lives under ``extra`` — the registry surfaces
                # the full OBBject (minus ``results``), and ``command``
                # belongs to OBBject's ``extra`` slot. Empty string
                # fallback covers OBBjects from non-CLI sources that
                # never got the command stamped in.
                command = (value.get("extra") or {}).get("command", "")
                mt.add_raw(
                    f"[yellow]OBB{key}[/yellow]: {command}",
                    left_spacing=True,
                )

        session.console.print(text=mt.menu_text, menu="Home")
        self.update_runtime_choices()

    def call_settings(self, _):
        """Process settings command."""
        from openbb_cli.controllers.settings_controller import (
            SettingsController,
        )

        self.queue = self.load_class(SettingsController, self.queue)

    def call_user(self, _):
        """Process user command."""
        from openbb_cli.controllers.user_controller import UserController

        self.queue = self.load_class(UserController, self.queue)

    def call_feature(self, _):
        """Process feature engineering command."""
        from openbb_cli.controllers.feature_controller import (
            FeatureController,
        )

        self.queue = self.load_class(FeatureController, self.queue)

    def call_exe(self, other_args: list[str]):
        """Process exe command."""
        other_args += self.queue

        if not other_args:
            session.console.print(
                "[info]Provide a path to the routine you wish to execute. For an example, please use "
                "`exe --example`.\n[/info]"
            )
            return
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exe",
            description="Execute automated routine script. For an example, please use `exe --example`.",
        )
        parser.add_argument(
            "--file",
            "-f",
            help="The path or .openbb file to run.",
            dest="file",
            required="-h" not in other_args
            and "--help" not in other_args
            and "-e" not in other_args
            and "--example" not in other_args,
            type=str,
            nargs="+",
        )
        parser.add_argument(
            "-i",
            "--input",
            help="Select multiple inputs to be replaced in the routine and separated by commas. E.g. GME,AMC,BTC-USD",
            dest="routine_args",
            type=str,
        )
        parser.add_argument(
            "-e",
            "--example",
            help="Run an example script to understand how routines can be used.",
            dest="example",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--file")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.example:
                routine_path = ASSETS_DIRECTORY / "routines" / "routine_example.openbb"
                session.console.print(
                    "[info]Executing an example, please visit our docs to learn how to create your own script.[/info]\n"
                )
            elif ns_parser.file:
                file_path = " ".join(ns_parser.file)
                routine_path = Path(self.ROUTINE_FILES.get(file_path, file_path))
            else:
                return

            try:
                with open(routine_path) as fp:
                    raw_lines = list(fp)

                script_inputs = []
                if routine_args := ns_parser.routine_args:
                    pattern = r"\[(.*?)\]"
                    matches = re.findall(pattern, routine_args)

                    for match in matches:
                        routine_args = routine_args.replace(f"[{match}]", "")
                        script_inputs.append(match)

                    script_inputs.extend(
                        [val for val in routine_args.split(",") if val]
                    )

                err, parsed_script = parse_openbb_script(
                    raw_lines=raw_lines, script_inputs=script_inputs
                )

                if err:
                    session.console.print(err)
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
                    if export_path[0] == "~":
                        export_path = export_path.replace(
                            "~", HOME_DIRECTORY.as_posix()
                        )
                    elif export_path[0] != "/":
                        export_path = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), export_path
                        )

                    if os.path.isdir(export_path):
                        session.console.print(
                            f"Export data to be saved in the selected folder: '{export_path}'"
                        )
                    else:
                        os.makedirs(export_path)
                        session.console.print(
                            f"[green]Folder '{export_path}' successfully created.[/green]"
                        )
                    self.queue = self.queue[1:]

            except FileNotFoundError:
                session.console.print(
                    f"[red]File '{routine_path}' doesn't exist.[/red]"
                )
                return


def handle_job_cmds(jobs_cmds: list[str] | None) -> list[str] | None:
    """Handle job commands."""
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

    if os.path.isdir(export_path):
        session.console.print(
            f"Export data to be saved in the selected folder: '{export_path}'"
        )
    else:
        os.makedirs(export_path)
        session.console.print(
            f"[green]Folder '{export_path}' successfully created.[/green]"
        )
    return jobs_cmds


def run_cli(
    jobs_cmds: list[str] | None = None,
    test_mode=False,
    *,
    backend: Backend | None = None,
):
    """Run the CLI menu, optionally backed by a non-default ``Backend``."""
    ret_code = 1
    t_controller = CLIController(jobs_cmds, backend=backend)
    an_input = ""

    jobs_cmds = handle_job_cmds(jobs_cmds)

    bootup()
    if not jobs_cmds:
        welcome_message()

        if first_time_user():
            with contextlib.suppress(EOFError):
                webbrowser.open("https://docs.openbb.co/cli")

        t_controller.print_help()

    while ret_code:
        if t_controller.queue and len(t_controller.queue) > 0:
            if t_controller.queue[0] in ("q", "..", "quit"):
                print_goodbye()
                break

            an_input = t_controller.queue[0]
            t_controller.queue = t_controller.queue[1:]

            if an_input and an_input.split(" ")[0] in t_controller.CHOICES_COMMANDS:
                session.console.print(f"{get_flair_and_username()} / $ {an_input}")

        else:
            try:
                if session.prompt_session and session.settings.USE_PROMPT_TOOLKIT:
                    if session.settings.TOOLBAR_HINT:
                        an_input = session.prompt_session.prompt(
                            f"{get_flair_and_username()} / $ ",
                            completer=t_controller.completer,
                            search_ignore_case=True,
                            bottom_toolbar=HTML(
                                '<style bg="ansiblack" fg="ansiwhite">[h]</style> help menu    '
                                '<style bg="ansiblack" fg="ansiwhite">[q]</style> return to previous menu    '
                                '<style bg="ansiblack" fg="ansiwhite">[e]</style> exit the program    '
                                '<style bg="ansiblack" fg="ansiwhite">[cmd -h]</style> '
                                "see usage and available options    "
                            ),
                            style=Style.from_dict(
                                {
                                    "bottom-toolbar": "#ffffff bg:#333333",
                                }
                            ),
                        )
                    else:
                        an_input = session.prompt_session.prompt(
                            f"{get_flair_and_username()} / $ ",
                            completer=t_controller.completer,
                            search_ignore_case=True,
                        )

                else:
                    an_input = input(f"{get_flair_and_username()} / $ ")

            except (KeyboardInterrupt, EOFError):
                print_goodbye()
                break

        try:
            t_controller.queue = t_controller.switch(an_input)

            if an_input in ("q", "quit", "..", "exit", "e"):
                print_goodbye()
                break

            if an_input in ("r", "reset") or t_controller.update_success:
                reset(t_controller.queue if t_controller.queue else [])
                break

        except SystemExit:
            session.console.print(
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
                if " " in an_input:  # pragma: no cover
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        t_controller.queue = []
                        session.console.print("\n")
                        continue
                    an_input = candidate_input

                session.console.print(f"[green]Replacing by '{an_input}'.[/green]")
                t_controller.queue.insert(0, an_input)


def insert_start_slash(cmds: list[str]) -> list[str]:
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
    routines_args: list[str] | None = None,
    special_arguments: dict[str, str] | None = None,
    output: bool = True,
):
    """Run given .openbb scripts.

    Parameters
    ----------
    path : str
        The location of the .openbb file
    test_mode : bool
        Whether the CLI is in test mode
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
        session.console.print(f"File '{path}' doesn't exist. Launching base CLI.\n")
        if not test_mode:
            run_cli()

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
        elif special_arguments:
            lines = []
            for line in raw_lines:
                new_line = re.sub(
                    r"\${[^{]+=[^{]+}",
                    lambda x: replace_dynamic(x, special_arguments),
                    line,
                )
                lines.append(new_line)

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
        file_cmds = (
            [f"export {export_folder}{' '.join(file_cmds)}"]
            if export_folder
            else [" ".join(file_cmds)]
        )

        if not test_mode or verbose:
            run_cli(file_cmds, test_mode=True)
        else:
            with suppress_stdout():
                session.console.print(f"To ensure: {output}")
                if output:
                    timestamp = datetime.now().timestamp()
                    stamp_str = str(timestamp).replace(".", "")
                    whole_path = Path(REPOSITORY_DIRECTORY / "integration_test_output")
                    whole_path.mkdir(parents=True, exist_ok=True)
                    first_cmd = file_cmds[0].split("/")[1]
                    with (
                        open(
                            whole_path / f"{stamp_str}_{first_cmd}_output.txt", "w"
                        ) as output_file,
                        contextlib.redirect_stdout(output_file),
                    ):
                        run_cli(file_cmds, test_mode=True)
                else:
                    run_cli(file_cmds, test_mode=True)


def replace_dynamic(match: re.Match, special_arguments: dict[str, str]) -> str:
    """Replace ${key=default} with value in special_arguments if it exists, else with default.

    Parameters
    ----------
    match: re.Match[str]
        The match object
    special_arguments: Dict[str, str]
        The key value pairs to replace in the scripts

    Returns
    -------
    str
        The new string
    """
    cleaned = match[0].replace("{", "").replace("}", "").replace("$", "")
    key, default = cleaned.split("=")
    dict_value = special_arguments.get(key, default)
    if dict_value:
        return dict_value
    return default


def run_routine(file: str, routines_args: str | None = None):
    """Execute command routine from .openbb file."""
    user_routine_path = Path(session.user.preferences.export_directory, "routines")
    default_routine_path = ASSETS_DIRECTORY / "routines" / file

    if user_routine_path.exists():
        run_scripts(
            path=user_routine_path,
            routines_args=[routines_args] if routines_args else None,
        )
    elif default_routine_path.exists():
        run_scripts(
            path=default_routine_path,
            routines_args=[routines_args] if routines_args else None,
        )
    else:
        session.console.print(
            f"Routine not found, please put your `.openbb` file into : {user_routine_path}."
        )


def main(
    debug: bool,
    dev: bool,
    path_list: list[str],
    routines_args: list[str] | None = None,
    *,
    backend: Backend | None = None,
    **kwargs,
):
    """Run the CLI with various options.

    Parameters
    ----------
    debug : bool
        Whether to run the CLI in debug mode
    dev:
        Points backend towards development environment instead of production
    test : bool
        Whether to run the CLI in integrated test mode
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
        session.settings.DEBUG_MODE = True

    if dev:
        session.settings.DEV_BACKEND = True

    if isinstance(path_list, list) and path_list[0].endswith(".openbb"):
        run_routine(
            file=path_list[0],
            routines_args=",".join(routines_args) if routines_args else None,
        )
    elif path_list:
        argv_cmds = list([" ".join(path_list).replace(" /", "/home/")])
        argv_cmds = insert_start_slash(argv_cmds) if argv_cmds else argv_cmds
        run_cli(argv_cmds, backend=backend)
    else:
        run_cli(backend=backend)


def parse_args_and_run():
    """Parse input arguments and run CLI."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="cli",
        description="The OpenBB Platform CLI.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Runs the CLI in debug mode.",
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
            "Select multiple inputs to be replaced in the routine and separated by commas.E.g. GME,AMC,BTC-USD"
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
            "Run the CLI in testing mode. Also run this option and '-h' to see testing argument options."
        ),
    )
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

    if unknown:
        if ns_parser.debug:
            session.console.print(unknown)
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


def launch(
    debug: bool = False,
    dev: bool = False,
    queue: list[str] | None = None,
    *,
    backend: Backend | None = None,
) -> None:
    """Launch CLI, optionally with a non-default ``Backend``."""
    if queue:
        main(debug, dev, queue, module="", backend=backend)
    else:
        parse_args_and_run()


if __name__ == "__main__":
    parse_args_and_run()
