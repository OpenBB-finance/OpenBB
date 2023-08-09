import argparse
import inspect
from copy import deepcopy
from enum import Enum
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

from pydantic import BaseModel
from typing_extensions import Annotated

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter

SEP = "__"


class ArgparseActionType(Enum):
    store = "store"
    store_true = "store_true"


class ArgparseTranslator:
    def __init__(self, func: Callable, add_help: Optional[bool] = True):
        """
        Initializes the ArgparseTranslator.

        Args:
            func (Callable): The function to translate into an argparse program.
            add_help (Optional[bool], optional): Whether to add the help argument. Defaults to False.
        """
        self.func = func
        self.signature = inspect.signature(func)
        self.type_hints = get_type_hints(func)

        self._parser = argparse.ArgumentParser(
            prog=func.__name__,
            description=self._build_description(func.__doc__),
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=add_help,
        )
        self._required = self._parser.add_argument_group("required arguments")

        self._generate_argparse_arguments(self.signature.parameters)

    @property
    def parser(self) -> argparse.ArgumentParser:
        return deepcopy(self._parser)

    @staticmethod
    def _build_description(func_doc: str) -> str:
        """Builds the description of the argparse program from the function docstring."""

        patterns = ["openbb\n        ======", "Parameters\n        ----------"]

        for pattern in patterns:
            if pattern in func_doc:
                func_doc = func_doc[: func_doc.index(pattern)].strip()
                break

        return func_doc

    @staticmethod
    def _param_is_default(param: inspect.Parameter) -> bool:
        """Returns True if the parameter has a default value."""
        return param.default != inspect.Parameter.empty

    def _get_action_type(self, param: inspect.Parameter) -> str:
        """Returns the argparse action type for the given parameter."""
        param_type = self.type_hints[param.name]

        if param_type == bool:
            return ArgparseActionType.store_true.value
        return ArgparseActionType.store.value

    def _get_type_and_choices(
        self, param: inspect.Parameter
    ) -> Tuple[Type[Any], Tuple[Any, ...]]:
        """Returns the type and choices for the given parameter."""
        param_type = self.type_hints[param.name]
        type_origin = get_origin(param_type)

        choices = ()

        if type_origin is list:  # TODO: dict should also go here
            param_type = get_args(param_type)[0]
        if type_origin is Union:
            # if str type is available on Union, use it
            if str in get_args(param_type):
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
                    param_type = type(choices[0])

        return param_type, choices

    @staticmethod
    def _split_annotation(
        base_annotation: Type[Any],
    ) -> Tuple[Type[Any], List[OpenBBCustomParameter]]:
        """Find the base annotation and the custom annotations, namely the OpenBBCustomParameter."""
        if get_origin(base_annotation) is not Annotated:
            return base_annotation, []
        base_annotation, *maybe_custom_annotations = get_args(base_annotation)
        return base_annotation, [
            annotation
            for annotation in maybe_custom_annotations
            if isinstance(annotation, OpenBBCustomParameter)
        ]

    @classmethod
    def _get_argument_help(cls, param: inspect.Parameter) -> Optional[str]:
        """Returns the help annotation for the given parameter."""
        base_annotation = param.annotation
        _, custom_annotations = cls._split_annotation(base_annotation)
        help_annotation = (
            custom_annotations[0].description if custom_annotations else None
        )
        if not help_annotation:
            # try to get it from the docstring
            pass
        return help_annotation

    def _get_nargs(self, param: inspect.Parameter) -> Optional[str]:
        """Returns the nargs annotation for the given parameter."""
        param_type = self.type_hints[param.name]

        if get_origin(param_type) is list:
            return "+"
        return None

    def _generate_argparse_arguments(self, parameters) -> None:
        """Generates the argparse arguments from the function parameters."""
        for param in parameters.values():
            # TODO : how to handle kwargs?
            # it's possible to add unknown arguments when parsing as follows:
            # args, unknown_args = parser.parse_known_args()
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
                    child_param = child_param.replace(
                        name=f"{param.name}{SEP}{child_param.name}",
                        annotation=Annotated[
                            child_param.annotation,
                            OpenBBCustomParameter(
                                help=param_type.schema()["properties"][
                                    child_param.name
                                ].get("help", None)
                            ),
                        ],
                        kind=inspect.Parameter.KEYWORD_ONLY,
                    )
                    annotated_parameters.append(child_param)

                # replacing with the annotated parameters
                new_signature = inspect.Signature(
                    parameters=annotated_parameters,
                    return_annotation=sig.return_annotation,
                )
                self._generate_argparse_arguments(new_signature.parameters)

                # the custom type itself should not be added as an argument
                continue

            required = not self._param_is_default(param)

            kwargs = {
                "type": param_type,
                "dest": param.name,
                "default": param.default,
                "required": required,
                "action": self._get_action_type(param),
                "help": self._get_argument_help(param),
                "nargs": self._get_nargs(param),
            }

            if choices:
                kwargs["choices"] = choices

            if param_type == bool:
                # store_true action does not accept the below kwargs
                kwargs.pop("type")
                kwargs.pop("nargs")

            if required:
                self._required.add_argument(
                    f"--{param.name}",
                    **kwargs,
                )
            else:
                self._parser.add_argument(
                    f"--{param.name}",
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
            # TODO : how to handle kwargs?
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
        Executes the original function with the parsed arguments.

        Args:
            parsed_args (Optional[argparse.Namespace], optional): The parsed arguments. Defaults to None.

        Returns:
            Any: The return value of the original function.

        """
        kwargs = self._unflatten_args(vars(parsed_args))
        kwargs = self._update_with_custom_types(kwargs)

        # remove kwargs that doesn't match the signature
        kwargs = {
            key: value
            for key, value in kwargs.items()
            if key in self.signature.parameters
        }

        return self.func(**kwargs)

    def parse_args_and_execute(self) -> Any:
        """
        Parses the arguments and executes the original function.

        Returns:
            Any: The return value of the original function.
        """
        parsed_args = self._parser.parse_args()
        return self.execute_func(parsed_args)

    def translate(self) -> Callable:
        """
        Wraps the original function with an argparse program.

        Returns:
            Callable: The original function wrapped with an argparse program.
        """

        def wrapper_func():
            return self.parse_args_and_execute()

        return wrapper_func


# from openbb_sdk.openbb import obb

# translator = ArgparseTranslator(obb.stocks.load)
# stocks_load = translator.translate()
# result = stocks_load()
# print(result)
