"""Obtain the integration test coverage for the OpenBB Terminal."""

# IMPORT STANDARD
import importlib
import inspect
import json
import os
import re
from pathlib import Path

# IMPORT THIRD-PARTY
import pandas as pd

from openbb_terminal.core.integration_tests.utils import to_section_title

# IMPORT INTERNAL
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console

INTEGRATION_PATH = "./openbb_terminal/miscellaneous/integration_tests_scripts"


def find_controllers() -> list:
    """Find all controllers in the OpenBB Terminal."""
    controllers = []

    for root, _, files in os.walk("./openbb_terminal"):
        for file in files:
            if file.endswith("_controller.py") and "sdk" not in root:
                controllers.append(os.path.join(root, file))

    return controllers


def find_integration_tests() -> list:
    """Find all integration tests in the OpenBB Terminal."""
    test = []
    for root, _, files in os.walk(INTEGRATION_PATH):
        for file in files:
            if file.endswith(".openbb"):
                test.append(os.path.join(root, file))

    test = [
        re.sub(r"^\./openbb_terminal/miscellaneous/integration_tests_scripts", "", i)
        for i in test
    ]
    return test


def create_matching_dict() -> dict:
    """Fill the controller and integration test matches by outlier files."""
    return {
        "./openbb_terminal/mutual_funds/mutual_fund_controller.py": "/mutual_funds/test_mutual_fund.openbb",
        "./openbb_terminal/stocks/options/screen/screener_controller.py": "/stocks/test_screen.openbb",
        "./openbb_terminal/stocks/discovery/disc_controller.py": "/stocks/test_disc.openbb",
    }


def match_controller_with_test(controllers: list, tests: list) -> dict:
    """Match controllers with integration tests."""
    matched = create_matching_dict()

    for key, value in matched.items():
        controllers.remove(key)
        tests.remove(value)

    for controller in controllers:
        try:
            controller_name = re.search(  # type: ignore
                r"(?<=/)[a-zA-Z]+(?=_controller)", controller
            ).group(0)
        except AttributeError:
            controller_name = "mutual_fund"

        for test in tests:
            try:
                test_name = re.search(r"(?<=/test_)[a-zA-Z]+(?=.openbb)", test).group(0)  # type: ignore
            except AttributeError:
                test_name = "mutual_fund"

            if controller_name == test_name:
                if controller_name in ["ta", "qa"]:
                    controller_path = re.search(  # type: ignore
                        r"(?<=openbb_terminal/)[a-zA-Z/]+(?=/)", controller
                    ).group(0)
                    if controller_path in test:
                        matched[controller] = test
                        tests.remove(test)
                else:
                    matched[controller] = test
                    tests.remove(test)

    if len(tests) > 0:
        console.print(f"[red]Unmatched tests: {tests}[/red]")

    return matched


def get_module(module_path: str, module_name: str = "") -> object:
    """Obtain a module from a given path."""
    module = importlib.import_module(module_path)
    if module_name == "":
        module_name = re.sub(r".*\.", "", module.__name__)
        module_name = "".join([word.capitalize() for word in module_name.split("_")])
    try:
        module = getattr(module, module_name)
        return module
    except AttributeError:
        raise ModuleNotFoundError  # pylint: disable=raise-missing-from


def get_functions(module: object) -> list:
    """Obtain all functions from a given module."""
    filter_func = [
        "about",
        "cls",
        "home",
        "record",
        "resources",
        "screenshot",
        "stop",
        "support",
        "whoami",
        "wiki",
    ]
    functions = []
    for name in dir(module):
        if name.startswith("call_"):
            functions.append(name[5:])

    functions = [function for function in functions if function not in filter_func]
    return functions


def get_tested_commands(test_file: str) -> list:
    """Obtain all functions that are called in a given test file."""
    tested_commands = []
    with open(test_file) as f:
        for line in f:
            try:
                function = line.split()[0]
            except IndexError:
                continue

            if function != "#":
                tested_commands.append(function)

    tested_commands = list(dict.fromkeys(tested_commands))
    return list(tested_commands)


def find_all_calls(module) -> list:
    """Find all function calls in a module."""
    calls = []
    module_dict = module.__dict__
    for key, _ in module_dict.items():
        if "call_" in key:
            calls.append(key)
    return calls


def parse_args(module, func) -> list:
    """Parse the arguments of a given module function."""
    filters = [
        "-ape",
        "-yacht",
        "-club",
        "-h",
        "-to",
        "-seeking",
        "-sloping",
        "-neutral",
        "-known",
        "-yields",
        "-level",
        "-rating",
        "-traded",
        "-frens",
        "-ad",
        "-sheet",
        "-flow",
        "-weighted",
        "-curve",
        "-year",
    ]
    source = inspect.getsource(module.__dict__[func])
    params = re.findall(r"-\w+", source)
    params = [param for param in params if not param[1:].isupper()]
    params = [param for param in params if not param[1:].isdigit()]
    params = [param for param in params if not param[1].isupper()]
    params = [param for param in params if param not in filters]
    params = list(dict.fromkeys(params))
    return params


def get_tested_function_params(tested_commands: list, test_file: str) -> list:
    """Obtain all function parameters that are called in a given test file."""
    tested_commands = []
    with open(test_file) as f:
        for line in f:
            try:
                function = line.split()[0]
            except IndexError:
                continue

            params = re.findall(r"-\w+", line)
            tested_commands.append((function, params))
    return tested_commands


def map_module_to_calls(module) -> dict:
    """Map module to its function calls and parameters."""
    calls = find_all_calls(module)
    calls_dict = {}
    for call in calls:
        calls_dict[call] = parse_args(module, call)

    calls_dict = {k[5:]: v for k, v in calls_dict.items()}
    return calls_dict


def get_missing_params(
    tested_function_params: list, controller: str, module_dict: dict
) -> dict:
    """Get missing parameters for a given function."""
    missing_params = {}
    for function, params in tested_function_params:
        if function != controller:
            try:
                all_params = module_dict[function]
            except KeyError:
                # this catches the (sub)menu
                continue

            if set(params).issubset(set(all_params)):
                all_params = [param for param in all_params if param not in params]
                for param in params:
                    if param in all_params:
                        all_params.remove(param)
            else:
                unpacked_params = []
                used_unabbreviated_params = []
                for param in params:
                    unpacked_params.append(param)

                for param in unpacked_params:
                    for unabbreviated_param in all_params:
                        if unabbreviated_param.startswith(param):
                            used_unabbreviated_params.append(unabbreviated_param)

                missing_params[function] = [
                    param for param in all_params if param not in params
                ]

                for param in all_params:
                    for param2 in used_unabbreviated_params:
                        if param2.startswith(param):
                            try:
                                missing_params[function].remove(param)
                                missing_params[function].remove(param2)
                            except ValueError:
                                pass

                missing_params[function] = [
                    param
                    for param in missing_params[function]
                    if param not in used_unabbreviated_params
                ]

            try:
                missing_params[function] = list(dict.fromkeys(missing_params[function]))
            except KeyError:
                # this catches the (sub)menu
                continue

    for key, value in missing_params.items():
        missing_params[key] = list(value)
        for param in value:
            for param2 in value:
                if param != param2 and param2.startswith(param):
                    try:
                        missing_params[key].remove(param)
                        missing_params[key].remove(param2)
                    except ValueError:
                        pass

    missing_params = {k: v for k, v in missing_params.items() if v}

    return missing_params


def validate_missing_params(missing_params: dict, test_file: str) -> dict:
    """Validate missing parameters."""
    with open(test_file) as f:
        lines = f.readlines()
        for key, values in missing_params.items():
            for line in lines:
                for value in values:
                    if key in line and value in line:
                        missing_params[key].remove(value)

    missing_params = {k: v for k, v in missing_params.items() if v}
    return missing_params


def calculate_function_coverage(
    tested_commands: list,
    tested_function: str,
    module: object,
    limit: int = 5,
    output_table: bool = True,
) -> dict:
    """Compare tested functions with module."""
    module_dict = map_module_to_calls(module)
    tested_function_params = get_tested_function_params(
        tested_commands, tested_function
    )
    try:
        controller = str(module).split(".")[3].split("_")[0]
    except IndexError:
        controller = str(module).split(".")[2].split("_")[0]

    missing_params = get_missing_params(tested_function_params, controller, module_dict)
    # if the module is fixedincome, we need to remove the -term parameter
    if controller == "FixedIncomeController'>":
        for key, value in missing_params.items():
            try:
                missing_params[key].remove("-term")
            except ValueError:
                pass
        missing_params = {k: v for k, v in missing_params.items() if v}

    coverage_dict = {}
    for key, value in missing_params.items():
        try:
            coverage_dict[key] = round(
                (len(module_dict[key]) - len(value)) / len(module_dict[key]) * 100, 2
            )
        except ZeroDivisionError:
            coverage_dict[key] = 100
        if not output_table:
            console.print(f"[red]Coverage for {key}: {coverage_dict[key]}%[/red]")

    for key, value in module_dict.items():
        if key not in coverage_dict:
            coverage_dict[key] = 100

    if output_table:
        df = pd.DataFrame(
            coverage_dict.items(),
            columns=["Function", "Coverage %"],
        ).sort_values(by=["Coverage %"], ascending=True)
        average_coverage = round(df["Coverage %"].mean(), 2)
        df["Coverage %"] = df[  # pylint: disable=unsupported-assignment-operation
            "Coverage %"
        ].apply(lambda x: f"[green]{x}[/green]" if x >= 80 else f"[red]{x}[/red]")
        console.print("Integration Test Parameter Coverage")
        print_rich_table(
            df,
            headers=[
                "Function",
                f"Coverage {average_coverage}%",
            ],
            limit=limit,
        )

    if len(missing_params) > 0:
        missing_params = validate_missing_params(missing_params, tested_function)
        console.print(f"[red]Missing params: {missing_params}[/red]")

    return missing_params


def calculate_coverage_percentage(
    tested_commands: list, available_functions: list, output_table: bool = False
) -> tuple[float, list]:
    """Calculate the integration test coverage."""
    untested_commands = []
    coverage = min(100, round(len(tested_commands) / len(available_functions) * 100, 2))
    for function in available_functions:
        if function not in tested_commands:
            untested_commands.append(function)

    if output_table:
        df = pd.DataFrame({"function": available_functions})
        df["tested"] = df["function"].apply(lambda x: x in tested_commands)
        df = df.sort_values(by=["function"])
        df = df.astype({"tested": "str"})
        df["tested"] = df["tested"].apply(
            lambda x: "[red]False[/red]" if x == "False" else "[green]True[/green]"
        )
        print_rich_table(
            df,
            headers=[x.title() for x in df.columns],
            show_index=False,
            title=f"Integration test coverage: {coverage}%",
            automatic_coloring=True,
            columns_to_auto_color=["tested"],
        )
    else:
        console.print(
            f"Integration test coverage: {coverage}%\n"
            f"=======================================\n"
            f"[red]Untested commands: {untested_commands}[/red]\n"
            f"[green]Tested commands: {tested_commands}[/green]\n"
            f"=======================================\n"
        )

    return coverage, untested_commands


def get_coverage_all_controllers(output_table: bool = False) -> None:
    """Get integration test coverage for all controllers."""
    summary = {}

    parent_dir = os.path.join(Path(__file__).parent)
    with open(os.path.join(parent_dir, "controllers.json")) as f:
        controller_name_mapping = json.load(f)

    controllers = find_controllers()
    tests = find_integration_tests()
    matched = match_controller_with_test(controllers, tests)

    for controller, test in matched.items():
        path = controller.replace("/", ".")[2:-3]
        try:
            module = get_module(path)
        except ModuleNotFoundError:
            module_name = controller_name_mapping.get(path, "")
            try:
                module = get_module(path, module_name=module_name)
            except ModuleNotFoundError:
                console.print(f"Module {module_name} not found!")
        except OSError as e:
            console.print(e)
            continue

        available_functions = get_functions(module)
        tested_commands = get_tested_commands(INTEGRATION_PATH + test)

        console.print(to_section_title(controller), "\n")
        coverage, untested_commands = calculate_coverage_percentage(
            tested_commands, available_functions, output_table=output_table
        )
        missing_params = calculate_function_coverage(
            tested_commands, INTEGRATION_PATH + test, module
        )

        console.print(f"Finished calculating coverage for {controller}\n\n")

        summary[controller] = {
            "Coverage": coverage,
            "Untested commands": untested_commands,
            "Missing params": missing_params,
        }

    display_coverage_summary(summary)


def display_coverage_summary(summary: dict) -> None:
    """Display the coverage summary.

    Parameters
    ----------
    summary: dict
        Summary of the integration test coverage.
    """

    console.print(to_section_title("Integration Coverage Summary"))
    summary = dict(
        sorted(
            summary.items(), key=lambda item: item[1]["Coverage"], reverse=False  # type: ignore
        )
    )
    for key, value in summary.items():
        coverage = value["Coverage"]
        untested = value.get("Untested commands", [])
        missing = value.get("Missing params", {})

        console.print(f"[bold]\n{key}[/bold]")

        console.print(f"* Coverage: {coverage}%")

        if untested:
            console.print(f"* [red]Untested functions: {untested}[/red]")
        else:
            console.print("* [green]All functions tested![/green]")

        if missing:
            console.print(f"* [red]Missing params: {missing}[/red]")
        else:
            console.print("* [green]All params tested![/green]")


def get_coverage_single_controller(
    controller: str,
    integration_test: str,
    module_name: str = "",
    output_table: bool = False,
) -> None:
    """Get single controller integration test coverage.

    Parameters
    ----------
        controller (str): Controller to test.
        integration_test (str): Integration test to use.
        output_table (bool): Output a table with the results.

    Example:
    --------
        test_single_controller(
            "openbb_terminal.stocks.stocks_controller",
            "/stocks/test_stocks.openbb"
        )

    """
    module = get_module(controller, module_name=module_name)
    functions = get_functions(module)
    tested_commands = get_tested_commands(INTEGRATION_PATH + integration_test)
    calculate_coverage_percentage(tested_commands, functions, output_table)
    calculate_function_coverage(
        tested_commands, INTEGRATION_PATH + integration_test, module
    )
