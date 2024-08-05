"""Package Builder Class."""

# pylint: disable=too-many-lines
import builtins
import inspect
import re
import shutil
import sys
from dataclasses import Field as DCField
from functools import partial
from inspect import Parameter, _empty, isclass, signature
from json import dumps, load
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
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
    get_origin,
    get_type_hints,
)

from importlib_metadata import entry_points
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from starlette.routing import BaseRoute
from typing_extensions import Annotated, _AnnotatedAlias

from openbb_core.app.extension_loader import ExtensionLoader, OpenBBGroups
from openbb_core.app.model.example import Example
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import RouterLoader
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.static.utils.console import Console
from openbb_core.app.static.utils.linters import Linters
from openbb_core.app.version import CORE_VERSION, VERSION
from openbb_core.env import Env

if TYPE_CHECKING:
    # pylint: disable=import-outside-toplevel
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from openbb_core.provider.abstract.data import Data  # noqa

try:
    from openbb_charting import Charting  # type: ignore

    CHARTING_INSTALLED = True
except ImportError:
    CHARTING_INSTALLED = False

DataProcessingSupportedTypes = TypeVar(
    "DataProcessingSupportedTypes",
    list,
    dict,
    "DataFrame",
    List["DataFrame"],
    "Series",
    List["Series"],
    "ndarray",
    "Data",
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
        self.route_map = PathHandler.build_route_map()
        self.path_list = PathHandler.build_path_list(route_map=self.route_map)

    def auto_build(self) -> None:
        """Trigger build if there are differences between built and installed extensions."""
        if Env().AUTO_BUILD:
            reference = PackageBuilder._read(
                self.directory / "assets" / "reference.json"
            )
            ext_map = reference.get("info", {}).get("extensions", {})
            add, remove = PackageBuilder._diff(ext_map)
            if add:
                a = ", ".join(sorted(add))
                print(f"Extensions to add: {a}")  # noqa: T201

            if remove:
                r = ", ".join(sorted(remove))
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
        self._save_modules(modules, ext_map)
        self._save_package()
        self._save_reference_file(ext_map)
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
        og = OpenBBGroups.groups()
        ext_map: Dict[str, List[str]] = {}

        for group, entry_point in zip(og, el.entry_points):
            ext_map[group] = [
                f"{e.name}@{getattr(e.dist, 'version', '')}" for e in entry_point
            ]
        return ext_map

    def _save_modules(
        self,
        modules: Optional[Union[str, List[str]]] = None,
        ext_map: Optional[Dict[str, List[str]]] = None,
    ):
        """Save the modules."""
        self.console.log("\nWriting modules...")

        if not self.path_list:
            self.console.log("\nThere is nothing to write.")
            return

        MAX_LEN = max([len(path) for path in self.path_list if path != "/"])

        _path_list = (
            [path for path in self.path_list if path in modules]
            if modules
            else self.path_list
        )

        for path in _path_list:
            route = PathHandler.get_route(path, self.route_map)
            if route is None:
                code = ModuleBuilder.build(path, ext_map)
                name = PathHandler.build_module_name(path)
                self.console.log(f"({path})", end=" " * (MAX_LEN - len(path)))
                self._write(code, name)

    def _save_package(self):
        """Save the package."""
        self.console.log("\nWriting package __init__...")
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n"
        self._write(code=code, name="__init__")

    def _save_reference_file(self, ext_map: Optional[Dict[str, List[str]]] = None):
        """Save the reference.json file."""
        self.console.log("\nWriting reference file...")
        code = dumps(
            obj={
                "openbb": VERSION.replace("dev", ""),
                "info": {
                    "title": "OpenBB Platform (Python)",
                    "description": "Investment research for everyone, anywhere.",
                    "core": CORE_VERSION.replace("dev", ""),
                    "extensions": ext_map,
                },
                "paths": ReferenceGenerator.get_paths(self.route_map),
                "routers": ReferenceGenerator.get_routers(self.route_map),
            },
            indent=4,
        )
        self._write(code=code, name="reference", extension="json", folder="assets")

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
    def _diff(ext_map: Dict[str, List[str]]) -> Tuple[Set[str], Set[str]]:
        """Check differences between built and installed extensions.

        Parameters
        ----------
        ext_map: Dict[str, List[str]]
            Dictionary containing the extensions.
            Example:
                {
                    "openbb_core_extension": [
                        "commodity@1.0.1",
                        ...
                    ],
                    "openbb_provider_extension": [
                        "benzinga@1.1.3",
                        ...
                    ],
                    "openbb_obbject_extension": [
                        "openbb_charting@1.0.0",
                        ...
                    ]
                }

        Returns
        -------
        Tuple[Set[str], Set[str]]
            First element: set of installed extensions that are not in the package.
            Second element: set of extensions in the package that are not installed.
        """
        add: Set[str] = set()
        remove: Set[str] = set()
        groups = OpenBBGroups.groups()

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
        code += ImportDefinition.build(path)
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
            if not issubclass(return_type, OBBject):
                raise ValueError("Return type must be an OBBject.")
            hint_type = get_args(get_type_hints(return_type)["results"])[0]
            hint_type_list.append(hint_type)

        hint_type_list = cls.filter_hint_type_list(hint_type_list)

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

        # These imports were not detected before build, so we add them manually and
        # ruff --fix the resulting code to remove unused imports.
        # TODO: Find a better way to handle this. This is a temporary solution.
        code += "\nimport openbb_core.provider"
        code += "\nfrom openbb_core.provider.abstract.data import Data"
        code += "\nimport pandas"
        code += "\nfrom pandas import DataFrame, Series"
        code += "\nimport numpy"
        code += "\nfrom numpy import ndarray"
        code += "\nimport datetime"
        code += "\nfrom datetime import date"
        code += "\nimport pydantic"
        code += "\nfrom pydantic import BaseModel"
        code += "\nfrom inspect import Parameter"
        code += "\nimport typing"
        code += "\nfrom typing import TYPE_CHECKING, ForwardRef, List, Dict, Union, Optional, Literal, Any"
        code += "\nfrom annotated_types import Ge, Le, Gt, Lt"
        code += "\nfrom warnings import warn, simplefilter"
        if sys.version_info < (3, 9):
            code += "\nimport typing_extensions"
        else:
            code += "\nfrom typing_extensions import Annotated, deprecated"
        # code += "\nfrom openbb_core.app.utils import df_to_basemodel"
        code += "\nfrom openbb_core.app.static.utils.decorators import exception_handler, validate\n"
        code += "\nfrom openbb_core.app.static.utils.filters import filter_inputs\n"
        code += "\nfrom openbb_core.app.deprecation import OpenBBDeprecationWarning\n"
        code += "\nfrom openbb_core.app.model.field import OpenBBField"
        # if path.startswith("/quantitative"):
        #    code += "\nfrom openbb_quantitative.models import "
        #    code += "(CAPMModel,NormalityModel,OmegaModel,SummaryModel,UnitRootModel)"
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
        path_list = PathHandler.build_path_list(route_map)
        child_path_list = sorted(
            PathHandler.get_child_path_list(
                path=path,
                path_list=path_list,
            )
        )

        doc = f'    """{path}\n' if path else '    # fmt: off\n    """\nRouters:\n'
        methods = ""
        for c in child_path_list:
            route = PathHandler.get_route(c, route_map)
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
    def reorder_params(
        params: Dict[str, Parameter], var_kw: Optional[List[str]] = None
    ) -> "OrderedDict[str, Parameter]":
        """Reorder the params and make sure VAR_KEYWORD come after 'provider."""
        formatted_keys = list(params.keys())
        for k in ["provider"] + (var_kw or []):
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
                    OpenBBField(
                        description="Whether to create a chart or not, by default False.",
                    ),
                ],
                default=False,
            )

        formatted: Dict[str, Parameter] = {}
        var_kw = []
        for name, param in parameter_map.items():
            if name == "extra_params":
                formatted[name] = Parameter(name="kwargs", kind=Parameter.VAR_KEYWORD)
                var_kw.append(name)
            elif name == "provider_choices":
                fields = param.annotation.__args__[0].__dataclass_fields__
                field = fields["provider"]
                type_ = getattr(field, "type")
                default_priority = getattr(type_, "__args__")
                formatted["provider"] = Parameter(
                    name="provider",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Annotated[
                        Optional[MethodDefinition.get_type(field)],
                        OpenBBField(
                            description=(
                                "The provider to use, by default None. "
                                "If None, the priority list configured in the settings is used. "
                                f"Default priority: {', '.join(default_priority)}."
                            ),
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
                    types = new_type.__constraints__ + (param.annotation,)  # type: ignore
                    updated_type = Union[types]  # type: ignore
                else:
                    updated_type = (
                        param.annotation
                        if new_type is ...
                        else Union[param.annotation, new_type]
                    )

                formatted[name] = Parameter(
                    name=name,
                    kind=param.kind,
                    annotation=updated_type,
                    default=param.default,
                )
                if param.kind == Parameter.VAR_KEYWORD:
                    var_kw.append(name)

        return MethodDefinition.reorder_params(params=formatted, var_kw=var_kw)

    @staticmethod
    def add_field_custom_annotations(
        od: OrderedDict[str, Parameter], model_name: Optional[str] = None
    ):
        """Add the field custom description and choices to the param signature as annotations."""
        if model_name:
            available_fields: Dict[str, DCField] = (
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

                PartialParameter = partial(
                    OpenBBField,
                    description=description,
                )

                new_value = value.replace(
                    annotation=Annotated[
                        value.annotation,
                        (
                            PartialParameter(choices=choices)
                            if choices
                            else PartialParameter()
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
        func_params = func_params.replace("ForwardRef('Data')", "Data")
        func_params = func_params.replace("ForwardRef('DataFrame')", "DataFrame")
        func_params = func_params.replace("ForwardRef('Series')", "Series")
        func_params = func_params.replace("ForwardRef('ndarray')", "ndarray")
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
            if "DataFrame" in func_params
            or "Series" in func_params
            or "ndarray" in func_params
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

        info = {}

        code += "        return self._run(\n"
        code += f"""            "{path}",\n"""
        code += "            **filter_inputs(\n"
        for name, param in parameter_map.items():
            if name == "extra_params":
                fields = param.annotation.__args__[0].__dataclass_fields__
                values = {k: k for k in fields}
                for k in values:
                    if extra := MethodDefinition.get_extra(fields[k]):
                        info[k] = extra
                code += f"                {name}=kwargs,\n"
            elif name == "provider_choices":
                field = param.annotation.__args__[0].__dataclass_fields__["provider"]
                available = field.type.__args__
                cmd = path.strip("/").replace("/", ".")
                code += "                provider_choices={\n"
                code += '                    "provider": self._get_provider(\n'
                code += "                        provider,\n"
                code += f'                        "{cmd}",\n'
                code += f"                        {available},\n"
                code += "                    )\n"
                code += "                },\n"
            elif MethodDefinition.is_annotated_dc(param.annotation):
                fields = param.annotation.__args__[0].__dataclass_fields__
                values = {k: k for k in fields}
                code += f"                {name}={{\n"
                for k, v in values.items():
                    code += f'                    "{k}": {v},\n'
                    if extra := MethodDefinition.get_extra(fields[k]):
                        info[k] = extra
                code += "                },\n"
            else:
                code += f"                {name}={name},\n"

        if info:
            code += f"                info={info},\n"

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
        if extra and any(
            (
                v.get("multiple_items_allowed")
                if isinstance(v, dict)
                # For backwards compatibility, before this was a list
                else "multiple_items_allowed" in v
            )
            for v in extra.values()
        ):
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
        field_type: Any,
        is_required: bool,
        target: Literal["docstring", "website"] = "docstring",
    ) -> str:
        """Get the implicit data type of a defined Pydantic field.

        Parameters
        ----------
        field_type : Any
            Typing object containing the field type.
        is_required : bool
            Flag to indicate if the field is required.
        target : Literal["docstring", "website"]
            Target to return type for. Defaults to "docstring".

        Returns
        -------
        str
            String representation of the field type.
        """
        is_optional = not is_required

        try:
            _type = field_type

            if "BeforeValidator" in str(_type):
                _type = "Optional[int]" if is_optional else "int"  # type: ignore

            _type = (
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

            if "openbb_" in str(_type):
                _type = (
                    str(_type).split(".", maxsplit=1)[0].split("openbb_")[0]
                    + str(_type).rsplit(".", maxsplit=1)[-1]
                )

            _type = (
                f"Optional[{_type}]"
                if is_optional and "Optional" not in str(_type)
                else _type
            )

            if target == "website":
                _type = re.sub(r"Optional\[(.*)\]", r"\1", _type)

            return _type

        except TypeError:
            # Fallback to the annotation if the repr fails
            return field_type  # type: ignore

    @staticmethod
    def get_OBBject_description(
        results_type: str,
        providers: Optional[str],
    ) -> str:
        """Get the command output description."""
        available_providers = providers or "Optional[str]"
        indent = 2

        obbject_description = (
            f"{create_indent(indent)}OBBject\n"
            f"{create_indent(indent+1)}results : {results_type}\n"
            f"{create_indent(indent+2)}Serializable results.\n"
            f"{create_indent(indent+1)}provider : {available_providers}\n"
            f"{create_indent(indent+2)}Provider name.\n"
            f"{create_indent(indent+1)}warnings : Optional[List[Warning_]]\n"
            f"{create_indent(indent+2)}List of warnings.\n"
            f"{create_indent(indent+1)}chart : Optional[Chart]\n"
            f"{create_indent(indent+2)}Chart object.\n"
            f"{create_indent(indent+1)}extra : Dict[str, Any]\n"
            f"{create_indent(indent+2)}Extra info.\n"
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
        explicit_params: Dict[str, Parameter],
        kwarg_params: dict,
        returns: Dict[str, FieldInfo],
        results_type: str,
        sections: List[str],
    ) -> str:
        """Create the docstring for model."""

        def format_type(type_: str, char_limit: Optional[int] = None) -> str:
            """Format type in docstrings."""
            type_str = str(type_)
            type_str = (
                type_str.replace("<class '", "")
                .replace("'>", "")
                .replace("typing.", "")
                .replace("pydantic.types.", "")
                .replace("NoneType", "None")
                .replace("datetime.date", "date")
                .replace("datetime.datetime", "datetime")
            )
            if char_limit:
                type_str = type_str[:char_limit] + (
                    "..." if len(str(type_str)) > char_limit else ""
                )
            return type_str

        def format_description(description: str) -> str:
            """Format description in docstrings."""
            description = description.replace("\n", f"\n{create_indent(2)}")
            return description

        def get_param_info(parameter: Optional[Parameter]) -> Tuple[str, str]:
            """Get the parameter info."""
            if not parameter:
                return "", ""
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

        # Description summary
        if "description" in sections:
            docstring = summary.strip("\n").replace("\n    ", f"\n{create_indent(2)}")
            docstring += "\n\n"
        if "parameters" in sections:
            docstring += f"{create_indent(2)}Parameters\n"
            docstring += f"{create_indent(2)}----------\n"

            # Explicit parameters
            for param_name, param in explicit_params.items():
                type_, description = get_param_info(param)
                type_str = format_type(str(type_), char_limit=86)
                docstring += f"{create_indent(2)}{param_name} : {type_str}\n"
                docstring += f"{create_indent(3)}{format_description(description)}\n"

            # Kwargs
            for param_name, param in kwarg_params.items():
                p_type = getattr(param, "type", "")
                type_ = (
                    getattr(p_type, "__name__", "")
                    if inspect.isclass(p_type)
                    else p_type
                )

                if "NoneType" in str(type_):
                    type_ = f"Optional[{type_}]".replace(", NoneType", "")

                default = getattr(param, "default", "")
                description = getattr(default, "description", "")
                docstring += f"{create_indent(2)}{param_name} : {type_}\n"
                docstring += f"{create_indent(3)}{format_description(description)}\n"

        if "returns" in sections:
            # Returns
            docstring += "\n"
            docstring += f"{create_indent(2)}Returns\n"
            docstring += f"{create_indent(2)}-------\n"
            providers, _ = get_param_info(explicit_params.get("provider"))
            docstring += cls.get_OBBject_description(results_type, providers)

            # Schema
            underline = "-" * len(model_name)
            docstring += f"\n{create_indent(2)}{model_name}\n"
            docstring += f"{create_indent(2)}{underline}\n"

            for name, field in returns.items():
                field_type = cls.get_field_type(field.annotation, field.is_required())
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

        sections = SystemService().system_settings.python_settings.docstring_sections
        max_length = (
            SystemService().system_settings.python_settings.docstring_max_length
        )

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
                # Format the annotation to hide the metadata, tags, etc.
                annotation = func.__annotations__.get("return")
                results_type = (
                    cls._get_repr(
                        cls._get_generic_types(
                            annotation.model_fields["results"].annotation,  # type: ignore[union-attr,arg-type]
                            [],
                        ),
                        model_name,
                    )
                    if isclass(annotation) and issubclass(annotation, OBBject)  # type: ignore[arg-type]
                    else model_name
                )
                doc = cls.generate_model_docstring(
                    model_name=model_name,
                    summary=func.__doc__ or "",
                    explicit_params=explicit_params,
                    kwarg_params=kwarg_params,
                    returns=return_schema.model_fields,
                    results_type=results_type,
                    sections=sections,
                )
        else:
            doc = doc.replace("\n    ", f"\n{create_indent(2)}")

        if doc and examples and "examples" in sections:
            doc += cls.build_examples(
                path.replace("/", "."),
                param_types,
                examples,
            )

        if (
            max_length  # pylint: disable=chained-comparison
            and len(doc) > max_length
            and max_length > 3
        ):
            doc = doc[: max_length - 3] + "..."
        return doc

    @classmethod
    def _get_generic_types(cls, type_: type, items: list) -> List[str]:
        """Unpack generic types recursively.

        Parameters
        ----------
        type_ : type
            Type to unpack.
        items : list
            List to store the unpacked types.

        Returns
        -------
        List[str]
            List of unpacked type names.

        Examples
        --------
        Union[List[str], Dict[str, str], Tuple[str]] -> ["List", "Dict", "Tuple"]
        """
        if hasattr(type_, "__args__"):
            origin = get_origin(type_)
            # pylint: disable=unidiomatic-typecheck
            if (
                type(origin) is type
                and origin is not Annotated
                and (name := getattr(type_, "_name", getattr(type_, "__name__", None)))
            ):
                items.append(name.title())
            func = partial(cls._get_generic_types, items=items)
            set().union(*map(func, type_.__args__), items)  # type: ignore
        return items

    @staticmethod
    def _get_repr(items: List[str], model: str) -> str:
        """Get the string representation of the types list with the model name.

        Parameters
        ----------
        items : List[str]
            List of type names.
        model : str
            Model name to access the model providers.

        Returns
        -------
        str
            String representation of the unpacked types list.

        Examples
        --------
        [List, Dict, Tuple], M -> "Union[List[M], Dict[str, M], Tuple[M]]"
        """
        if s := [
            f"Dict[str, {model}]" if i == "Dict" else f"{i}[{model}]" for i in items
        ]:
            return f"Union[{', '.join(s)}]" if len(s) > 1 else s[0]
        return model


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
        return route_map.get(path)

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


class ReferenceGenerator:
    """Generate the reference for the Platform."""

    REFERENCE_FIELDS = [
        "deprecated",
        "description",
        "examples",
        "parameters",
        "returns",
        "data",
    ]

    # pylint: disable=protected-access
    pi = DocstringGenerator.provider_interface

    @classmethod
    def _get_endpoint_examples(
        cls,
        path: str,
        func: Callable,
        examples: Optional[List[Example]],
    ) -> str:
        """Get the examples for the given standard model or function.

        For a given standard model or function, the examples are fetched from the
        list of Example objects and formatted into a string.

        Parameters
        ----------
        path : str
            Path of the router.
        func : Callable
            Router endpoint function.
        examples : Optional[List[Example]]
            List of Examples (APIEx or PythonEx type)
        for the endpoint.

        Returns
        -------
        str:
            Formatted string containing the examples for the endpoint.
        """
        sig = signature(func)
        parameter_map = dict(sig.parameters)
        formatted_params = MethodDefinition.format_params(
            path=path, parameter_map=parameter_map
        )
        explicit_params = dict(formatted_params)
        explicit_params.pop("extra_params", None)
        param_types = {k: v.annotation for k, v in explicit_params.items()}

        return DocstringGenerator.build_examples(
            path.replace("/", "."),
            param_types,
            examples,
            "website",
        )

    @classmethod
    def _get_provider_parameter_info(cls, model: str) -> Dict[str, Any]:
        """Get the name, type, description, default value and optionality information for the provider parameter.

        Parameters
        ----------
        model : str
            Standard model to access the model providers.

        Returns
        -------
        Dict[str, Any]
            Dictionary of the provider parameter information
        """
        pi_model_provider = cls.pi.model_providers[model]
        provider_params_field = pi_model_provider.__dataclass_fields__["provider"]

        name = provider_params_field.name
        field_type = DocstringGenerator.get_field_type(
            provider_params_field.type, False, "website"
        )
        default_priority = provider_params_field.type.__args__
        description = (
            "The provider to use, by default None. "
            "If None, the priority list configured in the settings is used. "
            f"Default priority: {', '.join(default_priority)}."
        )

        provider_parameter_info = {
            "name": name,
            "type": field_type,
            "description": description,
            "default": None,
            "optional": True,
        }

        return provider_parameter_info

    @classmethod
    def _get_provider_field_params(
        cls,
        model: str,
        params_type: str,
        provider: str = "openbb",
    ) -> List[Dict[str, Any]]:
        """Get the fields of the given parameter type for the given provider of the standard_model.

        Parameters
        ----------
        model : str
            Model name to access the provider interface
        params_type : str
            Parameters to fetch data for (QueryParams or Data)
        provider : str
            Provider name. Defaults to "openbb".

        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries containing the field name, type, description, default,
            optional flag and standard flag for each provider.
        """
        provider_field_params = []
        expanded_types = MethodDefinition.TYPE_EXPANSION
        model_map = cls.pi.map[model]

        # TODO: Change this to read the package data instead of pi.map directly
        # We change some items (types, descriptions), so the reference.json
        # does not reflect entirely the package code.

        for field, field_info in model_map[provider][params_type]["fields"].items():
            # Determine the field type, expanding it if necessary and if params_type is "Parameters"
            field_type = field_info.annotation
            is_required = field_info.is_required()
            field_type = DocstringGenerator.get_field_type(
                field_type, is_required, "website"
            )

            cleaned_description = (
                str(field_info.description)
                .strip().replace('"', "'")
            )  # fmt: skip

            extra = field_info.json_schema_extra or {}
            choices = extra.get("choices")

            # Add information for the providers supporting multiple symbols
            if params_type == "QueryParams" and extra:
                providers: List = []
                for p, v in extra.items():  # type: ignore[union-attr]
                    if isinstance(v, dict) and v.get("multiple_items_allowed"):
                        providers.append(p)
                        choices = v.get("choices")  # type: ignore
                    elif isinstance(v, list) and "multiple_items_allowed" in v:
                        # For backwards compatibility, before this was a list
                        providers.append(p)
                    elif isinstance(v, dict) and "choices" in v:
                        choices = v.get("choices")

                if providers:
                    multiple_items = ", ".join(providers)
                    cleaned_description += (
                        f" Multiple items allowed for provider(s): {multiple_items}."
                    )
                    # Manually setting to List[<field_type>] for multiple items
                    # Should be removed if TYPE_EXPANSION is updated to include this
                    field_type = f"Union[{field_type}, List[{field_type}]]"
            elif field in expanded_types:
                expanded_type = DocstringGenerator.get_field_type(
                    expanded_types[field], is_required, "website"
                )
                field_type = f"Union[{field_type}, {expanded_type}]"

            default_value = "" if field_info.default is PydanticUndefined else field_info.default  # fmt: skip

            provider_field_params.append(
                {
                    "name": field,
                    "type": field_type,
                    "description": cleaned_description,
                    "default": default_value,
                    "optional": not is_required,
                    "choices": choices,
                }
            )

        return provider_field_params

    @staticmethod
    def _get_obbject_returns_fields(
        model: str,
        providers: str,
    ) -> List[Dict[str, str]]:
        """Get the fields of the OBBject returns object for the given standard_model.

        Parameters
        ----------
        model : str
            Standard model of the returned object.
        providers : str
            Available providers for the model.

        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries containing the field name, type, description, default
            and optionality of each field.
        """
        obbject_list = [
            {
                "name": "results",
                "type": f"List[{model}]",
                "description": "Serializable results.",
            },
            {
                "name": "provider",
                "type": f"Optional[{providers}]",
                "description": "Provider name.",
            },
            {
                "name": "warnings",
                "type": "Optional[List[Warning_]]",
                "description": "List of warnings.",
            },
            {
                "name": "chart",
                "type": "Optional[Chart]",
                "description": "Chart object.",
            },
            {
                "name": "extra",
                "type": "Dict[str, Any]",
                "description": "Extra info.",
            },
        ]

        return obbject_list

    @staticmethod
    def _get_post_method_parameters_info(
        docstring: str,
    ) -> List[Dict[str, Union[bool, str]]]:
        """Get the parameters for the POST method endpoints.

        Parameters
        ----------
        docstring : str
            Router endpoint function's docstring

        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries containing the name,type, description, default
            and optionality of each parameter.
        """
        parameters_list = []

        # Define a regex pattern to match parameter blocks
        # This pattern looks for a parameter name followed by " : ", then captures the type and description
        pattern = re.compile(
            r"\n\s*(?P<name>\w+)\s*:\s*(?P<type>[^\n]+?)(?:\s*=\s*(?P<default>[^\n]+))?\n\s*(?P<description>[^\n]+)"
        )

        # Find all matches in the docstring
        matches = pattern.finditer(docstring)

        if matches:
            # Iterate over the matches to extract details
            for match in matches:
                # Extract named groups as a dictionary
                param_info = match.groupdict()

                # Determine if the parameter is optional
                is_optional = "Optional" in param_info["type"]

                # If no default value is captured, set it to an empty string
                default_value = (
                    param_info["default"] if param_info["default"] is not None else ""
                )

                # Create a new dictionary with fields in the desired order
                param_dict = {
                    "name": param_info["name"],
                    "type": param_info["type"],
                    "description": param_info["description"],
                    "default": default_value,
                    "optional": is_optional,
                }

                # Append the dictionary to the list
                parameters_list.append(param_dict)

        return parameters_list

    @staticmethod
    def _get_post_method_returns_info(docstring: str) -> List[Dict[str, str]]:
        """Get the returns information for the POST method endpoints.

        Parameters
        ----------
        docstring: str
            Router endpoint function's docstring

        Returns
        -------
        List[Dict[str, str]]
            Single element list having a dictionary containing the name, type,
            description of the return value
        """
        returns_list = []

        # Define a regex pattern to match the Returns section
        # This pattern captures the model name inside "OBBject[]" and its description
        match = re.search(r"Returns\n\s*-------\n\s*([^\n]+)\n\s*([^\n]+)", docstring)

        if match:
            return_type = match.group(1).strip()  # type: ignore
            # Remove newlines and indentation from the description
            description = match.group(2).strip().replace("\n", "").replace("    ", "")  # type: ignore
            # Adjust regex to correctly capture content inside brackets, including nested brackets
            content_inside_brackets = re.search(
                r"OBBject\[\s*((?:[^\[\]]|\[[^\[\]]*\])*)\s*\]", return_type
            )
            return_type = content_inside_brackets.group(1)  # type: ignore

            returns_list = [
                {
                    "name": "results",
                    "type": return_type,
                    "description": description,
                }
            ]

        return returns_list

    @classmethod
    def get_paths(cls, route_map: Dict[str, BaseRoute]) -> Dict[str, Dict[str, Any]]:
        """Get path reference data.

        The reference data is a dictionary containing the description, parameters,
        returns and examples for each endpoint. This is currently useful for
        automating the creation of the website documentation files.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary containing the description, parameters, returns and
            examples for each endpoint.
        """
        reference: Dict[str, Dict] = {}

        for path, route in route_map.items():
            # Initialize the provider parameter fields as an empty dictionary
            provider_parameter_fields = {"type": ""}
            # Initialize the reference fields as empty dictionaries
            reference[path] = {field: {} for field in cls.REFERENCE_FIELDS}
            # Route method is used to distinguish between GET and POST methods
            route_method = getattr(route, "methods", None)
            # Route endpoint is the callable function
            route_func = getattr(route, "endpoint", lambda: None)
            # Attribute contains the model and examples info for the endpoint
            openapi_extra = getattr(route, "openapi_extra", {})
            # Standard model is used as the key for the ProviderInterface Map dictionary
            standard_model = openapi_extra.get("model", "")
            # Add endpoint model for GET methods
            reference[path]["model"] = standard_model
            # Add endpoint deprecation details
            reference[path]["deprecated"] = {
                "flag": MethodDefinition.is_deprecated_function(path),
                "message": MethodDefinition.get_deprecation_message(path),
            }
            # Add endpoint examples
            examples = openapi_extra.get("examples", [])
            reference[path]["examples"] = cls._get_endpoint_examples(
                path,
                route_func,
                examples,  # type: ignore
            )
            # Add data for the endpoints having a standard model
            if route_method == {"GET"}:
                reference[path]["description"] = getattr(
                    route, "description", "No description available."
                )

                # TODO: The reference is not getting populated when a command does not use a standard model
                # Access model map from the ProviderInterface
                model_map = cls.pi.map.get(standard_model, {})

                for provider in model_map:
                    if provider == "openbb":
                        # openbb provider is always present hence its the standard field
                        reference[path]["parameters"]["standard"] = (
                            cls._get_provider_field_params(
                                standard_model, "QueryParams"
                            )
                        )
                        # Add `provider` parameter fields to the openbb provider
                        provider_parameter_fields = cls._get_provider_parameter_info(
                            standard_model
                        )

                        # Add endpoint data fields for standard provider
                        reference[path]["data"]["standard"] = (
                            cls._get_provider_field_params(standard_model, "Data")
                        )
                        continue

                    # Adds provider specific parameter fields to the reference
                    reference[path]["parameters"][provider] = (
                        cls._get_provider_field_params(
                            standard_model, "QueryParams", provider
                        )
                    )

                    # Adds provider specific data fields to the reference
                    reference[path]["data"][provider] = cls._get_provider_field_params(
                        standard_model, "Data", provider
                    )

                    # Remove choices from 'standard' if choices for a parameter exist
                    # for both standard and provider, and are the same
                    standard = [
                        {d["name"]: d["choices"]}
                        for d in reference[path]["parameters"]["standard"]
                        if d.get("choices")
                    ]
                    standard = standard[0] if standard else []  # type: ignore
                    _provider = [
                        {d["name"]: d["choices"]}
                        for d in reference[path]["parameters"][provider]
                        if d.get("choices")
                    ]
                    _provider = _provider[0] if _provider else []  # type: ignore
                    if standard and _provider and standard == _provider:
                        for i, d in enumerate(
                            reference[path]["parameters"]["standard"]
                        ):
                            if d.get("name") in standard:
                                reference[path]["parameters"]["standard"][i][
                                    "choices"
                                ] = None

                # Add endpoint returns data
                # Currently only OBBject object is returned
                providers = provider_parameter_fields["type"]
                reference[path]["returns"]["OBBject"] = cls._get_obbject_returns_fields(
                    standard_model, providers
                )
            # Add data for the endpoints without a standard model (data processing endpoints)
            elif route_method == {"POST"}:
                # POST method router `description` attribute is unreliable as it may or
                # may not contain the "Parameters" and "Returns" sections. Hence, the
                # endpoint function docstring is used instead.
                docstring = getattr(route_func, "__doc__", "")
                description = docstring.split("Parameters")[0].strip()
                # Remove extra spaces in between the string
                reference[path]["description"] = re.sub(" +", " ", description)
                # Add endpoint parameters fields for POST methods
                reference[path]["parameters"]["standard"] = (
                    cls._get_post_method_parameters_info(docstring)
                )
                # Add endpoint returns data
                # Currently only OBBject object is returned
                reference[path]["returns"]["OBBject"] = (
                    cls._get_post_method_returns_info(docstring)
                )

        return reference

    @classmethod
    def get_routers(cls, route_map: Dict[str, BaseRoute]) -> Dict[str, Dict[str, Any]]:
        """Get router reference data.

        Parameters
        ----------
        route_map : Dict[str, BaseRoute]
            Dictionary containing the path and route object for the router.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary containing the description for each router.
        """
        main_router = RouterLoader.from_extensions()
        routers = {}
        for path in route_map:
            path_parts = path.split("/")
            # We start at 2: ["/", "some_router"] "/some_router"
            i = 2
            p = "/".join(path_parts[:i])
            while p != path:
                if p not in routers:
                    description = main_router.get_attr(p, "description")
                    if description is not None:
                        routers[p] = {"description": description}
                # We go down the path to include sub-routers
                i += 1
                p = "/".join(path_parts[:i])
        return routers
