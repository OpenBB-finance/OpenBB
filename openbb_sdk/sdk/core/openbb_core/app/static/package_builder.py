"""Package Builder Class."""

import builtins
import inspect
import shutil
import subprocess
from dataclasses import MISSING
from inspect import Parameter, _empty, isclass, signature
from json import dumps
from pathlib import Path
from typing import (
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    OrderedDict,
    Type,
    Union,
    get_args,
    get_type_hints,
)

import pandas as pd
from pydantic.fields import ModelField
from starlette.routing import BaseRoute
from typing_extensions import Annotated, _AnnotatedAlias

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.provider_interface import get_provider_interface
from openbb_core.app.router import RouterLoader


class PackageBuilder:
    """Build the extension package for the SDK."""

    @classmethod
    def build(
        cls,
        modules: Optional[Union[str, List[str]]] = None,
        lint: bool = True,
    ) -> None:
        """Build the extensions for the SDK."""
        print("\nBuilding extensions package...\n")
        cls.save_module_map()
        cls.save_modules(modules)
        cls.save_package()
        if lint:
            cls.run_linters()

    @classmethod
    def save_module_map(cls):
        """Save the module map."""
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        module_map = {
            PathHandler.build_module_name(path=path): path for path in path_list
        }
        module_code = dumps(obj=module_map, indent=4)
        module_name = "module_map"
        print("Writing module map...")
        cls.write_to_package(
            module_code=module_code, module_name=module_name, extension="json"
        )

    @classmethod
    def save_modules(cls, modules: Optional[Union[str, List[str]]] = None):
        """Save the modules."""
        print("\nWriting modules...")
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)

        if not path_list:
            print("\nThere is nothing to write.")
            return

        MAX_LEN = max([len(path) for path in path_list if path != "/"])

        if modules:
            path_list = [path for path in path_list if path in modules]

        for path in path_list:
            route = PathHandler.get_route(path=path, route_map=route_map)
            if route is None:
                module_code = ModuleBuilder.build(path=path)
                module_name = PathHandler.build_module_name(path=path)
                print(f"({path})", end=" " * (MAX_LEN - len(path)))
                cls.write_to_package(module_code=module_code, module_name=module_name)

    @classmethod
    def save_package(cls):
        """Save the package."""
        print("\nWriting package __init__...")
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        cls.write_to_package(module_code=code, module_name="__init__")

    @classmethod
    def run_linters(cls):
        """Run the linters."""
        print("\nRunning linters...")
        Linters.black()
        Linters.ruff()

    @staticmethod
    def write_to_package(module_code: str, module_name, extension="py") -> None:
        """Write the module to the package."""
        package_folder = Path(__file__).parent / "package"
        package_path = package_folder / f"{module_name}.{extension}"

        package_folder.mkdir(exist_ok=True)

        print(package_path)
        with package_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(module_code.replace("typing.", ""))


class ModuleBuilder:
    """Build the module for the SDK."""

    @staticmethod
    def build(path: str) -> str:
        """Build the module."""
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        code += ImportDefinition.build(path=path)
        code += ClassDefinition.build(path=path)

        return code


class ImportDefinition:
    """Build the import definition for the SDK."""

    @staticmethod
    def filter_hint_type_list(hint_type_list: List[Type]) -> List[Type]:
        """Filter the hint type list."""
        new_hint_type_list = []
        for hint_type in hint_type_list:
            if hint_type != _empty and hint_type.__module__ != "builtins":
                new_hint_type_list.append(hint_type)

        new_hint_type_list = list(set(new_hint_type_list))

        return new_hint_type_list

    @classmethod
    def get_function_hint_type_list(cls, func: Callable) -> List[Type]:
        """Get the hint type list from the function."""
        sig = signature(func)
        parameter_map = sig.parameters
        return_type = sig.return_annotation

        hint_type_list = []

        for parameter in parameter_map.values():
            hint_type_list.append(parameter.annotation)

        if return_type:
            hint_type = get_args(get_type_hints(return_type)["results"])[0]
            hint_type_list.append(hint_type)

        hint_type_list = cls.filter_hint_type_list(hint_type_list=hint_type_list)

        return hint_type_list

    @classmethod
    def get_path_hint_type_list(cls, path: str) -> List[Type]:
        """Get the hint type list from the path."""
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        child_path_list = PathHandler.get_child_path_list(
            path=path, path_list=path_list
        )
        hint_type_list = []
        for child_path in child_path_list:
            route = PathHandler.get_route(path=child_path, route_map=route_map)
            if route:
                function_hint_type_list = cls.get_function_hint_type_list(func=route.endpoint)  # type: ignore
                hint_type_list.extend(function_hint_type_list)

        hint_type_list = list(set(hint_type_list))
        return hint_type_list

    @classmethod
    def build(cls, path: str) -> str:
        """Build the import definition."""
        hint_type_list = cls.get_path_hint_type_list(path=path)
        code = "\nfrom openbb_core.app.static.container import Container"
        code += "\nfrom openbb_core.app.model.obbject import OBBject"
        code += (
            "\nfrom openbb_core.app.model.custom_parameter import OpenBBCustomParameter"
        )

        # These imports were not detected before build, so we add them manually and
        # ruff --fix the resulting code to remove unused imports.
        # TODO: Find a better way to handle this. This is a temporary solution.
        code += "\nimport openbb_provider"
        code += "\nimport pandas"
        code += "\nimport datetime"
        code += "\nimport pydantic"
        code += "\nfrom pydantic import validate_arguments, BaseModel"
        code += "\nfrom inspect import Parameter"
        code += "\nimport typing"
        code += "\nfrom typing import List, Dict, Union, Optional, Literal, Annotated"
        code += "\nimport typing_extensions"  # TODO: this should only bring `Annotated`
        code += "\nfrom openbb_core.app.utils import df_to_basemodel"
        code += "\nfrom openbb_core.app.static.filters import filter_inputs\n"

        module_list = [hint_type.__module__ for hint_type in hint_type_list]
        module_list = list(set(module_list))
        module_list.sort()

        code += "\n"
        for module in module_list:
            code += f"import {module}\n"

        return code


class ClassDefinition:
    """Build the class definition for the SDK."""

    @staticmethod
    def build(path: str) -> str:
        """Build the class definition."""
        class_name = PathHandler.build_module_class(path=path)
        code = f"\nclass {class_name}(Container):\n"

        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        child_path_list = sorted(
            PathHandler.get_child_path_list(
                path=path,
                path_list=path_list,
            )
        )

        doc = f'    """{path}\n'
        methods = ""
        for child_path in child_path_list:
            route = PathHandler.get_route(path=child_path, route_map=route_map)
            if route:
                doc += f"{route.name}\n"
                methods += MethodDefinition.build_command_method(
                    path=route.path,
                    func=route.endpoint,
                    model_name=route.openapi_extra.get("model", None)
                    if route.openapi_extra
                    else None,
                )  # type: ignore
            else:
                doc += "/" + child_path.split("/")[-1] + "\n"
                methods += MethodDefinition.build_class_loader_method(path=child_path)
        doc += '    """\n'

        code += doc
        code += "    def __repr__(self) -> str:\n"
        code += '        return self.__doc__ or ""\n'
        code += methods

        return code


class DocstringGenerator:
    """Dynamically generate docstrings for the commands."""

    provider_interface = get_provider_interface()

    @staticmethod
    def get_OBBject_description(model_name: str, providers: Optional[str]) -> str:
        """Get the command output description."""

        available_providers = providers or "Optional[PROVIDERS]"

        obbject_description = (
            "OBBject\n"
            f"    results : List[{model_name}]\n"
            "        Serializable results.\n"
            f"    provider : {available_providers}\n"
            "        Provider name.\n"
            "    warnings : Optional[List[Warning_]]\n"
            "        List of warnings.\n"
            "    chart : Optional[Chart]\n"
            "        Chart object.\n"
            "    metadata: Optional[Metadata]\n"
            "        Metadata info about the command execution.\n"
        )

        return obbject_description

    @classmethod
    def generate_model_docstring(
        cls,
        model_name: str,
        summary: str,
        explicit_params: dict,
        params: dict,
        returns: dict,
    ) -> str:
        """Create the docstring for model."""

        standard_dict = params["standard"].__dataclass_fields__
        extra_dict = params["extra"].__dataclass_fields__

        docstring = summary
        docstring += "\n"
        docstring += "\nParameters\n----------\n"

        # Explicit parameters
        for param_name, param in explicit_params.items():
            if param_name in standard_dict:
                # pylint: disable=W0212
                p_type = param._annotation.__args__[0]
                type_ = p_type.__name__ if inspect.isclass(p_type) else p_type
                meta = param._annotation.__metadata__
                description = getattr(meta[0], "description", "") if meta else ""
            else:
                # pylint: disable=W0212
                if param_name == "provider":
                    # pylint: disable=W0212
                    type_ = param._annotation
                    default = param._annotation.__args__[0].__args__[0]
                    description = f"""The provider to use for the query, by default None.
    If None, the provider specified in defaults is selected or '{default}' if there is
    no default."""
                elif param_name == "chart":
                    type_ = "bool"
                    description = "Whether to create a chart or not, by default False."
                else:
                    type_ = ""
                    description = ""

            docstring += f"{param_name} : {type_}\n"
            docstring += f"    {description}\n"

        # Kwargs
        for param_name, param in extra_dict.items():
            p_type = param.type
            type_ = p_type.__name__ if inspect.isclass(p_type) else p_type
            docstring += f"{param_name} : {type_}\n"
            docstring += f"    {param.default.description}\n"

        # Returns
        docstring += "\nReturns\n-------\n"
        provider_param = explicit_params.get("provider", None)
        available_providers = getattr(provider_param, "_annotation", None)
        docstring += cls.get_OBBject_description(model_name, available_providers)

        # Schema
        underline = "-" * len(model_name)
        docstring += f"\n{model_name}\n{underline}\n"

        for field_name, field in returns.items():
            try:
                field_type = field.__repr_args__()[1][1]
            except AttributeError:
                # Fallback to the annotation if the repr fails
                field_type = field.annotation

            docstring += f"{field_name} : {field_type}\n"
            docstring += f"    {field.field_info.description}\n"

        return docstring

    @classmethod
    def generate(
        cls,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
    ) -> Callable:
        """Generate the docstring for the function."""
        if model_name:
            params = cls.provider_interface.params.get(model_name, None)
            return_schema = cls.provider_interface.return_schema.get(model_name, None)
            if params and return_schema:
                explicit_dict = dict(formatted_params)
                explicit_dict.pop("extra_params", None)

                returns = return_schema.__fields__

                func.__doc__ = cls.generate_model_docstring(
                    model_name=model_name,
                    summary=func.__doc__ or "",
                    explicit_params=explicit_dict,
                    params=params,
                    returns=returns,
                )

        return func


class MethodDefinition:
    """Build the method definition for the SDK."""

    @staticmethod
    def build_class_loader_method(path: str) -> str:
        """Build the class loader method."""
        module_name = PathHandler.build_module_name(path=path)
        class_name = PathHandler.build_module_class(path=path)
        function_name = path.rsplit("/", maxsplit=1)[-1].strip("/")

        code = "\n    @property\n"
        code += f'    def {function_name}(self):  # route = "{path}"\n'
        code += f"        from openbb_core.app.static.package import {module_name}\n"
        code += f"        return {module_name}.{class_name}(command_runner=self._command_runner)\n"

        return code

    @staticmethod
    def get_type(field: ModelField) -> type:
        """Get the type of the field."""
        field_type = getattr(field, "type", Parameter.empty)
        if isclass(field_type):
            name = field_type.__name__
            if name.startswith("Constrained") and name.endswith("Value"):
                name = name[11:-5].lower()
                return getattr(builtins, name, field_type)
            return field_type
        return field_type

    @staticmethod
    def get_default(field: ModelField):
        """Get the default value of the field."""
        field_default = getattr(field, "default", None)
        if field_default is None or field_default is MISSING:
            return Parameter.empty

        default_default = getattr(field_default, "default", None)
        if default_default is MISSING or default_default is Ellipsis:
            return Parameter.empty

        return default_default

    @staticmethod
    def is_annotated_dc(annotation) -> bool:
        """Check if the annotation is an annotated dataclass."""
        return type(annotation) is _AnnotatedAlias and hasattr(
            annotation.__args__[0], "__dataclass_fields__"
        )

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
        parameter_map: Dict[str, Parameter]
    ) -> OrderedDict[str, Parameter]:
        """Format the params."""
        # These are types we want to expand.
        # For example, start_date is always a 'date', but we also accept 'str' as input.
        # Be careful, if the type is not coercible by pydantic to the original type, you
        # will need to add some conversion code in the input filter.
        TYPE_EXPANSION = {
            "symbol": List[str],
            "data": pd.DataFrame,
            "start_date": str,
            "end_date": str,
            "provider": None,
        }

        DEFAULT_REPLACEMENT = {
            "provider": None,
        }

        parameter_map.pop("cc", None)
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
                    name = field_name
                    type_ = MethodDefinition.get_type(field)
                    default = MethodDefinition.get_default(field)

                    new_type = TYPE_EXPANSION.get(name, ...)
                    updated_type = type_ if new_type is ... else Union[type_, new_type]

                    formatted[name] = Parameter(
                        name=name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=updated_type,
                        default=DEFAULT_REPLACEMENT.get(name, default),
                    )
            else:
                new_type = TYPE_EXPANSION.get(name, ...)
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
            available_fields = (
                get_provider_interface()
                .map[model_name]["openbb"]["QueryParams"]["fields"]
                .keys()
            )

            for param, value in od.items():
                if param not in available_fields:
                    continue

                description = (
                    get_provider_interface()
                    .map[model_name]["openbb"]["QueryParams"]["fields"][param]
                    .field_info.description
                )

                new_value = value.replace(
                    annotation=Annotated[
                        value.annotation, OpenBBCustomParameter(description=description)
                    ]
                )

                od[param] = new_value

    @staticmethod
    def build_func_params(formatted_params: OrderedDict[str, Parameter]) -> str:
        """Stringify function params."""
        func_params = ", ".join(str(param) for param in formatted_params.values())
        func_params = func_params.replace("NoneType", "None")
        func_params = func_params.replace(
            "pandas.core.frame.DataFrame", "pandas.DataFrame"
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
            item_type = get_args(get_type_hints(return_type)["results"])[0]
            if item_type.__module__ == "builtins":
                func_returns = f"OBBject[{item_type.__name__}]"
            # elif get_origin(item_type) == list:
            #     inner_type = get_args(item_type)[0]
            #     select = f"[{inner_type.__module__}.{inner_type.__name__}]"
            #     func_returns = f"OBBject[{item_type.__module__}.{item_type.__name__}[{select}]]"
            else:
                inner_type_name = (
                    item_type.__name__
                    if hasattr(item_type, "__name__")
                    else item_type._name
                )
                result_type = f"{item_type.__module__}.{inner_type_name}"

                if "pydantic.main" in result_type:
                    result_type = "BaseModel"

                func_returns = f"OBBject[{result_type}]"

        return func_returns

    @staticmethod
    def build_command_method_signature(
        func_name: str,
        formatted_params: OrderedDict[str, Parameter],
        return_type: type,
        model_name: Optional[str] = None,
    ) -> str:
        """Build the command method signature."""
        MethodDefinition.add_field_descriptions(
            od=formatted_params, model_name=model_name
        )  # this modified `od` in place
        func_params = MethodDefinition.build_func_params(formatted_params)
        func_returns = MethodDefinition.build_func_returns(return_type)

        extra = (
            "(config=dict(arbitrary_types_allowed=True))"
            if "pandas.DataFrame" in func_params
            else ""
        )
        code = f"\n    @validate_arguments{extra}"
        code += f"\n    def {func_name}(self, {func_params}) -> {func_returns}:\n"

        return code

    @staticmethod
    def build_command_method_doc(
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
    ):
        """Build the command method docstring."""
        if model_name:
            func = DocstringGenerator.generate(
                func=func, formatted_params=formatted_params, model_name=model_name
            )
        code = f'        """{func.__doc__}"""\n\n' if func.__doc__ else ""

        return code

    @staticmethod
    def build_command_method_implementation(path: str, func: Callable):
        """Build the command method implementation."""
        sig = signature(func)
        parameter_map = dict(sig.parameters)
        parameter_map.pop("cc", None)
        parameter_map["chart"] = Parameter(
            name="chart",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=bool,
            default=False,
        )

        code = "        inputs = filter_inputs(\n"
        for name, param in parameter_map.items():
            if name == "extra_params":
                code += f"            {name}=kwargs,\n"
            elif MethodDefinition.is_annotated_dc(param.annotation):
                fields = param.annotation.__args__[0].__dataclass_fields__
                value = {k: k for k in fields}
                code += f"            {name}={{"
                for k, v in value.items():
                    if k == "symbol":
                        code += f'"{k}": ",".join(symbol) if isinstance(symbol, list) else symbol, '
                        continue
                    code += f'"{k}": {v}, '
                code += "},\n"
            else:
                code += f"            {name}={name},\n"
        code += "        )\n\n"
        code += "        return self._command_runner.run(\n"
        code += f"""            "{path}",\n"""
        code += "            **inputs,\n"
        code += "        )\n"
        code += "\n"

        return code

    @classmethod
    def build_command_method(
        cls, path: str, func: Callable, model_name: Optional[str] = None
    ) -> str:
        """Build the command method."""
        func_name = func.__name__

        sig = signature(func)
        parameter_map = dict(sig.parameters)

        formatted_params = cls.format_params(parameter_map=parameter_map)

        code = cls.build_command_method_signature(
            func_name=func_name,
            formatted_params=formatted_params,
            return_type=sig.return_annotation,
            model_name=model_name,
        )
        code += cls.build_command_method_doc(
            func=func, formatted_params=formatted_params, model_name=model_name
        )
        code += cls.build_command_method_implementation(path=path, func=func)

        return code


class PathHandler:
    """Handle the paths for the SDK."""

    @staticmethod
    def build_route_map() -> Dict[str, BaseRoute]:
        """Build the route map."""
        router = RouterLoader.from_extensions()
        route_map = {route.path: route for route in router.api_router.routes}  # type: ignore

        return route_map

    @staticmethod
    def build_path_list(route_map: Dict[str, BaseRoute]) -> List[str]:
        """Build the path list."""
        path_list = []
        for route_path in route_map:
            if route_path not in path_list:
                path_list.append(route_path)

                sub_path_list = route_path.split("/")

                for length in range(len(sub_path_list)):
                    sub_path = "/".join(sub_path_list[:length])
                    if sub_path not in path_list:
                        path_list.append(sub_path)

        return path_list

    @staticmethod
    def get_route(path: str, route_map: Dict[str, BaseRoute]):
        """Get the route from the path."""
        return route_map.get(path, None)

    @staticmethod
    def get_child_path_list(path: str, path_list: List[str]) -> List[str]:
        """Get the child path list."""
        direct_children = []
        for p in path_list:
            if p.startswith(path):
                path_reminder = p[len(path) :]  # noqa: E203
                if path_reminder.count("/") == 1:
                    direct_children.append(p)

        return direct_children

    @staticmethod
    def clean_path(path: str) -> str:
        """Clean the path."""
        if path.startswith("/"):
            path = path[1:]
        return path.replace("-", "_").replace("/", "_")

    @classmethod
    def build_module_name(cls, path: str) -> str:
        """Build the module name."""
        if path == "":
            return "__extensions__"
        return cls.clean_path(path=path)

    @classmethod
    def build_module_class(cls, path: str) -> str:
        """Build the module class."""
        if path == "":
            return "Extensions"
        return f"CLASS_{cls.clean_path(path=path)}"


class Linters:
    """Run the linters for the SDK."""

    current_folder = str(Path(Path(__file__).parent, "package").absolute())

    @staticmethod
    def print_separator(symbol: str, length: int = 160):
        """Print a separator."""
        print(symbol * length)

    @staticmethod
    def run(
        linter: Literal["black", "ruff"],
        flags: Optional[List[str]] = None,
    ):
        """Run linter with flags."""
        if shutil.which(linter):
            print(f"\n* {linter}")
            Linters.print_separator("^")

            command = [linter, Linters.current_folder]
            if flags:
                command.extend(flags)
            subprocess.run(command, check=False)  # noqa: S603

            Linters.print_separator("-")
        else:
            print(f"\n* {linter} not found")

    @classmethod
    def black(cls):
        """Run black."""
        cls.run(linter="black")

    @classmethod
    def ruff(cls):
        """Run ruff."""
        cls.run(linter="ruff", flags=["--fix"])
