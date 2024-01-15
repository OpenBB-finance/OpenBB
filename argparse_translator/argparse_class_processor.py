import inspect
from typing import Dict, Type

from argparse_translator.argparse_translator import ArgparseTranslator


class ArgparseClassProcessor:
    """
    Process a target class to create ArgparseTranslators for its methods.
    """

    def __init__(
        self,
        target_class: Type,
        add_help: bool = False,
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
        self._paths: Dict[str, str] = {}

        self._translators = self._process_class(
            target=self._target_class, add_help=self._add_help
        )
        self._paths[self._get_class_name(self._target_class)] = "path"
        self._build_paths(target=self._target_class)

    @property
    def translators(self) -> Dict[str, ArgparseTranslator]:
        """
        Get the ArgparseTranslators associated with the target class.

        Returns
        -------
        Dict[str, ArgparseTranslator]
            The ArgparseTranslators associated with the target class.
        """
        return self._translators

    @property
    def paths(self) -> Dict[str, str]:
        """
        Get the paths associated with the target class.

        Returns
        -------
        Dict[str, str]
            The paths associated with the target class.
        """
        return self._paths

    @staticmethod
    def _process_class(
        target: type,
        add_help: bool = False,
    ) -> Dict[str, ArgparseTranslator]:
        methods = {}

        for name, member in inspect.getmembers(target):
            if name.startswith("__") or name.startswith("_"):
                continue
            if inspect.ismethod(member):
                class_name = ArgparseClassProcessor._get_class_name(target)
                methods[f"{class_name}_{name}"] = ArgparseTranslator(
                    func=member, add_help=add_help
                )
            else:
                methods = {
                    **methods,
                    **ArgparseClassProcessor._process_class(
                        target=getattr(target, name), add_help=add_help
                    ),
                }

        return methods

    @staticmethod
    def _get_class_name(target: type) -> str:
        return (
            str(type(target))
            .rsplit(".", maxsplit=1)[-1]
            .replace("'>", "")
            .replace("ROUTER_", "")
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

    def _build_paths(self, target: type, depth: int = 1):
        for name, member in inspect.getmembers(target):
            if name.startswith("__") or name.startswith("_"):
                continue
            if inspect.ismethod(member):
                pass
            else:
                self._build_paths(target=getattr(target, name), depth=depth + 1)
                self._paths[f"{name}"] = "sub" * depth + "path"
