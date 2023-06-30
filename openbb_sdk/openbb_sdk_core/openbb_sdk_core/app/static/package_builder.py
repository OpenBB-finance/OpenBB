from inspect import Parameter, _empty, signature
from json import dumps
from pathlib import Path
from typing import (
    Callable,
    Dict,
    List,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from uuid import NAMESPACE_DNS, uuid5

import pandas as pd
from starlette.routing import BaseRoute

from openbb_sdk_core.app.router import RouterLoader


class PackageBuilder:
    @staticmethod
    def write_to_package(module_code: str, module_name, extension="py") -> None:
        package_folder = Path(__file__).parent / "package"
        package_path = package_folder / f"{module_name}.{extension}"

        package_folder.mkdir(exist_ok=True)

        print(package_path)

        with package_path.open("w") as file:
            file.write(module_code)

    @classmethod
    def save_module_map(cls):
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        module_map = {
            PathHandler.build_module_name(path=path): path for path in path_list
        }
        module_code = dumps(obj=module_map, indent=4)
        module_name = "module_map"
        cls.write_to_package(
            module_code=module_code, module_name=module_name, extension="json"
        )

    @classmethod
    def save_modules(cls):
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)

        for path in path_list:
            route = PathHandler.get_route(path=path, route_map=route_map)
            if route is None:
                module_code = ModuleBuilder.build(path=path)
                module_name = PathHandler.build_module_name(path=path)
                cls.write_to_package(module_code=module_code, module_name=module_name)

    @classmethod
    def save_package_package(cls):
        cls.write_to_package(module_code="", module_name="__init__")

    @classmethod
    def build(cls) -> None:
        cls.save_module_map()
        cls.save_modules()
        cls.save_package_package()


class ModuleBuilder:
    @staticmethod
    def build(path: str) -> str:
        code = ImportDefinition.build(path=path)
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
            hint_type = get_args(get_type_hints(return_type)["item"])[0]
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
        code = "\nfrom openbb_sdk_core.app.static.container import Container\n"
        code += "\nfrom openbb_sdk_core.app.model.command_output import CommandOutput\n"
        # This is a patch, openbb_provider was not being imported for some reason. Remove when we merge the repos.
        code += "\nimport openbb_provider\n"

        module_list = [hint_type.__module__ for hint_type in hint_type_list]
        module_list = list(set(module_list))
        module_list.sort()

        for module in module_list:
            code += f"\nimport {module}\n"

        return code


class ClassDefinition:
    @staticmethod
    def build(path: str) -> str:
        class_name = PathHandler.build_module_class(path=path)
        code = f'\nclass {class_name}(Container): # route = "{path}"\n'
        route_map = PathHandler.build_route_map()
        path_list = PathHandler.build_path_list(route_map=route_map)
        child_path_list = PathHandler.get_child_path_list(
            path=path,
            path_list=path_list,
        )
        for child_path in child_path_list:
            route = PathHandler.get_route(path=child_path, route_map=route_map)
            if route:
                code += MethodDefinition.build_command_method(path=route.path, func=route.endpoint)  # type: ignore
            else:
                code += MethodDefinition.build_class_loader_method(path=child_path)

        return code


class MethodDefinition:
    @staticmethod
    def build_class_loader_method(path: str) -> str:
        module_name = PathHandler.build_module_name(path=path)
        class_name = PathHandler.build_module_class(path=path)
        function_name = path.rsplit("/", maxsplit=1)[-1].strip("/")

        code = "    @property\n"
        code += f'    def {function_name}(self):  # route = "{path}"\n'
        code += (
            f"        from openbb_sdk_core.app.static.package import {module_name}\n"
        )
        code += f"        return {module_name}.{class_name}(command_runner_session=self._command_runner_session)\n"

        return code

    @staticmethod
    def build_command_method_signature(
        func_name: str, parameter_map: Dict[str, Parameter], return_type: type
    ) -> str:
        func_params = ", ".join(str(param) for param in parameter_map.values())

        # Populate this list exaustively or find a better solution to handle typing. types in signature
        typing_types = ["List", "Literal", "Union", "Optional", "Dict"]

        for typing_type in typing_types:
            func_params = func_params.replace(
                f"{typing_type}[", f"typing.{typing_type}["
            )

        # Return
        if return_type == _empty:
            func_return = "None"
        elif return_type.__module__ == "builtins":
            func_return = return_type.__name__
        else:
            item_type = get_args(get_type_hints(return_type)["item"])[0]
            if item_type.__module__ == "builtins":
                func_return = f"CommandOutput[{item_type.__name__}]"
            elif get_origin(item_type) == list:
                inner_type = get_args(item_type)[0]
                select = f"[{inner_type.__module__}.{inner_type.__name__}]"
                func_return = f"CommandOutput[{item_type.__module__}.{item_type.__name__}{select}]"
            else:
                func_return = (
                    f"CommandOutput[{item_type.__module__}.{item_type.__name__}]"
                )

        code = f"\n    def {func_name}(self, {func_params}) -> {func_return}:\n"

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

        code = "        return self._command_runner_session.run(\n"
        code += f"""            "{path}",\n"""
        for param in parameter_map:
            param_var = "kwargs" if param == "extra_params" else param
            code += f"            {param} = {param_var},\n"
        code += "        ).output\n"

        return code

    @classmethod
    def build_command_method(cls, path: str, func: Callable) -> str:
        # Name
        func_name = func.__name__

        # Parameters
        sig = signature(func)
        parameter_map = dict(sig.parameters)
        parameter_map.pop("cc", None)
        if "extra_params" in parameter_map:
            parameter_map["extra_params"] = Parameter(
                name="kwargs", kind=Parameter.VAR_KEYWORD
            )

        if "data" in parameter_map:
            parameter_map["data"] = Parameter(
                name="data",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Union[
                    pd.DataFrame, parameter_map["data"].annotation  # noqa: 258
                ],
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
        router = RouterLoader.from_plugins()
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
                path_reminder = p[len(path) :]
                if path_reminder.count("/") == 1:
                    direct_children.append(p)

        return direct_children

    @staticmethod
    def hash_path(path: str) -> str:
        return str(uuid5(NAMESPACE_DNS, path)).replace("-", "_")

    @classmethod
    def build_module_name(cls, path: str) -> str:
        return f"MODULE_{cls.hash_path(path=path)}"

    @classmethod
    def build_module_class(cls, path: str) -> str:
        return f"CLASS_{cls.hash_path(path=path)}"
