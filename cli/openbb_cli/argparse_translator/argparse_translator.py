"""Module for translating a function into an argparse program."""

import argparse
import inspect
import re
from copy import deepcopy
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from openbb_core.app.model.field import OpenBBField
from pydantic import BaseModel, model_validator
from typing_extensions import Annotated

# pylint: disable=protected-access

SEP = "__"


class ArgparseArgumentModel(BaseModel):
    """Pydantic model for an argparse argument."""

    name: str
    type: Any
    dest: str
    default: Any
    required: bool
    action: Literal["store_true", "store"]
    help: Optional[str]
    nargs: Optional[Literal["+"]]
    choices: Optional[Tuple]

    @model_validator(mode="after")  # type: ignore
    @classmethod
    def validate_action(cls, values: "ArgparseArgumentModel"):
        """Validate the action based on the type."""
        if values.type is bool and values.action != "store_true":
            raise ValueError('If type is bool, action must be "store_true"')
        return values

    @model_validator(mode="after")  # type: ignore
    @classmethod
    def remove_props_on_store_true(cls, values: "ArgparseArgumentModel"):
        """Remove type, nargs, and choices if action is store_true."""
        if values.action == "store_true":
            values.type = None
            values.nargs = None
            values.choices = None
        return values

    # override
    def model_dump(self, **kwargs):
        """Override the model_dump method to remove empty choices."""
        res = super().model_dump(**kwargs)

        # Check if choices is present and if it's an empty tuple remove it
        if "choices" in res and not res["choices"]:
            del res["choices"]

        return res


class ArgparseArgumentGroupModel(BaseModel):
    """Pydantic model for a custom argument group."""

    name: str
    arguments: List[ArgparseArgumentModel]


class ReferenceToArgumentsProcessor:
    """Class to process the reference and build custom argument groups."""

    def __init__(self, reference: Dict[str, Dict]):
        """Initialize the ReferenceToArgumentsProcessor."""
        self.reference = reference
        self.custom_groups: Dict[str, List[ArgparseArgumentGroupModel]] = {}

        self.build_custom_groups()

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

    def build_custom_groups(self):
        """Build the custom groups from the reference."""
        for route, v in self.reference.items():
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

                if route not in self.custom_groups:
                    self.custom_groups[route] = []

                self.custom_groups[route].append(group)


class ArgparseTranslator:
    """Class to translate a function into an argparse program."""

    def __init__(
        self,
        func: Callable,
        custom_argument_groups: Optional[List[ArgparseArgumentGroupModel]] = None,
        add_help: Optional[bool] = True,
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
        self.provider_parameters: Dict[str, List[str]] = {}

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

        def _in_group(arg, group_title):
            for action_group in self._parser._action_groups:
                if action_group.title == group_title:
                    for action in action_group._group_actions:
                        opts = action.option_strings
                        if (opts and opts[0] == arg) or action.dest == arg:
                            return True
            return False

        def _remove_argument(arg) -> List[Optional[str]]:
            groups_w_arg = []

            # remove the argument from the parser
            for action in self._parser._actions:
                opts = action.option_strings
                if (opts and opts[0] == arg) or action.dest == arg:
                    self._parser._remove_action(action)
                    break

            # remove from all groups
            for action_group in self._parser._action_groups:
                for action in action_group._group_actions:
                    opts = action.option_strings
                    if (opts and opts[0] == arg) or action.dest == arg:
                        action_group._group_actions.remove(action)
                        groups_w_arg.append(action_group.title)

            # remove from _action_groups dict
            self._parser._option_string_actions.pop(f"--{arg}", None)

            return groups_w_arg

        def _get_arg_choices(arg) -> Tuple:
            for action in self._parser._actions:
                opts = action.option_strings
                if (opts and opts[0] == arg) or action.dest == arg:
                    return tuple(action.choices or ())
            return ()

        def _update_providers(
            input_string: str, new_provider: List[Optional[str]]
        ) -> str:
            pattern = r"\(provider:\s*(.*?)\)"
            providers = re.findall(pattern, input_string)
            providers.extend(new_provider)
            # remove pattern from help and add with new providers
            input_string = re.sub(pattern, "", input_string).strip()
            return f"{input_string} (provider: {', '.join(providers)})"

        # check if the argument is already in use, if not, add it
        if f"--{argument.name}" not in self._parser._option_string_actions:
            kwargs = argument.model_dump(exclude={"name"}, exclude_none=True)
            group.add_argument(f"--{argument.name}", **kwargs)
            if group.title in self.provider_parameters:
                self.provider_parameters[group.title].append(argument.name)

        else:
            kwargs = argument.model_dump(exclude={"name"}, exclude_none=True)
            model_choices = kwargs.get("choices", ()) or ()
            # extend choices
            choices = tuple(set(_get_arg_choices(argument.name) + model_choices))

            # check if the argument is in the required arguments
            if _in_group(argument.name, group_title="required arguments"):
                for action in self._required._group_actions:
                    if action.dest == argument.name and choices:
                        # update choices
                        action.choices = choices
                return

            # check if the argument is in the optional arguments
            if _in_group(argument.name, group_title="optional arguments"):
                for action in self._parser._actions:
                    if action.dest == argument.name:
                        # update choices
                        if choices:
                            action.choices = choices
                        if argument.name not in self.signature.parameters:
                            # update help
                            action.help = _update_providers(
                                action.help or "", [group.title]
                            )
                return

            # if the argument is in use, remove it from all groups
            # and return the groups that had the argument
            groups_w_arg = _remove_argument(argument.name)
            groups_w_arg.append(group.title)  # add current group

            # add it to the optional arguments group instead
            if choices:
                kwargs["choices"] = choices  # update choices
            # add provider info to the help
            kwargs["help"] = _update_providers(argument.help or "", groups_w_arg)
            self._parser.add_argument(f"--{argument.name}", **kwargs)

    @property
    def parser(self) -> argparse.ArgumentParser:
        """Get the argparse parser."""
        return deepcopy(self._parser)

    @staticmethod
    def _build_description(func_doc: str) -> str:
        """Build the description of the argparse program from the function docstring."""
        patterns = ["openbb\n        ======", "Parameters\n        ----------"]

        if func_doc:
            for pattern in patterns:
                if pattern in func_doc:
                    func_doc = func_doc[: func_doc.index(pattern)].strip()
                    break

        return func_doc

    @staticmethod
    def _param_is_default(param: inspect.Parameter) -> bool:
        """Return True if the parameter has a default value."""
        return param.default != inspect.Parameter.empty

    def _get_action_type(self, param: inspect.Parameter) -> str:
        """Return the argparse action type for the given parameter."""
        param_type = self.type_hints[param.name]
        type_origin = get_origin(param_type)

        if param_type == bool or (
            type_origin is Union and bool in get_args(param_type)
        ):
            return "store_true"
        return "store"

    def _get_type_and_choices(
        self, param: inspect.Parameter
    ) -> Tuple[Type[Any], Tuple[Any, ...]]:
        """Return the type and choices for the given parameter."""
        param_type = self.type_hints[param.name]
        type_origin = get_origin(param_type)

        choices: tuple[Any, ...] = ()

        if type_origin is Literal:
            choices = get_args(param_type)
            param_type = type(choices[0])  # type: ignore

        if type_origin is list:
            param_type = get_args(param_type)[0]

            if get_origin(param_type) is Literal:
                choices = get_args(param_type)
                param_type = type(choices[0])  # type: ignore

        if type_origin is Union:
            union_args = get_args(param_type)
            if str in union_args:
                param_type = str

            # check if it's an Optional, which would be a Union with NoneType
            if type(None) in get_args(param_type):
                # remove NoneType from the args
                args = [arg for arg in get_args(param_type) if arg != type(None)]
                # if there is only one arg left, use it
                if len(args) > 1:
                    raise ValueError(
                        "Union with NoneType should have only one type left"
                    )
                param_type = args[0]

                if get_origin(param_type) is Literal:
                    choices = get_args(param_type)
                    param_type = type(choices[0])  # type: ignore

        # if there are custom choices, override
        choices = self._get_argument_custom_choices(param) or choices  # type: ignore

        return param_type, choices

    @staticmethod
    def _split_annotation(
        base_annotation: Type[Any], custom_annotation_type: Type
    ) -> Tuple[Type[Any], List[Any]]:
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
    def _get_argument_custom_help(cls, param: inspect.Parameter) -> Optional[str]:
        """Return the help annotation for the given parameter."""
        base_annotation = param.annotation
        _, custom_annotations = cls._split_annotation(base_annotation, OpenBBField)
        help_annotation = (
            custom_annotations[0].description if custom_annotations else None
        )
        return help_annotation

    @classmethod
    def _get_argument_custom_choices(cls, param: inspect.Parameter) -> Optional[str]:
        """Return the help annotation for the given parameter."""
        base_annotation = param.annotation
        _, custom_annotations = cls._split_annotation(base_annotation, OpenBBField)
        choices_annotation = (
            custom_annotations[0].choices if custom_annotations else None
        )
        return choices_annotation

    def _get_nargs(self, param: inspect.Parameter) -> Optional[str]:
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
                annotated_parameters: List[inspect.Parameter] = []
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

            argument = ArgparseArgumentModel(
                name=param.name,
                type=param_type,
                dest=param.name,
                default=param.default,
                required=required,
                action=self._get_action_type(param),
                help=self._get_argument_custom_help(param),
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
    def _unflatten_args(args: dict) -> Dict[str, Any]:
        """Unflatten the args that were flattened by the custom types."""
        result: Dict[str, Any] = {}
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

    def _update_with_custom_types(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
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
        parsed_args: Optional[argparse.Namespace] = None,
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
        provider_args = []
        if provider and provider in self.provider_parameters:
            provider_args = self.provider_parameters[provider]
        else:
            for args in self.provider_parameters.values():
                provider_args.extend(args)

        # remove kwargs that doesn't match the signature or provider parameters
        kwargs = {
            key: value
            for key, value in kwargs.items()
            if key in self.signature.parameters or key in provider_args
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
