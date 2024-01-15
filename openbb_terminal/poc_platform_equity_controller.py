"""Platform Equity Controller."""
__docformat__ = "numpy"

import logging
from functools import partial, update_wrapper
from types import MethodType
from typing import List, Optional

from openbb import obb

from argparse_translator.argparse_class_processor import ArgparseClassProcessor
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=R1710,import-outside-toplevel

logger = logging.getLogger(__name__)

equity = ArgparseClassProcessor(target_class=obb.equity)


class PocPlatformEquityController(BaseController):
    """Forex Controller class."""

    CHOICES_COMMANDS = list(equity.translators.keys())

    PATH = "/pocplat/"
    # FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct Data."""
        super().__init__(queue)

        self._generate_commands()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def _generate_commands(self):
        for name, translator in equity.translators.items():

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
            bound_method = MethodType(method, self.__class__)

            # Update the wrapper and set the attribute
            bound_method = update_wrapper(
                partial(bound_method, translator=translator), method
            )
            setattr(self.__class__, f"call_{name}", bound_method)

    def print_help(self):
        """Print help."""
        mt = MenuText("poc_plat_equity/", 80)

        menus = equity.paths
        commands = self.CHOICES_COMMANDS.copy()

        for path in menus:
            if equity.paths[path] == "path":
                continue
            mt.add_menu(path)
            new_commands = [command for command in commands if path in command]
            for command in new_commands:
                mt.add_cmd(command)

            mt.add_raw("\n")

        console.print(text=mt.menu_text, menu="POC Platform Equity")
