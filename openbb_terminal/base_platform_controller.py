"""Platform Equity Controller."""

__docformat__ = "numpy"

import os
from functools import partial, update_wrapper
from types import MethodType
from typing import Dict, List, Optional

import pandas as pd
from openbb import obb
from openbb_charting.core.openbb_figure import OpenBBFigure

from argparse_translator.argparse_class_processor import ArgparseClassProcessor
from openbb_terminal.core.session.current_settings import get_current_settings
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console


class DummyTranslation:
    """Dummy Translation for testing."""

    def __init__(self):
        """Construct a Dummy Translation Class."""
        self.paths = {}
        self.translators = {}


class PlatformController(BaseController):
    """Platform Controller Base class."""

    CHOICES_GENERATION = True

    def __init__(
        self,
        name: str,
        parent_path: List[str],
        platform_target: Optional[type] = None,
        queue: Optional[List[str]] = None,
        translators: Optional[Dict] = None,
    ):
        """Construct a Platform based Controller."""
        self.PATH = f"/{'/'.join(parent_path)}/{name}/" if parent_path else f"/{name}/"
        super().__init__(queue)
        self._name = name

        if not (platform_target or translators):
            raise ValueError("Either platform_target or translators must be provided.")

        reference: Dict[str, Dict] = {}
        if coverage := getattr(obb, "coverage", None):
            reference = getattr(coverage, "reference", {})

        self._translated_target = (
            ArgparseClassProcessor(target_class=platform_target, reference=reference)
            if platform_target
            else DummyTranslation()
        )
        self.translators = (
            translators
            if translators is not None
            else getattr(self._translated_target, "translators", {})
        )
        self.paths = getattr(self._translated_target, "paths", {})

        if self.translators:
            self._generate_commands()
            self._generate_sub_controllers()

            if session and get_current_settings().USE_PROMPT_TOOLKIT:
                choices: dict = self.choices_default
                self.completer = NestedCompleter.from_nested_dict(choices)

    def _generate_sub_controllers(self):
        """Handle paths."""
        for path, value in self.paths.items():
            if value == "path":
                continue

            sub_menu_translators = {}
            choices_commands = []

            for translator_name, translator in self.translators.items():
                if f"{self._name}_{path}" in translator_name:
                    new_name = translator_name.replace(f"{self._name}_{path}_", "")
                    sub_menu_translators[new_name] = translator
                    choices_commands.append(new_name)

                    if translator_name in self.CHOICES_COMMANDS:
                        self.CHOICES_COMMANDS.remove(translator_name)

            # Create the sub controller as a new class
            class_name = f"{self._name.capitalize()}{path.capitalize()}Controller"
            SubController = type(
                class_name,
                (PlatformController,),
                {
                    "CHOICES_GENERATION": True,
                    # "CHOICES_MENUS": [],
                    "CHOICES_COMMANDS": choices_commands,
                },
            )

            self._generate_controller_call(
                controller=SubController,
                name=path,
                parent_path=self.path,
                translators=sub_menu_translators,
            )

    def _generate_commands(self):
        """Generate commands."""
        for name, translator in self.translators.items():
            # Prepare the translator name to create a command call in the controller
            new_name = name.replace(f"{self._name}_", "")

            self._generate_command_call(name=new_name, translator=translator)

    def _generate_command_call(self, name, translator):
        def method(self, other_args: List[str], translator=translator):
            parser = translator.parser

            if ns_parser := self.parse_known_args_and_warn(
                parser=parser,
                other_args=other_args,
                export_allowed="raw_data_and_figures",
            ):
                try:
                    obbject = translator.execute_func(parsed_args=ns_parser)
                    df: pd.DataFrame = None
                    fig: OpenBBFigure = None

                    if hasattr(ns_parser, "chart") and ns_parser.chart:
                        obbject.show()
                        fig = obbject.chart.fig
                        if hasattr(obbject, "to_dataframe"):
                            df = obbject.to_dataframe()
                        elif isinstance(obbject, dict):
                            df = pd.DataFrame.from_dict(obbject, orient="index")
                        else:
                            df = None

                    elif hasattr(obbject, "to_dataframe"):
                        df = obbject.to_dataframe()
                        print_rich_table(df, show_index=True)

                    elif isinstance(obbject, dict):
                        df = pd.DataFrame.from_dict(obbject, orient="index")
                        print_rich_table(df, show_index=True)

                    elif obbject:
                        console.print(obbject)

                    if hasattr(ns_parser, "export") and ns_parser.export:
                        sheet_name = getattr(ns_parser, "sheet_name", None)
                        export_data(
                            export_type=ns_parser.export,
                            dir_path=os.path.dirname(os.path.abspath(__file__)),
                            func_name=translator.func.__name__,
                            df=df,
                            sheet_name=sheet_name,
                            figure=fig,
                        )

                except Exception as e:
                    console.print(f"[red]{e}[/]\n")
                    return

        # Bind the method to the class
        bound_method = MethodType(method, self)

        # Update the wrapper and set the attribute
        bound_method = update_wrapper(
            partial(bound_method, translator=translator), method
        )
        setattr(self, f"call_{name}", bound_method)

    def _generate_controller_call(self, controller, name, parent_path, translators):
        def method(self, _, controller, name, parent_path, translators):
            self.queue = self.load_class(
                class_ins=controller,
                name=name,
                parent_path=parent_path,
                translators=translators,
                queue=self.queue,
            )

        # Bind the method to the class
        bound_method = MethodType(method, self)

        # Update the wrapper and set the attribute
        bound_method = update_wrapper(
            partial(
                bound_method,
                name=name,
                parent_path=parent_path,
                translators=translators,
                controller=controller,
            ),
            method,
        )
        setattr(self, f"call_{name}", bound_method)

    def _get_command_description(self, command: str) -> str:
        """Get command description."""
        command_description = obb.coverage.reference.get(
            f"{self.PATH}{command}", {}
        ).get("description", "")

        if not command_description:
            trl = self.translators.get(
                f"{self._name}_{command}"
            ) or self.translators.get(command)
            if trl and hasattr(trl, "parser"):
                command_description = trl.parser.description

        return command_description.split(".")[0].lower()

    def print_help(self):
        """Print help."""
        mt = MenuText(self.PATH)

        if self.CHOICES_MENUS:
            for menu in self.CHOICES_MENUS:
                mt.add_menu(menu)

        if self.CHOICES_COMMANDS:
            mt.add_raw("\n")
            for command in self.CHOICES_COMMANDS:
                command_description = self._get_command_description(command)

                mt.add_cmd(
                    key_command=command.replace(f"{self._name}_", ""),
                    command_description=command_description,
                )

        console.print(text=mt.menu_text, menu=self._name)

        settings = get_current_settings()
        dev_mode = settings.DEBUG_MODE or settings.TEST_MODE
        if mt.warnings and dev_mode:
            console.print("")
            for w in mt.warnings:
                w_str = str(w).replace("{", "").replace("}", "").replace("'", "")
                console.print(f"[yellow]{w_str}[/yellow]")
            console.print("")
