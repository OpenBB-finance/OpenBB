"""Module for the ReferenceToArgumentsProcessor class."""

import re
from typing import Any, Literal, get_origin

from openbb_cli.argparse_translator.argparse_argument import (
    ArgparseArgumentGroupModel,
    ArgparseArgumentModel,
)


class ReferenceToArgumentsProcessor:
    """Class to process the reference and build custom argument groups."""

    def __init__(self, reference: dict[str, dict]):
        """Initialize the ReferenceToArgumentsProcessor."""
        self._reference = reference
        self._custom_groups: dict[str, list[ArgparseArgumentGroupModel]] = {}

        self._build_custom_groups()

    @property
    def custom_groups(self) -> dict[str, list[ArgparseArgumentGroupModel]]:
        """Get the custom groups."""
        return self._custom_groups

    @staticmethod
    def _parse_type(type_string: str) -> type:
        """Parse the type from the string representation."""
        if "Optional" in type_string or "|" in type_string:
            match = re.search(r"Optional\[(\w+)]|(\w+)\s*\|\s*None", type_string)
            if match:
                type_string = next(
                    (group for group in match.groups() if group is not None), "str"
                )

        if "Literal" in type_string:
            return str

        if "Annotated" in type_string:
            match = re.search(r"Annotated\[(\w+),", type_string)
            if match:
                type_string = match.group(1)

        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "date": str,
            "datetime": str,
            "time": str,
        }
        return type_map.get(type_string, str)

    def _get_nargs(self, type_: type) -> Literal["+"] | None:
        """Get the nargs for the given type."""
        if get_origin(type_) is list:
            return "+"
        return None

    def _get_choices(self, type_string: str, custom_choices: Any) -> tuple | None:
        """Get the choices for the given type."""
        if custom_choices:
            return tuple(custom_choices)

        literal_matches = re.findall(r"Literal\[(.*?)\]", type_string)
        if not literal_matches:
            return None

        all_choices: list = []
        for match in literal_matches:
            choices = [c.strip().strip("'\"") for c in match.split(",") if c.strip()]
            all_choices.extend(choices)

        return tuple(set(all_choices)) if all_choices else None

    def _build_custom_groups(self):
        """Build the custom groups from the reference."""
        for route, v in self._reference.items():
            for provider, args in v["parameters"].items():
                if provider == "standard":
                    continue

                custom_arguments = []
                for arg in args:
                    if arg.get("standard"):
                        continue

                    type_ = self._parse_type(arg["type"])

                    custom_arguments.append(
                        ArgparseArgumentModel(
                            name=arg["name"],
                            type=type_,
                            dest=arg["name"],
                            default=arg["default"],
                            required=not (arg["optional"]),
                            action="store" if type_ is not bool else "store_true",
                            help=arg["description"],
                            nargs=self._get_nargs(type_),
                            choices=self._get_choices(
                                arg["type"], custom_choices=arg["choices"]
                            ),
                        )
                    )

                group = ArgparseArgumentGroupModel(
                    name=provider, arguments=custom_arguments
                )

                if route not in self._custom_groups:
                    self._custom_groups[route] = []

                self._custom_groups[route].append(group)
