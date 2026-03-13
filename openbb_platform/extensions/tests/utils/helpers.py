"""Test helpers."""

import doctest
import glob
import importlib
import inspect
import logging
import os
import re
from ast import AsyncFunctionDef, Call, FunctionDef, Name, parse, unparse
from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from inspect import getmembers, isfunction
from sys import version_info
from typing import Any

from importlib_metadata import EntryPoints
from openbb_core.app.provider_interface import ProviderInterface

pi = ProviderInterface()

logging.basicConfig(level=logging.INFO)


def get_packages_info() -> dict[str, str]:
    """Get the paths and names of all the static packages."""
    paths_and_names: dict[str, str] = {}
    package_paths = glob.glob("openbb_platform/core/openbb/package/*.py")
    for path in package_paths:
        name = os.path.basename(path).split(".")[0]
        paths_and_names[path] = name

    paths_and_names = {
        path: name for path, name in paths_and_names.items() if not name.startswith("_")
    }
    return paths_and_names


def execute_docstring_examples(module_name: str, path: str) -> list[str]:
    """Execute the docstring examples of a module."""
    errors = []
    module = importlib.import_module(f"openbb.package.{module_name}")
    doc_tests = doctest.DocTestFinder().find(module)

    for dt in doc_tests:
        code = "".join([ex.source for ex in dt.examples])
        try:
            print(f"* Executing example from {path}")  # noqa: T201
            exec(code)  # pylint: disable=exec-used  # noqa: S102
        except Exception as e:
            error = f"{'_' * 136}\nPath: {path}\nCode:\n{code}\nError: {str(e)}\n{'_' * 136}"
            print(error)  # noqa: T201
            errors.append(error)

    return errors


def check_docstring_examples() -> list[str]:
    """Test that the docstring examples execute without errors."""
    errors = []
    paths_and_names = get_packages_info()

    for path, name in paths_and_names.items():
        result = execute_docstring_examples(name, path)
        if result:
            errors.extend(result)

    return errors


def filter_eps(eps: EntryPoints | dict, group: str) -> tuple[EntryPoint, ...]:
    if version_info[:2] == (3, 12):
        return eps.select(group=group) or ()  # type: ignore[union-attr]
    return eps.get(group, ())  # type: ignore[union-attr]


def list_openbb_extensions() -> tuple[set[str], set[str], set[str]]:
    """list installed openbb extensions and providers.

    Returns
    -------
    Tuple[Set[str], Set[str], Set[str]]
        First element: set of installed core extensions.
        Second element: set of installed provider extensions.
        Third element: set of installed obbject extensions.
    """

    core_extensions = set()
    provider_extensions = set()
    obbject_extensions = set()

    entry_points_dict = entry_points()

    # Compatibility for different Python versions
    if hasattr(entry_points_dict, "select"):  # Python 3.12+
        core_entry_points = entry_points_dict.select(group="openbb_core_extension")
        provider_entry_points = entry_points_dict.select(
            group="openbb_provider_extension"
        )
        obbject_entry_points = entry_points_dict.select(
            group="openbb_obbject_extension"
        )
    else:
        core_entry_points = entry_points_dict.get("openbb_core_extension", [])  # type: ignore  pylint: disable=E1101
        provider_entry_points = entry_points_dict.get("openbb_provider_extension", [])  # type: ignore  pylint: disable=E1101
        obbject_entry_points = entry_points_dict.get("openbb_obbject_extension", [])  # type: ignore  pylint: disable=E1101

    for entry_point in core_entry_points:
        core_extensions.add(f"{entry_point.name}")

    for entry_point in provider_entry_points:
        provider_extensions.add(f"{entry_point.name}")

    for entry_point in obbject_entry_points:
        obbject_extensions.add(f"{entry_point.name}")

    return core_extensions, provider_extensions, obbject_extensions


def collect_routers(target_dir: str) -> list[str]:
    """Collect all routers in the target directory."""
    current_dir = os.path.dirname(__file__)
    base_path = os.path.abspath(os.path.join(current_dir, "../../../"))

    full_target_path = os.path.abspath(os.path.join(base_path, target_dir))
    routers = []

    for root, _, files in os.walk(full_target_path):
        for name in files:
            if name.endswith("_router.py"):
                full_path = os.path.join(root, name)
                # Convert the full path to a module path
                relative_path = os.path.relpath(full_path, base_path)
                module_path = (
                    relative_path.replace("\\", ".")
                    .replace("/", ".")
                    .replace(".py", "")
                )
                routers.append(module_path)

    return routers


def import_routers(routers: list) -> list:
    """Import all routers."""
    loaded_routers: list = []
    for router in routers:
        module = importlib.import_module(router)
        loaded_routers.append(module)

    return loaded_routers


def collect_router_functions(loaded_routers: list) -> dict:
    """Collect all router functions."""
    router_functions = {}
    for router in loaded_routers:
        router_functions[router.__name__] = [
            function[1]
            for function in getmembers(router, isfunction)
            if function[0] != "router"
        ]

    return router_functions


def find_decorator(file_path: str, function_name: str) -> str:
    """Find the @router.command decorator of the function in the file, supporting multiline decorators."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    normalized_dir = this_dir.replace("\\", "/")
    base_path = normalized_dir.split("openbb_platform/")[0]
    file_path = os.path.join(base_path, "openbb_platform", file_path)

    with open(file_path) as file:
        lines = file.readlines()

    decorator_lines = []
    capturing_decorator = False
    for line in lines:
        stripped_line = line.strip()
        # Start capturing lines if we encounter a decorator
        if stripped_line.startswith("@router.command"):
            capturing_decorator = True
            decorator_lines.append(stripped_line)
        elif capturing_decorator:
            # If we're currently capturing a decorator and the line is part of it (indentation or open parenthesis)
            if (
                stripped_line.startswith("@")
                or "def" in stripped_line
                and function_name in stripped_line
            ):
                # If we've reached another decorator or the function definition, stop capturing
                capturing_decorator = False
                # If it's the target function, break, else clear decorator_lines for the next decorator
                if "def" in stripped_line and function_name in stripped_line:
                    break
                decorator_lines = []
            else:
                # It's part of the multiline decorator
                decorator_lines.append(stripped_line)

    decorator = " ".join(decorator_lines)
    return decorator


@dataclass
class Decorator:
    """Decorator."""

    name: str
    args: dict | None = None
    kwargs: dict | None = None


def get_decorator_details(function) -> Decorator | None:
    """Extract decorators and their arguments from a function."""
    source = inspect.getsource(function)
    parsed_source = parse(source)

    if isinstance(parsed_source.body[0], (FunctionDef, AsyncFunctionDef)):
        func_def = parsed_source.body[0]
        for decorator in func_def.decorator_list:
            if isinstance(decorator, Call):
                name = (
                    decorator.func.id
                    if isinstance(decorator.func, Name)
                    else unparse(decorator.func)
                )
                args = {i: unparse(arg) for i, arg in enumerate(decorator.args)}
                kwargs = {kw.arg: unparse(kw.value) for kw in decorator.keywords}
            else:
                name = (
                    decorator.id if isinstance(decorator, Name) else unparse(decorator)
                )
        return Decorator(name, args, kwargs)
    return None


def find_missing_router_function_models(
    router_functions: dict, pi_map: dict
) -> list[str]:
    """Find the missing models in the router functions."""
    missing_models: list[str] = []
    for router_name, functions in router_functions.items():
        for function in functions:
            decorator = find_decorator(
                os.path.join(*router_name.split(".")) + ".py",
                function.__name__,
            )
            if (
                decorator
                and "model" in decorator
                and "POST" not in decorator
                and "GET" not in decorator
            ):
                if (
                    returns := str(function.__annotations__.get("return"))
                ) and returns.rsplit(".", maxsplit=1)[-1].startswith("OBBject"):
                    model = returns.rsplit("_", maxsplit=1)[-1].replace("'>", "")
                else:
                    model = decorator.split("model=")[1].split(",")[0].strip('"')
                if (
                    model not in pi_map
                    and "POST" not in decorator
                    and "GET" not in decorator
                ):
                    missing_models.append(
                        f"{function.__name__} in {router_name} model doesn't exist in the provider interface map."
                    )

    return missing_models


def parse_example_string(example_string: str) -> dict[str, Any]:
    """Parse a string of examples into nested dictionaries.

    This is capturing all instances of PythonEx and APIEx, including their "parameters", "code", and "description".
    """
    # Initialize the result dictionary
    result = {}

    # Regular expression patterns to find PythonEx and APIEx examples
    pythonex_pattern = r"PythonEx\(.*?code=(\[.*?\]).*?\)"
    apiex_pattern = r"APIEx\(.*?parameters=(\{.*?\}).*?\)"

    # Function to parse individual examples
    def parse_examples(matches, example_type):
        examples = []
        for match in matches:
            examples.append(
                {"code": [match]} if example_type == "PythonEx" else {"params": match}
            )
        return examples

    # Find and parse all PythonEx examples
    pythonex_matches = re.findall(pythonex_pattern, example_string, re.DOTALL)
    result["PythonEx"] = parse_examples(pythonex_matches, "PythonEx")

    # Find and parse all APIEx examples
    apiex_matches = re.findall(apiex_pattern, example_string, re.DOTALL)
    result["APIEx"] = parse_examples(apiex_matches, "APIEx")

    return result


def get_required_fields(model: str) -> list[str]:
    """Get the required fields of a model."""
    fields = pi.map[model]["openbb"]["QueryParams"]["fields"]
    return [field for field, info in fields.items() if info.is_required()]


def get_all_fields(model: str) -> list[str]:
    """Get all the fields of a model."""
    all_fields: list[str] = []
    info = pi.map[model]
    # for every key, grab the fields
    for _, provider_info in info.items():
        for field, _ in provider_info["QueryParams"]["fields"].items():
            all_fields.append(field)

    return all_fields
