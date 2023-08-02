import builtins
import shutil
import subprocess
from collections import OrderedDict
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
    Type,
    Union,
    get_args,
    get_type_hints,
    Annotated,
)

import pandas as pd
from pydantic.fields import ModelField
from pydantic import BaseModel
from starlette.routing import BaseRoute
from typing_extensions import _AnnotatedAlias

from openbb_core.app.provider_interface import get_provider_interface
from openbb_core.app.router import RouterLoader


class OpenBBCustomParameter(BaseModel):
    """Custom parameter for OpenBB."""

    description: str


class PackageBuilder:
    """Build the extension package for the SDK."""

    @classmethod
    def build(cls, modules: Optional[List[str]] = None, lint: bool = True) -> None:
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
    def save_modules(cls, modules: Optional[List[str]] = None):
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
        Linters.mypy()

    @staticmethod
    def write_to_package(module_code: str, module_name, extension="py") -> None:
        """Write the module to the package."""
        package_folder = Path(__file__).parent / "package"
        package_path = package_folder / f"{module_name}.{extension}"

        package_folder.mkdir(exist_ok=True)

        print(package_path)
        with package_path.open("w") as file:
            file.write(module_code)


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
        code += "\nfrom openbb_core.app.model.command_output import CommandOutput"
        code += (
            "\nfrom openbb_core.app.static.package_builder import OpenBBCustomParameter"
        )

        # These imports were not detected before build, so we add them manually and
        # ruff --fix the resulting code to remove unused imports.
        # TODO: Find a better way to handle this. This is a temporary solution.
        code += "\nimport openbb_provider"
        code += "\nimport pandas"
        code += "\nimport datetime"
        code += "\nimport pydantic"
        code += "\nfrom pydantic import validate_arguments"
        code += "\nfrom inspect import Parameter"
        code += "\nfrom typing import List, Dict, Union, Optional, Literal, Annotated"
        code += "\nfrom openbb_core.app.utils import df_to_basemodel"
        code += "\nfrom openbb_core.app.static.filters import filter_call, filter_inputs, filter_output\n"

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
        child_path_list = PathHandler.get_child_path_list(
            path=path,
            path_list=path_list,
        )
        for child_path in child_path_list:
            route = PathHandler.get_route(path=child_path, route_map=route_map)
            if route:
                code += MethodDefinition.build_command_method(
                    path=route.path,
                    func=route.endpoint,
                    model_name=route.openapi_extra.get("model", None)
                    if route.openapi_extra
                    else None,
                )  # type: ignore
            else:
                code += MethodDefinition.build_class_loader_method(path=child_path)

        return code


class DocstringGenerator:
    """Dynamically generate docstrings for the commands."""

    @staticmethod
    def get_command_output_description() -> str:
        """Get the command output description."""
        command_output_description = (
            "\nReturns\n"
            "-------\n"
            "CommandOutput\n"
            "    results: List[Data]\n"
            "        Serializable results.\n"
            "    provider: Optional[PROVIDERS]\n"
            "        Provider name.\n"
            "    warnings: Optional[List[Warning_]]\n"
            "        List of warnings.\n"
            "    error: Optional[Error]\n"
            "        Caught exceptions.\n"
            "    chart: Optional[Chart]\n"
            "        Chart object.\n"
        )

        return command_output_description

    @staticmethod
    def get_available_providers(query_mapping: dict) -> str:
        """Return a string of available providers."""
        available_providers = ", ".join(query_mapping.keys())
        available_providers = available_providers.replace("openbb, ", "")
        available_providers = available_providers.replace("openbb", "")

        provider_string = f"provider: Literal[{available_providers}]\n"
        provider_string += "    The provider to use for the query.\n"

        return provider_string

    @staticmethod
    def reorder_dictionary(dictionary: dict, key_to_move_first: str) -> dict:
        """Reorder a dictionary so that a given key is first."""
        if key_to_move_first in dictionary:
            ordered_dict = OrderedDict(
                [(key_to_move_first, dictionary[key_to_move_first])]
            )

            for key, value in dictionary.items():
                if key != key_to_move_first:
                    ordered_dict[key] = value

            return ordered_dict
        else:
            return dictionary

    @classmethod
    def extract_field_details(
        cls,
        model_name: str,
        provider: str,
        section_name: str,
        section_docstring: str,
        mapping: dict,
    ) -> str:
        """Extract the field details from the map and add them to the docstring."""
        if section_docstring == "":
            return section_docstring

        padding = "    "

        field_mapping = mapping[model_name][provider.lower()][section_name]["fields"]
        fields = field_mapping.keys()

        if len(fields) == 0:
            section_docstring += "All fields are standardized.\n"
        else:
            for field in fields:
                # We need to get the string representation of the field type
                # because Pydantic uses a custom repr.
                try:
                    field_type = field_mapping[field].__repr_args__()[1][1]
                except AttributeError:
                    # Fallback to the annotation if the repr fails
                    field_type = field_mapping[field].annotation

                field_description = field_mapping[field].field_info.description

                section_docstring += f"{field} : {field_type}\n"
                section_docstring += f"{padding}{field_description}\n"

        if provider == "openbb" and section_name == "QueryParams":
            section_docstring += cls.get_command_output_description()

        return section_docstring

    @classmethod
    def generate_provider_docstrings(
        cls,
        docstring: str,
        query_mapping: dict,
        model_name: str,
        provider_interface_mapping: dict,
    ) -> str:
        """Generate the docstring for the provider."""
        for provider, model_mapping in query_mapping.items():
            docstring += f"\n{provider}"
            docstring += f"\n{'=' * len(provider)}"

            for section_name in model_mapping:
                section_docstring = ""
                if section_name == "QueryParams":
                    section_docstring += "\nParameters\n----------\n"
                    if provider == "openbb":
                        section_docstring += (
                            f"{cls.get_available_providers(query_mapping)}"
                        )
                        # TODO: How do we know if the model has a chart parameter?
                elif section_name == "Data":
                    underline = "-" * len(model_name)
                    section_docstring += f"\n{model_name}\n{underline}\n"
                else:
                    continue

                section_docstring = cls.extract_field_details(
                    model_name=model_name,
                    provider=provider,
                    section_name=section_name,
                    section_docstring=section_docstring,
                    mapping=provider_interface_mapping,
                )

                docstring += f"\n{section_docstring}"

        return docstring

    @classmethod
    def generate_command_docstring(cls, func: Callable, model_name: str) -> Callable:
        """Generate the docstring for the command."""
        provider_interface_mapping = get_provider_interface().map
        query_mapping = provider_interface_mapping.get(model_name, None)
        if query_mapping:
            docstring = func.__doc__ or ""
            docstring += "\n\n"

            query_mapping_ordered = cls.reorder_dictionary(query_mapping, "openbb")
            docstring = cls.generate_provider_docstrings(
                docstring=docstring,
                query_mapping=query_mapping_ordered,
                model_name=model_name,
                provider_interface_mapping=provider_interface_mapping,
            )

            func.__doc__ = docstring
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
        code += f"        return {module_name}.{class_name}(command_runner_session=self._command_runner_session)\n"

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
    ) -> "OrderedDict[str, Parameter]":
        """Format the params."""
        # These are types we want to expand.
        # For example, start_date is always a 'date', but we also accept 'str' as input.
        # Be careful, if the type is not coercible by pydantic to the original type, you
        # will need to add some conversion code in the input filter.
        TYPE_EXPANSION = {
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
    def build_func_params(
        parameter_map: Dict[str, Parameter], model_name: Optional[str]
    ) -> str:
        od = MethodDefinition.format_params(parameter_map=parameter_map)

        if model_name:
            for param, value in od.items():
                if (
                    (param == "chart")
                    or (param == "provider")
                    or (param == "extra_params")
                ):
                    # TODO: These are special cases that are params but not inside
                    # the interface. We should find a better way to handle this.
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

        func_params = ", ".join(str(param) for param in od.values())
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
                func_returns = f"CommandOutput[{item_type.__name__}]"
            # elif get_origin(item_type) == list:
            #     inner_type = get_args(item_type)[0]
            #     select = f"[{inner_type.__module__}.{inner_type.__name__}]"
            #     func_returns = f"CommandOutput[{item_type.__module__}.{item_type.__name__}[{select}]]"
            else:
                inner_type_name = (
                    item_type.__name__
                    if hasattr(item_type, "__name__")
                    else item_type._name
                )
                func_returns = (
                    f"CommandOutput[{item_type.__module__}.{inner_type_name}]"
                )

        return func_returns

    @staticmethod
    def build_command_method_signature(
        func_name: str,
        parameter_map: Dict[str, Parameter],
        return_type: type,
        model_name: Optional[str],
    ) -> str:
        func_params = MethodDefinition.build_func_params(parameter_map, model_name)
        func_returns = MethodDefinition.build_func_returns(return_type)
        code = "\n    @filter_call"

        extra = (
            "(config=dict(arbitrary_types_allowed=True))"
            if "pandas.DataFrame" in func_params
            else ""
        )
        code += f"\n    @validate_arguments{extra}"
        code += f"\n    def {func_name}(self, {func_params}) -> {func_returns}:\n"

        return code

    @staticmethod
    def build_command_method_doc(func: Callable):
        """Build the command method docstring."""
        code = f'        """{func.__doc__}"""\n' if func.__doc__ else ""

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
                    code += f'"{k}": {v}, '
                code += "},\n"
            else:
                code += f"            {name}={name},\n"
        code += "        )\n\n"
        code += "        o = self._command_runner_session.run(\n"
        code += f"""            "{path}",\n"""
        code += "            **inputs,\n"
        code += "        ).output\n"
        code += "\n"
        code += "        return filter_output(o)\n"

        return code

    @classmethod
    def build_command_method(
        cls, path: str, func: Callable, model_name: Optional[str]
    ) -> str:
        """Build the command method."""
        func_name = func.__name__

        sig = signature(func)
        parameter_map = dict(sig.parameters)

        if model_name:
            func = DocstringGenerator.generate_command_docstring(
                func=func, model_name=model_name
            )

        code = cls.build_command_method_signature(
            func_name=func_name,
            parameter_map=parameter_map,
            return_type=sig.return_annotation,
            model_name=model_name,
        )
        code += cls.build_command_method_doc(func=func)
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
        linter: Literal["black", "ruff", "mypy"], flags: Optional[List[str]] = None
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

    @classmethod
    def mypy(cls):
        """Run mypy."""
        cls.run(linter="mypy", flags=["--ignore-missing-imports"])
