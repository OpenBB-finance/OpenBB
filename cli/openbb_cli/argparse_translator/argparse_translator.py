"""Module for translating a function into an argparse program."""

import argparse
import inspect
import re
from collections.abc import Callable
from copy import deepcopy
from typing import (
    Annotated,
    Any,
    Literal,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from openbb_core.app.model.field import OpenBBField
from pydantic import BaseModel

from openbb_cli.argparse_translator.argparse_argument import (
    ArgparseArgumentGroupModel,
    ArgparseArgumentModel,
)
from openbb_cli.argparse_translator.utils import (
    get_argument_choices,
    get_argument_optional_choices,
    in_group,
    remove_argument,
    set_optional_choices,
)

# pylint: disable=protected-access

SEP = "__"


class ArgparseTranslator:
    """Class to translate a function into an argparse program."""

    def __init__(
        self,
        func: Callable,
        custom_argument_groups: list[ArgparseArgumentGroupModel] | None = None,
        add_help: bool | None = True,
    ):
        """
        Initialize the ArgparseTranslator.

        Args:
            func (Callable): The function to translate into an argparse program.
            add_help (Optional[bool], optional): Whether to add the help argument. Defaults to False.
        """
        self.func = func
        self.signature = inspect.signature(func)
        self.type_hints = get_type_hints(func)
        self.provider_parameters: dict[str, list[str]] = {}

        self._parser = argparse.ArgumentParser(
            prog=func.__name__,
            description=self._build_description(func.__doc__),  # type: ignore
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=add_help if add_help else False,
        )
        self._required = self._parser.add_argument_group("required arguments")

        if any(param in self.type_hints for param in self.signature.parameters):
            self._generate_argparse_arguments(self.signature.parameters)

        if custom_argument_groups:
            for group in custom_argument_groups:
                self.provider_parameters[group.name] = []
                argparse_group = self._parser.add_argument_group(group.name)
                for argument in group.arguments:
                    self._handle_argument_in_groups(argument, argparse_group)

    def _handle_argument_in_groups(self, argument, group):
        """Handle the argument and add it to the parser."""

        def _update_providers(input_string: str, new_provider: list[str | None]) -> str:
            pattern = r"\(provider:\s*(.*?)\)"
            providers = re.findall(pattern, input_string)
            providers.extend(new_provider)
            # remove pattern from help and add with new providers
            input_string = re.sub(pattern, "", input_string).strip()
            return f"{input_string} (provider: {', '.join(providers)})"

        # check if the argument is already in use, if not, add it
        if f"--{argument.name}" not in self._parser._option_string_actions:
            kwargs = argument.model_dump(exclude={"name"}, exclude_none=True)
            if "help" in kwargs:
                kwargs["help"] = ArgparseTranslator._escape_help(kwargs["help"])
            group.add_argument(f"--{argument.name}", **kwargs)
            if group.title in self.provider_parameters:
                self.provider_parameters[group.title].append(argument.name)

        else:
            kwargs = argument.model_dump(exclude={"name"}, exclude_none=True)
            model_choices = kwargs.get("choices", ()) or ()
            # extend choices
            existing_choices = get_argument_choices(self._parser, argument.name)
            choices = tuple(set(existing_choices + model_choices))
            optional_choices = bool(existing_choices and not model_choices)

            # check if the argument is in the required arguments
            if in_group(self._parser, argument.name, group_title="required arguments"):
                for action in self._required._group_actions:
                    if action.dest == argument.name and choices:
                        # update choices
                        action.choices = choices
                        set_optional_choices(action, optional_choices)
                return

            # check if the argument is in the optional arguments
            if in_group(self._parser, argument.name, group_title="optional arguments"):
                for action in self._parser._actions:
                    if action.dest == argument.name:
                        # update choices
                        if choices:
                            action.choices = choices
                            set_optional_choices(action, optional_choices)
                        if argument.name not in self.signature.parameters:
                            # update help
                            action.help = ArgparseTranslator._escape_help(
                                _update_providers(action.help or "", [group.title])
                            )
                return

            # we need to check if the optional choices were set in other group
            # before we remove the argument from the group, otherwise we will lose info
            if not optional_choices:
                optional_choices = get_argument_optional_choices(
                    self._parser, argument.name
                )

            # if the argument is in use, remove it from all groups
            # and return the groups that had the argument
            groups_w_arg = remove_argument(self._parser, argument.name)
            groups_w_arg.append(group.title)  # add current group

            # add it to the optional arguments group instead
            if choices:
                kwargs["choices"] = choices  # update choices
            # add provider info to the help
            kwargs["help"] = ArgparseTranslator._escape_help(
                _update_providers(argument.help or "", groups_w_arg)
            )
            action = self._parser.add_argument(f"--{argument.name}", **kwargs)
            set_optional_choices(action, optional_choices)

    @property
    def parser(self) -> argparse.ArgumentParser:
        """Get the argparse parser."""
        return deepcopy(self._parser)

    @staticmethod
    def _escape_help(text: str | None) -> str | None:
        """Escape percent signs in help strings for argparse.

        Python 3.14+ validates help strings at add_argument time using
        %-formatting. Bare '%' characters that aren't valid format
        specifiers (like '%(default)s') cause a ValueError.
        """
        if text is None:
            return None
        return text.replace("%", "%%")

    @staticmethod
    def _build_description(func_doc: str) -> str:
        """Build the description of the argparse program from the function docstring."""
        if not func_doc:
            return ""

        # Remove the openbb header if present
        func_doc = re.sub(r"openbb\n\s+={3,}\n", "", func_doc, flags=re.DOTALL)

        # Senior Approach: The main description should only be the summary.
        # Sections like Parameters, Returns, and Examples are handled by argparse or are redundant.
        for section in ["Parameters", "Returns", "Examples", "Raises"]:
            pattern = rf"\n\s*{section}\n\s*-{{3,}}\n.*"
            func_doc = re.sub(pattern, "", func_doc, flags=re.DOTALL | re.IGNORECASE)

        # Clean up any remaining type-style annotations in the summary
        def clean_type_annotation(type_str: str) -> str:
            """Clean up type annotations for human readability."""
            # Handle pipe unions: int | str -> int or str
            type_str = re.sub(r"\s*\|\s*", " or ", type_str)
            # Handle Annotated[type, ...] -> type
            type_str = re.sub(r"Annotated\[\s*([^,\]]+).*?\]", r"\1", type_str)
            # Handle Union[A, B] -> A or B
            type_str = re.sub(
                r"Union\[\s*(.*?)\s*\]",
                lambda m: m.group(1).replace(", ", " or "),
                type_str,
            )
            # Handle Optional[A] -> A or None
            type_str = re.sub(r"Optional\[\s*(.*?)\s*\]", r"\1 or None", type_str)

            return type_str.strip()

        lines = func_doc.split("\n")
        cleaned_lines = []
        for line in lines:
            # If a line still looks like a parameter definition (e.g. "param : type"), clean it
            if ":" in line and not line.strip().startswith("#"):
                parts = line.split(":", 1)
                param_name = parts[0]
                type_info = parts[1].strip()
                cleaned_type = clean_type_annotation(type_info)
                cleaned_lines.append(f"{param_name}: {cleaned_type}")
            else:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    @staticmethod
    def _param_is_default(param: inspect.Parameter) -> bool:
        """Return True if the parameter has a default value."""
        return param.default != inspect.Parameter.empty

    def _get_action_type(
        self, param: inspect.Parameter
    ) -> Literal["store_true", "store"]:
        """Return the argparse action type for the given parameter."""
        param_type = self.type_hints[param.name]
        origin = get_origin(param_type)
        args = get_args(param_type)

        if param_type is bool:
            return "store_true"

        if origin is Union and bool in args:
            return "store_true"

        # Special case for Optional[bool] which is Union[bool, None]
        if origin is Union and bool in args and type(None) in args:
            return "store_true"

        return "store"

    def _get_type_and_choices(
        self, param: inspect.Parameter
    ) -> tuple[type[Any], tuple[Any, ...]]:
        """Return the type and choices for the given parameter."""

        def get_base_type(  # pylint: disable=R0911 #  noqa:PLR0911
            t: Any,
        ) -> type:
            """Recursively find the base type for argparse."""
            origin = get_origin(t)
            args = get_args(t)

            if origin is Union or "types.UnionType" in str(type(t)):
                non_none_args = [a for a in args if a is not type(None)]
                if len(non_none_args) == 1:
                    return get_base_type(non_none_args[0])
                # For Union[A, B, C], check for bool first, then default to str
                if bool in non_none_args:
                    return bool
                # If we have multiple types including str, prefer str as it's most flexible
                if str in non_none_args:
                    return str
                # Otherwise, try to get the first concrete type
                for arg in non_none_args:
                    if arg not in (type(None), Any):
                        return get_base_type(arg)
                return str
            if origin is Literal:
                return type(args[0]) if args else str
            if origin is list:
                return get_base_type(args[0]) if args else Any  # type: ignore
            if t is Any:
                return str
            # Handle actual type objects (like datetime.date)
            if isinstance(t, type):
                return t
            return str

        def get_choices(t: Any) -> tuple:
            """Recursively find the choices for argparse."""
            origin = get_origin(t)
            args = get_args(t)

            if origin is Union or "types.UnionType" in str(type(t)):
                non_none_args = [a for a in args if a is not type(None)]
                all_choices: list = []
                for arg in non_none_args:
                    all_choices.extend(get_choices(arg))
                return tuple(set(all_choices))
            if origin is Literal:
                return args
            if origin is list and args:
                return get_choices(args[0])
            return ()

        param_type_hint = self.type_hints[param.name]

        base_type = get_base_type(param_type_hint)
        choices = get_choices(param_type_hint)

        custom_choices = self._get_argument_custom_choices(param)
        if custom_choices:
            choices = tuple(custom_choices)

        if base_type is bool:
            choices = ()

        return base_type, choices

    @staticmethod
    def _split_annotation(
        base_annotation: type[Any], custom_annotation_type: type
    ) -> tuple[type[Any], list[Any]]:
        """Find the base annotation and the custom annotations, namely the OpenBBField."""
        if get_origin(base_annotation) is not Annotated:
            return base_annotation, []
        base_annotation, *maybe_custom_annotations = get_args(base_annotation)
        return base_annotation, [
            annotation
            for annotation in maybe_custom_annotations
            if isinstance(annotation, custom_annotation_type)
        ]

    @classmethod
    def _get_argument_custom_help(cls, param: inspect.Parameter) -> str | None:
        """Return the help annotation for the given parameter."""
        base_annotation = param.annotation
        _, custom_annotations = cls._split_annotation(base_annotation, OpenBBField)
        help_annotation = (
            custom_annotations[0].description if custom_annotations else None
        )
        return help_annotation

    @classmethod
    def _get_argument_custom_choices(cls, param: inspect.Parameter) -> str | None:
        """Return the help annotation for the given parameter."""
        base_annotation = param.annotation
        _, custom_annotations = cls._split_annotation(base_annotation, OpenBBField)
        choices_annotation = (
            custom_annotations[0].choices if custom_annotations else None
        )
        return choices_annotation

    def _get_nargs(self, param: inspect.Parameter) -> Literal["+"] | None:
        """Return the nargs annotation for the given parameter."""
        param_type = self.type_hints[param.name]
        origin = get_origin(param_type)

        if origin is list:
            return "+"

        if origin is Union and any(
            get_origin(arg) is list for arg in get_args(param_type)
        ):
            return "+"

        return None

    def _generate_argparse_arguments(self, parameters) -> None:
        """Generate the argparse arguments from the function parameters."""
        for param in parameters.values():
            if param.name == "kwargs":
                continue

            param_type, choices = self._get_type_and_choices(param)

            # if the param is a custom type, we need to flatten it
            if inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                # update type hints with the custom type fields
                type_hints = get_type_hints(param_type)
                # prefix the type hints keys with the param name
                type_hints = {
                    f"{param.name}{SEP}{key}": value
                    for key, value in type_hints.items()
                }
                self.type_hints.update(type_hints)
                # create a signature from the custom type
                sig = inspect.signature(param_type)

                # add help to the annotation
                annotated_parameters: list[inspect.Parameter] = []
                for child_param in sig.parameters.values():
                    new_child_param = child_param.replace(
                        name=f"{param.name}{SEP}{child_param.name}",
                        annotation=Annotated[
                            child_param.annotation,
                            OpenBBField(
                                description=param_type.model_json_schema()[
                                    "properties"
                                ][child_param.name].get("description", None)
                            ),
                        ],
                        kind=inspect.Parameter.KEYWORD_ONLY,
                    )
                    annotated_parameters.append(new_child_param)

                # replacing with the annotated parameters
                new_signature = inspect.Signature(
                    parameters=annotated_parameters,
                    return_annotation=sig.return_annotation,
                )
                self._generate_argparse_arguments(new_signature.parameters)

                # the custom type itself should not be added as an argument
                continue

            required = not self._param_is_default(param)

            # Get the appropriate action based on the parameter type
            action = self._get_action_type(param)

            # For boolean parameters with action="store_true", we should not use any choices
            if param_type is bool:
                choices = ()
                action = "store_true"

            argument = ArgparseArgumentModel(
                name=param.name,
                type=param_type,
                dest=param.name,
                default=param.default,
                required=required,
                action=action,
                help=self._escape_help(self._get_argument_custom_help(param)),
                nargs=self._get_nargs(param),
                choices=choices,
            )
            kwargs = argument.model_dump(exclude={"name"}, exclude_none=True)

            if required:
                self._required.add_argument(
                    f"--{argument.name}",
                    **kwargs,
                )
            else:
                self._parser.add_argument(
                    f"--{argument.name}",
                    **kwargs,
                )

    @staticmethod
    def _unflatten_args(args: dict) -> dict[str, Any]:
        """Unflatten the args that were flattened by the custom types."""
        result: dict[str, Any] = {}
        for key, value in args.items():
            if SEP in key:
                parts = key.split(SEP)
                nested_dict = result
                for part in parts[:-1]:
                    if part not in nested_dict:
                        nested_dict[part] = {}
                    nested_dict = nested_dict[part]
                nested_dict[parts[-1]] = value
            else:
                result[key] = value
        return result

    def _update_with_custom_types(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Update the kwargs with the custom types."""
        # for each argument in the signature that is a custom type, we need to
        # update the kwargs with the custom type kwargs
        for param in self.signature.parameters.values():
            if param.name == "kwargs":
                continue
            param_type, _ = self._get_type_and_choices(param)
            if inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                custom_type_kwargs = kwargs[param.name]
                kwargs[param.name] = param_type(**custom_type_kwargs)

        return kwargs

    def execute_func(
        self,
        parsed_args: argparse.Namespace | None = None,
    ) -> Any:
        """
        Execute the original function with the parsed arguments.

        Args:
            parsed_args (Optional[argparse.Namespace], optional): The parsed arguments. Defaults to None.

        Returns:
            Any: The return value of the original function.

        """
        kwargs = self._unflatten_args(vars(parsed_args))
        kwargs = self._update_with_custom_types(kwargs)
        provider = kwargs.get("provider")
        provider_args: list = []
        if provider and provider in self.provider_parameters:
            provider_args = self.provider_parameters[provider]
        else:
            for args in self.provider_parameters.values():
                provider_args.extend(args)

        # remove kwargs not matching the signature, provider parameters, or are empty.
        kwargs = {
            key: value
            for key, value in kwargs.items()
            if (
                (key in self.signature.parameters or key in provider_args)
                and (value or value is False)
            )
        }
        return self.func(**kwargs)

    def parse_args_and_execute(self) -> Any:
        """
        Parse the arguments and executes the original function.

        Returns:
            Any: The return value of the original function.
        """
        parsed_args = self._parser.parse_args()

        return self.execute_func(parsed_args)

    def translate(self) -> Callable:
        """
        Wrap the original function with an argparse program.

        Returns:
            Callable: The original function wrapped with an argparse program.
        """

        def wrapper_func():
            return self.parse_args_and_execute()

        return wrapper_func
