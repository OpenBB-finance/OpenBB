import builtins
import shutil
import subprocess
from collections import OrderedDict
from dataclasses import MISSING
from inspect import Parameter, _empty, isclass, signature
from json import dumps
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import pandas as pd
from starlette.routing import BaseRoute

from openbb_core.app.provider_interface import get_provider_interface
from openbb_core.app.router import RouterLoader


class PackageBuilder:
    """Build the extension package for the SDK."""

    @classmethod
    def build(cls, lint: bool = True) -> None:
        """Build the extensions for the SDK."""
        print("\nBuilding extensions package...\n")
        cls.save_module_map()
        cls.save_modules()
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
    def save_modules(cls):
        """Save the modules."""
        print("\nWriting modules...")
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)

        if not path_list:
            print("\nThere is nothing to write.")
            return

        MAX_LEN = max([len(path) for path in path_list if path != "/"])

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
    @staticmethod
    def build(path: str) -> str:
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        code += ImportDefinition.build(path=path)
        code += ClassDefinition.build(path=path)

        return code


class ImportDefinition:
    @staticmethod
    def filter_hint_type_list(hint_type_list: List[Type]) -> List[Type]:
        new_hint_type_list = []
        for hint_type in hint_type_list:
            if hint_type != _empty and hint_type.__module__ != "builtins":
                new_hint_type_list.append(hint_type)

        new_hint_type_list = list(set(new_hint_type_list))

        return new_hint_type_list

    @classmethod
    def get_function_hint_type_list(cls, func: Callable) -> List[Type]:
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
        hint_type_list = cls.get_path_hint_type_list(path=path)
        code = "\nfrom openbb_core.app.static.container import Container"
        code += "\nfrom openbb_core.app.model.command_output import CommandOutput"

        # These imports were not detected before build, so we add them manually and
        # ruff --fix the resulting code to remove unused imports.
        # TODO: Find a better way to handle this. This is a temporary solution.
        code += "\nimport openbb_provider"
        code += "\nimport pandas"
        code += "\nimport datetime"
        code += "\nfrom types import NoneType"
        code += "\nimport pydantic"
        code += "\nfrom pydantic import validate_arguments"
        code += "\nfrom inspect import Parameter"
        code += "\nfrom typing import List, Dict, Union, Optional, Literal"
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
    @staticmethod
    def build(path: str) -> str:
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
    """Generate docstrings for the commands dynamically."""

    @staticmethod
    def get_docstrings(query_mapping: dict) -> dict:
        """Get docstrings from the query mapping."""
        mapping = query_mapping.copy()
        for _, model_mapping in mapping.items():
            for _, query_params_mapping in model_mapping.items():
                query_params_mapping.pop("fields", None)
        return mapping

    @staticmethod
    def clean_provider_docstring(
        section_name: Literal["QueryParams", "Data"], docstring: str, model_name: str
    ) -> str:
        """Clean the provider docstring from standard fields."""
        provider_interface = get_provider_interface()
        if section_name == "QueryParams":
            standard_fields = provider_interface.params[model_name][
                "standard"
            ].__dataclass_fields__.keys()
        elif section_name == "Data":
            standard_fields = provider_interface.data[model_name][
                "standard"
            ].__dataclass_fields__.keys()
        else:
            return docstring

        doc_lines = docstring.split("\n")
        cleaned_lines = []
        skip_lines = False

        for line in doc_lines:
            stripped_line = line.strip()
            parameter_word = stripped_line.split(" : ")[0]

            if parameter_word in standard_fields:
                skip_lines = True
            elif ":" in stripped_line and parameter_word not in standard_fields:
                skip_lines = False

            if not skip_lines:
                cleaned_lines.append(line)

        for i, line in enumerate(cleaned_lines):
            try:
                if line == "---------" and cleaned_lines[i + 1] == "    ":
                    cleaned_lines[i] = "---------"
                    cleaned_lines[i + 1] = "All fields are standardized.\n"
                    break
            except IndexError:
                cleaned_lines.append("All fields are standardized.\n")

        return "\n".join(cleaned_lines)

    @classmethod
    def generate_provider_docstrings(
        cls, docstring: str, docstring_mapping: dict, model_name: str
    ) -> str:
        """Generate the docstring for the provider."""
        for provider, model_mapping in docstring_mapping.items():
            docstring += f"\n{provider}"
            docstring += f"\n{'=' * len(provider)}"
            for section_name, section_docstring in model_mapping.items():
                missing_doc = "\nReturns\n-------\nDocumentation not available.\n\n"
                section_docstring = (
                    section_docstring["docstring"]
                    if section_docstring["docstring"]
                    else missing_doc
                )

                # clean the docstring from its original indentation
                if missing_doc != section_docstring:
                    section_docstring = "\n".join(
                        line[4:] for line in section_docstring.split("\n")[1:]
                    )
                    section_docstring = "\n".join(
                        f"{line}" for line in section_docstring.split("\n")
                    )

                    if provider != "Standard":
                        section_docstring = cls.clean_provider_docstring(
                            section_name,
                            docstring=section_docstring,
                            model_name=model_name,
                        )

                docstring += f"\n{section_docstring}"

        return docstring

    @classmethod
    def generate_command_docstring(cls, func: Callable, model_name: str) -> Callable:
        """Generate the docstring for the command."""
        provider_interface_mapping = get_provider_interface().map
        query_mapping = provider_interface_mapping.get(model_name, None)
        if query_mapping:
            docstring_mapping = cls.get_docstrings(query_mapping)

            docstring = func.__doc__ or ""

            available_providers = ", ".join(docstring_mapping.keys())
            available_providers = available_providers.replace("openbb, ", "")
            available_providers = available_providers.replace("openbb", "")

            docstring += f"\n\nAvailable providers: {available_providers}\n"

            docstring_mapping_ordered = {
                "Standard": docstring_mapping.pop("openbb", None),  # type: ignore
                **docstring_mapping,
            }

            docstring = cls.generate_provider_docstrings(
                docstring, docstring_mapping_ordered, model_name
            )

            func.__doc__ = docstring
        return func


class MethodDefinition:
    @staticmethod
    def build_class_loader_method(path: str) -> str:
        module_name = PathHandler.build_module_name(path=path)
        class_name = PathHandler.build_module_class(path=path)
        function_name = path.rsplit("/", maxsplit=1)[-1].strip("/")

        code = "\n    @property\n"
        code += f'    def {function_name}(self):  # route = "{path}"\n'
        code += f"        from openbb_core.app.static.package import {module_name}\n"
        code += f"        return {module_name}.{class_name}(command_runner_session=self._command_runner_session)\n"

        return code

    @staticmethod
    def get_type(field: Any) -> type:
        field_type = getattr(field, "type", Parameter.empty)
        if isclass(field_type):
            name = field_type.__name__
            if name.startswith("Constrained") and name.endswith("Value"):
                name = name[11:-5].lower()
                return getattr(builtins, name, field_type)
            return field_type
        return field_type

    @staticmethod
    def get_default(field: Any):
        field_default = getattr(field, "default", None)
        if field_default is None or field_default is MISSING:
            return Parameter.empty

        default_default = getattr(field_default, "default", None)
        if default_default is MISSING or default_default is Ellipsis:
            return Parameter.empty

        return default_default

    @staticmethod
    def is_annotated_dc(annotation) -> bool:
        return get_origin(annotation) == Annotated and hasattr(
            annotation.__args__[0], "__dataclass_fields__"
        )

    @staticmethod
    def reorder_params(params: Dict[str, Parameter]) -> OrderedDict[str, Parameter]:
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
        # These are types we want to expand.
        # For example, start_date is always a 'date', but we also accept 'str' as input.
        # Be careful, if the type is not coercible by pydantic to the original type, you
        # will need to had some conversion code to the method implementation.
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
    def build_func_params(parameter_map: Dict[str, Parameter]) -> str:
        od = MethodDefinition.format_params(parameter_map=parameter_map)
        func_params = ", ".join(str(param) for param in od.values())
        func_params = func_params.replace("NoneType", "None")
        func_params = func_params.replace(
            "pandas.core.frame.DataFrame", "pandas.DataFrame"
        )

        return func_params

    @staticmethod
    def build_func_returns(return_type: type) -> str:
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
                # inner_type = getattr(item_type, "__name__", "_name")
                func_returns = (
                    f"CommandOutput[{item_type.__module__}.{item_type.__name__}]"
                )

        return func_returns

    @staticmethod
    def build_command_method_signature(
        func_name: str, parameter_map: Dict[str, Parameter], return_type: type
    ) -> str:
        func_params = MethodDefinition.build_func_params(parameter_map)
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
        code = f'        """{func.__doc__}"""\n' if func.__doc__ else ""

        return code

    @staticmethod
    def build_command_method_implementation(path: str, func: Callable):
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
        )
        code += cls.build_command_method_doc(func=func)
        code += cls.build_command_method_implementation(path=path, func=func)

        return code


class PathHandler:
    @staticmethod
    def build_route_map() -> Dict[str, BaseRoute]:
        router = RouterLoader.from_extensions()
        route_map = {route.path: route for route in router.api_router.routes}  # type: ignore

        return route_map

    @staticmethod
    def build_path_list(route_map: Dict[str, BaseRoute]) -> List[str]:
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
        return route_map.get(path, None)

    @staticmethod
    def get_child_path_list(path: str, path_list: List[str]) -> List[str]:
        direct_children = []
        for p in path_list:
            if p.startswith(path):
                path_reminder = p[len(path) :]  # noqa: E203
                if path_reminder.count("/") == 1:
                    direct_children.append(p)

        return direct_children

    @staticmethod
    def clean_path(path: str) -> str:
        if path.startswith("/"):
            path = path[1:]
        return path.replace("-", "_").replace("/", "_")

    @classmethod
    def build_module_name(cls, path: str) -> str:
        if path == "":
            return "app"
        return cls.clean_path(path=path)

    @classmethod
    def build_module_class(cls, path: str) -> str:
        if path == "":
            return "App"
        return f"CLASS_{cls.clean_path(path=path)}"


class Linters:
    current_folder = str(Path(Path(__file__).parent, "package").absolute())

    @staticmethod
    def print_separator(symbol: str, length: int = 160):
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
        cls.run(linter="black")

    @classmethod
    def ruff(cls):
        cls.run(linter="ruff", flags=["--fix"])

    @classmethod
    def mypy(cls):
        cls.run(linter="mypy", flags=["--ignore-missing-imports"])
