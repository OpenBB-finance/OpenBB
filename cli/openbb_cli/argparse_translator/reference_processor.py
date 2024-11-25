"""Module for the ReferenceToArgumentsProcessor class."""

# `ForwardRef`needs to be imported because the usage of `eval()`,
# which creates a ForwardRef
# which would raise a not defined error if it's not imported here.
# pylint: disable=unused-import
from typing import (
    Any,
    Dict,
    ForwardRef,  # noqa: F401
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
)

from openbb_cli.argparse_translator.argparse_argument import (
    ArgparseArgumentGroupModel,
    ArgparseArgumentModel,
)


class ReferenceToArgumentsProcessor:
    """Class to process the reference and build custom argument groups."""

    def __init__(self, reference: Dict[str, Dict]):
        """Initialize the ReferenceToArgumentsProcessor."""
        self._reference = reference
        self._custom_groups: Dict[str, List[ArgparseArgumentGroupModel]] = {}

        self._build_custom_groups()

    @property
    def custom_groups(self) -> Dict[str, List[ArgparseArgumentGroupModel]]:
        """Get the custom groups."""
        return self._custom_groups

    @staticmethod
    def _make_type_parsable(type_: str) -> type:
        """Make the type parsable by removing the annotations."""
        if "Union" in type_ and "str" in type_:
            return str
        if "Union" in type_ and "int" in type_:
            return int
        if type_ in ["date", "datetime.time", "time"]:
            return str

        if any(x in type_ for x in ["gt=", "ge=", "lt=", "le="]):
            if "Annotated" in type_:
                type_ = type_.replace("Annotated[", "").replace("]", "")
            type_ = type_.split(",")[0]

        return eval(type_)  # noqa: S307, E501 pylint: disable=eval-used

    def _parse_type(self, type_: str) -> type:
        """Parse the type from the string representation."""
        type_ = self._make_type_parsable(type_)  # type: ignore

        if get_origin(type_) is Literal:
            type_ = type(get_args(type_)[0])  # type: ignore

        return type_  # type: ignore

    def _get_nargs(self, type_: type) -> Optional[Union[int, str]]:
        """Get the nargs for the given type."""
        if get_origin(type_) is list:
            return "+"
        return None

    def _get_choices(self, type_: str, custom_choices: Any) -> Tuple:
        """Get the choices for the given type."""
        type_ = self._make_type_parsable(type_)  # type: ignore
        type_origin = get_origin(type_)

        choices: tuple[Any, ...] = ()

        if type_origin is Literal:
            choices = get_args(type_)

        if type_origin is list:
            type_ = get_args(type_)[0]

            if get_origin(type_) is Literal:
                choices = get_args(type_)

        if type_origin is Union and type(None) in get_args(type_):
            # remove NoneType from the args
            args = [arg for arg in get_args(type_) if arg != type(None)]
            # if there is only one arg left, use it
            if len(args) > 1:
                raise ValueError("Union with NoneType should have only one type left")
            type_ = args[0]

            if get_origin(type_) is Literal:
                choices = get_args(type_)

        if custom_choices:
            return tuple(custom_choices)

        return choices

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
                            action="store" if type_ != bool else "store_true",
                            help=arg["description"],
                            nargs=self._get_nargs(type_),  # type: ignore
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
