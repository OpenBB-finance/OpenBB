"""Package Builder Class."""
# pylint: disable=too-many-lines
import builtins
import inspect
import shutil
import subprocess
import sys
from inspect import Parameter, _empty, isclass, signature
from json import dumps
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    OrderedDict,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import numpy as np
import pandas as pd
from importlib_metadata import entry_points
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from starlette.routing import BaseRoute
from typing_extensions import Annotated, _AnnotatedAlias

from openbb_core.app.charting_service import ChartingService
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap, RouterLoader
from openbb_core.env import Env
from openbb_core.provider.abstract.data import Data

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


class Console:
    """Console to be used by builder and linters."""

    def __init__(self, verbose: bool):
        """Initialize the console."""
        self.verbose = verbose

    def log(self, message: str, **kwargs):
        """Console log method."""
        if self.verbose or Env().DEBUG_MODE:
            print(message, **kwargs)  # noqa: T201


class PackageBuilder:
    """Build the extension package for the Platform."""

    def __init__(
        self, directory: Optional[Path] = None, lint: bool = True, verbose: bool = False
    ) -> None:
        """Initialize the package builder."""
        self.directory = directory or Path(__file__).parent
        self.lint = lint
        self.verbose = verbose
        self.console = Console(verbose)

    def clean_package(self, modules: Optional[Union[str, List[str]]] = None) -> None:
        """Delete the package folder or modules before building."""
        if modules:
            for module in modules:
                module_path = self.directory / "package" / f"{module}.py"
                if module_path.exists():
                    module_path.unlink()
        else:
            shutil.rmtree(self.directory / "package", ignore_errors=True)

    def build(
        self,
        modules: Optional[Union[str, List[str]]] = None,
    ) -> None:
        """Build the extensions for the Platform."""
        self.console.log("\nBuilding extensions package...\n")
        self.clean_package(modules)
        ext_map = self.get_extension_map()
        self.save_extension_map(ext_map)
        self.save_module_map()
        self.save_modules(modules, ext_map)
        self.save_package()
        if self.lint:
            self.run_linters()

    def get_extension_map(self) -> Dict[str, List[str]]:
        """Get map of extensions available at build time."""
        groups = ("openbb_core_extension", "openbb_provider_extension")
        ext_map = {
            g: sorted(
                [
                    f"{e.name}@{getattr(e.dist, 'version', '')}"
                    for e in entry_points(group=g)
                ]
            )
            for g in groups
        }
        return ext_map

    def save_extension_map(self, ext_map: Dict[str, List[str]]) -> None:
        """Save the map of extensions available at build time."""
        code = dumps(obj=dict(sorted(ext_map.items())), indent=4)
        self.console.log("Writing extension map...")
        self.write_to_package(code=code, name="extension_map", extension="json")

    def save_module_map(self):
        """Save the module map."""
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        module_map = {
            PathHandler.build_module_name(path=path): path for path in path_list
        }
        code = dumps(obj=dict(sorted(module_map.items())), indent=4)
        self.console.log("\nWriting module map...")
        self.write_to_package(code=code, name="module_map", extension="json")

    def save_modules(
        self,
        modules: Optional[Union[str, List[str]]] = None,
        ext_map: Optional[Dict[str, List[str]]] = None,
    ):
        """Save the modules."""
        self.console.log("\nWriting modules...")
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)

        if not path_list:
            self.console.log("\nThere is nothing to write.")
            return

        MAX_LEN = max([len(path) for path in path_list if path != "/"])

        if modules:
            path_list = [path for path in path_list if path in modules]

        for path in path_list:
            route = PathHandler.get_route(path=path, route_map=route_map)
            if route is None:
                module_code = ModuleBuilder.build(
                    path=path,
                    ext_map=ext_map,
                )
                module_name = PathHandler.build_module_name(path=path)
                self.console.log(f"({path})", end=" " * (MAX_LEN - len(path)))
                self.write_to_package(code=module_code, name=module_name)

    def save_package(self):
        """Save the package."""
        self.console.log("\nWriting package __init__...")
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        self.write_to_package(code=code, name="__init__")

    def run_linters(self):
        """Run the linters."""
        self.console.log("\nRunning linters...")
        linters = Linters(self.directory / "package", self.verbose)
        linters.ruff()
        linters.black()

    def write_to_package(self, code: str, name: str, extension="py") -> None:
        """Write the module to the package."""
        package_folder = self.directory / "package"
        package_path = package_folder / f"{name}.{extension}"

        package_folder.mkdir(exist_ok=True)

        self.console.log(str(package_path))
        with package_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(code.replace("typing.", ""))


class ModuleBuilder:
    """Build the module for the Platform."""

    @staticmethod
    def build(path: str, ext_map: Optional[Dict[str, List[str]]] = None) -> str:
        """Build the module."""
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        code += ImportDefinition.build(path=path)
        code += ClassDefinition.build(path, ext_map)

        return code


class ImportDefinition:
    """Build the import definition for the Platform."""

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
        code += "\nimport openbb_core.provider"
        code += "\nimport pandas"
        code += "\nimport numpy"
        code += "\nimport datetime"
        code += "\nimport pydantic"
        code += "\nfrom pydantic import BaseModel"
        code += "\nfrom inspect import Parameter"
        code += "\nimport typing"
        code += "\nfrom typing import List, Dict, Union, Optional, Literal"
        code += "\nfrom annotated_types import Ge, Le, Gt, Lt"
        if sys.version_info < (3, 9):
            code += "\nimport typing_extensions"
        else:
            code += "\nfrom typing_extensions import Annotated"
        code += "\nfrom openbb_core.app.utils import df_to_basemodel"
        code += "\nfrom openbb_core.app.static.decorators import validate\n"
        code += "\nfrom openbb_core.app.static.filters import filter_inputs\n"
        code += "\nfrom openbb_core.provider.abstract.data import Data"
        if path.startswith("/quantitative"):
            code += "\nfrom openbb_quantitative.models import "
            code += "(CAPMModel,NormalityModel,OmegaModel,SummaryModel,UnitRootModel)"

        module_list = [hint_type.__module__ for hint_type in hint_type_list]
        module_list = list(set(module_list))
        module_list.sort()

        code += "\n"
        for module in module_list:
            code += f"import {module}\n"

        return code


class ClassDefinition:
    """Build the class definition for the Platform."""

    @staticmethod
    def build(path: str, ext_map: Optional[Dict[str, List[str]]] = None) -> str:
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

        doc = f'    """{path}\n' if path else '    # fmt: off\n    """\nRouters:\n'
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
                doc += "/" if path else "    /"
                doc += child_path.split("/")[-1] + "\n"
                methods += MethodDefinition.build_class_loader_method(path=child_path)

        if not path:
            if ext_map:
                doc += "\n"
                doc += "Extensions:\n"
                doc += "\n".join(
                    [f"    - {ext}" for ext in ext_map.get("openbb_core_extension", [])]
                )
                doc += "\n\n"
                doc += "\n".join(
                    [
                        f"    - {ext}"
                        for ext in ext_map.get("openbb_provider_extension", [])
                    ]
                )
            doc += '    """\n'
            doc += "# fmt: on\n"
        else:
            doc += '    """\n'

        code += doc
        code += "    def __repr__(self) -> str:\n"
        code += '        return self.__doc__ or ""\n'
        code += methods

        return code


class DocstringGenerator:
    """Dynamically generate docstrings for the commands."""

    provider_interface = ProviderInterface()

    @staticmethod
    def get_OBBject_description(results_type: str, providers: Optional[str]) -> str:
        """Get the command output description."""
        available_providers = providers or "Optional[PROVIDERS]"

        obbject_description = (
            "OBBject\n"
            f"    results : {results_type}\n"
            "        Serializable results.\n"
            f"    provider : {available_providers}\n"
            "        Provider name.\n"
            "    warnings : Optional[List[Warning_]]\n"
            "        List of warnings.\n"
            "    chart : Optional[Chart]\n"
            "        Chart object.\n"
            "    extra: Dict[str, Any]\n"
            "        Extra info.\n"
        )
        obbject_description = obbject_description.replace("NoneType", "None")

        return obbject_description

    @staticmethod
    def get_model_standard_params(param_fields: Dict[str, FieldInfo]) -> Dict[str, Any]:
        """Get the test params for the fetcher based on the required standard params."""
        test_params: Dict[str, Any] = {}
        for field_name, field in param_fields.items():
            if field.default and field.default is not PydanticUndefined:
                test_params[field_name] = field.default
            elif field.default and field.default is PydanticUndefined:
                example_dict = {
                    "symbol": "AAPL",
                    "symbols": "AAPL,MSFT",
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-06",
                    "country": "Portugal",
                    "date": "2023-01-01",
                    "countries": ["portugal", "spain"],
                }
                if field_name in example_dict:
                    test_params[field_name] = example_dict[field_name]
                elif field.annotation == str:
                    test_params[field_name] = "TEST_STRING"
                elif field.annotation == int:
                    test_params[field_name] = 1
                elif field.annotation == float:
                    test_params[field_name] = 1.0
                elif field.annotation == bool:
                    test_params[field_name] = True
                elif get_origin(field.annotation) is Literal:  # type: ignore
                    option = field.annotation.__args__[0]  # type: ignore
                    if isinstance(option, str):
                        test_params[field_name] = f'"{option}"'
                    else:
                        test_params[field_name] = option

        return test_params

    @staticmethod
    def get_full_command_name(route: str) -> str:
        """Get the full command name."""
        cmd_parts = route.split("/")
        del cmd_parts[0]

        menu = cmd_parts[0]
        command = cmd_parts[-1]
        sub_menus = cmd_parts[1:-1]

        sub_menu_str_cmd = f".{'.'.join(sub_menus)}" if sub_menus else ""

        full_command = f"{menu}{sub_menu_str_cmd}.{command}"

        return full_command

    @classmethod
    def generate_example(
        cls,
        model_name: str,
        standard_params: Dict[str, FieldInfo],
    ) -> str:
        """Generate the example for the command."""
        # find the model router here
        cm = CommandMap()
        commands_model = cm.commands_model
        route = [k for k, v in commands_model.items() if v == model_name]

        if not route:
            return ""

        full_command_name = cls.get_full_command_name(route=route[0])
        example_params = cls.get_model_standard_params(param_fields=standard_params)

        # Edge cases (might find more)
        if "crypto" in route[0] and "symbol" in example_params:
            example_params["symbol"] = "BTCUSD"
        elif "currency" in route[0] and "symbol" in example_params:
            example_params["symbol"] = "EURUSD"
        elif (
            "index" in route[0]
            and "european" not in route[0]
            and "symbol" in example_params
        ):
            example_params["symbol"] = "SPX"
        elif (
            "index" in route[0]
            and "european" in route[0]
            and "symbol" in example_params
        ):
            example_params["symbol"] = "BUKBUS"
        elif (
            "futures" in route[0] and "curve" in route[0] and "symbol" in example_params
        ):
            example_params["symbol"] = "VX"
        elif "futures" in route[0] and "symbol" in example_params:
            example_params["symbol"] = "ES"

        example = "\nExample\n-------\n"
        example += ">>> from openbb import obb\n"
        example += f">>> obb.{full_command_name}("
        for param_name, param_value in example_params.items():
            if isinstance(param_value, str):
                param_value = f'"{param_value}"'  # noqa: PLW2901
            example += f"{param_name}={param_value}, "
        if example_params:
            example = example[:-2] + ")\n\n"
        else:
            example += ")\n\n"

        return example

    @classmethod
    def generate_model_docstring(
        cls,
        model_name: str,
        summary: str,
        explicit_params: dict,
        params: dict,
        returns: Dict[str, FieldInfo],
        results_type: str,
    ) -> str:
        """Create the docstring for model."""

        def format_type(type_: str, char_limit: Optional[int] = None) -> str:
            """Format type in docstrings."""
            type_str = str(type_)
            type_str = type_str.replace("NoneType", "None")
            if char_limit:
                type_str = type_str[:char_limit] + (
                    "..." if len(str(type_str)) > char_limit else ""
                )
            return type_str

        standard_dict = params["standard"].__dataclass_fields__
        extra_dict = params["extra"].__dataclass_fields__

        obb_query_fields: Dict[str, FieldInfo] = cls.provider_interface.map[model_name][
            "openbb"
        ]["QueryParams"]["fields"]

        example_docstring = cls.generate_example(
            model_name=model_name, standard_params=obb_query_fields
        )

        docstring = summary
        docstring += "\n"
        docstring += "\nParameters\n----------\n"

        # Explicit parameters
        for param_name, param in explicit_params.items():
            if param_name in standard_dict:
                # pylint: disable=W0212
                p_type = obb_query_fields[param_name].annotation
                type_ = p_type.__name__ if inspect.isclass(p_type) else p_type
                description = obb_query_fields[param_name].description
            elif param_name == "provider":
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

            type_str = format_type(type_, char_limit=79)  # type: ignore
            docstring += f"{param_name} : {type_str}\n"
            docstring += f"    {description}\n"

        # Kwargs
        for param_name, param in extra_dict.items():
            p_type = param.type
            type_ = p_type.__name__ if inspect.isclass(p_type) else p_type

            if "NoneType" in str(type_):
                type_ = f"Optional[{type_}]".replace(", NoneType", "")

            docstring += f"{param_name} : {type_}\n"
            docstring += f"    {param.default.description}\n"

        # Returns
        docstring += "\nReturns\n-------\n"
        provider_param = explicit_params.get("provider", None)
        available_providers = getattr(provider_param, "_annotation", None)

        docstring += cls.get_OBBject_description(results_type, available_providers)

        # Schema
        underline = "-" * len(model_name)
        docstring += f"\n{model_name}\n{underline}\n"

        for name, field in returns.items():
            try:
                _type = field.annotation
                is_optional = not field.is_required()
                if "BeforeValidator" in str(_type):
                    _type = "Optional[int]" if is_optional else "int"  # type: ignore

                field_type = (
                    str(_type)
                    .replace("<class '", "")
                    .replace("'>", "")
                    .replace("typing.", "")
                    .replace("pydantic.types.", "")
                    .replace("datetime.datetime", "datetime")
                    .replace("datetime.date", "date")
                    .replace("NoneType", "None")
                    .replace(", None", "")
                )
                field_type = (
                    f"Optional[{field_type}]"
                    if is_optional and "Optional" not in str(_type)
                    else field_type
                )
            except TypeError:
                # Fallback to the annotation if the repr fails
                field_type = field.annotation  # type: ignore

            docstring += f"{field.alias or name} : {field_type}\n"
            docstring += f"    {field.description}\n"

        docstring += example_docstring
        return docstring

    @classmethod
    def generate(
        cls,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
    ) -> Optional[str]:
        """Generate the docstring for the function."""
        doc = func.__doc__
        if model_name:
            params = cls.provider_interface.params.get(model_name, None)
            return_schema = cls.provider_interface.return_schema.get(model_name, None)
            if params and return_schema:
                explicit_dict = dict(formatted_params)
                explicit_dict.pop("extra_params", None)

                returns = return_schema.model_fields
                results_type = func.__annotations__.get("return", model_name)
                if hasattr(results_type, "results_type_repr"):
                    results_type = results_type.results_type_repr()

                return cls.generate_model_docstring(
                    model_name=model_name,
                    summary=func.__doc__ or "",
                    explicit_params=explicit_dict,
                    params=params,
                    returns=returns,
                    results_type=results_type,
                )
            return doc
        return doc


class MethodDefinition:
    """Build the method definition for the Platform."""

    @staticmethod
    def build_class_loader_method(path: str) -> str:
        """Build the class loader method."""
        module_name = PathHandler.build_module_name(path=path)
        class_name = PathHandler.build_module_class(path=path)
        function_name = path.rsplit("/", maxsplit=1)[-1].strip("/")

        code = "\n    @property\n"
        code += f'    def {function_name}(self):  # route = "{path}"\n'
        code += f"        from . import {module_name}\n"
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
        # These are types we want to expand.
        # For example, start_date is always a 'date', but we also accept 'str' as input.
        # Be careful, if the type is not coercible by pydantic to the original type, you
        # will need to add some conversion code in the input filter.
        TYPE_EXPANSION = {
            "symbol": List[str],
            "data": DataProcessingSupportedTypes,
            "start_date": str,
            "end_date": str,
            "provider": None,
        }

        DEFAULT_REPLACEMENT = {
            "provider": None,
        }

        parameter_map.pop("cc", None)
        # we need to add the chart parameter here bc of the docstring generation
        if (
            path.replace("/", "_")[1:]
            in ChartingService.get_implemented_charting_functions()
        ):
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

                    new_type = TYPE_EXPANSION.get(field_name, ...)
                    updated_type = type_ if new_type is ... else Union[type_, new_type]

                    formatted[field_name] = Parameter(
                        name=field_name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=updated_type,
                        default=DEFAULT_REPLACEMENT.get(field_name, default),
                    )
            else:
                new_type = TYPE_EXPANSION.get(name, ...)

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
            available_fields: Dict[str, FieldInfo] = ProviderInterface().map[
                model_name
            ]["openbb"]["QueryParams"]["fields"]

            for param, value in od.items():
                if param not in available_fields:
                    continue

                field = available_fields[param]

                new_value = value.replace(
                    annotation=Annotated[
                        value.annotation,
                        OpenBBCustomParameter(description=field.description),
                    ],
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
        func_params = func_params.replace(
            "openbb_core.provider.abstract.data.Data", "Data"
        )

        return func_params

    @staticmethod
    def build_func_returns(return_type: type, model_name: Optional[str] = None) -> str:
        """Build the function returns."""
        if return_type == _empty:
            func_returns = "None"
        elif return_type.__module__ == "builtins":
            func_returns = return_type.__name__
        else:
            item_type = get_args(get_type_hints(return_type)["results"])[0]
            if item_type.__module__ == "builtins":
                func_returns = f"OBBject[{item_type.__name__}]"
            else:
                func_returns = return_type.__qualname__
                if model_name:
                    func_returns = func_returns.replace(model_name, "Data")

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
        func_returns = MethodDefinition.build_func_returns(return_type, model_name)

        args = (
            "(config=dict(arbitrary_types_allowed=True))"
            if "pandas.DataFrame" in func_params
            else ""
        )
        code = f"\n    @validate{args}"
        code += f"\n    def {func_name}(self, {func_params}) -> {func_returns}:\n"

        return code

    @staticmethod
    def build_command_method_doc(
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
    ):
        """Build the command method docstring."""
        doc = func.__doc__
        if model_name:
            doc = DocstringGenerator.generate(
                func=func, formatted_params=formatted_params, model_name=model_name
            )
        code = f'        """{doc}"""  # noqa: E501\n\n' if doc else ""

        return code

    @staticmethod
    def build_command_method_implementation(path: str, func: Callable):
        """Build the command method implementation."""
        sig = signature(func)
        parameter_map = dict(sig.parameters)
        parameter_map.pop("cc", None)

        if (
            path.replace("/", "_")[1:]
            in ChartingService.get_implemented_charting_functions()
        ):
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

        if MethodDefinition.is_data_processing_function(path):
            code += "            data_processing=True,\n"

        code += "        )\n\n"
        code += "        return self._run(\n"
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

        formatted_params = cls.format_params(path=path, parameter_map=parameter_map)

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
    """Handle the paths for the Platform."""

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
        if not path:
            return "__extensions__"
        return cls.clean_path(path=path)

    @classmethod
    def build_module_class(cls, path: str) -> str:
        """Build the module class."""
        if not path:
            return "Extensions"
        return f"ROUTER_{cls.clean_path(path=path)}"


class Linters:
    """Run the linters for the Platform."""

    def __init__(self, directory: Path, verbose: bool = False) -> None:
        """Initialize the linters."""
        self.directory = directory
        self.verbose = verbose
        self.console = Console(verbose)

    def print_separator(self, symbol: str, length: int = 160):
        """Print a separator."""
        self.console.log(symbol * length)

    def run(
        self,
        linter: Literal["black", "ruff"],
        flags: Optional[List[str]] = None,
    ):
        """Run linter with flags."""
        if shutil.which(linter):
            self.console.log(f"\n* {linter}")
            self.print_separator("^")

            command = [linter] + list(self.directory.glob("*.py"))
            if flags:
                command.extend(flags)  # type: ignore
            subprocess.run(command, check=False)  # noqa: S603

            self.print_separator("-")
        else:
            self.console.log(f"\n* {linter} not found")

    def black(self):
        """Run black."""
        flags = []
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--quiet")
        self.run(linter="black", flags=flags)

    def ruff(self):
        """Run ruff."""
        flags = ["--fix"]
        if not self.verbose and not Env().DEBUG_MODE:
            flags.append("--silent")
        self.run(linter="ruff", flags=flags)
