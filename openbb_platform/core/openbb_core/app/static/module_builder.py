import sys
from inspect import _empty, signature
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Type,
    get_args,
    get_type_hints,
)

from openbb_core.app.static.method_definition import MethodDefinition
from openbb_core.app.static.path_handler import PathHandler


class ModuleBuilder:
    """Build the module for the Platform."""

    @classmethod
    def build(cls, path: str, ext_map: Optional[Dict[str, List[str]]] = None) -> str:
        """Build the module."""
        code = "### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###\n\n"
        code += cls.build_import_definition(path=path)
        code += cls.build_class_definition(path, ext_map)

        return code

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
    def build_import_definition(cls, path: str) -> str:
        """Build the import definition."""
        hint_type_list = cls.get_path_hint_type_list(path=path)
        code = "from openbb_core.app.static.container import Container"
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

    @staticmethod
    def build_class_definition(
        path: str, ext_map: Optional[Dict[str, List[str]]] = None
    ) -> str:
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
                    examples=route.openapi_extra.get("examples", None),
                )  # type: ignore
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
