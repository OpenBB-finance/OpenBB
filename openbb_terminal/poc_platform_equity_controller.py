"""Platform Equity Controller."""
__docformat__ = "numpy"

import logging
from typing import List, Optional

from openbb import obb

from argparse_translator.argparse_class_processor import ArgparseClassProcessor
from openbb_terminal.base_platform_controller import PlatformController
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.menu import session
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=R1710,import-outside-toplevel

logger = logging.getLogger(__name__)

equity = ArgparseClassProcessor(target_class=obb.equity)


class PocPlatformEquityController(PlatformController):
    """Equity Controller class."""

    CHOICES_COMMANDS = list(equity.translators.keys())
    CHOICES_MENUS = []

    for key, value in equity.paths.items():
        if value == "path":
            continue
        CHOICES_MENUS.append(key)

    # FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, name: str, queue: Optional[List[str]] = None):
        """Construct Data."""
        super().__init__(name, queue)

        self._slave_controllers = {}

        self._handle_paths(paths=equity.paths)
        self._generate_commands(translators=equity.translators)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def _handle_paths(self, paths: dict):
        """Handle paths."""
        for path in paths:
            if paths[path] == "path":
                continue

            sub_menu_translators = {}
            choices_commands = []

            for translator_name, translator in equity.translators.items():
                if f"{self._name}_{path}" in translator_name:
                    new_name = translator_name.replace(f"{self._name}_{path}_", "")
                    sub_menu_translators[new_name] = translator
                    choices_commands.append(new_name)

            PlatformController.CHOICES_COMMANDS.extend(choices_commands)

            self._generate_controller_call(
                controller=PlatformController,
                name=path,
                translators=sub_menu_translators,
            )

    def print_help(self):
        """Print help."""
        mt = MenuText("poc_plat_equity/", 80)

        menus = equity.paths

        for key, value in menus.items():
            if value == "path":
                continue
            mt.add_menu(key)

        console.print(text=mt.menu_text, menu="POC Platform Equity")
