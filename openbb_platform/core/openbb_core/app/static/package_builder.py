"""Package Builder Class."""

# pylint: disable=too-many-lines
import builtins
import inspect
import shutil
import sys
from dataclasses import Field
from inspect import Parameter, _empty, isclass, signature
from json import dumps, load
from pathlib import Path
from typing import (
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    OrderedDict,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_type_hints,
)

import numpy as np
import pandas as pd
from importlib_metadata import entry_points
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from starlette.routing import BaseRoute
from typing_extensions import Annotated, _AnnotatedAlias

from openbb_core.app.extension_loader import ExtensionLoader, OpenBBGroups
from openbb_core.app.model.custom_parameter import (
    OpenBBCustomChoices,
    OpenBBCustomParameter,
)
from openbb_core.app.model.example import Example
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import RouterLoader
from openbb_core.app.static.utils.console import Console
from openbb_core.app.static.utils.linters import Linters
from openbb_core.env import Env
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

TAB = "    "


def create_indent(n: int) -> str:
    """Create n indentation space."""
    return TAB * n


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

    def auto_build(self) -> None:
        """Trigger build if there are differences between built and installed extensions."""
        if Env().AUTO_BUILD:
            add, remove = PackageBuilder._diff(
                self.directory / "assets" / "extension_map.json"
            )
            if add:
                a = ", ".join(add)
                print(f"Extensions to add: {a}")  # noqa: T201

            if remove:
                r = ", ".join(remove)
                print(f"Extensions to remove: {r}")  # noqa: T201

            if add or remove:
                print("\nBuilding...")  # noqa: T201
                self.build()

    def build(
        self,
        modules: Optional[Union[str, List[str]]] = None,
    ) -> None:
        """Build the extensions for the Platform."""
        self.console.log("\nBuilding extensions package...\n")
        self._clean(modules)
        ext_map = self._get_extension_map()
        self._save_extension_map(ext_map)
        self._save_module_map()
        self._save_modules(modules, ext_map)
        self._save_package()
        if self.lint:
            self._run_linters()

    def _clean(self, modules: Optional[Union[str, List[str]]] = None) -> None:
        """Delete the assets and package folder or modules before building."""
        shutil.rmtree(self.directory / "assets", ignore_errors=True)
        if modules:
            for module in modules:
                module_path = self.directory / "package" / f"{module}.py"
                if module_path.exists():
                    module_path.unlink()
        else:
            shutil.rmtree(self.directory / "package", ignore_errors=True)

    def _get_extension_map(self) -> Dict[str, List[str]]:
        """Get map of extensions available at build time."""
        el = ExtensionLoader()
        ext_map: Dict[str, List[str]] = {}

        groups = [
            OpenBBGroups.core.value,
            OpenBBGroups.provider.value,
        ]
        entry_points_ = [
            el.core_entry_points,
            el.provider_entry_points,
        ]

        for group, entry_point in zip(groups, entry_points_):
            ext_map[group] = [
                f"{e.name}@{getattr(e.dist, 'version', '')}" for e in entry_point
            ]
        return ext_map

    def _save_extension_map(self, ext_map: Dict[str, List[str]]) -> None:
        """Save the map of extensions available at build time."""
        code = dumps(obj=dict(sorted(ext_map.items())), indent=4)
        self.console.log("Writing extension map...")
        self._write(code=code, name="extension_map", extension="json", folder="assets")

    def _save_module_map(self):
        """Save the module map."""
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        module_map = {
            PathHandler.build_module_name(path=path): path for path in path_list
        }
        code = dumps(obj=dict(sorted(module_map.items())), indent=4)
        self.console.log("\nWriting module map...")
        self._write(code=code, name="module_map", extension="json", folder="assets")

    def _save_modules(
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
                self._write(code=module_code, name=module_name)

    def _save_package(self):
        """Save the package."""
        self.console.log("\nWriting package __init__...")
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        self._write(code=code, name="__init__")

    def _run_linters(self):
        """Run the linters."""
        self.console.log("\nRunning linters...")
        linters = Linters(self.directory / "package", self.verbose)
        linters.ruff()
        linters.black()

    def _write(
        self, code: str, name: str, extension: str = "py", folder: str = "package"
    ) -> None:
        """Write the module to the package."""
        package_folder = self.directory / folder
        package_path = package_folder / f"{name}.{extension}"

        package_folder.mkdir(exist_ok=True)

        self.console.log(str(package_path))
        with package_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(code.replace("typing.", ""))

    @staticmethod
    def _read(path: Path) -> dict:
        """Get content from folder."""
        try:
            with open(Path(path)) as fp:
                content = load(fp)
        except Exception:
            content = {}

        return content

    @staticmethod
    def _diff(path: Path) -> Tuple[Set[str], Set[str]]:
        """Check differences between built and installed extensions.

        Parameters
        ----------
        path: Path
            The path to the folder where the extension map is stored.

        Returns
        -------
        Tuple[Set[str], Set[str]]
            First element: set of installed extensions that are not in the package.
            Second element: set of extensions in the package that are not installed.
        """
        ext_map = PackageBuilder._read(path)

        add: Set[str] = set()
        remove: Set[str] = set()
        groups = ("openbb_core_extension", "openbb_provider_extension")
        for g in groups:
            built = set(ext_map.get(g, {}))
            installed = set(
                f"{e.name}@{getattr(e.dist, 'version', '')}"
                for e in entry_points(group=g)
            )
            add = add.union(installed - built)
            remove = remove.union(built - installed)

        return add, remove


class ModuleBuilder:
    """Build the module for the Platform."""

    @staticmethod
    def build(path: str, ext_map: Optional[Dict[str, List[str]]] = None) -> str:
        """Build the module."""
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n\n"
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
                if route.deprecated:
                    hint_type_list.append(type(route.summary.metadata))
                function_hint_type_list = cls.get_function_hint_type_list(func=route.endpoint)  # type: ignore
                hint_type_list.extend(function_hint_type_list)

        hint_type_list = list(set(hint_type_list))
        return hint_type_list

    @classmethod
    def build(cls, path: str) -> str:
        """Build the import definition."""
        hint_type_list = cls.get_path_hint_type_list(path=path)
        code = "from openbb_core.app.static.container import Container"
        code += "\nfrom openbb_core.app.model.obbject import OBBject"
        code += "\nfrom openbb_core.app.model.custom_parameter import OpenBBCustomParameter, OpenBBCustomChoices"

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
        code += "\nfrom warnings import warn, simplefilter"
        if sys.version_info < (3, 9):
            code += "\nimport typing_extensions"
        else:
            code += "\nfrom typing_extensions import Annotated, deprecated"
        code += "\nfrom openbb_core.app.utils import df_to_basemodel"
        code += "\nfrom openbb_core.app.static.utils.decorators import exception_handler, validate\n"
        code += "\nfrom openbb_core.app.static.utils.filters import filter_inputs\n"
        code += "\nfrom openbb_core.provider.abstract.data import Data"
        code += "\nfrom openbb_core.app.deprecation import OpenBBDeprecationWarning\n"
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
        code = f"class {class_name}(Container):\n"

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
        for c in child_path_list:
            route = PathHandler.get_route(path=c, route_map=route_map)
            if route:
                doc += f"    {route.name}\n"
                methods += MethodDefinition.build_command_method(
                    path=route.path,
                    func=route.endpoint,
                    model_name=(
                        route.openapi_extra.get("model", None)
                        if route.openapi_extra
                        else None
                    ),
                    examples=(route.openapi_extra.get("examples", []) or []),
                )
            else:
                doc += "    /" if path else "    /"
                doc += c.split("/")[-1] + "\n"
                methods += MethodDefinition.build_class_loader_method(path=c)

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
            doc += "    # fmt: on\n"
        else:
            doc += '    """\n'

        code += doc + "\n"
        code += "    def __repr__(self) -> str:\n"
        code += '        return self.__doc__ or ""\n'
        code += methods

        return code


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
            # Getting json_schema_extra without changing the original dict
            json_schema_extra = getattr(field_default, "json_schema_extra", {}).copy()
            json_schema_extra.pop("choices", None)
            return json_schema_extra
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

        parameter_map.pop("cc", None)
        # we need to add the chart parameter here bc of the docstring generation
        if CHARTING_INSTALLED and path.replace("/", "_")[1:] in Charting.functions():
            parameter_map["chart"] = Parameter(
                name="chart",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[
                    bool,
                    OpenBBCustomParameter(
                        description="Whether to create a chart or not, by default False."
                    ),
                ],
                default=False,
            )

        formatted: Dict[str, Parameter] = {}

        for name, param in parameter_map.items():
            if name == "extra_params":
                formatted[name] = Parameter(name="kwargs", kind=Parameter.VAR_KEYWORD)
            elif name == "provider_choices":
                fields = param.annotation.__args__[0].__dataclass_fields__
                field = fields["provider"]
                type_ = getattr(field, "type")
                args = getattr(type_, "__args__")
                first = args[0] if args else None
                formatted["provider"] = Parameter(
                    name="provider",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[
                        Union[MethodDefinition.get_type(field), None],
                        OpenBBCustomParameter(
                            description=(
                                "The provider to use for the query, by default None.\n"
                                f"    If None, the provider specified in defaults is selected or '{first}' if there is\n"
                                "    no default."
                                ""
                            )
                        ),
                    ],
                    default=None,
                )
            elif MethodDefinition.is_annotated_dc(param.annotation):
                fields = param.annotation.__args__[0].__dataclass_fields__
                for field_name, field in fields.items():
                    type_ = MethodDefinition.get_type(field)
                    default = MethodDefinition.get_default(field)
                    extra = MethodDefinition.get_extra(field)
                    new_type = MethodDefinition.get_expanded_type(
                        field_name, extra, type_
                    )
                    updated_type = type_ if new_type is ... else Union[type_, new_type]

                    formatted[field_name] = Parameter(
                        name=field_name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=updated_type,
                        default=default,
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
                    default=param.default,
                )

        return MethodDefinition.reorder_params(params=formatted)

    @staticmethod
    def add_field_custom_annotations(
        od: OrderedDict[str, Parameter], model_name: Optional[str] = None
    ):
        """Add the field custom description and choices to the param signature as annotations."""
        if model_name:
            available_fields: Dict[str, Field] = (
                ProviderInterface().params[model_name]["standard"].__dataclass_fields__
            )

            for param, value in od.items():
                if param not in available_fields:
                    continue

                field_default = available_fields[param].default

                choices = getattr(field_default, "json_schema_extra", {}).get(
                    "choices", []
                )
                description = getattr(field_default, "description", "")

                if choices:
                    new_value = value.replace(
                        annotation=Annotated[
                            value.annotation,
                            OpenBBCustomParameter(description=description),
                            OpenBBCustomChoices(choices=choices),
                        ],
                    )
                else:
                    new_value = value.replace(
                        annotation=Annotated[
                            value.annotation,
                            OpenBBCustomParameter(description=description),
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
        MethodDefinition.add_field_custom_annotations(
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
        path: str,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
        examples: Optional[List[Example]] = None,
    ):
        """Build the command method docstring."""
        doc = func.__doc__
        doc = DocstringGenerator.generate(
            path=path,
            func=func,
            formatted_params=formatted_params,
            model_name=model_name,
            examples=examples,
        )
        code = (
            f'{create_indent(2)}"""{doc}{create_indent(2)}"""  # noqa: E501\n\n'
            if doc
            else ""
        )

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
                code += "                        provider,\n"
                code += f'                        "{path}",\n'
                code += f"                        {available},\n"
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
    def get_expanded_type(
        cls,
        field_name: str,
        extra: Optional[dict] = None,
        original_type: Optional[type] = None,
    ) -> object:
        """Expand the original field type."""
        if extra and "multiple_items_allowed" in extra:
            if original_type is None:
                raise ValueError(
                    "multiple_items_allowed requires the original type to be specified."
                )
            return List[original_type]  # type: ignore
        return cls.TYPE_EXPANSION.get(field_name, ...)

    @classmethod
    def build_command_method(
        cls,
        path: str,
        func: Callable,
        model_name: Optional[str] = None,
        examples: Optional[List[Example]] = None,
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
            path=path,
            func=func,
            formatted_params=formatted_params,
            model_name=model_name,
            examples=examples,
        )

        code += cls.build_command_method_body(path=path, func=func)

        return code


class DocstringGenerator:
    """Dynamically generate docstrings for the commands."""

    provider_interface = ProviderInterface()

    @staticmethod
    def get_field_type(
        field: FieldInfo, target: Literal["docstring", "website"] = "docstring"
    ) -> str:
        """Get the implicit data type of a defined Pydantic field.

        Args
        ----
            field (FieldInfo): Pydantic field object containing field information.
            target (Literal["docstring", "website"], optional): Target to return type for. Defaults to "docstring".

        Returns
        -------
            str: String representation of the field type.
        """
        is_optional = not field.is_required() if target == "docstring" else False

        try:
            _type = field.annotation

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

        return field_type

    @staticmethod
    def get_OBBject_description(
        results_type: str,
        providers: Optional[str],
    ) -> str:
        """Get the command output description."""
        available_providers = providers or "Optional[str]"

        obbject_description = (
            f"{create_indent(2)}OBBject\n"
            f"{create_indent(3)}results : {results_type}\n"
            f"{create_indent(4)}Serializable results.\n"
            f"{create_indent(3)}provider : {available_providers}\n"
            f"{create_indent(4)}Provider name.\n"
            f"{create_indent(3)}warnings : Optional[List[Warning_]]\n"
            f"{create_indent(4)}List of warnings.\n"
            f"{create_indent(3)}chart : Optional[Chart]\n"
            f"{create_indent(4)}Chart object.\n"
            f"{create_indent(3)}extra : Dict[str, Any]\n"
            f"{create_indent(4)}Extra info.\n"
        )
        obbject_description = obbject_description.replace("NoneType", "None")

        return obbject_description

    @staticmethod
    def build_examples(
        func_path: str,
        param_types: Dict[str, type],
        examples: Optional[List[Example]],
        target: Literal["docstring", "website"] = "docstring",
    ) -> str:
        """Get the example section from the examples."""
        if examples:
            if target == "docstring":
                prompt = ">>> "
                indent = create_indent(2)
            else:
                prompt = "\n```python\n"
                indent = create_indent(0)

            doc = f"\n{indent}Examples\n"
            doc += f"{indent}--------\n"
            doc += f"{indent}{prompt}from openbb import obb\n"

            for e in examples:
                doc += e.to_python(
                    func_path=func_path,
                    param_types=param_types,
                    indentation=indent,
                    prompt=">>> " if target == "docstring" else "",
                )
            return doc if target == "docstring" else doc + "```\n\n"
        return ""

    @classmethod
    def generate_model_docstring(
        cls,
        model_name: str,
        summary: str,
        explicit_params: dict,
        kwarg_params: dict,
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

        def format_description(description: str) -> str:
            """Format description in docstrings."""
            description = description.replace("\n", f"\n{create_indent(2)}")
            return description

        def get_param_info(parameter: Parameter) -> Tuple[str, str]:
            """Get the parameter info."""
            annotation = getattr(parameter, "_annotation", None)
            if isinstance(annotation, _AnnotatedAlias):
                args = getattr(annotation, "__args__", []) if annotation else []
                p_type = args[0] if args else None
            else:
                p_type = annotation
            type_ = (
                getattr(p_type, "__name__", "") if inspect.isclass(p_type) else p_type
            )
            metadata = getattr(annotation, "__metadata__", [])
            description = getattr(metadata[0], "description", "") if metadata else ""
            return type_, description

        docstring = summary.strip("\n").replace("\n    ", f"\n{create_indent(2)}")
        docstring += "\n\n"
        docstring += f"{create_indent(2)}Parameters\n"
        docstring += f"{create_indent(2)}----------\n"

        # Explicit parameters
        for param_name, param in explicit_params.items():
            type_, description = get_param_info(param)
            type_str = format_type(str(type_), char_limit=79)
            docstring += f"{create_indent(2)}{param_name} : {type_str}\n"
            docstring += f"{create_indent(3)}{format_description(description)}\n"

        # Kwargs
        for param_name, param in kwarg_params.items():
            p_type = getattr(param, "type", "")
            type_ = (
                getattr(p_type, "__name__", "") if inspect.isclass(p_type) else p_type
            )

            if "NoneType" in str(type_):
                type_ = f"Optional[{type_}]".replace(", NoneType", "")

            default = getattr(param, "default", "")
            description = getattr(default, "description", "")
            docstring += f"{create_indent(2)}{param_name} : {type_}\n"
            docstring += f"{create_indent(3)}{format_description(description)}\n"

        # Returns
        docstring += "\n"
        docstring += f"{create_indent(2)}Returns\n"
        docstring += f"{create_indent(2)}-------\n"
        providers, _ = get_param_info(explicit_params.get("provider", None))
        docstring += cls.get_OBBject_description(results_type, providers)

        # Schema
        underline = "-" * len(model_name)
        docstring += f"\n{create_indent(2)}{model_name}\n"
        docstring += f"{create_indent(2)}{underline}\n"

        for name, field in returns.items():
            field_type = cls.get_field_type(field)
            description = getattr(field, "description", "")
            docstring += f"{create_indent(2)}{field.alias or name} : {field_type}\n"
            docstring += f"{create_indent(3)}{format_description(description)}\n"
        return docstring

    @classmethod
    def generate(
        cls,
        path: str,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
        examples: Optional[List[Example]] = None,
    ) -> Optional[str]:
        """Generate the docstring for the function."""
        doc = func.__doc__ or ""
        param_types = {}

        # Parameters explicit in the function signature
        explicit_params = dict(formatted_params)
        explicit_params.pop("extra_params", None)
        # Map of parameter names to types
        param_types = {k: v.annotation for k, v in explicit_params.items()}

        if model_name:
            params = cls.provider_interface.params.get(model_name, {})
            return_schema = cls.provider_interface.return_schema.get(model_name, None)
            if params and return_schema:
                # Parameters passed as **kwargs
                kwarg_params = params["extra"].__dataclass_fields__
                param_types.update({k: v.type for k, v in kwarg_params.items()})

                returns = return_schema.model_fields
                results_type = func.__annotations__.get("return", model_name)
                if hasattr(results_type, "results_type_repr"):
                    results_type = results_type.results_type_repr()

                doc = cls.generate_model_docstring(
                    model_name=model_name,
                    summary=func.__doc__ or "",
                    explicit_params=explicit_params,
                    kwarg_params=kwarg_params,
                    returns=returns,
                    results_type=results_type,
                )
        else:
            doc = doc.replace("\n    ", f"\n{create_indent(2)}")

        if doc and examples:
            doc += cls.build_examples(
                path.replace("/", "."),
                param_types,
                examples,
            )

        return doc


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
