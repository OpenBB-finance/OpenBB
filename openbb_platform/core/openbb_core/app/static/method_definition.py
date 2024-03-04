import builtins
from dataclasses import Field
from inspect import Parameter, _empty, isclass, signature
from typing import Callable, Dict, List, Optional, OrderedDict, TypeVar, Union

import numpy as np
import pandas as pd
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated, _AnnotatedAlias

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.static.docstring_generator import DocstringGenerator
from openbb_core.app.static.path_handler import PathHandler
from openbb_core.provider.abstract.data import Data

try:
    from openbb_charting import Charting  # type: ignore

    CHARTING_INSTALLED = True
except ImportError:
    CHARTING_INSTALLED = False


DataProcessingSupportedTypes = TypeVar(
    "DataProcessingSupportedTypes",
    list,
    dict,
    pd.DataFrame,
    List[pd.DataFrame],
    pd.Series,
    List[pd.Series],
    np.ndarray,
    Data,
)


class MethodDefinition:
    """Build the method definition for the Platform."""

    # These are types we want to expand.
    # For example, start_date is always a 'date', but we also accept 'str' as input.
    # Be careful, if the type is not coercible by pydantic to the original type, you
    # will need to add some conversion code in the input filter.
    TYPE_EXPANSION = {
        "data": DataProcessingSupportedTypes,
        "start_date": str,
        "end_date": str,
        "date": str,
        "provider": None,
    }

    @staticmethod
    def build_class_loader_method(path: str) -> str:
        """Build the class loader method."""
        module_name = PathHandler.build_module_name(path=path)
        class_name = PathHandler.build_module_class(path=path)
        function_name = path.rsplit("/", maxsplit=1)[-1].strip("/")

        code = "\n    @property\n"
        code += f"    def {function_name}(self):\n"
        code += "        # pylint: disable=import-outside-toplevel\n"
        code += f"        from . import {module_name}\n\n"
        code += f"        return {module_name}.{class_name}(command_runner=self._command_runner)\n"

        return code

    @staticmethod
    def get_type(field: FieldInfo) -> type:
        """Get the type of the field."""
        field_type = getattr(
            field, "annotation", getattr(field, "type", Parameter.empty)
        )
        if isclass(field_type):
            name = field_type.__name__
            if name.startswith("Constrained") and name.endswith("Value"):
                name = name[11:-5].lower()
                return getattr(builtins, name, field_type)
            return field_type
        return field_type

    @staticmethod
    def get_default(field: FieldInfo):
        """Get the default value of the field."""
        field_default = getattr(field, "default", None)
        if field_default is None or field_default is PydanticUndefined:
            return Parameter.empty

        default_default = getattr(field_default, "default", None)
        if default_default is PydanticUndefined or default_default is Ellipsis:
            return Parameter.empty

        return default_default

    @staticmethod
    def get_extra(field: FieldInfo) -> dict:
        """Get json schema extra."""
        field_default = getattr(field, "default", None)
        if field_default:
            return getattr(field_default, "json_schema_extra", {})
        return {}

    @staticmethod
    def is_annotated_dc(annotation) -> bool:
        """Check if the annotation is an annotated dataclass."""
        return isinstance(annotation, _AnnotatedAlias) and hasattr(
            annotation.__args__[0], "__dataclass_fields__"
        )

    @staticmethod
    def is_data_processing_function(path: str) -> bool:
        """Check if the function is a data processing function."""
        methods = PathHandler.build_route_map()[path].methods  # type: ignore
        return "POST" in methods

    @staticmethod
    def is_deprecated_function(path: str) -> bool:
        """Check if the function is deprecated."""
        return getattr(PathHandler.build_route_map()[path], "deprecated", False)

    @staticmethod
    def get_deprecation_message(path: str) -> str:
        """Get the deprecation message."""
        return getattr(PathHandler.build_route_map()[path], "summary", "")

    @staticmethod
    def reorder_params(params: Dict[str, Parameter]) -> "OrderedDict[str, Parameter]":
        """Reorder the params."""
        formatted_keys = list(params.keys())
        for k in ["provider", "extra_params"]:
            if k in formatted_keys:
                formatted_keys.remove(k)
                formatted_keys.append(k)

        od: OrderedDict[str, Parameter] = OrderedDict()
        for k in formatted_keys:
            od[k] = params[k]

        return od

    @staticmethod
    def format_params(
        path: str, parameter_map: Dict[str, Parameter]
    ) -> OrderedDict[str, Parameter]:
        """Format the params."""
        DEFAULT_REPLACEMENT = {
            "provider": None,
        }

        parameter_map.pop("cc", None)
        # we need to add the chart parameter here bc of the docstring generation
        if CHARTING_INSTALLED and path.replace("/", "_")[1:] in Charting.functions():
            parameter_map["chart"] = Parameter(
                name="chart",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=bool,
                default=False,
            )

        formatted: Dict[str, Parameter] = {}

        for name, param in parameter_map.items():
            if name == "extra_params":
                formatted[name] = Parameter(name="kwargs", kind=Parameter.VAR_KEYWORD)
            elif MethodDefinition.is_annotated_dc(param.annotation):
                fields = param.annotation.__args__[0].__dataclass_fields__
                for field_name, field in fields.items():
                    type_ = MethodDefinition.get_type(field)
                    default = MethodDefinition.get_default(field)
                    extra = MethodDefinition.get_extra(field)
                    new_type = MethodDefinition.get_expanded_type(field_name, extra)
                    updated_type = type_ if new_type is ... else Union[type_, new_type]

                    formatted[field_name] = Parameter(
                        name=field_name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=updated_type,
                        default=DEFAULT_REPLACEMENT.get(field_name, default),
                    )
            else:
                new_type = MethodDefinition.get_expanded_type(name)
                if hasattr(new_type, "__constraints__"):
                    types = new_type.__constraints__ + (param.annotation,)
                    updated_type = Union[types]  # type: ignore
                else:
                    updated_type = (
                        param.annotation
                        if new_type is ...
                        else Union[param.annotation, new_type]
                    )

                formatted[name] = Parameter(
                    name=name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=updated_type,
                    default=DEFAULT_REPLACEMENT.get(name, param.default),
                )

        return MethodDefinition.reorder_params(params=formatted)

    @staticmethod
    def add_field_descriptions(
        od: OrderedDict[str, Parameter], model_name: Optional[str] = None
    ):
        """Add the field description to the param signature."""
        if model_name:
            available_fields: Dict[str, Field] = (
                ProviderInterface().params[model_name]["standard"].__dataclass_fields__
            )

            for param, value in od.items():
                if param not in available_fields:
                    continue

                field = available_fields[param]

                new_value = value.replace(
                    annotation=Annotated[
                        value.annotation,
                        OpenBBCustomParameter(
                            description=getattr(field.default, "description", "")
                        ),
                    ],
                )

                od[param] = new_value

    @staticmethod
    def build_func_params(formatted_params: OrderedDict[str, Parameter]) -> str:
        """Stringify function params."""
        func_params = ",\n        ".join(
            str(param) for param in formatted_params.values()
        )
        func_params = func_params.replace("NoneType", "None")
        func_params = func_params.replace(
            "pandas.core.frame.DataFrame", "pandas.DataFrame"
        )
        func_params = func_params.replace(
            "openbb_core.provider.abstract.data.Data", "Data"
        )

        return func_params

    @staticmethod
    def build_func_returns(return_type: type) -> str:
        """Build the function returns."""
        if return_type == _empty:
            func_returns = "None"
        elif return_type.__module__ == "builtins":
            func_returns = return_type.__name__
        else:
            func_returns = "OBBject"

        return func_returns

    @staticmethod
    def build_command_method_signature(
        func_name: str,
        formatted_params: OrderedDict[str, Parameter],
        return_type: type,
        path: str,
        model_name: Optional[str] = None,
    ) -> str:
        """Build the command method signature."""
        MethodDefinition.add_field_descriptions(
            od=formatted_params, model_name=model_name
        )  # this modified `od` in place
        func_params = MethodDefinition.build_func_params(formatted_params)
        func_returns = MethodDefinition.build_func_returns(return_type)

        args = (
            "(config=dict(arbitrary_types_allowed=True))"
            if "pandas.DataFrame" in func_params
            else ""
        )

        code = ""
        deprecated = ""

        if MethodDefinition.is_deprecated_function(path):
            deprecation_message = MethodDefinition.get_deprecation_message(path)
            deprecation_type_class = type(
                deprecation_message.metadata  # type: ignore
            ).__name__

            deprecated = "\n    @deprecated("
            deprecated += f'\n        "{deprecation_message}",'
            deprecated += f"\n        category={deprecation_type_class},"
            deprecated += "\n    )"

        code += "\n    @exception_handler"
        code += f"\n    @validate{args}"
        code += deprecated
        code += f"\n    def {func_name}("
        code += f"\n        self,\n        {func_params}\n    ) -> {func_returns}:\n"

        return code

    @staticmethod
    def build_command_method_doc(
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
        examples: Optional[List[str]] = None,
    ):
        """Build the command method docstring."""
        doc = func.__doc__
        doc = DocstringGenerator.generate(
            func=func,
            formatted_params=formatted_params,
            model_name=model_name,
            examples=examples,
        )
        code = f'        """{doc}        """  # noqa: E501\n\n' if doc else ""

        return code

    @staticmethod
    def build_command_method_body(path: str, func: Callable):
        """Build the command method implementation."""
        sig = signature(func)
        parameter_map = dict(sig.parameters)
        parameter_map.pop("cc", None)
        code = ""

        if CHARTING_INSTALLED and path.replace("/", "_")[1:] in Charting.functions():
            parameter_map["chart"] = Parameter(
                name="chart",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=bool,
                default=False,
            )

        if MethodDefinition.is_deprecated_function(path):
            deprecation_message = MethodDefinition.get_deprecation_message(path)
            code += "        simplefilter('always', DeprecationWarning)\n"
            code += f"""        warn("{deprecation_message}", category=DeprecationWarning, stacklevel=2)\n\n"""

        extra_info = {}

        code += "        return self._run(\n"
        code += f"""            "{path}",\n"""
        code += "            **filter_inputs(\n"
        for name, param in parameter_map.items():
            if name == "extra_params":
                code += f"                {name}=kwargs,\n"
            elif name == "provider_choices":
                field = param.annotation.__args__[0].__dataclass_fields__["provider"]
                available = field.type.__args__
                code += "                provider_choices={\n"
                code += '                    "provider": self._get_provider(\n'
                code += "                       provider,\n"
                code += f'                       "{path}",\n'
                code += f"                       {available},\n"
                code += "                    )\n"
                code += "                },\n"
            elif MethodDefinition.is_annotated_dc(param.annotation):
                fields = param.annotation.__args__[0].__dataclass_fields__
                value = {k: k for k in fields}
                code += f"                {name}={{\n"
                for k, v in value.items():
                    code += f'                    "{k}": {v},\n'
                    # TODO: Extend this to extra_params
                    if extra := MethodDefinition.get_extra(fields[k]):
                        extra_info[k] = extra
                code += "                },\n"
            else:
                code += f"                {name}={name},\n"

        if extra_info:
            code += f"                extra_info={extra_info},\n"

        if MethodDefinition.is_data_processing_function(path):
            code += "                data_processing=True,\n"

        code += "            )\n"
        code += "        )\n"

        return code

    @classmethod
    def get_expanded_type(cls, field_name: str, extra: Optional[dict] = None) -> object:
        """Expand the original field type."""
        if extra and "multiple_items_allowed" in extra:
            return List[str]
        return cls.TYPE_EXPANSION.get(field_name, ...)

    @classmethod
    def build_command_method(
        cls,
        path: str,
        func: Callable,
        model_name: Optional[str] = None,
        examples: Optional[List[str]] = None,
    ) -> str:
        """Build the command method."""
        func_name = func.__name__

        sig = signature(func)
        parameter_map = dict(sig.parameters)

        formatted_params = cls.format_params(path=path, parameter_map=parameter_map)

        code = cls.build_command_method_signature(
            func_name=func_name,
            formatted_params=formatted_params,
            return_type=sig.return_annotation,
            path=path,
            model_name=model_name,
        )
        code += cls.build_command_method_doc(
            func=func,
            formatted_params=formatted_params,
            model_name=model_name,
            examples=examples,
        )

        code += cls.build_command_method_body(path=path, func=func)

        return code
