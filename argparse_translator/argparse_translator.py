import argparse
import inspect
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel
from typing_extensions import Annotated

SEP = "__"


class ArgparseCustomArgument(BaseModel):
    help: Optional[str] = None
    # action: Optional[Any] = None


class ArgparseActionType(Enum):
    store = "store"
    store_true = "store_true"


class ArgparseTranslator:
    def __init__(self, func: Callable, add_help: Optional[bool] = False):
        """
        Initializes the ArgparseTranslator.

        Args:
            func (Callable): The function to translate into an argparse program.
            add_help (Optional[bool], optional): Whether to add the help argument. Defaults to False.
        """
        self.func = func
        self.signature = inspect.signature(func)
        self.type_hints = get_type_hints(func)

        self.parser = argparse.ArgumentParser(
            description=func.__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=add_help,
        )

        self._generate_argparse_arguments(self.signature.parameters)

    @staticmethod
    def _param_is_default(param: inspect.Parameter) -> bool:
        return param.default != inspect.Parameter.empty

    def _get_action_type(self, param: inspect.Parameter) -> str:
        param_type = self.type_hints[param.name]

        if param_type == bool:
            return ArgparseActionType.store_true.value
        return ArgparseActionType.store.value

    def _get_type(self, param: inspect.Parameter):
        param_type = self.type_hints[param.name]

        if get_origin(param_type) is list:  # TODO: dict should also go here
            return get_args(param_type)[0]

        return param_type

    @staticmethod
    def _split_annotation(
        base_annotation: Type[Any],
    ) -> tuple[Type[Any], List[ArgparseCustomArgument]]:
        if get_origin(base_annotation) is not Annotated:
            return base_annotation, []
        base_annotation, *maybe_custom_annotations = get_args(base_annotation)
        return base_annotation, [
            annotation
            for annotation in maybe_custom_annotations
            if isinstance(annotation, ArgparseCustomArgument)
        ]

    @classmethod
    def _get_argument_help(cls, param: inspect.Parameter) -> Optional[str]:
        base_annotation = param.annotation
        _, custom_annotations = cls._split_annotation(base_annotation)
        help_annotation = custom_annotations[0].help if custom_annotations else None
        if not help_annotation:
            # try to get it from the docstring
            pass
        return help_annotation

    def _get_nargs(self, param: inspect.Parameter) -> Optional[str]:
        param_type = self.type_hints[param.name]

        if get_origin(param_type) is list:
            return "+"
        return None

    def _generate_argparse_arguments(self, parameters) -> None:
        for param in parameters.values():
            param_type = self._get_type(param)

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
                            ArgparseCustomArgument(
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

            self.parser.add_argument(
                f"--{param.name}",
                type=param_type,
                dest=param.name,
                default=param.default,
                required=not self._param_is_default(param),
                action=self._get_action_type(param),
                help=self._get_argument_help(param),
                nargs=self._get_nargs(param),
            )

    @staticmethod
    def _unflatten_args(args: dict) -> Dict[str, Any]:
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
        # for each argument in the signature that is a custom type, we need to
        # update the kwargs with the custom type kwargs
        for param in self.signature.parameters.values():
            param_type = self._get_type(param)
            if inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                custom_type_kwargs = kwargs[param.name]
                kwargs[param.name] = param_type(**custom_type_kwargs)

        return kwargs

    def execute_func(
        self,
        parsed_args: Optional[argparse.Namespace] = None,
    ) -> Any:
        kwargs = self._unflatten_args(vars(parsed_args))
        kwargs = self._update_with_custom_types(kwargs)
        kwargs.pop("help", None)
        return self.func(**kwargs)

    def parse_args_and_execute(self) -> Any:
        """
        Parses the arguments and executes the original function.

        Returns:
            Any: The return value of the original function.
        """
        parsed_args = self.parser.parse_args()
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


# def hello_world(name: str, age: int):
#     print(f"Hello {name}! You are {age} years old.")


# translator = ArgparseTranslator(hello_world)
# parser = translator.parser
# parsed_args = parser.parse_args()
# print(parsed_args)

# translator.execute_func(parsed_args)
