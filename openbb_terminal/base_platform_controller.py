"""Platform Equity Controller."""
__docformat__ = "numpy"

import logging
from functools import partial, update_wrapper
from types import MethodType
from typing import Dict, List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class PlatformController(BaseController):
    """Platform Controller Base class."""

    CHOICES_COMMANDS = []
    CHOICES_GENERATION = True

    def __init__(
        self,
        name: str,
        queue: Optional[List[str]] = None,
        translators: Optional[Dict] = None,
    ):
        """Construct Data."""
        self.PATH = f"/{name}/"
        super().__init__(queue)
        self._name = name

        if translators:
            self._generate_commands(translators=translators)
            self.CHOICES_COMMANDS = translators.keys()

            if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
                choices: dict = self.choices_default
                self.completer = NestedCompleter.from_nested_dict(choices)

    def _generate_commands(self, translators):
        for name, translator in translators.items():
            self._generate_command_call(name=name, translator=translator)

    def _generate_command_call(self, name, translator):
        def method(self, other_args: List[str], translator=translator):
            parser = translator.parser

            if ns_parser := self.parse_known_args_and_warn(parser, other_args):
                try:
                    obbject = translator.execute_func(parsed_args=ns_parser)
                    console.print(obbject.to_dataframe())

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

        for command in self.CHOICES_COMMANDS:
            mt.add_cmd(command)

        console.print(text=mt.menu_text, menu=self._name)
