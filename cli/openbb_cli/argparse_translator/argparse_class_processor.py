"""Module for the ArgparseClassProcessor class."""

import inspect
from typing import Any, Dict, Optional, Type

# TODO: this needs to be done differently
from openbb_core.app.static.container import Container

from openbb_cli.argparse_translator.argparse_translator import ArgparseTranslator
from openbb_cli.argparse_translator.reference_processor import (
    ReferenceToArgumentsProcessor,
)


class ArgparseClassProcessor:
    """Process a target class to create ArgparseTranslators for its methods."""

    # reference variable used to create custom groups for the ArgpaseTranslators
    _reference: Dict[str, Any] = {}

    def __init__(
        self,
        target_class: Type,
        add_help: bool = False,
        reference: Optional[Dict[str, Any]] = None,
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

        ArgparseClassProcessor._reference = reference or {}

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

    @classmethod
    def _custom_groups_from_reference(cls, class_name: str, function_name: str) -> Dict:
        route = f"/{class_name.replace('_', '/')}/{function_name}"
        reference = {route: cls._reference[route]} if route in cls._reference else {}
        if not reference:
            return {}
        rp = ReferenceToArgumentsProcessor(reference)
        return rp.custom_groups.get(route, {})  # type: ignore

    @classmethod
    def _process_class(
        cls,
        target: type,
        add_help: bool = False,
    ) -> Dict[str, ArgparseTranslator]:
        methods = {}

        for name, member in inspect.getmembers(target):
            if name.startswith("__") or name.startswith("_"):
                continue
            if inspect.ismethod(member):
                class_name = cls._get_class_name(target)
                methods[f"{class_name}_{name}"] = ArgparseTranslator(
                    func=member,
                    add_help=add_help,
                    custom_argument_groups=cls._custom_groups_from_reference(  # type: ignore
                        class_name=class_name, function_name=name
                    ),
                )
            elif isinstance(member, Container):
                methods = {
                    **methods,
                    **cls._process_class(
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
            .lower()
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
            elif isinstance(member, Container):
                self._build_paths(target=getattr(target, name), depth=depth + 1)
                self._paths[f"{name}"] = "sub" * depth + "path"
