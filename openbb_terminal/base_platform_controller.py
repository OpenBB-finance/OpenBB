"""Platform Equity Controller."""

__docformat__ = "numpy"

import logging
from functools import partial, update_wrapper
from types import MethodType
from typing import Dict, List, Optional

from argparse_translator.argparse_class_processor import ArgparseClassProcessor
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

import pandas as pd

logger = logging.getLogger(__name__)


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
        platform_target: Optional[type] = None,
        queue: Optional[List[str]] = None,
        translators: Optional[Dict] = None,
    ):
        """Construct a Platform based Controller."""
        self.PATH = f"/{name}/"
        super().__init__(queue)
        self._name = name

        if not (platform_target or translators):
            raise ValueError("Either platform_target or translators must be provided.")

        self._translated_target = (
            ArgparseClassProcessor(target_class=platform_target)
            if platform_target
            else DummyTranslation()
        )
        self.translators = translators or self._translated_target.translators
        self.paths = self._translated_target.paths

        if self.translators:
            self._generate_commands()
            self._generate_sub_controllers()

            if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
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

            if ns_parser := self.parse_known_args_and_warn(parser, other_args):
                try:
                    obbject = translator.execute_func(parsed_args=ns_parser)

                    if hasattr(ns_parser, "chart") and ns_parser.chart:
                        obbject.show()
                    elif hasattr(obbject, "to_dataframe"):
                        print_rich_table(obbject.to_dataframe())
                    elif isinstance(obbject, dict):
                        print_rich_table(
                            pd.DataFrame.from_dict(obbject, orient="index")
                        )
                    else:
                        console.print(obbject)

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

    def _generate_controller_call(self, controller, name, translators):
        def method(self, _, controller=controller, name=name, translators=translators):
            self.queue = self.load_class(
                controller, name, self.queue, translators=translators
            )

        # Bind the method to the class
        bound_method = MethodType(method, self)

        # Update the wrapper and set the attribute
        bound_method = update_wrapper(
            partial(
                bound_method, controller=controller, name=name, translators=translators
            ),
            method,
        )
        setattr(self, f"call_{name}", bound_method)

    def print_help(self):
        """Print help."""
        mt = MenuText(self._name, 80)

        if self.CHOICES_MENUS:
            mt.add_raw("Menus\n\n")
            for menu in self.CHOICES_MENUS:
                mt.add_menu(menu)

        if self.CHOICES_COMMANDS:
            mt.add_raw("\nCommands\n\n")
            for command in self.CHOICES_COMMANDS:
                mt.add_cmd(command.replace(f"{self._name}_", ""))

        console.print(text=mt.menu_text, menu=self._name)
