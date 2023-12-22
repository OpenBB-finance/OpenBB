import inspect
from typing import Dict, Type, Optional

from argparse_translator.argparse_translator import ArgparseTranslator


class ArgparseClassProcessor:
    """
    Process a target class to create ArgparseTranslators for its methods.
    """

    def __init__(
        self,
        target_class: Type,
        add_help: Optional[bool] = False,
    ):
        """
        Initialize the ArgparseClassProcessor.

        Parameters
        ----------
        target_class : Type
            The target class whose methods will be processed.
        add_help : Optional[bool]
            Whether to add help to the ArgparseTranslators.
        """
        self._target_class: Type = target_class
        self._add_help: bool = add_help
        self._translators: Dict[str, ArgparseTranslator] = {}

        self._process_methods()

    def _process_methods(self):
        """
        Process the methods of the target class to create ArgparseTranslators.
        """
        for name, method in inspect.getmembers(self._target_class, inspect.ismethod):
            if name.startswith("__") or name.startswith("_"):
                continue

            self._translators[name] = ArgparseTranslator(
                func=method, add_help=self._add_help
            )

    def get_translator(self, command: str) -> ArgparseTranslator:
        """
        Retrieve the ArgparseTranslator object associated with a specific menu and command.

        Parameters
        ----------
        command : str
            The command associated with the ArgparseTranslator.

        Returns
        -------
        ArgparseTranslator
            The ArgparseTranslator associated with the specified menu and command.
        """
        return self._translators[command]
