import inspect
from typing import Type

from argparse_translator.argparse_translator import ArgparseTranslator


class ArgparseClassProcessor:
    """
    Process a target class to create ArgparseTranslators for its methods.
    """

    def __init__(self, target_class: Type, menu_designation: str):
        """
        Initialize the ArgparseClassProcessor.

        Parameters
        ----------
        target_class : Type
            The target class whose methods will be processed.
        menu_designation : str
            The designation for the menu level associated with the target class.
        """
        self._target_class = target_class
        self._menu_designation = menu_designation
        self._translators = {self._menu_designation: {}}

        self._process_methods()

    def _process_methods(self):
        """
        Process the methods of the target class to create ArgparseTranslators.
        """
        for name, method in inspect.getmembers(self._target_class, inspect.ismethod):
            if name.startswith("__"):
                continue
            self._translators[self._menu_designation][name] = ArgparseTranslator(method)

    def get_translator(self, menu: str, command: str) -> ArgparseTranslator:
        """
        Retrieve the ArgparseTranslator object associated with a specific menu and command.

        Parameters
        ----------
        menu : str
            The menu designation.
        command : str
            The command associated with the ArgparseTranslator.

        Returns
        -------
        ArgparseTranslator
            The ArgparseTranslator associated with the specified menu and command.
        """
        return self._translators[menu][command]
